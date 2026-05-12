"""Run one-iteration execution-feedback repair for saved live direct-code outputs.

The first generation pass is replayed from saved raw outputs. Failed cases are
sent back to the same model once with the observed syntax, interface, runtime,
trade-validity, semantic, backtest, and risk-check feedback. This is a live
diagnostic baseline for build-test-patch style direct-code generation.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.baselines import DEFAULT_BENCHMARK_PATH, DEFAULT_DATA_PATH
from experiments.run_live_direct_code import (
    DIRECT_CODE_SYSTEM_PROMPT,
    DirectCodeResult,
    evaluate_direct_code,
    replay_live_direct_code,
    write_direct_results,
    write_method_results,
)
from experiments.run_live_llm import (
    AuditedOpenAIClient,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    RawCall,
    guard_api_terms,
    normalize_model_name,
    read_api_key,
    write_audit_jsonl,
    write_metadata,
    write_token_usage,
)


REPAIR_PROMPT = """You previously generated a Python strategy function that failed validation.

Original user request:
{query}

Previous generated code:
{code}

Validation feedback:
{feedback}

Repair the function once.

Required interface:
def generate_signals(df: pd.DataFrame) -> pd.Series:
    ...

Input df columns: date, open, high, low, close, volume.
Return a pd.Series with the same index as df. Values must be 1 for long, 0 for cash, or -1 only if the user explicitly allows short selling.
Do not fetch data, read files, call network APIs, or print anything.
Return exactly one Python function. No markdown and no prose.
"""


def run_live_direct_code_repair(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    api_key_file: str | Path | None = None,
    base_url: str = DEFAULT_BASE_URL,
    repair_models: list[str] | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    allow_coding_plan: bool = False,
    checkpoint_dir: str | Path | None = None,
) -> tuple[list[DirectCodeResult], list[RawCall], dict[str, Any]]:
    """Replay first-pass outputs and make one live repair call for failures."""
    api_key = read_api_key(api_key_file)
    guard_api_terms(api_key, base_url, allow_coding_plan)
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    records = _load_records_by_id(benchmark_path)
    raw_calls = _load_raw_calls(raw_output_path)
    raw_by_key = {(call.method, call.case_id): call for call in raw_calls}
    first_pass = replay_live_direct_code(
        raw_output_path=raw_output_path,
        metadata_path=metadata_path,
        benchmark_path=benchmark_path,
        data_path=data_path,
    )
    first_by_key = {(result.method, result.case_id): result for result in first_pass}
    price_data = pd.read_csv(data_path)
    audit: list[RawCall] = []
    repaired_results: list[DirectCodeResult] = []
    checkpoint = Path(checkpoint_dir) if checkpoint_dir is not None else None
    if checkpoint is not None:
        checkpoint.mkdir(parents=True, exist_ok=True)

    for model_name in [str(model) for model in metadata["models"]]:
        source_model = normalize_model_name(model_name)
        source_method = f"live_direct_code::{source_model}"
        repair_model_candidates = [normalize_model_name(model) for model in (repair_models or [source_model])]
        repaired_method = "live_direct_code_feedback_repair::" + "+".join(repair_model_candidates)
        for case_id in [str(value) for value in metadata["case_ids"]]:
            record = records[case_id]
            initial = first_by_key[(source_method, case_id)]
            if initial.end_to_end_success:
                repaired_results.append(_rename_result(initial, repaired_method))
                _write_checkpoint(repaired_results, audit, checkpoint)
                continue

            raw_call = raw_by_key.get((source_method, case_id))
            previous_code = raw_call.raw_output if raw_call is not None else ""
            feedback = _feedback_from_result(initial)
            evaluated: DirectCodeResult | None = None
            api_errors: list[str] = []
            for repair_model in repair_model_candidates:
                call_method = f"{repaired_method}__call_{repair_model}"
                client = AuditedOpenAIClient(
                    api_key=api_key,
                    base_url=base_url,
                    model=repair_model,
                    method=call_method,
                    case_id=case_id,
                    audit=audit,
                    max_tokens=max_tokens,
                    system_prompt=DIRECT_CODE_SYSTEM_PROMPT,
                )
                try:
                    repaired_output = client.generate(
                        REPAIR_PROMPT.format(
                            query=record["user_query"],
                            code=previous_code[:6000],
                            feedback=feedback,
                        )
                    )
                    evaluated = evaluate_direct_code(record, repaired_method, repaired_output, price_data)
                    break
                except Exception as exc:
                    api_errors.append(f"{repair_model}: {type(exc).__name__}: {exc}")

            if evaluated is None:
                evaluated = _rename_result(
                    initial,
                    repaired_method,
                    extra_error="repair_api_error: " + " | ".join(api_errors),
                )
            repaired_results.append(evaluated)
            _write_checkpoint(repaired_results, audit, checkpoint)

    repaired_metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_path": str(benchmark_path),
        "data_path": str(data_path),
        "base_url": base_url,
        "source_models": [normalize_model_name(str(model)) for model in metadata["models"]],
        "repair_models": [normalize_model_name(model) for model in (repair_models or [str(metadata["models"][0])])],
        "case_count": len(metadata["case_ids"]),
        "case_ids": [str(value) for value in metadata["case_ids"]],
        "source_raw_output_path": str(raw_output_path),
        "source_metadata_path": str(metadata_path),
        "max_tokens": max_tokens,
        "repair_iterations": 1,
        "methods": ["live_direct_code_feedback_repair::" + "+".join([normalize_model_name(model) for model in (repair_models or [str(metadata["models"][0])])])],
    }
    return repaired_results, audit, repaired_metadata


def _write_checkpoint(results: list[DirectCodeResult], audit: list[RawCall], checkpoint: Path | None) -> None:
    if checkpoint is None:
        return
    write_direct_results(results, checkpoint / "live_direct_code_feedback_repair_results.partial.csv")
    write_method_results(results, checkpoint / "live_direct_code_feedback_repair_method_results.partial.csv")
    write_audit_jsonl(audit, checkpoint / "live_direct_code_feedback_repair_raw_outputs.partial.jsonl")


def _load_records_by_id(path: str | Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            records[str(record["id"])] = record
    return records


def _load_raw_calls(path: str | Path) -> list[RawCall]:
    calls: list[RawCall] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
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


def _feedback_from_result(result: DirectCodeResult) -> str:
    failures: list[str] = []
    for label, passed in [
        ("syntax_success", result.syntax_success),
        ("interface_success", result.interface_success),
        ("runtime_success", result.runtime_success),
        ("trade_validity", result.trade_validity),
        ("semantic_match", result.semantic_match),
        ("backtest_success", result.backtest_success),
    ]:
        if not passed:
            failures.append(f"{label}=false")
    if result.risk_violation:
        failures.append("risk_violation=true")
    if result.should_reject:
        failures.append("this benchmark case expects refusal or boundary handling, but the direct-code interface cannot express a refusal")
    if result.errors:
        failures.append("errors: " + "; ".join(result.errors))
    return "\n".join(failures) if failures else "end_to_end_success=false"


def _rename_result(result: DirectCodeResult, method: str, extra_error: str | None = None) -> DirectCodeResult:
    errors = list(result.errors)
    if extra_error is not None:
        errors.append(extra_error)
    return DirectCodeResult(
        case_id=result.case_id,
        category=result.category,
        method=method,
        should_reject=result.should_reject,
        rejected=result.rejected,
        syntax_success=result.syntax_success,
        interface_success=result.interface_success,
        runtime_success=result.runtime_success,
        trade_validity=result.trade_validity,
        semantic_match=result.semantic_match,
        risk_violation=result.risk_violation,
        backtest_success=result.backtest_success,
        end_to_end_success=result.end_to_end_success,
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one-iteration live direct-code execution-feedback repair.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--api-key-file", default="docs/LiveLLM API KEY.txt")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--repair-models",
        nargs="+",
        default=None,
        help="Repair model fallback order. Defaults to the source first-pass model.",
    )
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--allow-coding-plan-automation", action="store_true")
    parser.add_argument("--replay-raw-output", default="experiments/results/live_direct_code_raw_outputs.jsonl")
    parser.add_argument("--replay-metadata", default="experiments/results/live_direct_code_metadata.json")
    parser.add_argument("--output", default="experiments/results/live_direct_code_feedback_repair_results.csv")
    parser.add_argument("--method-output", default="experiments/results/live_direct_code_feedback_repair_method_results.csv")
    parser.add_argument("--raw-output", default="experiments/results/live_direct_code_feedback_repair_raw_outputs.jsonl")
    parser.add_argument("--metadata-output", default="experiments/results/live_direct_code_feedback_repair_metadata.json")
    parser.add_argument("--usage-output", default="experiments/results/live_direct_code_feedback_repair_token_usage.csv")
    parser.add_argument("--checkpoint-dir", default="experiments/results/checkpoints/live_direct_code_feedback_repair")
    args = parser.parse_args(argv)

    results, audit, metadata = run_live_direct_code_repair(
        raw_output_path=args.replay_raw_output,
        metadata_path=args.replay_metadata,
        benchmark_path=args.benchmark,
        data_path=args.data,
        api_key_file=args.api_key_file,
        base_url=args.base_url,
        repair_models=args.repair_models,
        max_tokens=args.max_tokens,
        allow_coding_plan=args.allow_coding_plan_automation,
        checkpoint_dir=args.checkpoint_dir,
    )
    write_direct_results(results, args.output)
    write_method_results(results, args.method_output)
    write_audit_jsonl(audit, args.raw_output)
    write_metadata(metadata, args.metadata_output)
    write_token_usage(audit, args.usage_output)
    print(f"Wrote {len(results)} direct-code feedback-repair rows to {args.output}")
    print(f"Wrote MethodResult-compatible rows to {args.method_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
