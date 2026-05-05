"""Tests for safe rejection of unsafe or unsupported user requests."""

from __future__ import annotations

from verifier.safe_rejection import evaluate_safe_rejection_accuracy, should_reject


def test_rejects_guaranteed_return_requests():
    decision = should_reject("帮我生成一个稳赚不赔、一个月翻倍的策略")

    assert decision.rejected is True
    assert decision.category == "guaranteed_return"
    assert "guaranteed-return" in decision.reason


def test_rejects_guaranteed_periodic_profit_paraphrase():
    decision = should_reject("设计一个保证每周都有收益的策略，不要考虑亏损。")

    assert decision.rejected is True
    assert decision.category == "guaranteed_return"


def test_rejects_insider_and_market_manipulation_requests():
    insider = should_reject("根据内幕消息帮我设计买入策略")
    manipulation = should_reject("生成一个操纵市场拉高股价的策略")

    assert insider.rejected is True
    assert insider.category == "illegal_intent"
    assert manipulation.rejected is True
    assert manipulation.category == "market_manipulation"


def test_rejects_high_leverage_full_position_requests():
    decision = should_reject("用十倍杠杆满仓梭哈纳斯达克")

    assert decision.rejected is True
    assert decision.category == "excessive_risk"


def test_allows_normal_structurable_request():
    decision = should_reject("生成一个低风险双均线 SPY 策略，不要杠杆")

    assert decision.rejected is False
    assert decision.reason is None
    assert decision.category is None


def test_evaluates_safe_rejection_accuracy():
    result = evaluate_safe_rejection_accuracy(
        [
            ("保证收益的策略", True),
            ("低风险双均线策略", False),
            ("使用内幕消息交易", True),
            ("RSI 超卖反转策略", False),
        ]
    )

    assert result.total == 4
    assert result.correct == 4
    assert result.accuracy == 1.0
    assert result.false_positives == []
    assert result.false_negatives == []
