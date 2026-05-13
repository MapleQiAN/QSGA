"""Tests for Route B slot-to-QYIR construction utilities."""

from __future__ import annotations

from qsgi.construction import (
    StrategySlotSpec,
    build_qyir_from_slots,
    canonicalize_qyir,
    canonicalize_reference,
    normalize_percentage,
)
from qyir.validator import validate_qyir


def test_slot_schema_accepts_generate_alias():
    spec = StrategySlotSpec.model_validate(
        {
            "strategy_family": "trend_following",
            "indicators": [{"name": "sma", "window": 20, "role": "fast"}],
            "safe_action": "generate",
        }
    )

    assert spec.safe_action == "construct"
    assert spec.indicators[0].name == "SMA"


def test_slot_schema_normalizes_common_live_model_variants():
    spec = StrategySlotSpec.model_validate(
        {
            "strategy_family": "mean_reversion",
            "market_scope": {"symbol": "unknown", "asset_type": "UNKNOWN", "timeframe": "UNKNOWN"},
            "indicators": [{"name": "RSI", "window": 14, "role": "momentum"}],
            "entry_logic": {"operator": "less_than", "left": "rsi14", "right": 35},
            "exit_logic": None,
            "risk_constraints": None,
            "safe_action": "construct",
        }
    )

    assert spec.indicators[0].role == "unknown"
    assert spec.market_scope.symbol is None
    assert spec.market_scope.asset_type == "unknown"
    assert spec.exit_logic.operator is None
    assert spec.risk_constraints.leverage is None


def test_canonicalize_reference_normalizes_common_aliases():
    value, events = canonicalize_reference("SMA_20")

    assert value == "sma_20"
    assert events[0].rule_id == "reference.indicator_alias"


def test_normalize_percentage_strings():
    assert normalize_percentage("20%") == 0.2
    assert normalize_percentage("百分之十") == 0.1
    assert normalize_percentage("30") == 0.3


def test_canonicalize_qyir_updates_alias_references_and_risk_strings():
    qyir = {
        "strategy_name": "route_b_case",
        "version": "1.0",
        "market": {
            "symbol": "SPY",
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": [
            {"name": "SMA", "params": {"window": 20}, "alias": "SMA_20"},
            {"name": "SMA", "params": {"window": 60}, "alias": "sma60"},
        ],
        "entry_rules": [{"type": "cross_over", "left": "SMA_20", "right": "sma60"}],
        "exit_rules": [{"type": "cross_under", "left": "SMA_20", "right": "sma60"}],
        "risk_control": {
            "position_size": "50%",
            "stop_loss": "10%",
            "take_profit": None,
            "max_drawdown_limit": "20%",
            "allow_short": "别做空",
            "leverage": "不要杠杆",
        },
    }

    result = canonicalize_qyir(qyir)

    assert result.canonical_qyir["indicators"][0]["alias"] == "sma_20"
    assert result.canonical_qyir["indicators"][1]["alias"] == "sma_60"
    assert result.canonical_qyir["entry_rules"][0]["left"] == "sma_20"
    assert result.canonical_qyir["risk_control"]["position_size"] == 0.5
    assert result.canonical_qyir["risk_control"]["leverage"] == 1.0
    assert validate_qyir(result.canonical_qyir).valid


def test_builder_constructs_valid_ma_cross_qyir():
    result = build_qyir_from_slots(
        {
            "strategy_family": "trend_following",
            "market_scope": {"symbol": "SPY", "asset_type": "etf", "timeframe": "daily"},
            "indicators": [
                {"name": "SMA", "window": 20, "role": "fast"},
                {"name": "SMA", "window": 60, "role": "slow"},
            ],
            "entry_logic": {"operator": "cross_over", "left": "sma20", "right": "sma60"},
            "exit_logic": {"operator": "cross_under", "left": "sma20", "right": "sma60"},
            "risk_constraints": {
                "position_size": 0.4,
                "max_drawdown_limit": 0.2,
                "allow_short": False,
                "leverage": 1.0,
            },
            "safe_action": "construct",
        },
        strategy_name="MA Cross Route B",
    )

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["strategy_name"] == "ma_cross_route_b"
    assert result.qyir["entry_rules"][0] == {"type": "cross_over", "left": "sma_20", "right": "sma_60"}
    assert validate_qyir(result.qyir).valid


def test_builder_constructs_rsi_mean_reversion_defaults():
    result = build_qyir_from_slots(
        {
            "strategy_family": "mean_reversion",
            "indicators": [{"name": "RSI", "window": 14, "role": "threshold"}],
            "risk_constraints": {"position_size": 0.5, "leverage": 1.0},
            "safe_action": "construct",
        }
    )

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["entry_rules"][0]["type"] == "less_than"
    assert result.qyir["entry_rules"][0]["right"] == 30.0
    assert result.qyir["risk_control"]["stop_loss"] == 0.08
    assert validate_qyir(result.qyir).valid


def test_builder_converts_single_ma_price_breakout_to_supported_ma_cross():
    result = build_qyir_from_slots(
        {
            "strategy_family": "trend_following",
            "market_scope": {"symbol": "GLD", "asset_type": "etf", "timeframe": "daily"},
            "indicators": [{"name": "SMA", "window": 120, "role": "trend"}],
            "entry_logic": {"operator": "cross_over", "left": "close", "right": "sma120"},
            "exit_logic": {"operator": "cross_under", "left": "close", "right": "sma120"},
            "safe_action": "construct",
        }
    )

    assert result.success is True
    assert result.qyir is not None
    assert {indicator["alias"] for indicator in result.qyir["indicators"]} == {"sma_20", "sma_120"}
    assert result.qyir["entry_rules"][0] == {"type": "cross_over", "left": "sma_20", "right": "sma_120"}
    assert validate_qyir(result.qyir).valid


def test_builder_refuses_unknown_indicator():
    result = build_qyir_from_slots(
        {
            "strategy_family": "unknown",
            "indicators": [{"name": "UNKNOWN", "role": "unknown"}],
            "safe_action": "construct",
        }
    )

    assert result.success is False
    assert result.errors[0]["path"] == "indicators[0].name"


def test_builder_returns_clarification_failure():
    result = build_qyir_from_slots(
        {
            "strategy_family": "unknown",
            "ambiguity": {
                "requires_clarification": True,
                "missing_slots": ["entry_logic", "risk_constraints"],
            },
            "safe_action": "clarify",
        }
    )

    assert result.success is False
    assert "Clarification required" in result.errors[0]["message"]
