"""Tests for QYIR generation prompt constraints."""

from generator.prompt import build_qyir_prompt


def test_prompt_requires_json_only_and_no_python():
    prompt = build_qyir_prompt("我想做一个稳一点的双均线策略，不要杠杆")

    assert "Return JSON only" in prompt
    assert "Do not output Python code" in prompt
    assert "Do not include markdown" in prompt


def test_prompt_limits_supported_indicators_and_rules():
    prompt = build_qyir_prompt("用 RSI 做低吸")

    assert "Use only supported indicators" in prompt
    assert "SMA" in prompt
    assert "EMA" in prompt
    assert "RSI" in prompt
    assert "MACD" in prompt
    assert "BOLLINGER" in prompt
    assert "Use only supported rule types" in prompt
    assert "cross_over" in prompt
    assert "greater_than" in prompt


def test_prompt_requires_risk_control_and_no_profit_promises():
    prompt = build_qyir_prompt("低风险策略")

    assert "risk_control" in prompt
    assert "position_size" in prompt
    assert "stop_loss" in prompt
    assert "max_drawdown_limit" in prompt
    assert "Do not promise profit" in prompt
    assert "guaranteed performance" in prompt
