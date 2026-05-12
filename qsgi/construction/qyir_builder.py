"""Deterministic Route B builder from extracted strategy slots to QYIR."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from qsgi.construction.canonicalizer import CanonicalizationEvent, canonicalize_qyir
from qsgi.construction.slot_schema import IndicatorSlot, StrategySlotSpec
from qyir.validator import validate_qyir


@dataclass(frozen=True)
class BuildResult:
    """Result of deterministic slot-to-QYIR construction."""

    success: bool
    qyir: dict[str, Any] | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    canonicalization_log: list[CanonicalizationEvent] = field(default_factory=list)


def build_qyir_from_slots(
    slots: StrategySlotSpec | dict[str, Any],
    *,
    strategy_name: str = "qsga_route_b_strategy",
    description: str | None = None,
) -> BuildResult:
    """Build a QYIR candidate from validated slots and run QYIR validation."""
    spec = slots if isinstance(slots, StrategySlotSpec) else StrategySlotSpec.model_validate(slots)

    if spec.safe_action == "reject":
        return _failed("safe_action", "Slot extractor marked the request as reject.")
    if spec.safe_action == "clarify":
        missing = ", ".join(spec.ambiguity.missing_slots) or "missing or ambiguous slots"
        return _failed("safe_action", f"Clarification required: {missing}.")

    indicator_result = _build_indicators(spec.indicators, spec.strategy_family)
    if indicator_result.errors:
        return BuildResult(success=False, errors=indicator_result.errors)

    indicators = indicator_result.indicators
    aliases = [indicator["alias"] for indicator in indicators]
    entry_rules, exit_rules = _build_rules(spec, aliases)
    if not entry_rules or not exit_rules:
        return _failed("rules", "Could not build entry and exit rules from slots.")

    risk_control, risk_errors = _build_risk_control(spec)
    if risk_errors:
        return BuildResult(success=False, errors=risk_errors)

    qyir = {
        "strategy_name": _snake_case(strategy_name),
        "description": (description or _description(spec))[:512],
        "version": "1.0",
        "market": {
            "symbol": (spec.market_scope.symbol or "SPY").upper(),
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": indicators,
        "entry_rules": entry_rules,
        "exit_rules": exit_rules,
        "risk_control": risk_control,
    }

    canonicalized = canonicalize_qyir(qyir)
    validation = validate_qyir(canonicalized.canonical_qyir)
    if not validation.valid:
        return BuildResult(
            success=False,
            qyir=canonicalized.canonical_qyir,
            errors=[{"path": issue.path, "message": issue.message} for issue in validation.issues],
            canonicalization_log=canonicalized.canonicalization_log,
        )

    return BuildResult(
        success=True,
        qyir=canonicalized.canonical_qyir,
        canonicalization_log=canonicalized.canonicalization_log,
    )


@dataclass(frozen=True)
class _IndicatorBuild:
    indicators: list[dict[str, Any]]
    errors: list[dict[str, str]]


def _build_indicators(slots: list[IndicatorSlot], strategy_family: str) -> _IndicatorBuild:
    if not slots:
        slots = _default_indicator_slots(strategy_family)

    indicators: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen: set[str] = set()

    for index, slot in enumerate(slots):
        if slot.name == "UNKNOWN":
            errors.append({"path": f"indicators[{index}].name", "message": "Unsupported or unknown indicator."})
            continue
        for indicator in _indicator_to_qyir(slot):
            alias = indicator["alias"]
            if alias in seen:
                continue
            seen.add(alias)
            indicators.append(indicator)

    if not indicators and not errors:
        errors.append({"path": "indicators", "message": "At least one supported indicator is required."})
    if len(indicators) == 1 and indicators[0]["name"] in {"SMA", "EMA"}:
        companion = _single_ma_companion(indicators[0])
        if companion["alias"] not in seen:
            indicators.append(companion)
    return _IndicatorBuild(indicators=indicators, errors=errors)


def _default_indicator_slots(strategy_family: str) -> list[IndicatorSlot]:
    if strategy_family == "mean_reversion":
        return [IndicatorSlot(name="RSI", window=14, role="threshold")]
    return [
        IndicatorSlot(name="SMA", window=20, role="fast"),
        IndicatorSlot(name="SMA", window=60, role="slow"),
    ]


def _indicator_to_qyir(slot: IndicatorSlot) -> list[dict[str, Any]]:
    name = slot.name
    if name in {"SMA", "EMA"}:
        window = slot.window or (20 if slot.role in {"fast", "unknown"} else 60)
        return [{"name": name, "params": {"window": int(window)}, "alias": f"{name.lower()}_{int(window)}"}]
    if name == "RSI":
        window = slot.window or 14
        return [{"name": "RSI", "params": {"window": int(window)}, "alias": f"rsi_{int(window)}"}]
    if name == "MACD":
        return [
            {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
                "alias": "macd_line",
            },
            {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "signal_line"},
                "alias": "signal_line",
            },
        ]
    if name == "BOLLINGER":
        window = slot.window or 20
        return [
            {
                "name": "BOLLINGER",
                "params": {"window": int(window), "num_std": 2.0, "output": "upper"},
                "alias": "bollinger_upper",
            },
            {
                "name": "BOLLINGER",
                "params": {"window": int(window), "num_std": 2.0, "output": "lower"},
                "alias": "bollinger_lower",
            },
        ]
    return []


def _single_ma_companion(indicator: dict[str, Any]) -> dict[str, Any]:
    """Add a reference MA so price-vs-MA language can fit QYIR v1 alias rules."""
    name = str(indicator["name"])
    window = int(indicator.get("params", {}).get("window") or 20)
    companion_window = 60 if window <= 20 else 20
    return {
        "name": name,
        "params": {"window": companion_window},
        "alias": f"{name.lower()}_{companion_window}",
    }


def _build_rules(spec: StrategySlotSpec, aliases: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entry = _explicit_rule(spec.entry_logic.operator, spec.entry_logic.left, spec.entry_logic.right, aliases)
    exit_ = _explicit_rule(spec.exit_logic.operator, spec.exit_logic.left, spec.exit_logic.right, aliases)
    if entry and exit_:
        return [entry], [exit_]

    if "rsi" in aliases[0]:
        rsi = aliases[0]
        return (
            [{"type": "less_than", "left": rsi, "right": _threshold(spec.entry_logic.right, 30)}],
            [{"type": "greater_than", "left": rsi, "right": _threshold(spec.exit_logic.right, 70)}],
        )

    if "macd_line" in aliases and "signal_line" in aliases:
        return (
            [{"type": "cross_over", "left": "macd_line", "right": "signal_line"}],
            [{"type": "cross_under", "left": "macd_line", "right": "signal_line"}],
        )

    moving_average_aliases = [alias for alias in aliases if alias.startswith(("sma_", "ema_"))]
    if len(moving_average_aliases) >= 2:
        fast, slow = sorted(moving_average_aliases[:2], key=_alias_window)
        return (
            [{"type": "cross_over", "left": fast, "right": slow}],
            [{"type": "cross_under", "left": fast, "right": slow}],
        )

    if len(aliases) >= 2:
        return (
            [{"type": "cross_over", "left": aliases[0], "right": aliases[1]}],
            [{"type": "cross_under", "left": aliases[0], "right": aliases[1]}],
        )

    return [], []


def _explicit_rule(operator: str | None, left: str | None, right: str | float | None, aliases: list[str]) -> dict[str, Any] | None:
    if not operator or operator == "unknown" or not left:
        return None
    left_alias = _resolve_alias(left, aliases)
    right_value = _resolve_alias(right, aliases) if isinstance(right, str) else right
    if left_alias not in aliases:
        return None
    if isinstance(right_value, str) and right_value not in aliases:
        return None
    if operator in {"cross_over", "cross_under", "greater_than", "less_than"} and right_value is not None:
        return {"type": operator, "left": left_alias, "right": right_value}
    return None


def _resolve_alias(value: str | None, aliases: list[str]) -> str:
    if value is None:
        return aliases[0]
    normalized = value.strip().lower().replace(" ", "_")
    normalized = re.sub(r"^(sma|ema|rsi)_?(\d+)$", lambda m: f"{m.group(1)}_{int(m.group(2))}", normalized)
    if normalized in aliases:
        return normalized
    for alias in aliases:
        if normalized == alias.replace("_", ""):
            return alias
    return normalized


def _build_risk_control(spec: StrategySlotSpec) -> tuple[dict[str, Any], list[dict[str, str]]]:
    risk = spec.risk_constraints
    if risk.leverage is not None and risk.leverage > 1.0:
        return {}, [{"path": "risk_constraints.leverage", "message": "QYIR v1 does not support leverage above 1.0."}]

    return (
        {
            "position_size": risk.position_size if risk.position_size is not None else 0.5,
            "stop_loss": risk.stop_loss if risk.stop_loss is not None else 0.08,
            "take_profit": risk.take_profit,
            "max_drawdown_limit": risk.max_drawdown_limit if risk.max_drawdown_limit is not None else 0.2,
            "allow_short": bool(risk.allow_short) if risk.allow_short is not None else False,
            "leverage": 1.0,
        },
        [],
    )


def _threshold(value: Any, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return float(default)
    return float(default)


def _alias_window(alias: str) -> int:
    match = re.search(r"_(\d+)$", alias)
    if not match:
        return 999
    return int(match.group(1))


def _snake_case(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return cleaned[:64] or "qsga_route_b_strategy"


def _description(spec: StrategySlotSpec) -> str:
    parts = [
        spec.entry_logic.natural_language.strip(),
        spec.exit_logic.natural_language.strip(),
    ]
    text = "; ".join(part for part in parts if part)
    return text or f"Route B {spec.strategy_family} QYIR candidate."


def _failed(path: str, message: str) -> BuildResult:
    return BuildResult(success=False, errors=[{"path": path, "message": message}])
