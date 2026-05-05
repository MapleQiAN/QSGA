"""Tests for phase 11-15 experiment harness."""

from __future__ import annotations

import json

import pandas as pd

from experiments.baselines import build_qyir_from_record, load_benchmark, run_methods
from experiments.eval_metrics import compute_metrics
from experiments.paper_tables import generate_paper_tables
from qyir.validator import validate_qyir


def test_build_qyir_from_record_is_schema_valid() -> None:
    record = load_benchmark()[0]
    qyir = build_qyir_from_record(record)
    result = validate_qyir(qyir)
    assert result.valid, result.summary


def test_run_full_method_returns_rows_for_subset() -> None:
    records = load_benchmark()[:3]
    results = run_methods(records, ["qsga_full"])
    assert len(results) == 3
    assert {result.method for result in results} == {"qsga_full"}
    assert all(result.schema_valid for result in results)
    assert all(result.compile_success for result in results)


def test_semantic_ablation_is_still_scored_against_gold_slots() -> None:
    record = next(record for record in load_benchmark() if record["category"] == "ambiguous_intent")

    result = run_methods([record], ["wo_semantic_verification"])[0]

    assert result.schema_valid is True
    assert result.semantic_consistent is False
    assert result.end_to_end_success is False


def test_full_method_can_repair_risk_constraint_violations() -> None:
    record = load_benchmark()[0]

    result = run_methods([record], ["qsga_full"])[0]

    assert result.repair_triggered is True
    assert result.repair_success is True
    assert result.risk_violation is False


def test_metric_aggregation_uses_expected_columns() -> None:
    rows = [
        {
            "method": "m",
            "should_reject": False,
            "schema_valid": True,
            "semantic_consistent": True,
            "compile_success": True,
            "backtest_success": False,
            "risk_violation": False,
            "repair_triggered": False,
            "repair_success": False,
            "safe_rejection_correct": True,
            "end_to_end_success": False,
        },
        {
            "method": "m",
            "should_reject": True,
            "schema_valid": False,
            "semantic_consistent": False,
            "compile_success": False,
            "backtest_success": False,
            "risk_violation": False,
            "repair_triggered": False,
            "repair_success": False,
            "safe_rejection_correct": True,
            "end_to_end_success": True,
        },
    ]
    metrics = compute_metrics(pd.DataFrame(rows))
    assert list(metrics.columns) == [
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
    assert metrics.loc[0, "schema_validity"] == 1.0
    assert metrics.loc[0, "safe_rejection_accuracy"] == 1.0


def test_generate_paper_tables(tmp_path) -> None:
    metrics = pd.DataFrame(
        [
            {
                "method": "qsga_full",
                "schema_validity": 1.0,
                "semantic_consistency": 1.0,
                "compile_success": 1.0,
                "backtest_success": 1.0,
                "risk_violation": 0.0,
                "repair_success": 1.0,
                "safe_rejection_accuracy": 1.0,
                "end_to_end_success": 1.0,
            }
        ]
    )
    results = pd.DataFrame(
        [
            {
                "method": "qsga_full",
                "category": "unsafe_request",
                "should_reject": True,
                "repair_triggered": False,
                "repair_success": False,
                "safe_rejection_correct": True,
            }
        ]
    )
    metrics_csv = tmp_path / "metrics.csv"
    results_csv = tmp_path / "results.csv"
    metrics.to_csv(metrics_csv, index=False)
    results.to_csv(results_csv, index=False)

    paths = generate_paper_tables(metrics_csv, results_csv, tmp_path / "tables", metrics_csv)

    assert len(paths) == 5
    assert all(path.exists() for path in paths)
    assert "QSGA Result" in (tmp_path / "tables" / "case_analysis.md").read_text(encoding="utf-8")
    assert (tmp_path / "tables" / "ablation_comparison.md").exists()
