"""Run executable live direct-code baselines for QSI-Bench.

This runner records raw model output, executes only the required
`generate_signals(df)` interface, and reports direct-code-specific outcomes.
It is intentionally separate from deterministic simulated baselines.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import numpy as np

from backtester.simple_backtester import run_backtest
from experiments.baselines import DEFAULT_BENCHMARK_PATH, DEFAULT_DATA_PATH, load_benchmark, results_to_csv
from experiments.run_live_llm import (
    AuditedOpenAIClient,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    RawCall,
    guard_api_terms,
    normalize_model_name,
    read_api_key,
    select_records,
    write_audit_jsonl,
    write_metadata,
    write_token_usage,
)


DIRECT_CODE_SYSTEM_PROMPT = (
    "You generate Python only. Return exactly one function named generate_signals. "
    "No markdown, no prose, no imports except pandas/numpy aliases already available."
)

DIRECT_CODE_PROMPT = """Given the user request, generate a Python strategy function.

Required interface:
def generate_signals(df: pd.DataFrame) -> pd.Series:
    ...

Input df columns: date, open, high, low, close, volume.
Return a pd.Series with the same index as df. Values must be 1 for long, 0 for cash, or -1 only if the user explicitly allows short selling.
Do not fetch data, read files, call network APIs, or print anything.
User request:
{query}
"""


@dataclass(frozen=True)
class DirectCodeResult:
    """One live direct-code result row."""

    case_id: str
    category: str
    method: str
    should_reject: bool
    rejected: bool
    syntax_success: bool
    interface_success: bool
    runtime_success: bool
    trade_validity: bool
    semantic_match: bool
    risk_violation: bool
    backtest_success: bool
    end_to_end_success: bool
    errors: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "category": self.category,
            "method": self.method,
            "should_reject": self.should_reject,
            "rejected": self.rejected,
            "syntax_success": self.syntax_success,
            "interface_success": self.interface_success,
            "runtime_success": self.runtime_success,
            "trade_validity": self.trade_validity,
            "semantic_match": self.semantic_match,
            "risk_violation": self.risk_violation,
            "backtest_success": self.backtest_success,
            "end_to_end_success": self.end_to_end_success,
            "errors": "; ".join(self.errors),
        }

    def to_method_result(self) -> Any:
        from experiments.baselines import MethodResult

        return MethodResult(
            case_id=self.case_id,
            category=self.category,
            method=self.method,
            should_reject=self.should_reject,
            rejected=self.rejected,
            schema_valid=False,
            semantic_consistent=self.semantic_match,
            compile_success=self.interface_success,
            backtest_success=self.backtest_success,
            risk_violation=self.risk_violation,
            repair_triggered=False,
            repair_success=False,
            safe_rejection_correct=False if self.should_reject else not self.rejected,
            clarification_requested=False,
            clarification_correct=False,
            end_to_end_success=self.end_to_end_success,
            errors=self.errors,
        )


def run_live_direct_code(
    *,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_BASE_URL,
    models: Iterable[str] = ("qwen3.6-flash",),
    case_limit: int | None = None,
    case_ids: set[str] | None = None,
    seed: int = 20260505,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    allow_coding_plan: bool = False,
    checkpoint_dir: str | Path | None = None,
) -> tuple[list[DirectCodeResult], list[RawCall], dict[str, Any]]:
    api_key = read_api_key(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    selected = select_records(load_benchmark(benchmark_path), case_limit=case_limit, seed=seed, case_ids=case_ids)
    price_data = pd.read_csv(data_path)
    audit: list[RawCall] = []
    results: list[DirectCodeResult] = []
    normalized_models = [normalize_model_name(model) for model in models]
    checkpoint = Path(checkpoint_dir) if checkpoint_dir is not None else None
    if checkpoint is not None:
        checkpoint.mkdir(parents=True, exist_ok=True)

    for model in normalized_models:
        for record in selected:
            method = f"live_direct_code::{model}"
            client = AuditedOpenAIClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                method=method,
                case_id=str(record["id"]),
                audit=audit,
                max_tokens=max_tokens,
                system_prompt=DIRECT_CODE_SYSTEM_PROMPT,
            )
            prompt = DIRECT_CODE_PROMPT.format(query=record["user_query"])
            try:
                raw = client.generate(prompt)
            except Exception as exc:
                results.append(_failed_result(record, method, f"api_error: {type(exc).__name__}: {exc}"))
            else:
                results.append(evaluate_direct_code(record, method, raw, price_data))
            if checkpoint is not None:
                write_direct_results(results, checkpoint / "live_direct_code_results.partial.csv")
                write_method_results(results, checkpoint / "live_direct_code_method_results.partial.csv")
                write_audit_jsonl(audit, checkpoint / "live_direct_code_raw_outputs.partial.jsonl")

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "models": normalized_models,
        "case_count": len(selected),
        "case_ids": [str(record["id"]) for record in selected],
        "seed": seed,
        "max_tokens": max_tokens,
        "methods": [f"live_direct_code::{model}" for model in normalized_models],
    }
    return results, audit, metadata


def replay_live_direct_code(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[DirectCodeResult]:
    """Recompute live direct-code metrics from saved raw outputs without API calls."""
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    selected: list[dict[str, Any]] = []
    for case_id in metadata["case_ids"]:
        case_key = str(case_id)
        if case_key not in records:
            raise ValueError(f"Metadata references unknown case id: {case_key}")
        selected.append(records[case_key])

    price_data = pd.read_csv(data_path)
    raw_calls = _load_raw_calls(raw_output_path)
    calls_by_key = {(call.method, call.case_id): call for call in raw_calls}
    results: list[DirectCodeResult] = []
    for model in [str(model) for model in metadata["models"]]:
        method = f"live_direct_code::{model}"
        for record in selected:
            call = calls_by_key.get((method, str(record["id"])))
            if call is None:
                results.append(_failed_result(record, method, "replay_error: missing raw call"))
            elif call.error:
                results.append(_failed_result(record, method, f"api_error: {call.error}"))
            else:
                results.append(evaluate_direct_code(record, method, call.raw_output, price_data))
    return results


def evaluate_direct_code(
    record: dict[str, Any],
    method: str,
    raw_output: str,
    price_data: pd.DataFrame,
) -> DirectCodeResult:
    code = _extract_code(raw_output)
    errors: list[str] = []
    syntax_success = False
    interface_success = False
    runtime_success = False
    trade_validity = False
    semantic_match = False
    risk_violation = bool(record["should_reject"])
    backtest_success = False

    try:
        tree = ast.parse(code)
        syntax_success = True
    except SyntaxError as exc:
        return _result(record, method, errors=[f"syntax_error: {exc}"])

    interface_success = _has_generate_signals(tree)
    if not interface_success:
        return _result(record, method, syntax_success=True, errors=["interface_error: missing generate_signals(df)"])

    try:
        signals = _execute_generate_signals(code, price_data)
        runtime_success = True
    except Exception as exc:
        return _result(
            record,
            method,
            syntax_success=True,
            interface_success=True,
            errors=[f"runtime_error: {type(exc).__name__}: {exc}"],
        )

    signal_error = _validate_signals(signals, price_data, record)
    if signal_error is None:
        trade_validity = True
    else:
        errors.append(signal_error)

    if trade_validity:
        backtest = run_backtest(
            pd.DataFrame({"date": price_data["date"], "close": price_data["close"], "position": signals.astype(int)}),
            risk_control={"position_size": 1.0, "stop_loss": None, "take_profit": None},
        )
        backtest_success = backtest.success
        errors.extend(backtest.errors)

    semantic_match = runtime_success and trade_validity and _direct_code_semantic_match(code, record)
    risk_violation = risk_violation or _direct_code_risk_violation(code, record)
    e2e = (
        syntax_success
        and interface_success
        and runtime_success
        and trade_validity
        and semantic_match
        and backtest_success
        and not risk_violation
        and not bool(record["should_reject"])
    )
    return _result(
        record,
        method,
        syntax_success=syntax_success,
        interface_success=interface_success,
        runtime_success=runtime_success,
        trade_validity=trade_validity,
        semantic_match=semantic_match,
        risk_violation=risk_violation,
        backtest_success=backtest_success,
        end_to_end_success=e2e,
        errors=errors,
    )


def write_direct_results(results: Iterable[DirectCodeResult], output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result.to_row() for result in results]).to_csv(output, index=False)


def write_method_results(results: Iterable[DirectCodeResult], output_path: str | Path) -> None:
    results_to_csv([result.to_method_result() for result in results], output_path)


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


def _extract_code(raw_output: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", raw_output, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else raw_output.strip()


def _has_generate_signals(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "generate_signals":
            return len(node.args.args) >= 1 and node.args.args[0].arg == "df"
    return False


def _execute_generate_signals(code: str, price_data: pd.DataFrame) -> pd.Series:
    namespace: dict[str, Any] = {
        "__builtins__": {"abs": abs, "bool": bool, "float": float, "int": int, "len": len, "max": max, "min": min, "range": range},
        "pd": pd,
        "np": np,
    }
    exec(compile(code, "<live_direct_code>", "exec"), namespace)
    fn = namespace["generate_signals"]
    result = fn(price_data.copy())
    if not isinstance(result, pd.Series):
        result = pd.Series(result, index=price_data.index)
    return result


def _validate_signals(signals: pd.Series, price_data: pd.DataFrame, record: dict[str, Any]) -> str | None:
    if len(signals) != len(price_data):
        return "signal_error: length mismatch"
    if signals.isna().any():
        return "signal_error: contains missing values"
    values = set(pd.Series(signals).astype(int).unique())
    if not values <= {-1, 0, 1}:
        return f"signal_error: invalid position values {sorted(values)}"
    slots = dict(record.get("expected_slots") or {})
    if slots.get("allow_short") is False and -1 in values:
        return "signal_error: short position used despite no-short intent"
    if len(values) <= 1:
        return "signal_error: no position change"
    return None


def _direct_code_semantic_match(code: str, record: dict[str, Any]) -> bool:
    if record["category"] == "ambiguous_intent":
        return False
    if record["should_reject"]:
        return False
    slots = dict(record.get("expected_slots") or {})
    text = code.lower()
    checks: list[bool] = []
    for key in ("fast_window", "slow_window", "lookback_window"):
        if isinstance(slots.get(key), int):
            checks.append(str(slots[key]) in text)
    family = str(slots.get("strategy_family") or "").lower()
    if "rsi" in family:
        checks.append("rsi" in text)
    if "macd" in family:
        checks.append("macd" in text)
    if "ema" in family:
        checks.append("ema" in text or "ewm" in text)
    if "bollinger" in family:
        checks.append("std" in text or "bollinger" in text)
    if slots.get("stop_loss_required") or slots.get("stop_loss") is not None:
        checks.append("stop" in text or "loss" in text or "止损" in code)
    if slots.get("max_position_weight") is not None or slots.get("position_size") in {"small", "not_full", "conservative"}:
        checks.append("position_size" in text or "weight" in text or "仓位" in code)
    return all(checks) if checks else True


def _direct_code_risk_violation(code: str, record: dict[str, Any]) -> bool:
    slots = dict(record.get("expected_slots") or {})
    if record["should_reject"]:
        return True
    if slots.get("allow_leverage") is False and re.search(r"leverage|margin|杠杆", code, flags=re.IGNORECASE):
        return True
    if slots.get("stop_loss_required") and not re.search(r"stop|loss|止损", code, flags=re.IGNORECASE):
        return True
    if slots.get("max_drawdown_limit") is not None and not re.search(r"drawdown|回撤|stop|loss", code, flags=re.IGNORECASE):
        return True
    if slots.get("max_position_weight") is not None and not re.search(r"position_size|weight|仓位", code, flags=re.IGNORECASE):
        return True
    return False


def _failed_result(record: dict[str, Any], method: str, error: str) -> DirectCodeResult:
    return _result(record, method, risk_violation=bool(record["should_reject"]), errors=[error])


def _result(
    record: dict[str, Any],
    method: str,
    *,
    syntax_success: bool = False,
    interface_success: bool = False,
    runtime_success: bool = False,
    trade_validity: bool = False,
    semantic_match: bool = False,
    risk_violation: bool = False,
    backtest_success: bool = False,
    end_to_end_success: bool = False,
    errors: list[str] | None = None,
) -> DirectCodeResult:
    return DirectCodeResult(
        case_id=str(record["id"]),
        category=str(record["category"]),
        method=method,
        should_reject=bool(record["should_reject"]),
        rejected=False,
        syntax_success=syntax_success,
        interface_success=interface_success,
        runtime_success=runtime_success,
        trade_validity=trade_validity,
        semantic_match=semantic_match,
        risk_violation=risk_violation,
        backtest_success=backtest_success,
        end_to_end_success=end_to_end_success,
        errors=errors or [],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run executable live direct-code baseline.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="docs/LiveLLM API KEY.txt")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--models", nargs="+", default=["qwen3.6-flash"])
    parser.add_argument("--case-limit", type=int, default=0, help="0 means all benchmark cases.")
    parser.add_argument("--case-ids", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=20260505)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--output", default="experiments/results/live_direct_code_results.csv")
    parser.add_argument("--method-output", default="experiments/results/live_direct_code_method_results.csv")
    parser.add_argument("--raw-output", default="experiments/results/live_direct_code_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/live_direct_code_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/live_direct_code_token_usage.csv")
    parser.add_argument("--checkpoint-dir", default=None, help="Optional directory for partial results during long live runs.")
    parser.add_argument("--replay-raw-output", default=None, help="Recompute results from saved direct-code raw JSONL.")
    parser.add_argument("--replay-metadata", default=None, help="Metadata JSON for --replay-raw-output.")
    args = parser.parse_args(argv)

    if args.replay_raw_output:
        if not args.replay_metadata:
            parser.error("--replay-metadata is required with --replay-raw-output")
        results = replay_live_direct_code(
            raw_output_path=args.replay_raw_output,
            metadata_path=args.replay_metadata,
            benchmark_path=args.benchmark,
            data_path=args.data,
        )
        write_direct_results(results, args.output)
        write_method_results(results, args.method_output)
        print(f"Replayed {len(results)} direct-code rows to {args.output}")
        print(f"Wrote MethodResult-compatible rows to {args.method_output}")
        return 0

    case_limit = None if args.case_limit == 0 else args.case_limit
    results, audit, metadata = run_live_direct_code(
        benchmark_path=args.benchmark,
        data_path=args.data,
        api_key_file=args.api_key_file,
        base_url=args.base_url,
        models=args.models,
        case_limit=case_limit,
        case_ids=set(args.case_ids) if args.case_ids else None,
        seed=args.seed,
        max_tokens=args.max_tokens,
        allow_coding_plan=args.allow_coding_plan_automation,
        checkpoint_dir=args.checkpoint_dir,
    )
    write_direct_results(results, args.output)
    write_method_results(results, args.method_output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} direct-code rows to {args.output}")
    print(f"Wrote MethodResult-compatible rows to {args.method_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
