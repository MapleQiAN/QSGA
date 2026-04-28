"""Tests for explicit intent-slot semantic verification."""

from __future__ import annotations

from verifier.semantic_verifier import extract_intent_slots, semantic_verify


def base_qyir() -> dict:
    return {
        "strategy_name": "ma_cross_spy",
        "description": "SMA20 上穿 SMA60 买入，下穿卖出",
        "version": "1.0",
        "market": {
            "symbol": "SPY",
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": [
            {"name": "SMA", "params": {"window": 20}, "alias": "sma_short"},
            {"name": "SMA", "params": {"window": 60}, "alias": "sma_long"},
        ],
        "entry_rules": [
            {"type": "cross_over", "left": "sma_short", "right": "sma_long"}
        ],
        "exit_rules": [
            {"type": "cross_under", "left": "sma_short", "right": "sma_long"}
        ],
        "risk_control": {
            "position_size": 0.4,
            "stop_loss": 0.08,
            "take_profit": None,
            "max_drawdown_limit": 0.2,
            "allow_short": False,
            "leverage": 1.0,
        },
    }


def test_extracts_supported_explicit_slots():
    slots = extract_intent_slots("适合新手，低风险，不要杠杆，不要做空，不要满仓，控制回撤，设置止损，做中线")

    assert {
        "novice_friendly",
        "low_risk",
        "no_leverage",
        "no_short",
        "no_full_position",
        "drawdown_control",
        "stop_loss_required",
        "medium_horizon",
    }.issubset(slots)


def test_semantic_verify_passes_aligned_qyir():
    result = semantic_verify(
        "我想做一个适合新手的低风险中线双均线策略，不要杠杆，不要做空，控制回撤在20%，设置止损",
        base_qyir(),
    )

    assert result.passed is True
    assert result.violations == []


def test_detects_leverage_and_short_conflicts():
    qyir = base_qyir()
    qyir["risk_control"]["leverage"] = 2.0
    qyir["risk_control"]["allow_short"] = True

    result = semantic_verify("不要杠杆，也不要做空", qyir)

    assert result.passed is False
    assert {violation.path for violation in result.violations} == {
        "risk_control.leverage",
        "risk_control.allow_short",
    }


def test_detects_conservative_and_full_position_conflicts():
    qyir = base_qyir()
    qyir["risk_control"]["position_size"] = 0.95

    result = semantic_verify("稳一点，不要满仓，适合新手", qyir)

    assert result.passed is False
    assert [violation.path for violation in result.violations].count("risk_control.position_size") == 2


def test_detects_stop_loss_and_drawdown_conflicts():
    qyir = base_qyir()
    qyir["risk_control"]["stop_loss"] = None
    qyir["risk_control"]["max_drawdown_limit"] = 0.3

    result = semantic_verify("设置止损，最大回撤控制在20%以内", qyir)

    assert result.passed is False
    assert {violation.path for violation in result.violations} == {
        "risk_control.stop_loss",
        "risk_control.max_drawdown_limit",
    }


def test_detects_horizon_conflict():
    qyir = base_qyir()
    qyir["indicators"] = [
        {"name": "SMA", "params": {"window": 5}, "alias": "sma_fast"},
        {"name": "SMA", "params": {"window": 20}, "alias": "sma_slow"},
    ]

    result = semantic_verify("做长线均线策略", qyir)

    assert result.passed is False
    assert result.violations[0].path == "indicators"

