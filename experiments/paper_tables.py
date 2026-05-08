"""Generate phase-14 paper tables from aggregated metrics."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def generate_paper_tables(
    metrics_csv: str | Path,
    results_csv: str | Path,
    output_dir: str | Path = "experiments/tables",
    ablation_metrics_csv: str | Path | None = None,
    no_oracle_metrics_csv: str | Path | None = None,
    live_direct_code_metrics_csv: str | Path | None = None,
    live_direct_code_shared_rejection_metrics_csv: str | Path | None = None,
) -> list[Path]:
    """Write main comparison, repair, safe-rejection, and case-analysis tables."""
    metrics = pd.read_csv(metrics_csv)
    results = pd.read_csv(results_csv)
    main_metrics = [metrics]
    for optional_csv in (
        live_direct_code_metrics_csv,
        live_direct_code_shared_rejection_metrics_csv,
        no_oracle_metrics_csv,
    ):
        if optional_csv is not None:
            optional_path = Path(optional_csv)
            if optional_path.exists():
                main_metrics.append(pd.read_csv(optional_path))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths = [
        _write_main_table(pd.concat(main_metrics, ignore_index=True), out / "main_comparison.md"),
        _write_repair_table(results, out / "repair_effect.md"),
        _write_safe_rejection_table(results, out / "safe_rejection.md"),
        _write_case_table(out / "case_analysis.md"),
    ]
    if ablation_metrics_csv is not None:
        ablation_metrics = pd.read_csv(ablation_metrics_csv)
        paths.append(_write_ablation_table(ablation_metrics, out / "ablation_comparison.md"))
    return paths


def _write_main_table(metrics: pd.DataFrame, path: Path) -> Path:
    rows: list[dict[str, object]] = []
    for label, candidates in [
        ("Direct code diagnostic", ["live_direct_code::qwen3.6-flash", "direct_code"]),
        (
            "Direct code + shared rejection",
            ["live_direct_code_shared_rejection::qwen3.6-flash"],
        ),
        ("QSGA no-oracle", ["qsga_no_oracle_slots"]),
        ("QSGA oracle-slot upper bound", ["qsga_full"]),
    ]:
        row = _first_metric_row(metrics, candidates)
        if row is None:
            continue
        rows.append(
            {
                "Method": label,
                "E2E": _format_main_rate(row["end_to_end_success"]),
                "Construction": _format_main_rate(row["construction_success"]),
                "Risk Violation": _format_main_rate(row["risk_violation"]),
                "Unsafe Rejection": _format_main_rate(row["safe_rejection_accuracy"]),
            }
        )
    table = pd.DataFrame(
        rows
        or [
            {
                "Method": "n/a",
                "E2E": 0.0,
                "Construction": 0.0,
                "Risk Violation": 0.0,
                "Unsafe Rejection": 0.0,
            }
        ]
    )
    path.write_text(_to_markdown(table), encoding="utf-8")
    return path


def _first_metric_row(metrics: pd.DataFrame, method_names: list[str]) -> pd.Series | None:
    for method_name in method_names:
        matched = metrics[metrics["method"] == method_name]
        if not matched.empty:
            return matched.iloc[0]
    return None


def _format_main_rate(value: object) -> str:
    return f"{float(value) + 1e-12:.3f}"


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
    unsafe = unsafe[~unsafe["method"].isin(["direct_code", "direct_json"])]
    rows = []
    for method, group in unsafe.groupby("method", sort=False):
        rows.append(
            {
                "Method": method,
                "Unsafe Samples": int(len(group)),
                "Correct Rejection": int(group["safe_rejection_correct"].astype(bool).sum()),
                "Accuracy": float(group["safe_rejection_correct"].astype(bool).mean()) if len(group) else 0.0,
            }
        )
    table = pd.DataFrame(
        rows or [{"Method": "n/a", "Unsafe Samples": 0, "Correct Rejection": 0, "Accuracy": 0.0}]
    )
    path.write_text(_to_markdown(table), encoding="utf-8")
    return path


def _write_ablation_table(metrics: pd.DataFrame, path: Path) -> Path:
    renamed = metrics.rename(
        columns={
            "method": "Method",
            "semantic_consistency": "Semantic Consistency ↑",
            "risk_violation": "Risk Violation ↓",
            "safe_rejection_accuracy": "Safe Rejection Accuracy ↑",
            "repair_success": "Repair Success ↑",
            "clarification_accuracy": "Clarification Accuracy ↑",
            "construction_success": "Construction Success ↑",
            "end_to_end_success": "E2E Success ↑",
        }
    )
    cols = [
        "Method",
        "Semantic Consistency ↑",
        "Risk Violation ↓",
        "Safe Rejection Accuracy ↑",
        "Repair Success ↑",
        "Clarification Accuracy ↑",
        "Construction Success ↑",
        "E2E Success ↑",
    ]
    path.write_text(_to_markdown(renamed[cols]), encoding="utf-8")
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
    parser.add_argument("--ablation-metrics")
    parser.add_argument("--no-oracle-metrics")
    parser.add_argument("--live-direct-code-metrics")
    parser.add_argument("--live-direct-code-shared-rejection-metrics")
    parser.add_argument("--output-dir", default="experiments/tables")
    args = parser.parse_args(argv)

    paths = generate_paper_tables(
        args.metrics,
        args.results,
        args.output_dir,
        args.ablation_metrics,
        args.no_oracle_metrics,
        args.live_direct_code_metrics,
        args.live_direct_code_shared_rejection_metrics,
    )
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
