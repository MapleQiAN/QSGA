"""Explicit intent-slot semantic verification for QYIR.

The verifier intentionally checks only explicit, normalizable user intents.
It does not claim to infer arbitrary financial semantics from vague text.
"""

from __future__ import annotations

import re
import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class SemanticViolation:
    """A semantic inconsistency between the user query and QYIR."""

    type: str
    path: str
    message: str
    intent_slot: str
    expected: str
    actual: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "path": self.path,
            "message": self.message,
            "intent_slot": self.intent_slot,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass(frozen=True)
class SemanticVerificationResult:
    """Structured semantic verification result."""

    passed: bool
    violations: list[SemanticViolation] = field(default_factory=list)
    detected_slots: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """Compatibility alias for other validators."""
        return self.passed

    @property
    def issues(self) -> list[SemanticViolation]:
        """Compatibility alias for generator error handling."""
        return self.violations

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "detected_slots": self.detected_slots,
            "violations": [violation.to_dict() for violation in self.violations],
        }


def semantic_verify(user_query: str, qyir: dict[str, Any]) -> SemanticVerificationResult:
    """Verify whether QYIR satisfies explicit intent slots in the user query."""
    slots = extract_intent_slots(user_query)
    risk = qyir.get("risk_control", {}) if isinstance(qyir, dict) else {}
    violations: list[SemanticViolation] = []

    leverage = _number(risk.get("leverage", 1.0), default=1.0)
    allow_short = bool(risk.get("allow_short", False))
    position_size = _number(risk.get("position_size", 1.0), default=1.0)
    stop_loss = risk.get("stop_loss")
    max_drawdown_limit = risk.get("max_drawdown_limit")

    if "no_leverage" in slots and leverage > 1.0:
        violations.append(
            _violation(
                "risk_control.leverage",
                "no_leverage",
                "leverage <= 1.0",
                leverage,
                "User explicitly forbids leverage, but QYIR uses leverage.",
            )
        )

    if "no_short" in slots and allow_short:
        violations.append(
            _violation(
                "risk_control.allow_short",
                "no_short",
                "allow_short is false",
                allow_short,
                "User explicitly forbids short selling, but QYIR allows short selling.",
            )
        )

    if ("low_risk" in slots or "novice_friendly" in slots) and position_size > 0.5:
        violations.append(
            _violation(
                "risk_control.position_size",
                "low_risk",
                "position_size <= 0.5",
                position_size,
                "Conservative or novice-friendly intent conflicts with high position size.",
            )
        )

    if "no_full_position" in slots and position_size >= 0.9:
        violations.append(
            _violation(
                "risk_control.position_size",
                "no_full_position",
                "position_size < 0.9",
                position_size,
                "User forbids full-position trading, but QYIR uses near full position.",
            )
        )

    if "stop_loss_required" in slots and stop_loss is None:
        violations.append(
            _violation(
                "risk_control.stop_loss",
                "stop_loss_required",
                "stop_loss is set",
                stop_loss,
                "User explicitly asks for stop-loss, but QYIR does not set stop_loss.",
            )
        )

    drawdown_threshold = _extract_drawdown_threshold(user_query)
    if "drawdown_control" in slots:
        if max_drawdown_limit is None:
            violations.append(
                _violation(
                    "risk_control.max_drawdown_limit",
                    "drawdown_control",
                    "max_drawdown_limit is set",
                    max_drawdown_limit,
                    "User asks to control drawdown, but QYIR does not set max_drawdown_limit.",
                )
            )
        elif drawdown_threshold is not None and _number(max_drawdown_limit, 1.0) > drawdown_threshold:
            violations.append(
                _violation(
                    "risk_control.max_drawdown_limit",
                    "drawdown_control",
                    f"max_drawdown_limit <= {drawdown_threshold}",
                    max_drawdown_limit,
                    "User specifies a drawdown limit, but QYIR uses a looser max_drawdown_limit.",
                )
            )

    horizon_violation = _verify_horizon(slots, qyir)
    if horizon_violation is not None:
        violations.append(horizon_violation)

    return SemanticVerificationResult(
        passed=not violations,
        violations=violations,
        detected_slots=sorted(slots),
    )


def extract_intent_slots(user_query: str) -> set[str]:
    """Extract supported explicit intent slots from a Chinese user query."""
    text = _normalize(user_query)
    slots: set[str] = set()

    if _contains_any(text, ("不要杠杆", "不用杠杆", "不使用杠杆", "无杠杆", "禁止杠杆", "别加杠杆")):
        slots.add("no_leverage")
    if _contains_any(text, ("不要做空", "不做空", "禁止做空", "不能做空", "别做空")):
        slots.add("no_short")
    if _contains_any(text, ("低风险", "稳一点", "稳健", "保守", "不要太激进", "别太激进")):
        slots.add("low_risk")
    if _contains_any(text, ("不要满仓", "不满仓", "别满仓", "避免满仓")):
        slots.add("no_full_position")
    if _contains_any(text, ("控制回撤", "回撤控制", "最大回撤", "回撤不要超过", "回撤不超过")):
        slots.add("drawdown_control")
    if _contains_any(text, ("设置止损", "加止损", "带止损", "止损")) and not _contains_any(text, ("不要止损", "不设止损", "不用止损")):
        slots.add("stop_loss_required")
    if "短线" in text:
        slots.add("short_horizon")
    if "中线" in text:
        slots.add("medium_horizon")
    if "长线" in text:
        slots.add("long_horizon")
    if _contains_any(text, ("适合新手", "新手友好", "给新手")):
        slots.add("novice_friendly")

    return slots


def _verify_horizon(slots: set[str], qyir: dict[str, Any]) -> SemanticViolation | None:
    windows = list(_indicator_windows(qyir.get("indicators", [])))
    if not windows:
        return None

    max_window = max(windows)
    min_window = min(windows)
    if "short_horizon" in slots and min_window > 30:
        return _violation(
            "indicators",
            "short_horizon",
            "at least one indicator window <= 30",
            windows,
            "User asks for a short-term strategy, but QYIR uses only long lookback windows.",
        )
    if "medium_horizon" in slots and (max_window < 20 or min_window > 120):
        return _violation(
            "indicators",
            "medium_horizon",
            "indicator windows overlap 20-120 days",
            windows,
            "User asks for a medium-term strategy, but QYIR indicator windows are outside the expected range.",
        )
    if "long_horizon" in slots and max_window < 60:
        return _violation(
            "indicators",
            "long_horizon",
            "at least one indicator window >= 60",
            windows,
            "User asks for a long-term strategy, but QYIR uses only short lookback windows.",
        )
    return None


def _indicator_windows(indicators: Iterable[dict[str, Any]]) -> Iterable[int]:
    for indicator in indicators:
        params = indicator.get("params", {})
        for key in ("window", "slow"):
            value = params.get(key)
            if isinstance(value, int):
                yield value


def _extract_drawdown_threshold(user_query: str) -> float | None:
    text = _normalize(user_query)
    match = re.search(r"(?:最大)?回撤(?:控制)?(?:在|到|不超过|不要超过|小于|低于)?\s*(\d+(?:\.\d+)?)\s*%?", text)
    if match is None:
        return None
    value = float(match.group(1))
    if value > 1:
        value = value / 100
    return value


def _violation(path: str, intent_slot: str, expected: str, actual: Any, message: str) -> SemanticViolation:
    return SemanticViolation(
        type="semantic_violation",
        path=path,
        message=message,
        intent_slot=intent_slot,
        expected=expected,
        actual=actual,
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _number(value: Any, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for explicit semantic verification."""
    parser = argparse.ArgumentParser(description="Verify explicit user intent slots against a QYIR JSON file.")
    parser.add_argument("--query", required=True, help="Original user strategy query.")
    parser.add_argument("--qyir", required=True, help="Path to QYIR JSON file.")
    args = parser.parse_args(argv)

    qyir_path = Path(args.qyir)
    data = json.loads(qyir_path.read_text(encoding="utf-8"))
    result = semantic_verify(args.query, data)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
