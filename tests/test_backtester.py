"""Tests for backtester module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtester.metrics import (
    annualized_return,
    compute_all_metrics,
    max_drawdown,
    num_trades,
    sharpe_ratio,
    total_return,
    volatility,
    win_rate,
)
from backtester.simple_backtester import (
    BacktestResult,
    run_backtest,
    run_backtest_pipeline,
    format_backtest_summary,
)


# ---------------------------------------------------------------------------
# Metrics tests
# ---------------------------------------------------------------------------


class TestTotalReturn:
    def test_positive_return(self):
        equity = pd.Series([100, 110, 123.5])
        assert total_return(equity) == pytest.approx(0.235)

    def test_negative_return(self):
        equity = pd.Series([100, 90, 80])
        assert total_return(equity) == pytest.approx(-0.2)

    def test_flat(self):
        equity = pd.Series([100, 100, 100])
        assert total_return(equity) == pytest.approx(0.0)

    def test_single_point(self):
        assert total_return(pd.Series([100])) == 0.0


class TestAnnualizedReturn:
    def test_one_year(self):
        # 252 trading days, 10% return
        equity = pd.Series([100] + [100 * 1.10 ** (i / 251) for i in range(1, 252)])
        result = annualized_return(equity)
        assert result == pytest.approx(0.10, abs=0.01)

    def test_single_point(self):
        assert annualized_return(pd.Series([100])) == 0.0


class TestSharpeRatio:
    def test_zero_std(self):
        returns = pd.Series([0.0, 0.0, 0.0])
        assert sharpe_ratio(returns) == 0.0

    def test_positive_sharpe(self):
        returns = pd.Series([0.01, 0.02, 0.015, 0.005, 0.01])
        result = sharpe_ratio(returns)
        assert result > 0

    def test_short_series(self):
        assert sharpe_ratio(pd.Series([0.01])) == 0.0


class TestMaxDrawdown:
    def test_simple_drawdown(self):
        equity = pd.Series([100, 120, 90, 110])
        # Peak is 120, trough is 90 → drawdown = 90/120 - 1 = -0.25
        assert max_drawdown(equity) == pytest.approx(-0.25)

    def test_no_drawdown(self):
        equity = pd.Series([100, 110, 120])
        assert max_drawdown(equity) == pytest.approx(0.0)

    def test_single_point(self):
        assert max_drawdown(pd.Series([100])) == 0.0


class TestVolatility:
    def test_basic(self):
        returns = pd.Series([0.01, -0.01, 0.02, -0.02])
        result = volatility(returns)
        assert result > 0

    def test_zero_returns(self):
        returns = pd.Series([0.0, 0.0, 0.0])
        assert volatility(returns) == 0.0


class TestWinRate:
    def test_all_wins(self):
        assert win_rate([0.01, 0.05, 0.02]) == pytest.approx(1.0)

    def test_half_wins(self):
        assert win_rate([0.01, -0.02]) == pytest.approx(0.5)

    def test_empty(self):
        assert win_rate([]) == 0.0


class TestNumTrades:
    def test_basic(self):
        # Two round trips: 1→0, 1→0
        pos = pd.Series([0, 1, 1, 0, 1, 1, 0])
        assert num_trades(pos) == 2

    def test_no_trades(self):
        pos = pd.Series([0, 0, 0])
        assert num_trades(pos) == 0

    def test_open_position(self):
        # Position never closes
        pos = pd.Series([0, 1, 1, 1])
        assert num_trades(pos) == 0


class TestComputeAllMetrics:
    def test_returns_dict(self):
        equity = pd.Series([100, 105, 110, 108, 112])
        returns = equity.pct_change().fillna(0)
        position = pd.Series([0, 1, 1, 1, 0])
        result = compute_all_metrics(equity, returns, position, [0.05, -0.02])
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
        assert "num_trades" in result


# ---------------------------------------------------------------------------
# Backtester integration tests
# ---------------------------------------------------------------------------


def _make_signals(
    prices: list[float],
    positions: list[int],
) -> pd.DataFrame:
    """Helper: create a minimal signals DataFrame."""
    dates = pd.date_range("2020-01-01", periods=len(prices), freq="D")
    return pd.DataFrame({
        "date": dates,
        "close": prices,
        "position": positions,
    })


class TestRunBacktest:
    def test_simple_long(self):
        # Buy day 2, sell day 4
        signals = _make_signals(
            prices=[100, 101, 103, 102, 105, 100],
            positions=[0, 0, 1, 1, 0, 0],
        )
        result = run_backtest(signals, {"position_size": 1.0})
        assert result.success
        assert result.metrics["total_return"] > 0
        assert result.metrics["num_trades"] == 1

    def test_position_signal_does_not_capture_same_day_return(self):
        signals = _make_signals(
            prices=[100, 110],
            positions=[0, 1],
        )
        result = run_backtest(signals, {"position_size": 1.0})
        assert result.success
        assert result.metrics["total_return"] == pytest.approx(0.0)

    def test_missing_columns(self):
        df = pd.DataFrame({"close": [100, 101]})
        result = run_backtest(df)
        assert not result.success

    def test_with_stop_loss(self):
        # Price drops 10% after entry
        signals = _make_signals(
            prices=[100, 100, 90, 85],
            positions=[0, 1, 1, 0],
        )
        result = run_backtest(signals, {"position_size": 1.0, "stop_loss": 0.08})
        assert result.success
        # Stop loss should trigger
        assert any(t.exit_reason == "stop_loss" for t in result.trades)

    def test_stop_loss_changes_equity_curve(self):
        signals = _make_signals(
            prices=[100, 100, 90, 80],
            positions=[0, 1, 1, 1],
        )
        result = run_backtest(signals, {"position_size": 1.0, "stop_loss": 0.08})
        assert result.success
        assert result.metrics["total_return"] == pytest.approx(-0.1)

    def test_with_take_profit(self):
        # Price rises 15% after entry
        signals = _make_signals(
            prices=[100, 100, 115, 120],
            positions=[0, 1, 1, 0],
        )
        result = run_backtest(signals, {"position_size": 1.0, "take_profit": 0.10})
        assert result.success
        assert any(t.exit_reason == "take_profit" for t in result.trades)

    def test_equity_curve_monotonic_flat(self):
        # No trades, equity should stay at initial
        signals = _make_signals(
            prices=[100, 101, 102, 103],
            positions=[0, 0, 0, 0],
        )
        result = run_backtest(signals, {"position_size": 1.0})
        assert result.success
        assert result.equity_curve.iloc[-1] == 100_000.0


class TestFormatSummary:
    def test_success(self):
        signals = _make_signals(
            prices=[100, 101, 103, 102, 105],
            positions=[0, 1, 1, 0, 0],
        )
        result = run_backtest(signals, {"position_size": 1.0})
        summary = format_backtest_summary(result)
        assert "Backtest completed" in summary

    def test_failure(self):
        result = BacktestResult()
        result.add_error("Missing column: date")
        summary = format_backtest_summary(result)
        assert "Backtest failed" in summary


class TestPipeline:
    """Integration test: QYIR JSON → compile → backtest."""

    def test_ma_cross_pipeline(self, tmp_path):
        """Test full pipeline with ma_cross QYIR against sample data."""
        import json

        # Use existing sample data
        data_path = "data/raw/spy_sample.csv"
        qyir_path = "qyir/examples/ma_cross.json"

        result = run_backtest_pipeline(qyir_path, data_path)
        assert result.success, result.errors
        for key in ["total_return", "sharpe_ratio", "max_drawdown", "num_trades"]:
            assert key in result.metrics
