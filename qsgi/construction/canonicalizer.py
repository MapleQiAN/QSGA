"""QYIR canonicalization utilities for Route B construction."""

from __future__ import annotations

import copy
import re
from typing import Any

from pydantic import BaseModel, Field


class CanonicalizationEvent(BaseModel):
    """Auditable record of one canonicalization step."""

    field: str
    original: Any
    canonical: Any
    rule_id: str


class CanonicalizationResult(BaseModel):
    """Canonicalized QYIR plus an auditable transformation log."""

    canonical_qyir: dict[str, Any]
    canonicalization_log: list[CanonicalizationEvent] = Field(default_factory=list)


_MARKET_FIELD_ALIASES = {
    "close": "market.close",
    "price": "market.close",
    "closing_price": "market.close",
    "收盘价": "market.close",
    "open": "market.open",
    "开盘价": "market.open",
    "volume": "market.volume",
    "成交量": "market.volume",
}

_CHINESE_PERCENT_NUMBERS = {
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


def canonicalize_qyir(qyir: dict[str, Any]) -> CanonicalizationResult:
    """Canonicalize a QYIR-shaped dictionary without changing its intent."""
    canonical = copy.deepcopy(qyir)
    log: list[CanonicalizationEvent] = []
    alias_map: dict[str, str] = {}

    for index, indicator in enumerate(canonical.get("indicators", [])):
        if not isinstance(indicator, dict):
            continue
        alias = indicator.get("alias")
        normalized_alias, events = canonicalize_reference(
            alias,
            field=f"indicators[{index}].alias",
            market_fields=False,
        )
        log.extend(events)
        if isinstance(alias, str) and isinstance(normalized_alias, str):
            alias_map[alias] = normalized_alias
            alias_map[alias.lower()] = normalized_alias
            indicator["alias"] = normalized_alias

        params = indicator.get("params", {})
        if isinstance(params, dict):
            for key, value in list(params.items()):
                normalized = normalize_percentage(value)
                if normalized != value:
                    params[key] = normalized
                    log.append(
                        CanonicalizationEvent(
                            field=f"indicators[{index}].params.{key}",
                            original=value,
                            canonical=normalized,
                            rule_id="number.percentage",
                        )
                    )

    for section in ("entry_rules", "exit_rules"):
        for index, rule in enumerate(canonical.get(section, [])):
            if not isinstance(rule, dict):
                continue
            for field_name in ("left", "right", "lower", "upper"):
                if field_name not in rule:
                    continue
                value = rule[field_name]
                mapped = alias_map.get(value) if isinstance(value, str) else None
                if mapped is not None:
                    rule[field_name] = mapped
                    log.append(
                        CanonicalizationEvent(
                            field=f"{section}[{index}].{field_name}",
                            original=value,
                            canonical=mapped,
                            rule_id="alias.reference_map",
                        )
                    )
                    continue
                normalized, events = canonicalize_reference(
                    value,
                    field=f"{section}[{index}].{field_name}",
                    market_fields=True,
                )
                rule[field_name] = normalized
                log.extend(events)

    risk = canonical.get("risk_control", {})
    if isinstance(risk, dict):
        for key in ("position_size", "stop_loss", "take_profit", "max_drawdown_limit"):
            if key not in risk:
                continue
            value = risk[key]
            normalized = normalize_percentage(value)
            if normalized != value:
                risk[key] = normalized
                log.append(
                    CanonicalizationEvent(
                        field=f"risk_control.{key}",
                        original=value,
                        canonical=normalized,
                        rule_id="risk.percentage",
                    )
                )
        leverage = risk.get("leverage")
        if isinstance(leverage, str) and _contains_any(leverage, ("不要杠杆", "不用杠杆", "无杠杆", "no leverage")):
            risk["leverage"] = 1.0
            log.append(
                CanonicalizationEvent(
                    field="risk_control.leverage",
                    original=leverage,
                    canonical=1.0,
                    rule_id="risk.no_leverage",
                )
            )
        allow_short = risk.get("allow_short")
        if isinstance(allow_short, str) and _contains_any(allow_short, ("别做空", "不要做空", "不做空", "no short")):
            risk["allow_short"] = False
            log.append(
                CanonicalizationEvent(
                    field="risk_control.allow_short",
                    original=allow_short,
                    canonical=False,
                    rule_id="risk.no_short",
                )
            )

    return CanonicalizationResult(canonical_qyir=canonical, canonicalization_log=log)


def canonicalize_reference(
    value: Any,
    *,
    field: str = "value",
    market_fields: bool = True,
) -> tuple[Any, list[CanonicalizationEvent]]:
    """Normalize aliases and supported market-field synonyms."""
    if not isinstance(value, str):
        return value, []

    stripped = value.strip()
    normalized = stripped.lower().replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"__+", "_", normalized)

    if market_fields and normalized in _MARKET_FIELD_ALIASES:
        canonical = _MARKET_FIELD_ALIASES[normalized]
        return canonical, [
            CanonicalizationEvent(
                field=field,
                original=value,
                canonical=canonical,
                rule_id="reference.market_field",
            )
        ]

    alias = _normalize_indicator_alias(stripped)
    if alias != stripped:
        return alias, [
            CanonicalizationEvent(
                field=field,
                original=value,
                canonical=alias,
                rule_id="reference.indicator_alias",
            )
        ]

    if normalized != stripped:
        return normalized, [
            CanonicalizationEvent(
                field=field,
                original=value,
                canonical=normalized,
                rule_id="reference.snake_case",
            )
        ]

    return value, []


def normalize_percentage(value: Any) -> Any:
    """Normalize common percentage strings to decimal floats."""
    if isinstance(value, str):
        text = value.strip()
        match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%", text)
        if match:
            return float(match.group(1)) / 100
        match = re.fullmatch(r"百分之([一二两三四五六七八九十]|\d+(?:\.\d+)?)", text)
        if match:
            raw = match.group(1)
            number = _CHINESE_PERCENT_NUMBERS.get(raw)
            if number is None:
                number = float(raw)
            return float(number) / 100
        if re.fullmatch(r"\d+(?:\.\d+)?", text):
            number = float(text)
            if number > 1:
                return number / 100
    return value


def _normalize_indicator_alias(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"__+", "_", normalized)
    match = re.fullmatch(r"(sma|ema|rsi)_?(\d+)", normalized)
    if match:
        return f"{match.group(1)}_{int(match.group(2))}"
    match = re.fullmatch(r"(\d+)[日天]?(均线|平均线|平均价格线)", value.strip())
    if match:
        return f"sma_{int(match.group(1))}"
    if normalized in {"macd", "macd_line"}:
        return "macd_line"
    if normalized in {"signal", "signal_line", "macd_signal"}:
        return "signal_line"
    return normalized


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    normalized = text.strip().lower()
    return any(phrase.lower() in normalized for phrase in phrases)

