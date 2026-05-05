"""Run budget-bounded live LLM QYIR experiments against QSI-Bench.

This extension is intentionally separate from the deterministic CI harness:
it makes network calls, stores raw model outputs for auditability, and should
only be run with an approved API key and budget.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from backtester.simple_backtester import run_backtest
from compiler.qyir_compiler import compile_qyir
from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    MethodResult,
    expected_slots_match,
    load_benchmark,
    results_to_csv,
)
from generator.llm_client import LLMClient
from generator.prompt import build_qyir_prompt
from generator.qyir_generator import generate_qyir
from qyir.validator import validate_qyir
from verifier.risk_verifier import audit_risk
from verifier.safe_rejection import should_reject
from verifier.semantic_verifier import semantic_verify


DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODELS = [
    "qwen3.6-plus",
    "qwen3.6-flash",
    "deepseek-v4-flash",
    "kimi-k2.6",
]
DEFAULT_CASE_LIMIT = 20
DEFAULT_MAX_RETRIES = 1
DEFAULT_MAX_TOKENS = 1200
SYSTEM_PROMPT = "You generate strict QYIR JSON only. Never return Python, markdown, or prose."

MODEL_ALIASES = {
    "qwen3.6-plus": "qwen3.6-plus",
    "qwen3.6-plus(0402)": "qwen3.6-plus-2026-04-02",
    "qwen3.6-flash": "qwen3.6-flash",
    "qwen3.5-plus": "qwen3.5-plus",
    "qwen3.5-flash": "qwen3.5-flash",
    "glm-5.1": "glm-5.1",
    "glm-5": "glm-5",
    "minimax-m2.5": "minimax-m2.5",
    "kimi-k2.6": "kimi-k2.6",
    "kimi-k2.5": "kimi-k2.5",
    "deepseek-v4-flash": "deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek-v4-pro",
}


@dataclass
class RawCall:
    """One audited model call."""

    model: str
    method: str
    case_id: str
    attempt: int
    prompt: str
    raw_output: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    error: str | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "method": self.method,
            "case_id": self.case_id,
            "attempt": self.attempt,
            "prompt": self.prompt,
            "raw_output": self.raw_output,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "error": self.error,
        }


class AuditedOpenAIClient:
    """OpenAI-compatible client that records raw outputs and token usage."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        method: str,
        case_id: str,
        audit: list[RawCall],
        max_tokens: int,
    ) -> None:
        from openai import OpenAI

        self.model = model
        self.method = method
        self.case_id = case_id
        self.audit = audit
        self.max_tokens = max_tokens
        self._attempt = 0
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str) -> str:
        self._attempt += 1
        raw_output = ""
        prompt_tokens = None
        completion_tokens = None
        total_tokens = None
        error = None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=self.max_tokens,
            )
            content = response.choices[0].message.content or ""
            raw_output = content
            usage = getattr(response, "usage", None)
            if usage is not None:
                prompt_tokens = getattr(usage, "prompt_tokens", None)
                completion_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)
            return content
        except Exception as exc:  # pragma: no cover - requires live API failure
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            self.audit.append(
                RawCall(
                    model=self.model,
                    method=self.method,
                    case_id=self.case_id,
                    attempt=self._attempt,
                    prompt=prompt,
                    raw_output=raw_output,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    error=error,
                )
            )


class SingleResponseClient:
    """Test helper and raw-baseline adapter for one precomputed response."""

    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response


def select_records(
    records: list[dict[str, Any]],
    *,
    case_limit: int | None = DEFAULT_CASE_LIMIT,
    seed: int = 20260505,
    case_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Select a reproducible, category-stratified benchmark subset."""
    if case_ids:
        selected = [record for record in records if str(record["id"]) in case_ids]
        missing = sorted(case_ids - {str(record["id"]) for record in selected})
        if missing:
            raise ValueError(f"Unknown case ids: {', '.join(missing)}")
        return selected

    if case_limit is None or case_limit >= len(records):
        return records
    if case_limit <= 0:
        raise ValueError("case_limit must be positive")

    by_category: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_category.setdefault(str(record["category"]), []).append(record)

    rng = random.Random(seed)
    for group in by_category.values():
        rng.shuffle(group)

    selected: list[dict[str, Any]] = []
    categories = sorted(by_category)
    while len(selected) < case_limit and any(by_category.values()):
        for category in categories:
            group = by_category[category]
            if group and len(selected) < case_limit:
                selected.append(group.pop())
    return sorted(selected, key=lambda record: str(record["id"]))


def normalize_model_name(model: str) -> str:
    """Normalize approved display names to API model ids."""
    normalized = model.strip().lower().replace(" ", "")
    return MODEL_ALIASES.get(normalized, normalized)


def read_api_key(api_key_file: str | Path | None) -> str:
    """Load an API key from env or a local file without printing it."""
    key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        return key.strip()
    if api_key_file is None:
        raise ValueError("Set DASHSCOPE_API_KEY/OPENAI_API_KEY or pass --api-key-file.")
    text = Path(api_key_file).read_text(encoding="utf-8-sig").strip()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            name, value = stripped.split("=", 1)
            if name.strip().lower() in {"dashscope_api_key", "openai_api_key", "api_key"}:
                return value.strip().strip("\"'")
        return stripped.strip("\"'")
    raise ValueError(f"No API key found in {api_key_file}.")


def guard_api_terms(api_key: str, base_url: str, allow_coding_plan: bool) -> None:
    """Prevent accidental batch use of Coding Plan keys/endpoints."""
    looks_like_coding_key = api_key.startswith("sk-sp-")
    looks_like_coding_url = "coding.dashscope.aliyuncs.com" in base_url
    if (looks_like_coding_key or looks_like_coding_url) and not allow_coding_plan:
        raise ValueError(
            "The API key or base URL looks like Alibaba Cloud Coding Plan. "
            "Official Coding Plan docs restrict non-interactive batch/API automation. "
            "Use a standard Model Studio API key/base URL for this experiment, or rerun "
            "only after confirming your intended use is permitted."
        )


def run_live_llm(
    *,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_BASE_URL,
    models: Iterable[str] = DEFAULT_MODELS,
    case_limit: int | None = DEFAULT_CASE_LIMIT,
    case_ids: set[str] | None = None,
    seed: int = 20260505,
    max_retries: int = DEFAULT_MAX_RETRIES,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    allow_coding_plan: bool = False,
) -> tuple[list[MethodResult], list[RawCall], dict[str, Any]]:
    """Run live raw-QYIR and QSGA-QYIR methods for selected records."""
    api_key = read_api_key(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    selected = select_records(load_benchmark(benchmark_path), case_limit=case_limit, seed=seed, case_ids=case_ids)
    price_data = pd.read_csv(data_path)
    audit: list[RawCall] = []
    results: list[MethodResult] = []
    normalized_models = [normalize_model_name(model) for model in models]

    for model in normalized_models:
        for record in selected:
            results.append(_run_live_raw_qyir(record, model, api_key, base_url, price_data, audit, max_tokens))
            results.append(
                _run_live_qsga_qyir(
                    record,
                    model,
                    api_key,
                    base_url,
                    price_data,
                    audit,
                    max_retries=max_retries,
                    max_tokens=max_tokens,
                )
            )

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "models": normalized_models,
        "case_count": len(selected),
        "case_ids": [str(record["id"]) for record in selected],
        "seed": seed,
        "max_retries": max_retries,
        "max_tokens": max_tokens,
        "methods": ["live_raw_qyir", "live_qsga_qyir"],
    }
    return results, audit, metadata


def replay_live_llm(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[MethodResult]:
    """Recompute result metrics from saved raw model outputs without API calls.

    Replay is intended for evaluation-code fixes on zero-retry live runs. It
    cannot reconstruct successful generator repair traces that were not saved as
    final QYIR, but the current pilot uses max_retries=0 and had no successful
    repair cases.
    """
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    models = [str(model) for model in metadata["models"]]
    case_ids = {str(case_id) for case_id in metadata["case_ids"]}
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    selected = [records[case_id] for case_id in metadata["case_ids"]]
    missing = sorted(case_ids - set(records))
    if missing:
        raise ValueError(f"Metadata references unknown case ids: {', '.join(missing)}")

    price_data = pd.read_csv(data_path)
    raw_calls = _load_raw_calls(raw_output_path)
    calls_by_key = {(call.method, call.case_id): call for call in raw_calls}
    results: list[MethodResult] = []

    for model in models:
        for record in selected:
            raw_method = f"live_raw_qyir::{model}"
            qsga_method = f"live_qsga_qyir::{model}"
            results.append(_replay_method(record, raw_method, calls_by_key, price_data, raw_baseline=True))
            results.append(_replay_method(record, qsga_method, calls_by_key, price_data, raw_baseline=False))
    return results


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


def _replay_method(
    record: dict[str, Any],
    method: str,
    calls_by_key: dict[tuple[str, str], RawCall],
    price_data: pd.DataFrame,
    *,
    raw_baseline: bool,
) -> MethodResult:
    expected_reject = bool(record["should_reject"])
    if raw_baseline and expected_reject:
        return _method_result(
            record,
            method,
            rejected=False,
            schema_valid=False,
            semantic_consistent=False,
            compile_success=False,
            backtest_success=False,
            risk_violation=True,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=False,
            errors=["raw live LLM baseline has no safe-rejection gate"],
        )

    if not raw_baseline:
        rejection = should_reject(str(record["user_query"]))
        if rejection.rejected:
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

    call = calls_by_key.get((method, str(record["id"])))
    if call is None:
        return _failed_result(record, method, "replay_error: missing raw call")
    if call.error:
        return _failed_result(record, method, f"api_error: {call.error}")
    qyir, parse_error = _parse_json(call.raw_output)
    if parse_error is not None:
        return _failed_result(record, method, parse_error)
    return _evaluate_qyir(
        record,
        method,
        qyir,
        price_data,
        rejected=False,
        repair_triggered=False,
        repair_success=False,
    )


def _run_live_raw_qyir(
    record: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    price_data: pd.DataFrame,
    audit: list[RawCall],
    max_tokens: int,
) -> MethodResult:
    method = f"live_raw_qyir::{model}"
    expected_reject = bool(record["should_reject"])
    query = str(record["user_query"])
    if expected_reject:
        return _method_result(
            record,
            method,
            rejected=False,
            schema_valid=False,
            semantic_consistent=False,
            compile_success=False,
            backtest_success=False,
            risk_violation=True,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=False,
            errors=["raw live LLM baseline has no safe-rejection gate"],
        )

    client = AuditedOpenAIClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        method=method,
        case_id=str(record["id"]),
        audit=audit,
        max_tokens=max_tokens,
    )
    try:
        raw = client.generate(build_qyir_prompt(query))
    except Exception as exc:
        return _failed_result(record, method, f"api_error: {type(exc).__name__}: {exc}")

    qyir, parse_error = _parse_json(raw)
    if parse_error is not None:
        return _failed_result(record, method, parse_error)
    return _evaluate_qyir(record, method, qyir, price_data, rejected=False, repair_triggered=False, repair_success=False)


def _run_live_qsga_qyir(
    record: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    price_data: pd.DataFrame,
    audit: list[RawCall],
    *,
    max_retries: int,
    max_tokens: int,
) -> MethodResult:
    method = f"live_qsga_qyir::{model}"
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

    client: LLMClient = AuditedOpenAIClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        method=method,
        case_id=str(record["id"]),
        audit=audit,
        max_tokens=max_tokens,
    )
    try:
        generated = generate_qyir(query, client=client, max_retries=max_retries)
    except Exception as exc:
        return _failed_result(record, method, f"api_error: {type(exc).__name__}: {exc}")

    if generated.rejected:
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
            errors=[generated.rejection_reason or "safe rejection"],
        )
    if not generated.success or generated.qyir is None:
        errors = [f"{error['path']}: {error['message']}" for error in generated.errors]
        return _failed_result(record, method, "; ".join(errors) or "generation failed")
    return _evaluate_qyir(
        record,
        method,
        generated.qyir,
        price_data,
        rejected=False,
        repair_triggered=bool(generated.repair_trace),
        repair_success=bool(generated.repair_trace),
    )


def _evaluate_qyir(
    record: dict[str, Any],
    method: str,
    qyir: dict[str, Any],
    price_data: pd.DataFrame,
    *,
    rejected: bool,
    repair_triggered: bool,
    repair_success: bool,
) -> MethodResult:
    validation = validate_qyir(qyir)
    errors = [f"{issue.path}: {issue.message}" for issue in validation.issues]
    schema_valid = validation.valid
    semantic_consistent = False
    compile_success = False
    backtest_success = False
    risk_violation = False

    if schema_valid:
        semantic_result = semantic_verify(str(record["user_query"]), qyir)
        semantic_consistent = semantic_result.passed and expected_slots_match(qyir, record)
        errors.extend(f"{issue.path}: {issue.message}" for issue in semantic_result.issues)

        compilation = compile_qyir(qyir, price_data)
        compile_success = compilation.success
        errors.extend(compilation.errors)
        if compilation.success and compilation.signals is not None:
            backtest = run_backtest(compilation.signals, qyir.get("risk_control", {}))
            backtest_success = backtest.success
            errors.extend(backtest.errors)
            if backtest.success:
                risk = audit_risk(qyir, backtest.metrics)
                risk_violation = _has_risk_constraint_violation(risk)
                errors.extend(f"{issue.path}: {issue.message}" for issue in risk.issues)

    e2e = (
        schema_valid
        and semantic_consistent
        and compile_success
        and backtest_success
        and not risk_violation
        and not bool(record["should_reject"])
    )
    return _method_result(
        record,
        method,
        rejected=rejected,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=repair_triggered,
        repair_success=repair_success,
        end_to_end_success=e2e,
        errors=errors,
    )


def _parse_json(raw: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"json: Invalid JSON from live LLM: {exc}"
    if not isinstance(parsed, dict):
        return None, "json: Live LLM output must be a JSON object"
    return parsed, None


def _has_risk_constraint_violation(risk: Any) -> bool:
    """Use the same risk-constraint counting convention as the deterministic harness."""
    constraint_paths = {
        "risk_control.position_size",
        "risk_control.leverage",
        "risk_control.stop_loss",
        "backtest_metrics.max_drawdown",
        "backtest_metrics.risk_return_balance",
    }
    return any(issue.severity == "rejected" or issue.path in constraint_paths for issue in risk.issues)


def _failed_result(record: dict[str, Any], method: str, error: str) -> MethodResult:
    return _method_result(
        record,
        method,
        rejected=False,
        schema_valid=False,
        semantic_consistent=False,
        compile_success=False,
        backtest_success=False,
        risk_violation=bool(record["should_reject"]),
        repair_triggered=False,
        repair_success=False,
        end_to_end_success=False,
        errors=[error],
    )


def _method_result(
    record: dict[str, Any],
    method: str,
    *,
    rejected: bool,
    schema_valid: bool,
    semantic_consistent: bool,
    compile_success: bool,
    backtest_success: bool,
    risk_violation: bool,
    repair_triggered: bool,
    repair_success: bool,
    end_to_end_success: bool,
    errors: list[str],
) -> MethodResult:
    should_reject = bool(record["should_reject"])
    return MethodResult(
        case_id=str(record["id"]),
        category=str(record["category"]),
        method=method,
        should_reject=should_reject,
        rejected=rejected,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=repair_triggered,
        repair_success=repair_success,
        safe_rejection_correct=(rejected == should_reject) if should_reject else not rejected,
        end_to_end_success=end_to_end_success,
        errors=errors,
    )


def write_audit_jsonl(audit: Iterable[RawCall], output_path: str | Path) -> None:
    """Write raw call audit records as JSONL."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for call in audit:
            handle.write(json.dumps(call.to_row(), ensure_ascii=False) + "\n")


def write_metadata(metadata: dict[str, Any], output_path: str | Path) -> None:
    """Write run metadata as JSON."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def write_token_usage(audit: Iterable[RawCall], output_path: str | Path) -> None:
    """Aggregate token usage by model and method."""
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for call in audit:
        key = (call.model, call.method)
        row = rows.setdefault(
            key,
            {
                "model": call.model,
                "method": call.method,
                "calls": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "api_errors": 0,
            },
        )
        row["calls"] += 1
        row["prompt_tokens"] += int(call.prompt_tokens or 0)
        row["completion_tokens"] += int(call.completion_tokens or 0)
        row["total_tokens"] += int(call.total_tokens or 0)
        row["api_errors"] += int(call.error is not None)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["model", "method", "calls", "prompt_tokens", "completion_tokens", "total_tokens", "api_errors"],
        )
        writer.writeheader()
        writer.writerows(rows.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run budget-bounded live LLM QYIR experiments.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="docs/LiveLLM API KEY.txt")
    parser.add_argument("--base-url", default=os.getenv("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--case-limit", type=int, default=DEFAULT_CASE_LIMIT)
    parser.add_argument("--case-ids", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=20260505)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--output", default="experiments/results/live_llm_results.csv")
    parser.add_argument("--raw-output", default="experiments/results/live_llm_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/live_llm_run_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/live_llm_token_usage.csv")
    parser.add_argument("--replay-raw-output", default=None, help="Recompute results from an existing raw-output JSONL.")
    parser.add_argument("--replay-metadata", default=None, help="Metadata JSON for --replay-raw-output.")
    args = parser.parse_args(argv)

    if args.replay_raw_output:
        if not args.replay_metadata:
            parser.error("--replay-metadata is required with --replay-raw-output")
        results = replay_live_llm(
            raw_output_path=args.replay_raw_output,
            metadata_path=args.replay_metadata,
            benchmark_path=args.benchmark,
            data_path=args.data,
        )
        results_to_csv(results, args.output)
        print(f"Replayed {len(results)} result rows to {args.output}")
        return 0

    case_limit = None if args.case_limit == 0 else args.case_limit
    results, audit, metadata = run_live_llm(
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
    )
    results_to_csv(results, args.output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} result rows to {args.output}")
    print(f"Wrote {len(audit)} raw call records to {args.raw_output}")
    print(f"Wrote token usage to {args.usage_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
