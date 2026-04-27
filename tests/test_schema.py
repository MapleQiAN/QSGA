"""Tests for QYIR v1 Pydantic schema — field-level and model-level constraints."""

import copy

import pytest
from pydantic import ValidationError

from qyir.schema import (
    IndicatorConfig,
    MarketConfig,
    QYIR,
    RiskControlConfig,
    RuleConfig,
)

# ---------------------------------------------------------------------------
# MarketConfig
# ---------------------------------------------------------------------------


class TestMarketConfig:
    def test_valid(self):
        m = MarketConfig(symbol="SPY", start_date="2020-01-01", end_date="2024-12-31")
        assert m.symbol == "SPY"
        assert m.timeframe == "1d"

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError, match="YYYY-MM-DD"):
            MarketConfig(symbol="SPY", start_date="2020/01/01", end_date="2024-12-31")

    def test_date_order(self):
        with pytest.raises(ValidationError, match="must be before"):
            MarketConfig(symbol="SPY", start_date="2025-01-01", end_date="2024-01-01")

    def test_empty_symbol(self):
        with pytest.raises(ValidationError):
            MarketConfig(symbol="", start_date="2020-01-01", end_date="2024-12-31")


# ---------------------------------------------------------------------------
# IndicatorConfig
# ---------------------------------------------------------------------------


class TestIndicatorConfig:
    def test_sma_valid(self):
        ind = IndicatorConfig(name="SMA", params={"window": 20}, alias="sma_20")
        assert ind.name == "SMA"

    def test_sma_missing_window(self):
        with pytest.raises(ValidationError, match="requires 'window'"):
            IndicatorConfig(name="SMA", params={}, alias="sma_20")

    def test_sma_window_too_small(self):
        with pytest.raises(ValidationError, match="must be int in"):
            IndicatorConfig(name="SMA", params={"window": 0}, alias="bad")

    def test_ema_valid(self):
        ind = IndicatorConfig(name="EMA", params={"window": 12}, alias="ema_12")
        assert ind.alias == "ema_12"

    def test_rsi_valid(self):
        ind = IndicatorConfig(name="RSI", params={"window": 14}, alias="rsi_14")
        assert ind.name == "RSI"

    def test_rsi_default_window(self):
        # RSI allows default window=14, so empty params should work
        ind = IndicatorConfig(name="RSI", params={}, alias="rsi")
        assert ind.params == {}

    def test_rsi_window_too_large(self):
        with pytest.raises(ValidationError, match="RSI.window"):
            IndicatorConfig(name="RSI", params={"window": 200}, alias="rsi")

    def test_macd_valid(self):
        ind = IndicatorConfig(
            name="MACD",
            params={"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
            alias="macd_line",
        )
        assert ind.name == "MACD"

    def test_macd_fast_ge_slow(self):
        with pytest.raises(ValidationError, match="fast.*must be < .*slow"):
            IndicatorConfig(
                name="MACD",
                params={"fast": 30, "slow": 26, "signal": 9, "output": "macd_line"},
                alias="macd",
            )

    def test_macd_missing_output(self):
        with pytest.raises(ValidationError, match="MACD.output must be"):
            IndicatorConfig(
                name="MACD",
                params={"fast": 12, "slow": 26, "signal": 9},
                alias="macd",
            )

    def test_bollinger_valid(self):
        ind = IndicatorConfig(
            name="BOLLINGER",
            params={"window": 20, "num_std": 2.0, "output": "upper"},
            alias="boll_upper",
        )
        assert ind.name == "BOLLINGER"

    def test_bollinger_missing_output(self):
        with pytest.raises(ValidationError, match="BOLLINGER.output must be"):
            IndicatorConfig(
                name="BOLLINGER",
                params={"window": 20, "num_std": 2.0},
                alias="boll",
            )

    def test_unsupported_indicator(self):
        with pytest.raises(ValidationError, match="STOCHASTIC"):
            IndicatorConfig(name="STOCHASTIC", params={}, alias="stoch")

    def test_bad_alias_chars(self):
        with pytest.raises(ValidationError, match="alias must match"):
            IndicatorConfig(name="SMA", params={"window": 20}, alias="SMA-20")


# ---------------------------------------------------------------------------
# RuleConfig
# ---------------------------------------------------------------------------


class TestRuleConfig:
    def test_cross_over_valid(self):
        r = RuleConfig(type="cross_over", left="a", right="b")
        assert r.type == "cross_over"

    def test_between_valid(self):
        r = RuleConfig(type="between", left="rsi", lower=30, upper=70)
        assert r.lower == 30

    def test_between_lower_ge_upper(self):
        with pytest.raises(ValidationError, match="lower.*must be < .*upper"):
            RuleConfig(type="between", left="rsi", lower=70, upper=30)

    def test_cross_over_missing_right(self):
        with pytest.raises(ValidationError, match="requires 'right'"):
            RuleConfig(type="cross_over", left="a")

    def test_between_missing_bounds(self):
        with pytest.raises(ValidationError, match="requires both"):
            RuleConfig(type="between", left="a")

    def test_unsupported_rule_type(self):
        with pytest.raises(ValidationError, match="rank_top_k"):
            RuleConfig(type="rank_top_k", left="a", right=3)


# ---------------------------------------------------------------------------
# RiskControlConfig
# ---------------------------------------------------------------------------


class TestRiskControlConfig:
    def test_valid(self):
        rc = RiskControlConfig(
            position_size=0.5,
            stop_loss=0.1,
            take_profit=None,
            max_drawdown_limit=0.2,
            allow_short=False,
            leverage=1.0,
        )
        assert rc.leverage == 1.0

    def test_leverage_rejected(self):
        with pytest.raises(ValidationError, match="leverage must be 1.0"):
            RiskControlConfig(
                position_size=0.5,
                leverage=3.0,
            )

    def test_position_size_out_of_range(self):
        with pytest.raises(ValidationError):
            RiskControlConfig(position_size=2.0, leverage=1.0)

    def test_position_size_zero(self):
        with pytest.raises(ValidationError):
            RiskControlConfig(position_size=0.0, leverage=1.0)

    def test_stop_loss_out_of_range(self):
        with pytest.raises(ValidationError):
            RiskControlConfig(position_size=0.5, stop_loss=0.8, leverage=1.0)

    def test_all_optional_null(self):
        rc = RiskControlConfig(position_size=0.5, leverage=1.0)
        assert rc.stop_loss is None
        assert rc.take_profit is None
        assert rc.max_drawdown_limit is None


# ---------------------------------------------------------------------------
# QYIR full model
# ---------------------------------------------------------------------------


VALID_QYIR = {
    "strategy_name": "test_strategy",
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
    "entry_rules": [{"type": "cross_over", "left": "sma_short", "right": "sma_long"}],
    "exit_rules": [{"type": "cross_under", "left": "sma_short", "right": "sma_long"}],
    "risk_control": {
        "position_size": 0.5,
        "stop_loss": 0.1,
        "take_profit": None,
        "max_drawdown_limit": 0.2,
        "allow_short": False,
        "leverage": 1.0,
    },
}


class TestQYIR:
    def test_valid_full(self):
        q = QYIR.model_validate(VALID_QYIR)
        assert q.strategy_name == "test_strategy"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            QYIR.model_validate({"strategy_name": "x"})

    def test_duplicate_alias(self):
        data = copy.deepcopy(VALID_QYIR)
        data["indicators"][1]["alias"] = "sma_short"  # duplicate
        with pytest.raises(ValidationError, match="Duplicate alias"):
            QYIR.model_validate(data)

    def test_unknown_alias_reference(self):
        data = copy.deepcopy(VALID_QYIR)
        data["entry_rules"][0]["right"] = "ema_50"  # not defined
        with pytest.raises(ValidationError, match="unknown alias"):
            QYIR.model_validate(data)

    def test_empty_indicators(self):
        data = copy.deepcopy(VALID_QYIR)
        data["indicators"] = []
        with pytest.raises(ValidationError, match="at least 1"):
            QYIR.model_validate(data)

    def test_strategy_name_bad_chars(self):
        data = copy.deepcopy(VALID_QYIR)
        data["strategy_name"] = "My Strategy!"
        with pytest.raises(ValidationError, match="strategy_name must match"):
            QYIR.model_validate(data)

    def test_description_too_long(self):
        data = copy.deepcopy(VALID_QYIR)
        data["description"] = "x" * 600
        with pytest.raises(ValidationError, match="description must be <= 512"):
            QYIR.model_validate(data)
