"""Integration tests for QYIR generation and repair trace."""

from __future__ import annotations

import json
from types import SimpleNamespace

import run_qsga
from generator.qyir_generator import generate_qyir
from tests.test_qyir_generator import (
    FakeLLMClient,
    passing_validator,
    valid_qyir,
)
from verifier.semantic_verifier import semantic_verify


def test_generate_qyir_triggers_repair_after_semantic_failure():
    qyir = valid_qyir()
    qyir["risk_control"]["position_size"] = 0.95
    client = FakeLLMClient([json.dumps(qyir, ensure_ascii=False)])

    result = generate_qyir(
        "稳一点，适合新手的双均线策略",
        client=client,
        validator=passing_validator,
        semantic_validator=semantic_verify,
    )

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["risk_control"]["position_size"] == 0.3
    assert result.repair_trace == [
        {
            "round": 1,
            "violations_before": [
                "Conservative or novice-friendly intent conflicts with high position size."
            ],
            "repair_action": "Set risk_control.position_size to 0.3.",
            "passed_after_repair": True,
        }
    ]


def test_run_qsga_success_prints_repair_trace(monkeypatch, capsys):
    qyir = valid_qyir()
    monkeypatch.setattr(
        run_qsga,
        "generate_qyir",
        lambda query: SimpleNamespace(
            success=True,
            qyir=qyir,
            errors=[],
            repair_trace=[
                {
                    "round": 1,
                    "violations_before": ["high position size"],
                    "repair_action": "Set risk_control.position_size to 0.3.",
                    "passed_after_repair": True,
                }
            ],
        ),
    )

    exit_code = run_qsga.main(["--query", "稳一点"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Repair trace:" in captured.out
    assert '"round": 1' in captured.out
    assert "Set risk_control.position_size to 0.3." in captured.out
