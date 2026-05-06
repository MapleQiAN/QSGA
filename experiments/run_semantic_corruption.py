"""Run semantic slot-corruption checks for QYIR intent verification.

This experiment constructs schema-valid QYIR candidates that deliberately
conflict with explicit user intent slots. It isolates the semantic verifier's
role from oracle-slot construction by asking whether conflicts would pass if
schema validation were the only gate.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from experiments.baselines import BenchmarkRecord, build_qyir_from_record, load_benchmark
from qyir.validator import validate_qyir
from verifier.semantic_verifier import semantic_verify


@dataclass(frozen=True)
class CorruptionCase:
    """One semantic corruption to apply to a benchmark-derived QYIR."""

    case_id: str
    label: str
    corruption: Callable[[dict[str, Any]], None]


def run_semantic_corruption(
    benchmark_path: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return per-case and aggregate semantic-corruption results."""
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    rows: list[dict[str, Any]] = []
    for case in _corruption_cases():
        record = records[case.case_id]
        qyir = build_qyir_from_record(record)
        case.corruption(qyir)
        schema = validate_qyir(qyir)
        semantic = semantic_verify(str(record["user_query"]), qyir)
        without_semantic_passes = schema.valid
        with_semantic_detects = schema.valid and not semantic.passed
        rows.append(
            {
                "case_id": str(record["id"]),
                "category": str(record["category"]),
                "label": case.label,
                "schema_valid": schema.valid,
                "without_semantic_passes": without_semantic_passes,
                "with_semantic_detects": with_semantic_detects,
                "detected_slots": ",".join(semantic.detected_slots),
                "violation_paths": ",".join(issue.path for issue in semantic.issues),
                "violation_messages": " | ".join(issue.message for issue in semantic.issues),
            }
        )
    results = pd.DataFrame(rows)
    metrics = pd.DataFrame(
        [
            {
                "schema_valid_cases": int(results["schema_valid"].astype(bool).sum()),
                "total_cases": int(len(results)),
                "without_semantic_pass_through_rate": float(
                    results["without_semantic_passes"].astype(bool).mean()
                ),
                "with_semantic_detection_rate": float(results["with_semantic_detects"].astype(bool).mean()),
            }
        ]
    )
    return results, metrics


def _corruption_cases() -> list[CorruptionCase]:
    return [
        CorruptionCase("qsi_023", "no_short_but_allow_short", _allow_short),
        CorruptionCase("qsi_048", "drawdown_limit_loosened", _loosen_drawdown),
        CorruptionCase("qsi_041", "low_risk_full_position", _full_position),
        CorruptionCase("qsi_039", "no_full_position_near_full", _near_full_position),
        CorruptionCase("qsi_042", "stop_loss_removed", _remove_stop_loss),
        CorruptionCase("qsi_055", "novice_full_position", _full_position),
        CorruptionCase("qsi_006", "long_horizon_short_windows", _short_windows),
    ]


def _allow_short(qyir: dict[str, Any]) -> None:
    qyir["risk_control"]["allow_short"] = True


def _loosen_drawdown(qyir: dict[str, Any]) -> None:
    qyir["risk_control"]["max_drawdown_limit"] = 0.2


def _full_position(qyir: dict[str, Any]) -> None:
    qyir["risk_control"]["position_size"] = 1.0


def _near_full_position(qyir: dict[str, Any]) -> None:
    qyir["risk_control"]["position_size"] = 0.95


def _remove_stop_loss(qyir: dict[str, Any]) -> None:
    qyir["risk_control"]["stop_loss"] = None


def _short_windows(qyir: dict[str, Any]) -> None:
    for indicator, window in zip(qyir.get("indicators", []), (5, 10)):
        if "window" in indicator.get("params", {}):
            indicator["params"]["window"] = window
        if "slow" in indicator.get("params", {}):
            indicator["params"]["slow"] = window


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run semantic slot-corruption experiment.")
    parser.add_argument("--benchmark", default="benchmark/qsi_bench_v1.jsonl")
    parser.add_argument("--output", default="experiments/results/semantic_corruption_results.csv")
    parser.add_argument("--metrics-output", default="experiments/results/semantic_corruption_metrics.csv")
    args = parser.parse_args(argv)

    results, metrics = run_semantic_corruption(args.benchmark)
    output = Path(args.output)
    metrics_output = Path(args.metrics_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output, index=False)
    metrics.to_csv(metrics_output, index=False)
    print(metrics.to_string(index=False))
    print(f"Wrote {len(results)} semantic-corruption rows to {output}")
    print(f"Wrote semantic-corruption metrics to {metrics_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
