"""Tests for verification-guided QYIR repair."""

from __future__ import annotations

import json
from types import SimpleNamespace

from repair.repair_agent import repair_qyir
from repair.repair_prompt import build_repair_prompt
from repair.repair_operators import apply_rule_based_repairs
from verifier.semantic_verifier import semantic_verify


def base_qyir() -> dict:
    return {
        "strategy_name": "ma_cross_spy",
        "description": "SMA20 上穿 SMA60 买入，下穿卖出",
        "version": "1.0",
        "market": {
            "symbol": "SPY",
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": [
            {"name": "SMA", "params": {"window": 20}, "alias": "sma_short"},
            {"name": "SMA", "params": {"window": 60}, "alias": "sma_long"},
        ],
        "entry_rules": [
            {"type": "cross_over", "left": "sma_short", "right": "sma_long"}
        ],
        "exit_rules": [
            {"type": "cross_under", "left": "sma_short", "right": "sma_long"}
        ],
        "risk_control": {
            "position_size": 0.4,
            "stop_loss": 0.08,
            "take_profit": None,
            "max_drawdown_limit": 0.2,
            "allow_short": False,
            "leverage": 1.0,
        },
    }


class FakeLLMClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.outputs.pop(0)


def always_failing_validator(data: dict) -> SimpleNamespace:
    return SimpleNamespace(
        valid=False,
        issues=[
            SimpleNamespace(
                path="risk_control.position_size",
                message="position_size remains invalid",
            )
        ],
    )


def passing_validator(data: dict) -> SimpleNamespace:
    return SimpleNamespace(valid=True, issues=[])


def passing_semantic_validator(query: str, data: dict) -> SimpleNamespace:
    return SimpleNamespace(valid=True, issues=[])


def test_build_repair_prompt_contains_context_and_requirements():
    prompt = build_repair_prompt(
        user_query="稳一点，不要杠杆",
        qyir={"risk_control": {"leverage": 2.0}},
        violations=[
            {
                "path": "risk_control.leverage",
                "message": "leverage must be 1.0",
            }
        ],
    )

    assert "The generated QYIR failed verification." in prompt
    assert "Original user query:" in prompt
    assert "稳一点，不要杠杆" in prompt
    assert '"leverage": 2.0' in prompt
    assert "risk_control.leverage" in prompt
    assert "Output valid JSON only." in prompt
    assert "Do not output Python code." in prompt


def test_rule_based_repair_preserves_input_and_applies_supported_actions():
    qyir = base_qyir()
    qyir["risk_control"]["position_size"] = 0.95
    qyir["risk_control"]["allow_short"] = True
    qyir["risk_control"]["leverage"] = 2.0

    repaired, actions = apply_rule_based_repairs(
        "稳一点，不要杠杆，不要做空",
        qyir,
        [
            {"path": "risk_control.position_size", "message": "high size"},
            {"path": "risk_control.allow_short", "message": "short conflict"},
            {"path": "risk_control.leverage", "message": "leverage conflict"},
        ],
    )

    assert qyir["risk_control"]["position_size"] == 0.95
    assert repaired["risk_control"]["position_size"] == 0.3
    assert repaired["risk_control"]["allow_short"] is False
    assert repaired["risk_control"]["leverage"] == 1.0
    assert actions == [
        "Set risk_control.leverage to 1.0.",
        "Set risk_control.allow_short to false.",
        "Set risk_control.position_size to 0.3.",
    ]


def test_repair_qyir_revalidates_after_rule_based_repair():
    qyir = base_qyir()
    qyir["risk_control"]["position_size"] = 0.95

    result = repair_qyir(
        "稳一点，适合新手",
        qyir,
        validator=passing_validator,
        semantic_validator=semantic_verify,
    )

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["risk_control"]["position_size"] == 0.3
    assert len(result.trace) == 1
    assert result.trace[0].round == 1
    assert result.trace[0].violations_before == [
        "Conservative or novice-friendly intent conflicts with high position size."
    ]
    assert result.trace[0].repair_action == "Set risk_control.position_size to 0.3."
    assert result.trace[0].passed_after_repair is True


def test_repair_qyir_uses_llm_repair_and_stops_after_two_rounds():
    client = FakeLLMClient(
        [
            json.dumps(base_qyir(), ensure_ascii=False),
            json.dumps(base_qyir(), ensure_ascii=False),
            json.dumps(base_qyir(), ensure_ascii=False),
        ]
    )

    result = repair_qyir(
        "稳一点",
        base_qyir(),
        client=client,
        validator=always_failing_validator,
        semantic_validator=passing_semantic_validator,
        max_rounds=2,
    )

    assert result.success is False
    assert [entry.round for entry in result.trace] == [1, 2]
    assert len(client.prompts) == 2
    assert all("Please repair the QYIR" in prompt for prompt in client.prompts)
    assert all(entry.passed_after_repair is False for entry in result.trace)
