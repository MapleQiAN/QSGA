"""Unsupported Route B semantics guard for QYIR v1."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UnsupportedSemanticsResult:
    """Detection result for semantics outside QYIR v1."""

    unsupported: bool
    reason: str = ""
    cues: list[str] = field(default_factory=list)


def detect_unsupported_semantics(query: str) -> UnsupportedSemanticsResult:
    """Detect concrete but unsupported strategy semantics before slot extraction."""
    text = "".join(query.lower().split())
    cues: list[str] = []

    if _contains_any(text, ("低波动", "波动率低", "最低波动", "lowvolatility")):
        cues.append("low_volatility_selection")

    if _contains_any(text, ("轮动", "股票池", "排名", "排行", "涨幅最高", "收益排名", "表现最好", "表现最强")):
        cues.append("cross_sectional_ranking_or_rotation")

    if _contains_any(text, ("等权", "最多持有", "不少于", "持仓数量", "topk", "top1", "top2", "top3")):
        cues.append("portfolio_cardinality_or_weighting")

    if re.search(r"连续[一二三四五六七八九十\d]+[天日]?(下跌|上涨)", text):
        cues.append("consecutive_day_pattern")

    if not cues:
        return UnsupportedSemanticsResult(unsupported=False)

    reason = "Unsupported QYIR v1 semantics: " + ", ".join(cues)
    return UnsupportedSemanticsResult(unsupported=True, reason=reason, cues=cues)


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)
