"""Aggregate QSGA experiment results into paper metrics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd


METRIC_COLUMNS = [
    "method",
    "schema_validity",
    "semantic_consistency",
    "compile_success",
    "backtest_success",
    "risk_violation",
    "repair_success",
    "safe_rejection_accuracy",
    "end_to_end_success",
]


def compute_metrics(results: pd.DataFrame) -> pd.DataFrame:
    """Compute phase-12 metrics from per-case result rows."""
    rows: list[dict[str, Any]] = []
    for method, group in results.groupby("method", sort=False):
        non_rejected = group[group["should_reject"] == False]  # noqa: E712
        unsafe = group[group["should_reject"] == True]  # noqa: E712
        repair_cases = group[group["repair_triggered"] == True]  # noqa: E712
        rows.append(
            {
                "method": method,
                "schema_validity": _mean(non_rejected, "schema_valid"),
                "semantic_consistency": _mean(non_rejected, "semantic_consistent"),
                "compile_success": _mean(non_rejected, "compile_success"),
                "backtest_success": _mean(non_rejected, "backtest_success"),
                "risk_violation": _mean(non_rejected, "risk_violation"),
                "repair_success": _mean(repair_cases, "repair_success"),
                "safe_rejection_accuracy": _mean(unsafe, "safe_rejection_correct"),
                "end_to_end_success": _mean(group, "end_to_end_success"),
            }
        )
    return pd.DataFrame(rows, columns=METRIC_COLUMNS)


def write_metrics(results_csv: str | Path, output_csv: str | Path) -> pd.DataFrame:
    """Load result CSV, aggregate metrics, write output CSV."""
    results = pd.read_csv(results_csv)
    metrics = compute_metrics(results)
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output, index=False)
    return metrics


def _mean(group: pd.DataFrame, column: str) -> float:
    if group.empty:
        return 0.0
    return float(group[column].astype(bool).mean())


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for metric aggregation."""
    parser = argparse.ArgumentParser(description="Aggregate QSGA experiment metrics.")
    parser.add_argument("--input", required=True, help="Per-case result CSV.")
    parser.add_argument("--output", default="experiments/results/metrics.csv")
    args = parser.parse_args(argv)

    metrics = write_metrics(args.input, args.output)
    print(metrics.to_string(index=False))
    print(f"Wrote metrics to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

