"""Pydantic slot schema for Route B natural-language-to-QYIR construction."""

from __future__ import annotations

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


StrategyFamily = Literal[
    "trend_following",
    "mean_reversion",
    "momentum",
    "breakout",
    "risk_controlled",
    "unknown",
]
AssetType = Literal["stock", "etf", "index", "unknown"]
SlotTimeframe = Literal["daily", "weekly", "unknown"]
IndicatorName = Literal["SMA", "EMA", "RSI", "MACD", "BOLLINGER", "UNKNOWN"]
IndicatorRole = Literal["fast", "slow", "signal", "threshold", "unknown"]
RuleOperator = Literal[
    "cross_over",
    "cross_under",
    "greater_than",
    "less_than",
    "between",
    "stop_loss",
    "take_profit",
    "unknown",
]
SafeAction = Literal["construct", "clarify", "reject"]


class MarketScope(BaseModel):
    """Simplified market scope extracted from user intent."""

    symbol: Optional[str] = None
    asset_type: AssetType = "unknown"
    timeframe: SlotTimeframe = "daily"

    @field_validator("symbol", mode="before")
    @classmethod
    def _normalize_symbol(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if normalized.lower() in {"", "unknown", "none", "null"}:
                return None
            return normalized.upper()
        return value

    @field_validator("asset_type", "timeframe", mode="before")
    @classmethod
    def _normalize_market_enum(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class IndicatorSlot(BaseModel):
    """One extracted indicator mention."""

    name: IndicatorName
    window: Optional[int] = Field(default=None, ge=1)
    role: IndicatorRole = "unknown"

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_name(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("role", mode="before")
    @classmethod
    def _normalize_role(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {
                "entry",
                "exit",
                "entry_signal",
                "exit_signal",
                "trend",
                "trend_signal",
                "filter",
                "risk_filter",
                "condition",
                "trigger",
            }:
                return "unknown"
            return normalized
        return value


class LogicSlot(BaseModel):
    """Simplified trading rule slot."""

    operator: Optional[RuleOperator] = None
    left: Optional[str] = None
    right: Optional[Union[str, float]] = None
    natural_language: str = ""


class RiskConstraints(BaseModel):
    """Explicit risk constraints extracted from user intent."""

    position_size: Optional[float] = Field(default=None, gt=0, le=1)
    max_drawdown_limit: Optional[float] = Field(default=None, gt=0, le=1)
    stop_loss: Optional[float] = Field(default=None, gt=0, le=1)
    take_profit: Optional[float] = Field(default=None, gt=0, le=1)
    allow_short: Optional[bool] = None
    leverage: Optional[float] = Field(default=None, gt=0)


class Ambiguity(BaseModel):
    """Ambiguity markers for safe clarification instead of construction."""

    requires_clarification: bool = False
    missing_slots: List[str] = Field(default_factory=list)
    ambiguous_phrases: List[str] = Field(default_factory=list)


class StrategySlotSpec(BaseModel):
    """Route B slot schema consumed by the deterministic QYIR builder."""

    strategy_family: StrategyFamily = "unknown"
    market_scope: MarketScope = Field(default_factory=MarketScope)
    indicators: List[IndicatorSlot] = Field(default_factory=list)
    entry_logic: LogicSlot = Field(default_factory=LogicSlot)
    exit_logic: LogicSlot = Field(default_factory=LogicSlot)
    risk_constraints: RiskConstraints = Field(default_factory=RiskConstraints)
    ambiguity: Ambiguity = Field(default_factory=Ambiguity)
    safe_action: SafeAction = "construct"

    @field_validator("safe_action", mode="before")
    @classmethod
    def _normalize_safe_action(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "generate":
                return "construct"
            return normalized
        return value

    @field_validator("entry_logic", "exit_logic", mode="before")
    @classmethod
    def _default_logic_slot(cls, value: object) -> object:
        if value is None:
            return {}
        return value

    @field_validator("risk_constraints", "ambiguity", mode="before")
    @classmethod
    def _default_nested_slot(cls, value: object) -> object:
        if value is None:
            return {}
        return value
