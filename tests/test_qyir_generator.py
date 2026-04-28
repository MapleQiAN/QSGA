"""Mocked tests for Chinese query to QYIR generation."""

from __future__ import annotations

import json
from types import SimpleNamespace

import run_qsga
from generator.qyir_generator import generate_qyir


def valid_qyir() -> dict:
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
            "position_size": 0.5,
            "stop_loss": 0.1,
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


def passing_validator(data: dict) -> SimpleNamespace:
    return SimpleNamespace(valid=True, issues=[])


def leverage_failing_validator(data: dict) -> SimpleNamespace:
    return SimpleNamespace(
        valid=False,
        issues=[
            SimpleNamespace(
                path="risk_control.leverage",
                message="leverage must be 1.0 in QYIR v1",
            )
        ],
    )


def passing_semantic_validator(query: str, data: dict) -> SimpleNamespace:
    return SimpleNamespace(valid=True, issues=[])


def failing_semantic_validator(query: str, data: dict) -> SimpleNamespace:
    return SimpleNamespace(
        valid=False,
        issues=[
            SimpleNamespace(
                path="risk_control.position_size",
                message="Conservative intent conflicts with high position size.",
            )
        ],
    )


def test_generate_qyir_valid_json_passes_schema():
    client = FakeLLMClient([json.dumps(valid_qyir(), ensure_ascii=False)])

    result = generate_qyir(
        "我想做一个稳一点的双均线策略，不要杠杆",
        client=client,
        validator=passing_validator,
        semantic_validator=passing_semantic_validator,
    )

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["risk_control"]["leverage"] == 1.0
    assert result.attempts == 1


def test_generate_qyir_retries_invalid_json_then_succeeds():
    client = FakeLLMClient(["not json", json.dumps(valid_qyir(), ensure_ascii=False)])

    result = generate_qyir(
        "用双均线生成策略",
        client=client,
        max_retries=1,
        validator=passing_validator,
        semantic_validator=passing_semantic_validator,
    )

    assert result.success is True
    assert result.attempts == 2
    assert len(client.prompts) == 2
    assert "Previous output failed validation" in client.prompts[1]
    assert "Invalid JSON from LLM" in client.prompts[1]


def test_generate_qyir_schema_failure_is_structured():
    bad = valid_qyir()
    bad["risk_control"] = {"position_size": 0.5, "leverage": 2.0}
    client = FakeLLMClient([json.dumps(bad), json.dumps(bad)])

    result = generate_qyir(
        "不要杠杆",
        client=client,
        max_retries=1,
        validator=leverage_failing_validator,
        semantic_validator=passing_semantic_validator,
    )

    assert result.success is False
    assert result.attempts == 2
    assert result.errors
    assert all(set(error) == {"path", "message"} for error in result.errors)
    assert any("leverage" in error["message"] for error in result.errors)


def test_generate_qyir_semantic_failure_is_structured():
    client = FakeLLMClient([json.dumps(valid_qyir()), json.dumps(valid_qyir())])

    result = generate_qyir(
        "稳一点",
        client=client,
        max_retries=1,
        validator=passing_validator,
        semantic_validator=failing_semantic_validator,
    )

    assert result.success is False
    assert result.attempts == 2
    assert result.errors == [
        {
            "path": "risk_control.position_size",
            "message": "Conservative intent conflicts with high position size.",
        }
    ]


def test_generate_qyir_rejects_unsafe_query_before_llm():
    class FailingLLMClient:
        def generate(self, prompt: str) -> str:
            raise AssertionError("LLM must not be called for rejected requests")

    result = generate_qyir(
        "帮我生成一个稳赚不赔、一个月翻倍的策略",
        client=FailingLLMClient(),
        validator=passing_validator,
        semantic_validator=passing_semantic_validator,
    )

    assert result.success is False
    assert result.rejected is True
    assert result.rejection_reason is not None
    assert "guaranteed-return" in result.rejection_reason
    assert result.attempts == 0
    assert result.errors == [
        {
            "path": "safe_rejection",
            "message": result.rejection_reason,
        }
    ]


def test_run_qsga_success_prints_required_lines(monkeypatch, capsys):
    monkeypatch.setattr(
        run_qsga,
        "generate_qyir",
        lambda query: SimpleNamespace(success=True, qyir=valid_qyir(), errors=[]),
    )

    exit_code = run_qsga.main(["--query", "稳一点的双均线策略"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "QYIR generated successfully." in captured.out
    assert "Schema verification passed." in captured.out
    assert "Semantic verification passed." in captured.out


def test_run_qsga_failure_returns_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(
        run_qsga,
        "generate_qyir",
        lambda query: SimpleNamespace(
            success=False,
            qyir=None,
            errors=[{"path": "json", "message": "Invalid JSON from LLM"}],
        ),
    )

    exit_code = run_qsga.main(["--query", "非法输出"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "QYIR generation failed." in captured.err
    assert "[json] Invalid JSON from LLM" in captured.err


def test_run_qsga_rejection_prints_rejected_message(monkeypatch, capsys):
    monkeypatch.setattr(
        run_qsga,
        "generate_qyir",
        lambda query: SimpleNamespace(
            success=False,
            rejected=True,
            rejection_reason="Unsafe request detected: guaranteed-return expectation.",
            qyir=None,
            errors=[
                {
                    "path": "safe_rejection",
                    "message": "Unsafe request detected: guaranteed-return expectation.",
                }
            ],
        ),
    )

    exit_code = run_qsga.main(["--query", "稳赚不赔"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "QYIR request rejected." in captured.err
    assert "Unsafe request detected" in captured.err
