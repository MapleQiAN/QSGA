"""Tests for phase 11-15 experiment harness."""

from __future__ import annotations

import json

import pandas as pd

from experiments.baselines import build_qyir_from_record, load_benchmark, run_methods
from experiments.eval_metrics import compute_metrics
from experiments.paper_tables import generate_paper_tables
from experiments.run_no_oracle import run_no_oracle_method
from experiments.run_live_direct_code import evaluate_direct_code, replay_live_direct_code
from experiments.run_live_constrained_qyir import build_response_format
from experiments.run_live_llm import normalize_model_name, select_records
from experiments.run_live_simple_json import simple_json_to_qyir, write_simple_json_metrics
from experiments.run_multi_asset_smoke import run_multi_asset_smoke
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


def test_no_oracle_ambiguous_intent_requests_clarification() -> None:
    record = next(record for record in load_benchmark() if record["category"] == "ambiguous_intent")
    data = pd.read_csv("data/raw/spy_sample.csv")

    result = run_no_oracle_method(record, data)

    assert result.clarification_requested is True
    assert result.clarification_correct is True
    assert result.end_to_end_success is True


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
            "clarification_requested": False,
            "clarification_correct": False,
            "end_to_end_success": False,
        },
        {
            "category": "unsafe_request",
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
            "clarification_requested": False,
            "clarification_correct": False,
            "end_to_end_success": True,
        },
        {
            "category": "ambiguous_intent",
            "method": "m",
            "should_reject": False,
            "schema_valid": False,
            "semantic_consistent": True,
            "compile_success": False,
            "backtest_success": False,
            "risk_violation": False,
            "repair_triggered": False,
            "repair_success": False,
            "safe_rejection_correct": True,
            "clarification_requested": True,
            "clarification_correct": True,
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
        "clarification_accuracy",
        "construction_success",
        "end_to_end_success",
    ]
    assert metrics.loc[0, "schema_validity"] == 1.0
    assert metrics.loc[0, "safe_rejection_accuracy"] == 1.0
    assert metrics.loc[0, "clarification_accuracy"] == 1.0


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
                "clarification_accuracy": 1.0,
                "construction_success": 1.0,
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


def test_generate_paper_tables_includes_constrained_qyir_when_available(tmp_path) -> None:
    baseline_metrics = pd.DataFrame(
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
                "clarification_accuracy": 1.0,
                "construction_success": 1.0,
                "end_to_end_success": 1.0,
            }
        ]
    )
    constrained_metrics = pd.DataFrame(
        [
            {
                "method": "live_constrained_qyir::json_object::deepseek-v4-flash",
                "schema_validity": 0.538,
                "semantic_consistency": 0.538,
                "compile_success": 0.538,
                "backtest_success": 0.538,
                "risk_violation": 0.077,
                "repair_success": 0.143,
                "safe_rejection_accuracy": 1.0,
                "clarification_accuracy": 1.0,
                "construction_success": 0.462,
                "end_to_end_success": 0.65,
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
    baseline_csv = tmp_path / "baseline_metrics.csv"
    constrained_csv = tmp_path / "constrained_metrics.csv"
    results_csv = tmp_path / "results.csv"
    baseline_metrics.to_csv(baseline_csv, index=False)
    constrained_metrics.to_csv(constrained_csv, index=False)
    results.to_csv(results_csv, index=False)

    generate_paper_tables(
        baseline_csv,
        results_csv,
        tmp_path / "tables",
        live_constrained_qyir_metrics_csv=constrained_csv,
    )

    main_table = (tmp_path / "tables" / "main_comparison.md").read_text(encoding="utf-8")
    assert "Live QYIR + constrained JSON" in main_table


def test_simple_json_adapter_converts_basic_ma_json() -> None:
    record = load_benchmark()[0]
    simple_json = {
        "strategy_type": "moving_average",
        "asset": "SPY",
        "indicators": ["SMA20", "SMA60"],
        "buy_condition": "SMA20 crosses above SMA60",
        "sell_condition": "SMA20 crosses below SMA60",
        "risk": {"position_size": "low", "stop_loss": "8%", "leverage": "no"},
    }

    qyir, errors = simple_json_to_qyir(simple_json, record)

    assert qyir is not None
    assert validate_qyir(qyir).valid, errors
    assert qyir["entry_rules"][0]["type"] == "cross_over"


def test_simple_json_metrics_include_parse_and_conversion(tmp_path) -> None:
    results = pd.DataFrame(
        [
            {
                "method": "live_simple_json_adapter::test",
                "category": "trend_following",
                "should_reject": False,
                "json_parse_success": True,
                "qyir_conversion_success": False,
                "semantic_consistent": False,
                "compile_success": False,
                "risk_violation": False,
                "safe_rejection_correct": True,
                "end_to_end_success": False,
            },
            {
                "method": "live_simple_json_adapter::test",
                "category": "unsafe_request",
                "should_reject": True,
                "json_parse_success": False,
                "qyir_conversion_success": False,
                "semantic_consistent": True,
                "compile_success": False,
                "risk_violation": False,
                "safe_rejection_correct": True,
                "end_to_end_success": True,
            },
        ]
    )
    results_csv = tmp_path / "simple_results.csv"
    metrics_csv = tmp_path / "simple_metrics.csv"
    results.to_csv(results_csv, index=False)

    metrics = write_simple_json_metrics(results_csv, metrics_csv)

    assert metrics.loc[0, "json_parse_success"] == 1.0
    assert metrics.loc[0, "qyir_conversion_success"] == 0.0
    assert metrics.loc[0, "safe_rejection_accuracy"] == 1.0


def test_live_llm_subset_selection_is_reproducible_and_stratified() -> None:
    records = load_benchmark()

    first = select_records(records, case_limit=12, seed=20260505)
    second = select_records(records, case_limit=12, seed=20260505)

    assert [record["id"] for record in first] == [record["id"] for record in second]
    assert len(first) == 12
    assert len({record["category"] for record in first}) > 1


def test_live_llm_model_aliases_match_approved_display_names() -> None:
    assert normalize_model_name("Qwen3.6-Plus") == "qwen3.6-plus"
    assert normalize_model_name("Qwen3.6-Plus(0402)") == "qwen3.6-plus-2026-04-02"


def test_constrained_qyir_response_format_modes() -> None:
    assert build_response_format("none") is None
    assert build_response_format("json_object") == {"type": "json_object"}

    json_schema_format = build_response_format("json_schema")
    assert json_schema_format is not None
    assert json_schema_format["type"] == "json_schema"
    assert json_schema_format["json_schema"]["name"] == "qyir_v1"


def test_wo_qyir_ablation_emits_canonical_result() -> None:
    record = load_benchmark()[0]

    result = run_methods([record], ["wo_qyir"])[0]

    assert result.method == "wo_qyir"
    assert result.case_id == record["id"]
    assert result.end_to_end_success is False


def test_live_direct_code_evaluator_accepts_required_interface() -> None:
    record = load_benchmark()[0]
    data = pd.read_csv("data/raw/spy_sample.csv")
    code = """
def generate_signals(df):
    fast = df["close"].rolling(20).mean()
    slow = df["close"].rolling(60).mean()
    return (fast > slow).astype(int)
"""

    result = evaluate_direct_code(record, "live_direct_code::test", code, data)

    assert result.syntax_success
    assert result.interface_success
    assert result.runtime_success
    assert result.trade_validity
    assert result.backtest_success


def test_live_direct_code_replay_uses_saved_raw_outputs(tmp_path) -> None:
    code = """
def generate_signals(df):
    fast = df["close"].rolling(20).mean()
    slow = df["close"].rolling(60).mean()
    return (fast > slow).astype(int)
"""
    raw_path = tmp_path / "raw.jsonl"
    metadata_path = tmp_path / "metadata.json"
    raw_path.write_text(
        json.dumps(
            {
                "model": "test-model",
                "method": "live_direct_code::test-model",
                "case_id": "qsi_001",
                "attempt": 1,
                "prompt": "prompt",
                "raw_output": code,
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 2,
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    metadata_path.write_text(
        json.dumps({"models": ["test-model"], "case_ids": ["qsi_001"]}),
        encoding="utf-8",
    )

    results = replay_live_direct_code(raw_output_path=raw_path, metadata_path=metadata_path)

    assert len(results) == 1
    assert results[0].method == "live_direct_code::test-model"
    assert results[0].runtime_success


def test_multi_asset_smoke_runs_synthetic_symbols() -> None:
    results = run_multi_asset_smoke(case_id="qsi_001")

    assert len(results) == 5
    assert {result.symbol for result in results} == {"SPY", "QQQ", "GLD"}
    assert all(result.compile_success for result in results)
    assert all(result.backtest_success for result in results)
    assert all(result.risk_audit_runnable for result in results)
