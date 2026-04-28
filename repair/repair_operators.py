"""Rule-based local repair operators for QYIR."""

from __future__ import annotations

import copy
from typing import Any


def apply_rule_based_repairs(
    user_query: str,
    qyir: dict[str, Any],
    violations: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    """Apply deterministic local repairs for supported semantic/risk slots."""
    repaired = copy.deepcopy(qyir)
    risk = repaired.setdefault("risk_control", {})
    actions: list[str] = []
    text = _normalize(user_query)
    paths = {str(violation.get("path", "")) for violation in violations}

    if _mentions_no_leverage(text) or "risk_control.leverage" in paths:
        if risk.get("leverage", 1.0) != 1.0:
            risk["leverage"] = 1.0
            actions.append("Set risk_control.leverage to 1.0.")

    if _mentions_no_short(text) or "risk_control.allow_short" in paths:
        if risk.get("allow_short") is not False:
            risk["allow_short"] = False
            actions.append("Set risk_control.allow_short to false.")

    if _mentions_conservative(text) or "risk_control.position_size" in paths:
        if _number(risk.get("position_size"), default=1.0) > 0.5:
            risk["position_size"] = 0.3
            actions.append("Set risk_control.position_size to 0.3.")

    if _mentions_stop_loss(text) and risk.get("stop_loss") is None:
        risk["stop_loss"] = 0.08
        actions.append("Set risk_control.stop_loss to 0.08.")

    if "risk_control.max_drawdown_limit" in paths and risk.get("max_drawdown_limit") is None:
        risk["max_drawdown_limit"] = 0.2
        actions.append("Set risk_control.max_drawdown_limit to 0.2.")

    return repaired, actions


def _normalize(text: str) -> str:
    return "".join(text.split())


def _mentions_no_leverage(text: str) -> bool:
    return any(
        phrase in text
        for phrase in ("不要杠杆", "不用杠杆", "不使用杠杆", "无杠杆", "禁止杠杆", "别加杠杆")
    )


def _mentions_no_short(text: str) -> bool:
    return any(phrase in text for phrase in ("不要做空", "不做空", "禁止做空", "不能做空", "别做空"))


def _mentions_conservative(text: str) -> bool:
    return any(
        phrase in text
        for phrase in (
            "低风险",
            "稳一点",
            "稳健",
            "保守",
            "不要太激进",
            "别太激进",
            "适合新手",
            "新手友好",
            "不要满仓",
            "不满仓",
            "别满仓",
            "避免满仓",
        )
    )


def _mentions_stop_loss(text: str) -> bool:
    if any(phrase in text for phrase in ("不要止损", "不设止损", "不用止损")):
        return False
    return any(phrase in text for phrase in ("设置止损", "加止损", "带止损", "止损"))


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default

