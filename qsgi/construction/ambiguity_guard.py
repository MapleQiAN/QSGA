"""Deterministic ambiguity guard for Route B construction."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AmbiguityGuardResult:
    """Conservative pre-extraction ambiguity decision."""

    clarify: bool
    missing_slots: list[str]
    reason: str


_VAGUE_PATTERNS = (
    "稳一点",
    "适合现在行情",
    "比较聪明",
    "差不多",
    "看到机会",
    "机会就买",
    "别追高",
    "不要太频繁",
    "不要太复杂",
    "低买高卖",
    "能赚钱",
    "风险别太大",
    "收益也别太低",
    "参数你自己看着办",
    "趋势好就买",
    "不好就卖",
)

_CONCRETE_PATTERNS = (
    "上穿",
    "下穿",
    "突破",
    "跌破",
    "小于",
    "大于",
    "低于",
    "高于",
    "超过",
    "回归",
    "rsi",
    "macd",
    "布林",
    "bollinger",
    "均线上穿",
    "均线下穿",
)


def detect_ambiguous_intent(query: str) -> AmbiguityGuardResult:
    """Return clarification for vague requests without concrete trading rules."""
    normalized = query.strip().lower()
    if not normalized:
        return AmbiguityGuardResult(True, ["strategy_family", "entry_logic", "exit_logic"], "empty query")

    has_vague_language = any(pattern in normalized for pattern in _VAGUE_PATTERNS)
    if not has_vague_language:
        return AmbiguityGuardResult(False, [], "")

    has_numeric_rule = bool(re.search(r"\d+\s*(日|天|周|月|年|%|倍)?", normalized))
    has_concrete_rule = has_numeric_rule or any(pattern in normalized for pattern in _CONCRETE_PATTERNS)
    if has_concrete_rule and "参数你自己看着办" not in normalized:
        return AmbiguityGuardResult(False, [], "")

    return AmbiguityGuardResult(
        True,
        ["strategy_family", "indicator_or_signal", "entry_logic", "exit_logic", "risk_constraints"],
        "vague intent lacks concrete strategy rules",
    )
