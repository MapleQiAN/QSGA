"""QYIR v1 constants: supported enums and constraint bounds."""

from enum import Enum


class IndicatorType(str, Enum):
    SMA = "SMA"
    EMA = "EMA"
    RSI = "RSI"
    MACD = "MACD"
    BOLLINGER = "BOLLINGER"


class RuleType(str, Enum):
    CROSS_OVER = "cross_over"
    CROSS_UNDER = "cross_under"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"


class Timeframe(str, Enum):
    DAILY = "1d"


class QYIRVersion(str, Enum):
    V1 = "1.0"


class MACDOutput(str, Enum):
    MACD_LINE = "macd_line"
    SIGNAL_LINE = "signal_line"
    HISTOGRAM = "histogram"


class BollingerOutput(str, Enum):
    UPPER = "upper"
    MIDDLE = "middle"
    LOWER = "lower"


# Constraint bounds
INDICATOR_WINDOW_MIN = 2
INDICATOR_WINDOW_MAX = 500
RSI_WINDOW_MAX = 100
BOLLINGER_NUM_STD_MIN = 0.1
BOLLINGER_NUM_STD_MAX = 5.0
POSITION_SIZE_MIN = 0.01
POSITION_SIZE_MAX = 1.0
STOP_LOSS_MAX = 0.50
TAKE_PROFIT_MAX = 1.0
MAX_DRAWDOWN_LIMIT_MAX = 0.50
LEVERAGE_LOCKED = 1.0
STRATEGY_NAME_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 512
INDICATORS_MIN = 1
INDICATORS_MAX = 10
RULES_MIN = 1
RULES_MAX = 10

# Multi-output indicators (require `output` field in params)
MULTI_OUTPUT_INDICATORS = {IndicatorType.MACD, IndicatorType.BOLLINGER}

# Rule types that require `right` field (all except BETWEEN)
RULES_REQUIRING_RIGHT = {
    RuleType.CROSS_OVER,
    RuleType.CROSS_UNDER,
    RuleType.GREATER_THAN,
    RuleType.LESS_THAN,
}
