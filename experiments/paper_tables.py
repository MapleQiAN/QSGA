"""Generate phase-14 paper tables from aggregated metrics."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def generate_paper_tables(
    metrics_csv: str | Path,
    results_csv: str | Path,
    output_dir: str | Path = "experiments/tables",
) -> list[Path]:
    """Write main comparison, repair, safe-rejection, and case-analysis tables."""
    metrics = pd.read_csv(metrics_csv)
    results = pd.read_csv(results_csv)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = [
        _write_main_table(metrics, out / "main_comparison.md"),
        _write_repair_table(results, out / "repair_effect.md"),
        _write_safe_rejection_table(results, out / "safe_rejection.md"),
        _write_case_table(out / "case_analysis.md"),
    ]
    return paths


def _write_main_table(metrics: pd.DataFrame, path: Path) -> Path:
    renamed = metrics.rename(
        columns={
            "method": "Method",
            "schema_validity": "Schema Validity ↑",
            "semantic_consistency": "Semantic Consistency ↑",
            "compile_success": "Compile Success ↑",
            "backtest_success": "Backtest Success ↑",
            "risk_violation": "Risk Violation ↓",
            "end_to_end_success": "E2E Success ↑",
        }
    )
    cols = [
        "Method",
        "Schema Validity ↑",
        "Semantic Consistency ↑",
        "Compile Success ↑",
        "Backtest Success ↑",
        "Risk Violation ↓",
        "E2E Success ↑",
    ]
    path.write_text(_to_markdown(renamed[cols]), encoding="utf-8")
    return path


def _write_repair_table(results: pd.DataFrame, path: Path) -> Path:
    repaired = results[results["repair_triggered"] == True]  # noqa: E712
    rows = []
    for method, group in repaired.groupby("method", sort=False):
        rows.append(
            {
                "Method": method,
                "Before Repair": int(len(group)),
                "After Repair": int(group["repair_success"].astype(bool).sum()),
                "Repair Success": float(group["repair_success"].astype(bool).mean()) if len(group) else 0.0,
            }
        )
    table = pd.DataFrame(rows or [{"Method": "n/a", "Before Repair": 0, "After Repair": 0, "Repair Success": 0.0}])
    path.write_text(_to_markdown(table), encoding="utf-8")
    return path


def _write_safe_rejection_table(results: pd.DataFrame, path: Path) -> Path:
    unsafe = results[results["should_reject"] == True]  # noqa: E712
    rows = []
    for category, group in unsafe.groupby("category", sort=False):
        rows.append(
            {
                "Category": category,
                "Samples": int(len(group)),
                "Correct Rejection": int(group["safe_rejection_correct"].astype(bool).sum()),
                "Accuracy": float(group["safe_rejection_correct"].astype(bool).mean()) if len(group) else 0.0,
            }
        )
    table = pd.DataFrame(rows or [{"Category": "unsafe_request", "Samples": 0, "Correct Rejection": 0, "Accuracy": 0.0}])
    path.write_text(_to_markdown(table), encoding="utf-8")
    return path


def _write_case_table(path: Path) -> Path:
    table = pd.DataFrame(
        [
            {
                "User Query": "低风险双均线",
                "Direct Code Result": "May run without schema/risk gates",
                "QSGA Result": "Valid QYIR plus risk audit",
                "Improvement": "Executable and auditable",
            },
            {
                "User Query": "不要杠杆",
                "Direct Code Result": "May ignore leverage constraint",
                "QSGA Result": "leverage locked to 1.0",
                "Improvement": "Explicit risk consistency",
            },
            {
                "User Query": "稳赚不赔",
                "Direct Code Result": "May produce unsafe strategy",
                "QSGA Result": "Safe rejection",
                "Improvement": "Unsafe intent blocked",
            },
        ]
    )
    path.write_text(_to_markdown(table), encoding="utf-8")
    return path


def _to_markdown(frame: pd.DataFrame) -> str:
    """Render a compact GitHub markdown table without optional tabulate."""
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = [_format_cell(row[column]) for column in frame.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _format_cell(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate paper-ready experiment tables.")
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--results", required=True)
    parser.add_argument("--output-dir", default="experiments/tables")
    args = parser.parse_args(argv)

    paths = generate_paper_tables(args.metrics, args.results, args.output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
