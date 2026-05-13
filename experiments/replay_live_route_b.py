"""Replay saved Route B slot outputs without calling a live API."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    MethodResult,
    load_benchmark,
    record_requires_clarification,
    results_to_csv,
)
from experiments.run_live_llm import _evaluate_qyir, _failed_result, _has_risk_constraint_violation
from backtester.simple_backtester import run_backtest
from compiler.qyir_compiler import compile_qyir
from qsgi.construction import construct_qyir_from_query, generate_risk_repair_candidates
from verifier.risk_verifier import audit_risk


DEFAULT_RAW_OUTPUT_PATH = ROOT / "experiments" / "results" / "route_b_live_deepseek_official_80_raw_outputs.jsonl"


class SavedSlotClient:
    """LLMClient-compatible replay client for one benchmark case."""

    def __init__(self, outputs: list[str], *, case_id: str) -> None:
        self.outputs = outputs
        self.case_id = case_id
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.outputs:
            raise RuntimeError(f"No saved slot output left for case {self.case_id}")
        return self.outputs.pop(0)


def replay_live_route_b(
    *,
    raw_output_path: str | Path = DEFAULT_RAW_OUTPUT_PATH,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
    model: str = "deepseek-v4-flash",
    max_retries: int = 1,
    enable_risk_repair: bool = False,
) -> list[MethodResult]:
    """Replay saved slot outputs through the current Route B pipeline."""
    calls_by_case = _load_saved_outputs(raw_output_path, model=model)
    records = load_benchmark(benchmark_path)
    price_data = pd.read_csv(data_path)
    results: list[MethodResult] = []
    for record in records:
        case_id = str(record["id"])
        client = SavedSlotClient(list(calls_by_case.get(case_id, [])), case_id=case_id)
        method_prefix = "replay_route_b_slot_builder_risk_repair" if enable_risk_repair else "replay_route_b_slot_builder"
        method = f"{method_prefix}::{model}"
        results.append(
            _run_replay_record(
                record,
                method,
                client,
                price_data,
                max_retries=max_retries,
                enable_risk_repair=enable_risk_repair,
            )
        )
    return results


def _run_replay_record(
    record: dict[str, Any],
    method: str,
    client: SavedSlotClient,
    price_data: pd.DataFrame,
    *,
    max_retries: int,
    enable_risk_repair: bool,
) -> MethodResult:
    try:
        constructed = construct_qyir_from_query(
            str(record["user_query"]),
            client=client,
            max_retries=max_retries,
        )
    except Exception as exc:
        return _failed_result(record, method, f"route_b_replay_error: {type(exc).__name__}: {exc}")

    expected_reject = bool(record["should_reject"])
    if constructed.rejected:
        return MethodResult(
            case_id=str(record["id"]),
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
            errors=[constructed.rejection_reason or "rejected"],
        )

    if constructed.clarification_requested:
        correct = record_requires_clarification(record)
        return MethodResult(
            case_id=str(record["id"]),
            category=str(record["category"]),
            method=method,
            should_reject=expected_reject,
            rejected=False,
            schema_valid=False,
            semantic_consistent=correct,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            safe_rejection_correct=not expected_reject,
            clarification_requested=True,
            clarification_correct=correct,
            end_to_end_success=correct,
            errors=[f"{error['path']}: {error['message']}" for error in constructed.errors],
        )

    if not constructed.success or constructed.qyir is None:
        return _failed_result(
            record,
            method,
            "; ".join(f"{error['path']}: {error['message']}" for error in constructed.errors) or "route_b replay failed",
        )

    if enable_risk_repair:
        return _evaluate_qyir_with_risk_repair(
            record,
            method,
            constructed.qyir,
            price_data,
            rejected=False,
        )

    return _evaluate_qyir(
        record,
        method,
        constructed.qyir,
        price_data,
        rejected=False,
        repair_triggered=False,
        repair_success=False,
    )


def _evaluate_qyir_with_risk_repair(
    record: dict[str, Any],
    method: str,
    qyir: dict[str, Any],
    price_data: pd.DataFrame,
    *,
    rejected: bool,
) -> MethodResult:
    original = _evaluate_qyir(
        record,
        method,
        qyir,
        price_data,
        rejected=rejected,
        repair_triggered=False,
        repair_success=False,
    )
    if (
        not original.risk_violation
        or original.should_reject
        or not original.schema_valid
        or not original.semantic_consistent
        or not original.compile_success
        or not original.backtest_success
    ):
        return original

    risk = _audit_compiled_risk(qyir, price_data)
    if risk is None or not _has_risk_constraint_violation(risk):
        return original

    attempted_actions: list[str] = []
    for candidate in generate_risk_repair_candidates(qyir, risk):
        attempted_actions.extend(candidate.actions)
        candidate_result = _evaluate_qyir(
            record,
            method,
            candidate.qyir,
            price_data,
            rejected=rejected,
            repair_triggered=True,
            repair_success=False,
        )
        if candidate_result.end_to_end_success:
            return replace(
                candidate_result,
                repair_success=True,
                errors=[*candidate_result.errors, _format_repair_note(candidate.actions)],
            )

    if attempted_actions:
        return replace(
            original,
            repair_triggered=True,
            repair_success=False,
            errors=[*original.errors, _format_repair_note(attempted_actions)],
        )
    return original


def _audit_compiled_risk(qyir: dict[str, Any], price_data: pd.DataFrame) -> Any | None:
    compilation = compile_qyir(qyir, price_data)
    if not compilation.success or compilation.signals is None:
        return None
    backtest = run_backtest(compilation.signals, qyir.get("risk_control", {}))
    if not backtest.success:
        return None
    return audit_risk(qyir, backtest.metrics)


def _format_repair_note(actions: list[str]) -> str:
    unique = list(dict.fromkeys(actions))
    return "risk_repair: " + " ".join(unique)


def _load_saved_outputs(raw_output_path: str | Path, *, model: str) -> dict[str, list[str]]:
    calls: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for line in Path(raw_output_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if str(row.get("model")) != model:
            continue
        if row.get("error"):
            continue
        case_id = str(row["case_id"])
        attempt = int(row.get("attempt") or 1)
        calls[case_id].append((attempt, str(row.get("raw_output") or "")))
    return {case_id: [raw for _, raw in sorted(values, key=lambda item: item[0])] for case_id, values in calls.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay saved Route B slot outputs without API calls.")
    parser.add_argument("--raw-output", default=str(DEFAULT_RAW_OUTPUT_PATH))
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--enable-risk-repair", action="store_true")
    parser.add_argument("--output", default="experiments/results/route_b_live_deepseek_official_80_replay_results.csv")
    args = parser.parse_args(argv)

    results = replay_live_route_b(
        raw_output_path=args.raw_output,
        benchmark_path=args.benchmark,
        data_path=args.data,
        model=args.model,
        max_retries=args.max_retries,
        enable_risk_repair=args.enable_risk_repair,
    )
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} replay rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
