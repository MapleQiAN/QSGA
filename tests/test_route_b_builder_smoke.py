"""Tests for the offline Route B builder smoke runner."""

from __future__ import annotations

from experiments.run_route_b_builder_smoke import expected_slots_to_spec


def test_expected_slots_to_spec_maps_construct_case():
    spec = expected_slots_to_spec(
        {
            "id": "qsi_test",
            "category": "trend_following",
            "user_query": "20日均线上穿60日均线买入",
            "should_reject": False,
            "expected_slots": {
                "strategy_family": "ma_cross",
                "fast_window": 20,
                "slow_window": 60,
                "allow_short": False,
                "allow_leverage": False,
                "safe_action": "generate",
            },
        }
    )

    assert spec.safe_action == "construct"
    assert [indicator.window for indicator in spec.indicators] == [20, 60]


def test_expected_slots_to_spec_maps_reject_case():
    spec = expected_slots_to_spec(
        {
            "id": "qsi_bad",
            "category": "unsafe_request",
            "user_query": "稳赚不赔",
            "should_reject": True,
            "expected_slots": {},
        }
    )

    assert spec.safe_action == "reject"


def test_expected_slots_to_spec_preserves_rsi_window():
    spec = expected_slots_to_spec(
        {
            "id": "qsi_rsi",
            "category": "mean_reversion",
            "user_query": "RSI 21 低买高卖",
            "should_reject": False,
            "expected_slots": {
                "strategy_family": "rsi_reversal",
                "lookback_window": 21,
                "entry_threshold": 30,
                "exit_threshold": 70,
                "safe_action": "generate",
            },
        }
    )

    assert spec.indicators[0].name == "RSI"
    assert spec.indicators[0].window == 21
    assert spec.entry_logic.left == "rsi21"


def test_expected_slots_to_spec_maps_clarify_case():
    spec = expected_slots_to_spec(
        {
            "id": "qsi_amb",
            "category": "ambiguous_intent",
            "user_query": "稳一点",
            "should_reject": False,
            "expected_slots": {"safe_action": "clarify"},
        }
    )

    assert spec.safe_action == "clarify"
    assert spec.ambiguity.requires_clarification is True
