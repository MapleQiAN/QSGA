"""Bounded risk-repair candidates for Route B QYIR outputs."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any, Iterable


RISK_REPAIR_PATHS = {
    "risk_control.position_size",
    "risk_control.leverage",
    "risk_control.stop_loss",
    "backtest_metrics.max_drawdown",
    "backtest_metrics.risk_return_balance",
}

_POSITION_TARGETS = (0.4, 0.3, 0.25, 0.2, 0.15, 0.1)


@dataclass(frozen=True)
class RiskRepairCandidate:
    """One conservative QYIR candidate derived from risk-audit feedback."""

    qyir: dict[str, Any]
    actions: list[str] = field(default_factory=list)
    issue_paths: list[str] = field(default_factory=list)


def generate_risk_repair_candidates(qyir: dict[str, Any], risk: Any) -> list[RiskRepairCandidate]:
    """Generate bounded, monotonic risk-repair candidates.

    The repair space is deliberately small and conservative: it may reduce
    exposure, set leverage to 1.0, disable shorting, and add or tighten a
    stop-loss. It never changes entry/exit logic, increases position size,
    raises leverage, enables shorting, or weakens an existing drawdown limit.
    """
    issue_paths = sorted(_risk_issue_paths(risk))
    if not RISK_REPAIR_PATHS.intersection(issue_paths):
        return []

    base = copy.deepcopy(qyir)
    base_actions = _apply_fixed_risk_repairs(base, issue_paths)
    needs_exposure_repair = bool(
        {"risk_control.position_size", "backtest_metrics.max_drawdown", "backtest_metrics.risk_return_balance"}
        .intersection(issue_paths)
    )

    candidates: list[RiskRepairCandidate] = []
    if base_actions:
        candidates.append(
            RiskRepairCandidate(qyir=copy.deepcopy(base), actions=list(base_actions), issue_paths=issue_paths)
        )

    if needs_exposure_repair:
        for target in _bounded_position_targets(qyir):
            candidate = copy.deepcopy(base)
            actions = list(base_actions)
            risk_control = candidate.setdefault("risk_control", {})
            current = _number(risk_control.get("position_size"), default=1.0)
            if target < current:
                risk_control["position_size"] = target
                actions.append(f"Set risk_control.position_size to {target:.2f}.")
            if _tighten_stop_loss(risk_control, 0.05):
                actions.append("Set risk_control.stop_loss to 0.05.")
            if actions:
                candidates.append(
                    RiskRepairCandidate(qyir=candidate, actions=actions, issue_paths=issue_paths)
                )

    return _dedupe_candidates(candidates)


def _risk_issue_paths(risk: Any) -> set[str]:
    return {str(getattr(issue, "path", "")) for issue in getattr(risk, "issues", [])}


def _apply_fixed_risk_repairs(qyir: dict[str, Any], issue_paths: Iterable[str]) -> list[str]:
    paths = set(issue_paths)
    risk_control = qyir.setdefault("risk_control", {})
    actions: list[str] = []

    if risk_control.get("leverage", 1.0) != 1.0:
        risk_control["leverage"] = 1.0
        actions.append("Set risk_control.leverage to 1.0.")

    if risk_control.get("allow_short") is not False:
        risk_control["allow_short"] = False
        actions.append("Set risk_control.allow_short to false.")

    if "risk_control.stop_loss" in paths and risk_control.get("stop_loss") is None:
        risk_control["stop_loss"] = 0.08
        actions.append("Set risk_control.stop_loss to 0.08.")

    if risk_control.get("max_drawdown_limit") is None:
        risk_control["max_drawdown_limit"] = 0.2
        actions.append("Set risk_control.max_drawdown_limit to 0.20.")

    return actions


def _bounded_position_targets(qyir: dict[str, Any]) -> list[float]:
    risk_control = qyir.get("risk_control", {})
    current = _number(risk_control.get("position_size"), default=1.0)
    return [target for target in _POSITION_TARGETS if target < current]


def _tighten_stop_loss(risk_control: dict[str, Any], target: float) -> bool:
    current = risk_control.get("stop_loss")
    if current is None:
        risk_control["stop_loss"] = target
        return True
    current_value = _number(current, default=target)
    if current_value > target:
        risk_control["stop_loss"] = target
        return True
    return False


def _dedupe_candidates(candidates: list[RiskRepairCandidate]) -> list[RiskRepairCandidate]:
    seen: set[str] = set()
    unique: list[RiskRepairCandidate] = []
    for candidate in candidates:
        key = json.dumps(candidate.qyir, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default
