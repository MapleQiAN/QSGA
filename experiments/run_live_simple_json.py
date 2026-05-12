"""Run live Simple JSON baseline diagnostics.

The baseline asks the model for an ordinary strategy JSON object rather than
QYIR. A deterministic adapter then attempts to map that object into QYIR and
passes the result through the same verifier/compiler/risk-audit chain used by
QSGA. The purpose is to separate "valid JSON is easy" from "domain-valid QYIR
is verifiable and compilable".
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    MethodResult,
    clarification_result,
    load_benchmark,
    query_needs_clarification,
)
from experiments.run_live_constrained_qyir import ConstrainedOpenAIClient
from experiments.run_live_llm import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    MODEL_ALIASES,
    RawCall,
    _evaluate_qyir,
    _failed_result,
    _method_result,
    _parse_json,
    guard_api_terms,
    normalize_model_name,
    read_api_key,
    select_records,
    write_audit_jsonl,
    write_metadata,
    write_token_usage,
)
from qyir.validator import validate_qyir
from verifier.safe_rejection import should_reject


DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_CASE_LIMIT = 20
DEFAULT_MAX_RETRIES = 0
SIMPLE_JSON_SYSTEM_PROMPT = (
    "You generate ordinary strategy JSON only. Do not output QYIR, Python, markdown, or prose."
)


@dataclass(frozen=True)
class SimpleJsonCaseResult:
    """One Simple JSON baseline result with adapter-specific diagnostics."""

    method_result: MethodResult
    json_parse_success: bool
    qyir_conversion_success: bool
    adapter_errors: list[str]

    def to_row(self) -> dict[str, Any]:
        row = self.method_result.to_row()
        row["json_parse_success"] = self.json_parse_success
        row["qyir_conversion_success"] = self.qyir_conversion_success
        row["adapter_errors"] = "; ".join(self.adapter_errors)
        return row


def build_simple_json_prompt(query: str, feedback: str | None = None) -> str:
    """Prompt for an ordinary strategy JSON object, intentionally not QYIR."""
    feedback_block = f"\nPrevious error to fix: {feedback}\n" if feedback else ""
    return f"""Convert the user request into a simple strategy JSON object.

This is NOT QYIR. Do not use QYIR fields such as entry_rules, exit_rules,
indicator aliases, operator enums, or risk_control.

Return one JSON object with this shape:
{{
  "strategy_type": "moving_average | mean_reversion | momentum | macd | bollinger | other",
  "asset": "SPY",
  "indicators": ["SMA20", "SMA60"],
  "buy_condition": "SMA20 crosses above SMA60",
  "sell_condition": "SMA20 crosses below SMA60",
  "risk": {{
    "position_size": "low",
    "stop_loss": "8%",
    "max_drawdown": "20%",
    "leverage": "no",
    "allow_short": "no"
  }}
}}

Use concise English condition strings even if the request is Chinese.
Preserve explicit risk constraints when present.
{feedback_block}
User request:
{query}
"""


def simple_json_to_qyir(simple_json: dict[str, Any], record: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Best-effort adapter from ordinary strategy JSON to QYIR."""
    errors: list[str] = []
    indicators = _parse_indicators(simple_json.get("indicators"), errors)
    if not indicators:
        indicators = _fallback_indicators(str(simple_json.get("strategy_type") or ""), errors)
    aliases = {str(ind["alias"]) for ind in indicators}

    entry_rule = _parse_condition(str(simple_json.get("buy_condition") or ""), aliases, default_type="cross_over")
    exit_rule = _parse_condition(str(simple_json.get("sell_condition") or ""), aliases, default_type="cross_under")
    if entry_rule is None:
        errors.append("adapter.buy_condition: could not map condition to QYIR rule")
    if exit_rule is None:
        errors.append("adapter.sell_condition: could not map condition to QYIR rule")
    if entry_rule is None or exit_rule is None:
        return None, errors

    risk = _parse_risk(simple_json.get("risk"), errors)
    qyir = {
        "strategy_name": f"simple_json_{str(record['id']).lower()}",
        "description": str(record["user_query"])[:512],
        "version": "1.0",
        "market": {
            "symbol": _parse_symbol(simple_json.get("asset")),
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": indicators,
        "entry_rules": [entry_rule],
        "exit_rules": [exit_rule],
        "risk_control": risk,
    }
    validation = validate_qyir(qyir)
    if not validation.valid:
        errors.extend(f"{issue.path}: {issue.message}" for issue in validation.issues)
    return qyir, errors


def run_live_simple_json(
    *,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_BASE_URL,
    models: Iterable[str] = (DEFAULT_MODEL,),
    case_limit: int | None = DEFAULT_CASE_LIMIT,
    case_ids: set[str] | None = None,
    seed: int = 20260505,
    max_retries: int = DEFAULT_MAX_RETRIES,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    allow_coding_plan: bool = False,
    checkpoint_output: str | Path | None = None,
    checkpoint_raw_output: str | Path | None = None,
    checkpoint_metadata_output: str | Path | None = None,
    checkpoint_usage_output: str | Path | None = None,
) -> tuple[list[SimpleJsonCaseResult], list[RawCall], dict[str, Any]]:
    """Run the live Simple JSON baseline on a stratified subset."""
    api_key = read_api_key(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    selected = select_records(load_benchmark(benchmark_path), case_limit=case_limit, seed=seed, case_ids=case_ids)
    price_data = pd.read_csv(data_path)
    audit: list[RawCall] = []
    results: list[SimpleJsonCaseResult] = []
    normalized_models = [normalize_model_name(model) for model in models]
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "models": normalized_models,
        "case_count": len(selected),
        "case_ids": [str(record["id"]) for record in selected],
        "completed_case_ids": [],
        "seed": seed,
        "max_retries": max_retries,
        "max_tokens": max_tokens,
        "response_format_mode": "json_object",
        "methods": ["live_simple_json_adapter"],
    }

    for model in normalized_models:
        for record in selected:
            result = _run_one_simple_json_record(
                record,
                model,
                api_key,
                base_url,
                price_data,
                audit,
                max_retries=max_retries,
                max_tokens=max_tokens,
            )
            results.append(result)
            metadata["completed_case_ids"].append(str(record["id"]))
            _write_checkpoints(
                results,
                audit,
                metadata,
                checkpoint_output=checkpoint_output,
                checkpoint_raw_output=checkpoint_raw_output,
                checkpoint_metadata_output=checkpoint_metadata_output,
                checkpoint_usage_output=checkpoint_usage_output,
            )
    return results, audit, metadata


def replay_live_simple_json(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[SimpleJsonCaseResult]:
    """Recompute Simple JSON adapter metrics from saved raw outputs."""
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    selected = [records[str(case_id)] for case_id in metadata["case_ids"]]
    price_data = pd.read_csv(data_path)
    raw_calls = _load_raw_calls(raw_output_path)
    calls_by_case: dict[str, list[RawCall]] = {}
    for call in raw_calls:
        calls_by_case.setdefault(call.case_id, []).append(call)

    results: list[SimpleJsonCaseResult] = []
    model = str(metadata["models"][0]) if metadata.get("models") else "unknown"
    method = f"live_simple_json_adapter::{model}"
    for record in selected:
        results.append(_replay_one_simple_json_record(record, method, calls_by_case, price_data))
    return results


def write_simple_json_results(results: Iterable[SimpleJsonCaseResult], output_path: str | Path) -> None:
    """Write Simple JSON per-case rows to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result.to_row() for result in results]).to_csv(output, index=False)


def write_simple_json_metrics(results_csv: str | Path, output_csv: str | Path) -> pd.DataFrame:
    """Write Simple JSON metrics requested by the paper baseline."""
    rows = pd.read_csv(results_csv)
    rows = _with_simple_defaults(rows)
    metrics: list[dict[str, Any]] = []
    for method, group in rows.groupby("method", sort=False):
        constructible = group[(group["should_reject"] == False) & (group["category"] != "ambiguous_intent")]  # noqa: E712
        unsafe = group[group["should_reject"] == True]  # noqa: E712
        metrics.append(
            {
                "method": method,
                "json_parse_success": _mean(constructible, "json_parse_success"),
                "qyir_conversion_success": _mean(constructible, "qyir_conversion_success"),
                "semantic_consistency": _mean(constructible, "semantic_consistent"),
                "compile_success": _mean(constructible, "compile_success"),
                "risk_violation": _mean(constructible, "risk_violation"),
                "safe_rejection_accuracy": _mean(unsafe, "safe_rejection_correct"),
                "construction_success": _mean(constructible, "qyir_conversion_success"),
                "end_to_end_success": _mean(group, "end_to_end_success"),
            }
        )
    frame = pd.DataFrame(metrics)
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame


def _run_one_simple_json_record(
    record: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    price_data: pd.DataFrame,
    audit: list[RawCall],
    *,
    max_retries: int,
    max_tokens: int,
) -> SimpleJsonCaseResult:
    method = f"live_simple_json_adapter::{model}"
    gated = _gated_terminal_result(record, method)
    if gated is not None:
        return SimpleJsonCaseResult(gated, json_parse_success=False, qyir_conversion_success=False, adapter_errors=[])

    client = ConstrainedOpenAIClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        method=method,
        case_id=str(record["id"]),
        audit=audit,
        max_tokens=max_tokens,
        response_format_mode="json_object",
        system_prompt=SIMPLE_JSON_SYSTEM_PROMPT,
    )
    feedback: str | None = None
    last_error = "generation failed"
    for _ in range(max_retries + 1):
        prompt = build_simple_json_prompt(str(record["user_query"]), feedback=feedback)
        try:
            raw = client.generate(prompt)
        except Exception as exc:
            result = _failed_result(record, method, f"api_error: {type(exc).__name__}: {exc}")
            return SimpleJsonCaseResult(result, False, False, [f"api_error: {type(exc).__name__}: {exc}"])
        parsed, parse_error = _parse_json(raw)
        if parse_error is not None:
            last_error = parse_error
            feedback = parse_error
            continue
        return _evaluate_simple_json(record, method, parsed, price_data)

    result = _failed_result(record, method, last_error)
    return SimpleJsonCaseResult(result, False, False, [last_error])


def _replay_one_simple_json_record(
    record: dict[str, Any],
    method: str,
    calls_by_case: dict[str, list[RawCall]],
    price_data: pd.DataFrame,
) -> SimpleJsonCaseResult:
    gated = _gated_terminal_result(record, method)
    if gated is not None:
        return SimpleJsonCaseResult(gated, json_parse_success=False, qyir_conversion_success=False, adapter_errors=[])
    calls = calls_by_case.get(str(record["id"]), [])
    if not calls:
        result = _failed_result(record, method, "replay_error: missing raw call")
        return SimpleJsonCaseResult(result, False, False, ["replay_error: missing raw call"])
    last_call = calls[-1]
    if last_call.error:
        result = _failed_result(record, method, f"api_error: {last_call.error}")
        return SimpleJsonCaseResult(result, False, False, [f"api_error: {last_call.error}"])
    parsed, parse_error = _parse_json(last_call.raw_output)
    if parse_error is not None:
        result = _failed_result(record, method, parse_error)
        return SimpleJsonCaseResult(result, False, False, [parse_error])
    return _evaluate_simple_json(record, method, parsed, price_data)


def _evaluate_simple_json(
    record: dict[str, Any],
    method: str,
    simple_json: dict[str, Any],
    price_data: pd.DataFrame,
) -> SimpleJsonCaseResult:
    qyir, adapter_errors = simple_json_to_qyir(simple_json, record)
    if qyir is None:
        result = _failed_result(record, method, "; ".join(adapter_errors) or "adapter failed")
        return SimpleJsonCaseResult(result, True, False, adapter_errors)
    validation = validate_qyir(qyir)
    result = _evaluate_qyir(
        record,
        method,
        qyir,
        price_data,
        rejected=False,
        repair_triggered=False,
        repair_success=False,
    )
    return SimpleJsonCaseResult(result, True, validation.valid, adapter_errors)


def _gated_terminal_result(record: dict[str, Any], method: str) -> MethodResult | None:
    query = str(record["user_query"])
    rejection = should_reject(query)
    if rejection.rejected:
        expected_reject = bool(record["should_reject"])
        return _method_result(
            record,
            method,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=expected_reject,
            errors=[rejection.reason or "safe rejection"],
        )
    if query_needs_clarification(query):
        return clarification_result(record, method)
    return None


def _parse_indicators(raw: Any, errors: list[str]) -> list[dict[str, Any]]:
    if isinstance(raw, str):
        raw_items = [raw]
    elif isinstance(raw, list):
        raw_items = raw
    else:
        errors.append("adapter.indicators: expected string or list")
        return []

    indicators: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_items:
        text = str(item).strip()
        indicator = _parse_one_indicator(text)
        if indicator is None:
            errors.append(f"adapter.indicators: unsupported indicator '{text}'")
            continue
        alias = str(indicator["alias"])
        if alias not in seen:
            indicators.append(indicator)
            seen.add(alias)
    return indicators[:10]


def _parse_one_indicator(text: str) -> dict[str, Any] | None:
    normalized = text.strip().lower().replace("-", "").replace("_", "")
    match = re.search(r"\b(sma|ma)(\d{1,3})\b", normalized)
    if match:
        window = int(match.group(2))
        return {"name": "SMA", "params": {"window": window}, "alias": f"sma_{window}"}
    match = re.search(r"\bema(\d{1,3})\b", normalized)
    if match:
        window = int(match.group(1))
        return {"name": "EMA", "params": {"window": window}, "alias": f"ema_{window}"}
    match = re.search(r"\brsi(\d{1,3})?\b", normalized)
    if match:
        window = int(match.group(1) or 14)
        return {"name": "RSI", "params": {"window": window}, "alias": f"rsi_{window}"}
    if "macd" in normalized:
        if "signal" in normalized:
            return {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "signal_line"},
                "alias": "macd_signal",
            }
        return {
            "name": "MACD",
            "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
            "alias": "macd_line",
        }
    if "bollinger" in normalized or normalized.startswith("bb"):
        if "upper" in normalized:
            output = "upper"
        elif "lower" in normalized:
            output = "lower"
        elif "middle" in normalized or "mid" in normalized:
            output = "middle"
        else:
            return None
        return {
            "name": "BOLLINGER",
            "params": {"window": 20, "num_std": 2.0, "output": output},
            "alias": f"bollinger_{output}",
        }
    return None


def _fallback_indicators(strategy_type: str, errors: list[str]) -> list[dict[str, Any]]:
    text = strategy_type.lower()
    errors.append("adapter.indicators: using fallback indicators from strategy_type")
    if "rsi" in text or "mean" in text:
        return [{"name": "RSI", "params": {"window": 14}, "alias": "rsi_14"}]
    if "macd" in text:
        return [
            {"name": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"}, "alias": "macd_line"},
            {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "signal_line"},
                "alias": "macd_signal",
            },
        ]
    return [
        {"name": "SMA", "params": {"window": 20}, "alias": "sma_20"},
        {"name": "SMA", "params": {"window": 60}, "alias": "sma_60"},
    ]


def _parse_condition(condition: str, aliases: set[str], *, default_type: str) -> dict[str, Any] | None:
    text = condition.lower().replace("_", "").replace("-", "")
    rule_type = default_type
    if any(cue in text for cue in ("crosses above", "cross above", "crossover", "cross over", "golden cross", "上穿", "金叉")):
        rule_type = "cross_over"
    elif any(cue in text for cue in ("crosses below", "cross below", "crossunder", "cross under", "death cross", "下穿", "死叉")):
        rule_type = "cross_under"
    elif any(cue in text for cue in ("greater than", "above", ">")):
        rule_type = "greater_than"
    elif any(cue in text for cue in ("less than", "below", "<")):
        rule_type = "less_than"

    operands = _condition_operands(condition, aliases)
    if len(operands) < 2:
        return None
    return {"type": rule_type, "left": operands[0], "right": operands[1]}


def _condition_operands(condition: str, aliases: set[str]) -> list[str | float]:
    tokens: list[tuple[int, str | float]] = []
    compact = condition.lower().replace("_", "").replace("-", "")
    for alias in aliases:
        alias_compact = alias.replace("_", "")
        idx = compact.find(alias_compact)
        if idx >= 0:
            tokens.append((idx, alias))
    if "close" in compact:
        tokens.append((compact.find("close"), "close"))
    for match in re.finditer(r"(?<![a-z])(\d+(?:\.\d+)?)(?![a-z])", compact):
        number = float(match.group(1))
        if number > 1:
            tokens.append((match.start(), number))
    tokens.sort(key=lambda pair: pair[0])
    deduped: list[str | float] = []
    for _, value in tokens:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _parse_risk(raw: Any, errors: list[str]) -> dict[str, Any]:
    risk = raw if isinstance(raw, dict) else {}
    if not isinstance(raw, dict):
        errors.append("adapter.risk: expected object, using defaults")
    return {
        "position_size": _parse_fraction(risk.get("position_size"), default=0.5, low_value=0.4),
        "stop_loss": _parse_optional_fraction(risk.get("stop_loss"), default=0.08),
        "take_profit": _parse_optional_fraction(risk.get("take_profit"), default=None),
        "max_drawdown_limit": _parse_optional_fraction(risk.get("max_drawdown"), default=0.2),
        "allow_short": _parse_bool(risk.get("allow_short"), default=False),
        "leverage": _parse_leverage(risk.get("leverage")),
    }


def _parse_symbol(raw: Any) -> str:
    text = str(raw or "SPY").upper()
    if "QQQ" in text or "NASDAQ" in text:
        return "QQQ"
    if "GLD" in text or "GOLD" in text:
        return "GLD"
    return "SPY"


def _parse_fraction(raw: Any, *, default: float, low_value: float) -> float:
    text = str(raw or "").strip().lower()
    if any(cue in text for cue in ("low", "small", "conservative", "低", "小", "保守")):
        return low_value
    if any(cue in text for cue in ("high", "full", "aggressive", "高", "满", "激进")):
        return 1.0
    parsed = _parse_optional_fraction(raw, default=None)
    return default if parsed is None else parsed


def _parse_optional_fraction(raw: Any, *, default: float | None) -> float | None:
    if raw is None or raw == "":
        return default
    if isinstance(raw, (int, float)):
        value = float(raw)
        return value / 100.0 if value > 1 else value
    text = str(raw).strip().lower()
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if match:
        return float(match.group(1)) / 100.0
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        value = float(match.group(1))
        return value / 100.0 if value > 1 else value
    return default


def _parse_bool(raw: Any, *, default: bool) -> bool:
    text = str(raw or "").strip().lower()
    if text in {"yes", "true", "1", "allow", "allowed", "可以", "允许"}:
        return True
    if text in {"no", "false", "0", "none", "not allowed", "不", "不允许"}:
        return False
    return default


def _parse_leverage(raw: Any) -> float:
    text = str(raw or "").strip().lower()
    if text in {"", "no", "none", "false", "1", "1x", "不", "不要", "无"}:
        return 1.0
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else 1.0


def _write_checkpoints(
    results: list[SimpleJsonCaseResult],
    audit: list[RawCall],
    metadata: dict[str, Any],
    *,
    checkpoint_output: str | Path | None,
    checkpoint_raw_output: str | Path | None,
    checkpoint_metadata_output: str | Path | None,
    checkpoint_usage_output: str | Path | None,
) -> None:
    if checkpoint_output is not None:
        write_simple_json_results(results, checkpoint_output)
    if checkpoint_raw_output is not None:
        write_audit_jsonl(audit, checkpoint_raw_output)
    if checkpoint_metadata_output is not None:
        write_metadata(metadata, checkpoint_metadata_output)
    if checkpoint_usage_output is not None:
        write_token_usage(audit, checkpoint_usage_output)


def _load_raw_calls(raw_output_path: str | Path) -> list[RawCall]:
    calls: list[RawCall] = []
    for line in Path(raw_output_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        calls.append(
            RawCall(
                model=str(row["model"]),
                method=str(row["method"]),
                case_id=str(row["case_id"]),
                attempt=int(row["attempt"]),
                prompt=str(row["prompt"]),
                raw_output=str(row["raw_output"]),
                prompt_tokens=row.get("prompt_tokens"),
                completion_tokens=row.get("completion_tokens"),
                total_tokens=row.get("total_tokens"),
                error=row.get("error"),
            )
        )
    return calls


def _with_simple_defaults(rows: pd.DataFrame) -> pd.DataFrame:
    if "category" not in rows.columns:
        rows["category"] = ""
    if "json_parse_success" not in rows.columns:
        rows["json_parse_success"] = False
    if "qyir_conversion_success" not in rows.columns:
        rows["qyir_conversion_success"] = False
    return rows


def _mean(group: pd.DataFrame, column: str) -> float:
    if group.empty:
        return 0.0
    return float(group[column].astype(bool).mean())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live Simple JSON baseline diagnostics.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="docs/LiveLLM API KEY.txt")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--models", nargs="+", default=[DEFAULT_MODEL], choices=sorted(set(MODEL_ALIASES) | {DEFAULT_MODEL}))
    parser.add_argument("--case-limit", type=int, default=DEFAULT_CASE_LIMIT)
    parser.add_argument("--case-ids", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=20260505)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--output", default="experiments/results/live_simple_json_results.csv")
    parser.add_argument("--metrics-output", default="experiments/results/live_simple_json_metrics.csv")
    parser.add_argument("--raw-output", default="experiments/results/live_simple_json_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/live_simple_json_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/live_simple_json_token_usage.csv")
    parser.add_argument("--replay-raw-output", default=None)
    parser.add_argument("--replay-metadata", default=None)
    args = parser.parse_args(argv)

    if args.replay_raw_output:
        if not args.replay_metadata:
            parser.error("--replay-metadata is required with --replay-raw-output")
        results = replay_live_simple_json(
            raw_output_path=args.replay_raw_output,
            metadata_path=args.replay_metadata,
            benchmark_path=args.benchmark,
            data_path=args.data,
        )
        write_simple_json_results(results, args.output)
        write_simple_json_metrics(args.output, args.metrics_output)
        print(f"Replayed {len(results)} Simple JSON result rows to {args.output}")
        return 0

    case_limit = None if args.case_limit == 0 else args.case_limit
    results, audit, metadata = run_live_simple_json(
        benchmark_path=args.benchmark,
        data_path=args.data,
        api_key_file=args.api_key_file,
        base_url=args.base_url,
        models=args.models,
        case_limit=case_limit,
        case_ids=set(args.case_ids) if args.case_ids else None,
        seed=args.seed,
        max_retries=args.max_retries,
        max_tokens=args.max_tokens,
        allow_coding_plan=args.allow_coding_plan_automation,
        checkpoint_output=args.output,
        checkpoint_raw_output=args.raw_output,
        checkpoint_metadata_output=args.metadata_output,
        checkpoint_usage_output=args.usage_output,
    )
    write_simple_json_results(results, args.output)
    write_simple_json_metrics(args.output, args.metrics_output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} Simple JSON result rows to {args.output}")
    print(f"Wrote {len(audit)} raw call records to {args.raw_output}")
    print(f"Wrote metrics to {args.metrics_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
