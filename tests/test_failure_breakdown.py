"""Tests for Route B live failure taxonomy classification."""

from __future__ import annotations

import pandas as pd

from experiments.analyze_failure_breakdown import classify_failure


def _row(**kwargs):
    defaults = {
        "should_reject": False,
        "rejected": False,
        "schema_valid": False,
        "semantic_consistent": False,
        "compile_success": False,
        "backtest_success": False,
        "risk_violation": False,
        "clarification_requested": False,
        "clarification_correct": False,
        "end_to_end_success": False,
        "errors": "",
    }
    defaults.update(kwargs)
    return pd.Series(defaults)


def test_classifies_alias_failure_before_generic_schema_failure():
    classification = classify_failure(
        _row(errors="root: Value error, entry_rules[0].left references unknown alias 'close'")
    )

    assert classification.failure_type == "alias_failure"
    assert classification.stage == "reference"


def test_classifies_parse_failure():
    classification = classify_failure(_row(errors="json: Invalid JSON from live LLM: line 1"))

    assert classification.failure_type == "parse_failure"


def test_classifies_semantic_mismatch_after_schema_passes():
    classification = classify_failure(
        _row(schema_valid=True, errors="risk_control.position_size: Conservative intent conflicts with high position size.")
    )

    assert classification.failure_type == "semantic_mismatch"


def test_classifies_risk_violation_after_execution_passes():
    classification = classify_failure(
        _row(
            schema_valid=True,
            semantic_consistent=True,
            compile_success=True,
            backtest_success=True,
            risk_violation=True,
            errors="backtest_metrics.max_drawdown: The backtest max drawdown exceeds 20.0%.",
        )
    )

    assert classification.failure_type == "risk_violation"


def test_classifies_unsafe_intent_failure_first():
    classification = classify_failure(_row(should_reject=True, errors="raw baseline has no safe-rejection gate"))

    assert classification.failure_type == "unsafe_intent_failure"
