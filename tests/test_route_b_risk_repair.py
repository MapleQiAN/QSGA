"""Tests for bounded Route B risk-repair candidates."""

from __future__ import annotations

from types import SimpleNamespace

from qsgi.construction import generate_risk_repair_candidates


def _qyir() -> dict:
    return {
        "strategy_name": "route_b_risk",
        "version": "1.0",
        "market": {
            "symbol": "SPY",
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": [
            {"name": "SMA", "params": {"window": 20}, "alias": "sma_20"},
            {"name": "SMA", "params": {"window": 60}, "alias": "sma_60"},
        ],
        "entry_rules": [{"type": "cross_over", "left": "sma_20", "right": "sma_60"}],
        "exit_rules": [{"type": "cross_under", "left": "sma_20", "right": "sma_60"}],
        "risk_control": {
            "position_size": 0.5,
            "stop_loss": 0.08,
            "take_profit": None,
            "max_drawdown_limit": 0.15,
            "allow_short": True,
            "leverage": 1.5,
        },
    }


def _risk(*paths: str) -> SimpleNamespace:
    return SimpleNamespace(issues=[SimpleNamespace(path=path) for path in paths])


def test_risk_repair_candidates_are_conservative_and_bounded() -> None:
    qyir = _qyir()

    candidates = generate_risk_repair_candidates(qyir, _risk("backtest_metrics.max_drawdown"))

    assert candidates
    assert qyir["risk_control"]["position_size"] == 0.5
    for candidate in candidates:
        risk = candidate.qyir["risk_control"]
        assert risk["position_size"] <= 0.5
        assert risk["leverage"] == 1.0
        assert risk["allow_short"] is False
        assert risk["max_drawdown_limit"] == 0.15
    assert candidates[-1].qyir["risk_control"]["position_size"] == 0.1


def test_risk_repair_does_not_generate_candidates_for_quality_only_warnings() -> None:
    candidates = generate_risk_repair_candidates(_qyir(), _risk("backtest_metrics.sharpe_ratio"))

    assert candidates == []
