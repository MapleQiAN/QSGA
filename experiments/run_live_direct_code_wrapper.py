"""Replay live direct-code outputs with a shared QSGA rejection wrapper.

This script does not make new API calls. It reuses saved live direct-code raw
outputs and applies the same deterministic safe-rejection gate before executing
the generated code. Non-rejected cases are evaluated with the existing direct
code interface checks and risk heuristics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from experiments.baselines import DEFAULT_BENCHMARK_PATH, DEFAULT_DATA_PATH, MethodResult, load_benchmark, results_to_csv
from experiments.run_live_direct_code import replay_live_direct_code
from verifier.safe_rejection import should_reject


def replay_live_direct_code_with_wrapper(
    *,
    raw_output_path: str | Path,
    metadata_path: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[MethodResult]:
    """Replay saved direct-code outputs with shared safe rejection applied first."""
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    raw_results = replay_live_direct_code(
        raw_output_path=raw_output_path,
        metadata_path=metadata_path,
        benchmark_path=benchmark_path,
        data_path=data_path,
    )
    raw_by_key = {(result.method, result.case_id): result for result in raw_results}
    wrapped: list[MethodResult] = []
    for model in [str(model) for model in metadata["models"]]:
        raw_method = f"live_direct_code::{model}"
        method = f"live_direct_code_shared_rejection::{model}"
        for case_id in [str(value) for value in metadata["case_ids"]]:
            record = records[case_id]
            decision = should_reject(str(record["user_query"]))
            if decision.rejected:
                expected_reject = bool(record["should_reject"])
                wrapped.append(
                    MethodResult(
                        case_id=case_id,
                        category=str(record["category"]),
                        method=method,
                        should_reject=expected_reject,
                        rejected=True,
                        schema_valid=False,
                        semantic_consistent=expected_reject,
                        compile_success=False,
                        backtest_success=False,
                        risk_violation=False,
                        repair_triggered=False,
                        repair_success=False,
                        safe_rejection_correct=expected_reject,
                        clarification_requested=False,
                        clarification_correct=False,
                        end_to_end_success=expected_reject,
                        errors=[decision.reason or "safe rejection"],
                    )
                )
                continue

            raw_result = raw_by_key[(raw_method, case_id)].to_method_result()
            wrapped.append(
                MethodResult(
                    case_id=raw_result.case_id,
                    category=raw_result.category,
                    method=method,
                    should_reject=raw_result.should_reject,
                    rejected=False,
                    schema_valid=raw_result.schema_valid,
                    semantic_consistent=raw_result.semantic_consistent,
                    compile_success=raw_result.compile_success,
                    backtest_success=raw_result.backtest_success,
                    risk_violation=raw_result.risk_violation,
                    repair_triggered=raw_result.repair_triggered,
                    repair_success=raw_result.repair_success,
                    safe_rejection_correct=not raw_result.should_reject,
                    clarification_requested=False,
                    clarification_correct=False,
                    end_to_end_success=raw_result.end_to_end_success,
                    errors=raw_result.errors,
                )
            )
    return wrapped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay live direct-code outputs with shared rejection.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--replay-raw-output", default="experiments/results/live_direct_code_raw_outputs.jsonl")
    parser.add_argument("--replay-metadata", default="experiments/results/live_direct_code_metadata.json")
    parser.add_argument("--output", default="experiments/results/live_direct_code_shared_rejection_results.csv")
    args = parser.parse_args(argv)

    results = replay_live_direct_code_with_wrapper(
        raw_output_path=args.replay_raw_output,
        metadata_path=args.replay_metadata,
        benchmark_path=args.benchmark,
        data_path=args.data,
    )
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} shared-rejection direct-code rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
