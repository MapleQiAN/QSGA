"""Tests for compiler/indicator_engine.py"""

import numpy as np
import pandas as pd
import pytest

from compiler.indicator_engine import (
    compute_bollinger,
    compute_ema,
    compute_indicator,
    compute_macd,
    compute_rsi,
    compute_sma,
)


@pytest.fixture
def prices() -> pd.Series:
    """100 periods of synthetic prices starting at 100."""
    rng = np.random.default_rng(123)
    returns = rng.normal(0.001, 0.02, 100)
    return pd.Series(100 * np.cumprod(1 + returns))


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------


class TestSMA:
    def test_output_length(self, prices):
        result = compute_sma(prices, 20)
        assert len(result) == len(prices)

    def test_first_n_nan(self, prices):
        result = compute_sma(prices, 20)
        assert result.iloc[:19].isna().all()
        assert not pd.isna(result.iloc[19])

    def test_manual_calculation(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = compute_sma(s, 3)
        assert np.isclose(result.iloc[2], 2.0)
        assert np.isclose(result.iloc[4], 4.0)


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------


class TestEMA:
    def test_output_length(self, prices):
        result = compute_ema(prices, 12)
        assert len(result) == len(prices)

    def test_not_all_nan(self, prices):
        result = compute_ema(prices, 12)
        assert result.iloc[11:].notna().any()


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------


class TestRSI:
    def test_range(self, prices):
        result = compute_rsi(prices, 14)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_default_window(self, prices):
        result = compute_rsi(prices)
        assert len(result) == len(prices)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


class TestMACD:
    def test_three_outputs(self, prices):
        macd_line, signal_line, histogram = compute_macd(prices)
        assert len(macd_line) == len(prices)
        assert len(signal_line) == len(prices)
        assert len(histogram) == len(prices)

    def test_histogram_equals_diff(self, prices):
        macd_line, signal_line, histogram = compute_macd(prices)
        np.testing.assert_allclose(
            histogram.dropna().values,
            (macd_line - signal_line).dropna().values,
            atol=1e-10,
        )


# ---------------------------------------------------------------------------
# BOLLINGER
# ---------------------------------------------------------------------------


class TestBollinger:
    def test_three_outputs(self, prices):
        upper, middle, lower = compute_bollinger(prices)
        assert len(upper) == len(prices)

    def test_upper_ge_lower(self, prices):
        upper, middle, lower = compute_bollinger(prices)
        valid = upper.dropna().index
        assert (upper[valid] >= lower[valid]).all()


# ---------------------------------------------------------------------------
# compute_indicator dispatch
# ---------------------------------------------------------------------------


class TestComputeIndicator:
    def test_sma_dispatch(self, prices):
        result = compute_indicator("SMA", prices, {"window": 20})
        expected = compute_sma(prices, 20)
        pd.testing.assert_series_equal(result, expected)

    def test_macd_dispatch(self, prices):
        result = compute_indicator(
            "MACD", prices, {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"}
        )
        expected, _, _ = compute_macd(prices, 12, 26, 9)
        pd.testing.assert_series_equal(result, expected)

    def test_bollinger_dispatch(self, prices):
        result = compute_indicator(
            "BOLLINGER", prices, {"window": 20, "num_std": 2.0, "output": "upper"}
        )
        expected, _, _ = compute_bollinger(prices, 20, 2.0)
        pd.testing.assert_series_equal(result, expected)

    def test_unsupported_indicator(self, prices):
        with pytest.raises(ValueError, match="Unsupported"):
            compute_indicator("STOCHASTIC", prices, {})
