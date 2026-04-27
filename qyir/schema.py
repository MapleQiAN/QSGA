"""QYIR v1 Pydantic schema definitions."""

from __future__ import annotations

import re
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from qyir.constants import (
    BOLLINGER_NUM_STD_MAX,
    BOLLINGER_NUM_STD_MIN,
    BollingerOutput,
    INDICATOR_WINDOW_MAX,
    INDICATOR_WINDOW_MIN,
    IndicatorType,
    LEVERAGE_LOCKED,
    MACDOutput,
    MAX_DRAWDOWN_LIMIT_MAX,
    POSITION_SIZE_MAX,
    POSITION_SIZE_MIN,
    QYIRVersion,
    RuleType,
    RSI_WINDOW_MAX,
    STOP_LOSS_MAX,
    STRATEGY_NAME_MAX_LEN,
    TAKE_PROFIT_MAX,
    Timeframe,
)

# ---------------------------------------------------------------------------
# Reusable validators
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-z0-9_]+$")


def _validate_alias(v: str) -> str:
    if not _NAME_RE.match(v):
        raise ValueError(
            f"alias must match [a-z0-9_], got '{v}'"
        )
    return v


def _validate_strategy_name(v: str) -> str:
    if not _NAME_RE.match(v):
        raise ValueError(
            f"strategy_name must match [a-z0-9_], got '{v}'"
        )
    if len(v) > STRATEGY_NAME_MAX_LEN:
        raise ValueError(
            f"strategy_name must be <= {STRATEGY_NAME_MAX_LEN} chars"
        )
    return v


def _validate_date(v: str) -> str:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        raise ValueError(f"date must be YYYY-MM-DD, got '{v}'")
    return v


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class MarketConfig(BaseModel):
    symbol: str = Field(..., min_length=1)
    timeframe: Timeframe = Timeframe.DAILY
    start_date: str
    end_date: str

    @field_validator("start_date", "end_date")
    @classmethod
    def _check_date_format(cls, v: str) -> str:
        return _validate_date(v)

    @model_validator(mode="after")
    def _check_date_order(self) -> "MarketConfig":
        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
            )
        return self


class IndicatorConfig(BaseModel):
    name: IndicatorType
    params: Dict[str, Any]
    alias: str

    @field_validator("alias")
    @classmethod
    def _check_alias(cls, v: str) -> str:
        return _validate_alias(v)

    @model_validator(mode="after")
    def _check_params(self) -> "IndicatorConfig":
        name = self.name
        params = self.params

        if name == IndicatorType.SMA or name == IndicatorType.EMA:
            if "window" not in params:
                raise ValueError(f"{name.value} requires 'window' param")
            w = params["window"]
            if not isinstance(w, int) or w < INDICATOR_WINDOW_MIN or w > INDICATOR_WINDOW_MAX:
                raise ValueError(
                    f"{name.value}.window must be int in [{INDICATOR_WINDOW_MIN}, {INDICATOR_WINDOW_MAX}]"
                )

        elif name == IndicatorType.RSI:
            w = params.get("window", 14)
            if not isinstance(w, int) or w < INDICATOR_WINDOW_MIN or w > RSI_WINDOW_MAX:
                raise ValueError(
                    f"RSI.window must be int in [{INDICATOR_WINDOW_MIN}, {RSI_WINDOW_MAX}]"
                )

        elif name == IndicatorType.MACD:
            fast = params.get("fast", 12)
            slow = params.get("slow", 26)
            signal = params.get("signal", 9)
            if not isinstance(fast, int) or not isinstance(slow, int):
                raise ValueError("MACD.fast and MACD.slow must be int")
            if fast >= slow:
                raise ValueError(f"MACD.fast ({fast}) must be < MACD.slow ({slow})")
            if not isinstance(signal, int) or signal < 2 or signal > 100:
                raise ValueError("MACD.signal must be int in [2, 100]")
            output = params.get("output")
            if output not in [e.value for e in MACDOutput]:
                raise ValueError(
                    f"MACD.output must be one of {[e.value for e in MACDOutput]}"
                )

        elif name == IndicatorType.BOLLINGER:
            window = params.get("window", 20)
            if not isinstance(window, int) or window < INDICATOR_WINDOW_MIN or window > INDICATOR_WINDOW_MAX:
                raise ValueError(
                    f"BOLLINGER.window must be int in [{INDICATOR_WINDOW_MIN}, {INDICATOR_WINDOW_MAX}]"
                )
            num_std = params.get("num_std", 2.0)
            if not isinstance(num_std, (int, float)) or num_std < BOLLINGER_NUM_STD_MIN or num_std > BOLLINGER_NUM_STD_MAX:
                raise ValueError(
                    f"BOLLINGER.num_std must be float in [{BOLLINGER_NUM_STD_MIN}, {BOLLINGER_NUM_STD_MAX}]"
                )
            output = params.get("output")
            if output not in [e.value for e in BollingerOutput]:
                raise ValueError(
                    f"BOLLINGER.output must be one of {[e.value for e in BollingerOutput]}"
                )

        return self


class RuleConfig(BaseModel):
    type: RuleType
    left: str
    right: Optional[Union[str, float]] = None
    lower: Optional[Union[str, float]] = None
    upper: Optional[Union[str, float]] = None

    @model_validator(mode="after")
    def _check_rule_fields(self) -> "RuleConfig":
        t = self.type
        if t in (RuleType.CROSS_OVER, RuleType.CROSS_UNDER, RuleType.GREATER_THAN, RuleType.LESS_THAN):
            if self.right is None:
                raise ValueError(f"Rule type '{t.value}' requires 'right' field")
            if self.lower is not None or self.upper is not None:
                raise ValueError(f"Rule type '{t.value}' does not use 'lower'/'upper' fields")
        elif t == RuleType.BETWEEN:
            if self.lower is None or self.upper is None:
                raise ValueError("Rule type 'between' requires both 'lower' and 'upper' fields")
            if self.right is not None:
                raise ValueError("Rule type 'between' does not use 'right' field")
            # Numeric bounds check
            if isinstance(self.lower, (int, float)) and isinstance(self.upper, (int, float)):
                if self.lower >= self.upper:
                    raise ValueError(
                        f"between.lower ({self.lower}) must be < between.upper ({self.upper})"
                    )
        return self


class RiskControlConfig(BaseModel):
    position_size: Annotated[float, Field(ge=POSITION_SIZE_MIN, le=POSITION_SIZE_MAX)]
    stop_loss: Optional[Annotated[float, Field(ge=0.01, le=STOP_LOSS_MAX)]] = None
    take_profit: Optional[Annotated[float, Field(ge=0.01, le=TAKE_PROFIT_MAX)]] = None
    max_drawdown_limit: Optional[Annotated[float, Field(ge=0.01, le=MAX_DRAWDOWN_LIMIT_MAX)]] = None
    allow_short: bool = False
    leverage: float = LEVERAGE_LOCKED

    @field_validator("leverage")
    @classmethod
    def _check_leverage(cls, v: float) -> float:
        if v != LEVERAGE_LOCKED:
            raise ValueError(f"leverage must be {LEVERAGE_LOCKED} in QYIR v1")
        return v


# ---------------------------------------------------------------------------
# Top-level QYIR model
# ---------------------------------------------------------------------------


class QYIR(BaseModel):
    strategy_name: str
    description: Optional[str] = None
    version: QYIRVersion = QYIRVersion.V1
    market: MarketConfig
    indicators: List[IndicatorConfig] = Field(..., min_length=1, max_length=10)
    entry_rules: List[RuleConfig] = Field(..., min_length=1, max_length=10)
    exit_rules: List[RuleConfig] = Field(..., min_length=1, max_length=10)
    risk_control: RiskControlConfig

    @field_validator("strategy_name")
    @classmethod
    def _check_strategy_name(cls, v: str) -> str:
        return _validate_strategy_name(v)

    @field_validator("description")
    @classmethod
    def _check_description_len(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 512:
            raise ValueError("description must be <= 512 chars")
        return v

    @model_validator(mode="after")
    def _check_alias_uniqueness(self) -> "QYIR":
        seen: Dict[str, int] = {}
        for i, ind in enumerate(self.indicators):
            if ind.alias in seen:
                raise ValueError(
                    f"Duplicate alias '{ind.alias}' at indicators[{seen[ind.alias]}] and indicators[{i}]"
                )
            seen[ind.alias] = i
        return self

    @model_validator(mode="after")
    def _check_rule_references(self) -> "QYIR":
        aliases = {ind.alias for ind in self.indicators}
        all_rules = list(self.entry_rules) + list(self.exit_rules)
        for i, rule in enumerate(all_rules):
            prefix = "entry_rules" if i < len(self.entry_rules) else "exit_rules"
            idx = i if i < len(self.entry_rules) else i - len(self.entry_rules)
            for field_name in ("left", "right", "lower", "upper"):
                val = getattr(rule, field_name, None)
                if isinstance(val, str) and val not in aliases:
                    raise ValueError(
                        f"{prefix}[{idx}].{field_name} references unknown alias '{val}'"
                    )
        return self
