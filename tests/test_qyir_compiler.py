"""Tests for compiler/qyir_compiler.py — end-to-end QYIR compilation."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from compiler.generate_sample_data import generate_spy_sample
from compiler.qyir_compiler import compile_qyir, compile_qyir_file

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "qyir" / "examples"


@pytest.fixture
def price_data() -> pd.DataFrame:
    """Synthetic price data covering 2020-01-01 to 2024-12-31."""
    return generate_spy_sample(start="2019-06-01", end="2024-12-31", seed=42)


@pytest.fixture
def ma_cross_qyir() -> dict:
    return json.loads((EXAMPLES_DIR / "ma_cross.json").read_text(encoding="utf-8"))


@pytest.fixture
def rsi_reversal_qyir() -> dict:
    return json.loads((EXAMPLES_DIR / "rsi_reversal.json").read_text(encoding="utf-8"))


@pytest.fixture
def bollinger_macd_qyir() -> dict:
    return json.loads((EXAMPLES_DIR / "bollinger_macd.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# MA Cross strategy
# ---------------------------------------------------------------------------


class TestMaCross:
    def test_compile_success(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        assert result.success, f"Errors: {result.errors}"

    def test_signals_dataframe(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        df = result.signals
        assert df is not None
        assert "entry_signal" in df.columns
        assert "exit_signal" in df.columns
        assert "position" in df.columns
        assert "sma_short" in df.columns
        assert "sma_long" in df.columns

    def test_has_trades(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        df = result.signals
        assert df["entry_signal"].any(), "Expected at least one entry signal"
        assert df["exit_signal"].any(), "Expected at least one exit signal"

    def test_position_changes(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        df = result.signals
        # Position should change at least once (0→1 or 1→0)
        pos_changes = df["position"].diff().abs()
        assert pos_changes.gt(0).any(), "Expected position to change"

    def test_position_values(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        df = result.signals
        # Long-only, so position should be 0 or 1
        assert df["position"].isin([0, 1]).all()

    def test_date_range_filtered(self, ma_cross_qyir, price_data):
        result = compile_qyir(ma_cross_qyir, price_data)
        df = result.signals
        start = pd.Timestamp(ma_cross_qyir["market"]["start_date"])
        end = pd.Timestamp(ma_cross_qyir["market"]["end_date"])
        assert df["date"].min() >= start
        assert df["date"].max() <= end


# ---------------------------------------------------------------------------
# RSI Reversal strategy
# ---------------------------------------------------------------------------


class TestRsiReversal:
    def test_compile_success(self, rsi_reversal_qyir, price_data):
        result = compile_qyir(rsi_reversal_qyir, price_data)
        assert result.success, f"Errors: {result.errors}"

    def test_indicators_computed(self, rsi_reversal_qyir, price_data):
        result = compile_qyir(rsi_reversal_qyir, price_data)
        df = result.signals
        assert "rsi_14" in df.columns
        # RSI should be in [0, 100]
        valid_rsi = df["rsi_14"].dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()

    def test_numeric_threshold_rules(self, rsi_reversal_qyir, price_data):
        result = compile_qyir(rsi_reversal_qyir, price_data)
        assert result.success
        df = result.signals
        # Entry when RSI < 30 (numeric threshold)
        assert df["entry_signal"].dtype == bool


# ---------------------------------------------------------------------------
# Bollinger + MACD strategy
# ---------------------------------------------------------------------------


class TestBollingerMacd:
    def test_compile_success(self, bollinger_macd_qyir, price_data):
        result = compile_qyir(bollinger_macd_qyir, price_data)
        assert result.success, f"Errors: {result.errors}"

    def test_all_indicators_present(self, bollinger_macd_qyir, price_data):
        result = compile_qyir(bollinger_macd_qyir, price_data)
        df = result.signals
        for alias in ["boll_lower", "boll_middle", "macd_line", "signal_line"]:
            assert alias in df.columns, f"Missing indicator: {alias}"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestCompilationErrors:
    def test_missing_price_columns(self, ma_cross_qyir):
        bad_data = pd.DataFrame({"x": [1, 2, 3]})
        result = compile_qyir(ma_cross_qyir, bad_data)
        assert not result.success
        assert any("missing columns" in e.lower() for e in result.errors)

    def test_no_data_in_range(self, ma_cross_qyir, price_data):
        # Modify dates to be outside data range
        qyir = json.loads(json.dumps(ma_cross_qyir))
        qyir["market"]["start_date"] = "2099-01-01"
        qyir["market"]["end_date"] = "2099-12-31"
        result = compile_qyir(qyir, price_data)
        assert not result.success

    def test_unsupported_indicator(self, price_data):
        qyir = {
            "strategy_name": "bad",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [{"name": "STOCHASTIC", "params": {}, "alias": "stoch"}],
            "entry_rules": [{"type": "greater_than", "left": "stoch", "right": 80}],
            "exit_rules": [{"type": "less_than", "left": "stoch", "right": 20}],
            "risk_control": {"position_size": 0.5, "leverage": 1.0},
        }
        result = compile_qyir(qyir, price_data)
        assert not result.success
        assert any("Unsupported" in e for e in result.errors)


# ---------------------------------------------------------------------------
# File-based compilation
# ---------------------------------------------------------------------------


class TestCompileQyirFile:
    def test_file_compilation(self, price_data, tmp_path):
        # Write QYIR
        qyir_path = tmp_path / "test.json"
        qyir_path.write_text(json.dumps({
            "strategy_name": "test",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [
                {"name": "SMA", "params": {"window": 20}, "alias": "sma20"},
                {"name": "SMA", "params": {"window": 60}, "alias": "sma60"},
            ],
            "entry_rules": [{"type": "cross_over", "left": "sma20", "right": "sma60"}],
            "exit_rules": [{"type": "cross_under", "left": "sma20", "right": "sma60"}],
            "risk_control": {"position_size": 0.5, "leverage": 1.0},
        }))

        # Write CSV
        csv_path = tmp_path / "data.csv"
        price_data.to_csv(csv_path, index=False)

        result = compile_qyir_file(qyir_path, csv_path)
        assert result.success
        assert result.signals is not None
