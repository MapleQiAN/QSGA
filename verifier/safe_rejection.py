"""Safe rejection rules for unsafe or unsupported strategy requests."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class SafeRejectionDecision:
    """Decision for one user request."""

    rejected: bool
    reason: str | None = None
    category: str | None = None
    pattern: str | None = None

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "status": "rejected" if self.rejected else "accepted",
            "rejected": self.rejected,
            "reason": self.reason,
            "category": self.category,
            "pattern": self.pattern,
        }


@dataclass(frozen=True)
class SafeRejectionAccuracy:
    """Accuracy summary for a labeled safe-rejection dataset."""

    total: int
    correct: int
    accuracy: float
    false_positives: list[str] = field(default_factory=list)
    false_negatives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
        }


_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "guaranteed_return",
        (
            "稳赚不赔",
            "稳赚",
            "保证收益",
            "一定赚钱",
            "稳赚策略",
            "保本保收益",
            "无风险收益",
        ),
        "Unsafe request detected: guaranteed-return expectation.",
    ),
    (
        "unrealistic_return",
        (
            "一个月翻倍",
            "一夜暴富",
            "快速暴富",
            "短期翻倍",
            "翻十倍",
            "10倍收益",
            "十倍收益",
        ),
        "Unsafe request detected: unrealistic return expectation.",
    ),
    (
        "excessive_risk",
        (
            "满仓梭哈",
            "梭哈",
            "十倍杠杆",
            "10倍杠杆",
            "高杠杆",
            "allin",
            "all-in",
        ),
        "Unsafe request detected: excessive-risk trading intent.",
    ),
    (
        "illegal_intent",
        (
            "内幕消息",
            "内幕交易",
            "未公开消息",
            "非法交易",
        ),
        "Unsafe request detected: illegal trading intent.",
    ),
    (
        "regulatory_evasion",
        (
            "规避监管",
            "绕过监管",
            "逃避监管",
            "避开监管",
        ),
        "Unsafe request detected: regulatory-evasion intent.",
    ),
    (
        "market_manipulation",
        (
            "操纵市场",
            "拉高股价",
            "拉盘",
            "砸盘",
            "对倒",
        ),
        "Unsafe request detected: market-manipulation intent.",
    ),
    (
        "ambiguous_unstructurable",
        (
            "随便来一个赚钱策略",
            "随便写个赚钱策略",
            "什么都行只要赚钱",
        ),
        "Unsafe request detected: request is too vague to structure safely.",
    ),
    (
        "unsupported_scope",
        (
            "彩票",
            "体育投注",
            "博彩",
            "期权裸卖",
            "裸卖期权",
        ),
        "Unsafe request detected: unsupported asset or strategy type.",
    ),
)


def should_reject(user_query: str) -> SafeRejectionDecision:
    """Return whether a user query should be rejected before LLM generation."""
    text = _normalize(user_query)
    for category, patterns, reason in _RULES:
        for pattern in patterns:
            if _normalize(pattern) in text:
                return SafeRejectionDecision(
                    rejected=True,
                    reason=reason,
                    category=category,
                    pattern=pattern,
                )
    return SafeRejectionDecision(rejected=False)


def evaluate_safe_rejection_accuracy(
    cases: Iterable[tuple[str, bool]],
) -> SafeRejectionAccuracy:
    """Compute safe-rejection accuracy for (query, expected_rejected) cases."""
    total = 0
    correct = 0
    false_positives: list[str] = []
    false_negatives: list[str] = []

    for query, expected_rejected in cases:
        total += 1
        actual_rejected = should_reject(query).rejected
        if actual_rejected == expected_rejected:
            correct += 1
        elif actual_rejected:
            false_positives.append(query)
        else:
            false_negatives.append(query)

    accuracy = correct / total if total else 0.0
    return SafeRejectionAccuracy(
        total=total,
        correct=correct,
        accuracy=accuracy,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()
