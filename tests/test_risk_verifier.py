"""Tests for QYIR risk auditing."""

from __future__ import annotations

import json
import subprocess
import sys

from verifier.risk_verifier import audit_risk


def base_qyir() -> dict:
    return {
        "strategy_name": "ma_cross_spy",
        "risk_control": {
            "position_size": 0.4,
            "stop_loss": 0.08,
            "take_profit": None,
            "max_drawdown_limit": 0.2,
            "allow_short": False,
            "leverage": 1.0,
        },
    }


def test_audit_passes_low_risk_qyir_and_metrics():
    result = audit_risk(
        base_qyir(),
        {
            "total_return": 0.12,
            "max_drawdown": -0.08,
            "sharpe_ratio": 1.1,
            "num_trades": 8,
        },
    )

    assert result.passed is True
    assert result.risk_level == "low"
    assert result.warnings == []
    assert result.recommendations == []


def test_rejects_position_size_above_one():
    qyir = base_qyir()
    qyir["risk_control"]["position_size"] = 1.2

    result = audit_risk(qyir)

    assert result.passed is False
    assert result.risk_level == "rejected"
    assert result.issues[0].path == "risk_control.position_size"
    assert "Reduce position size" in result.recommendations[0]


def test_warns_for_missing_stop_loss_and_leverage():
    qyir = base_qyir()
    qyir["risk_control"]["stop_loss"] = None
    qyir["risk_control"]["leverage"] = 1.5

    result = audit_risk(qyir)

    assert result.passed is True
    assert result.risk_level == "high"
    assert {issue.path for issue in result.issues} == {
        "risk_control.stop_loss",
        "risk_control.leverage",
    }
    assert "The strategy does not specify stop-loss." in result.warnings


def test_warns_when_backtest_drawdown_exceeds_qyir_limit():
    result = audit_risk(
        base_qyir(),
        {
            "total_return": 0.05,
            "max_drawdown": -0.31,
            "sharpe_ratio": 0.9,
            "num_trades": 6,
        },
    )

    assert result.passed is True
    assert result.risk_level == "high"
    assert any(issue.path == "backtest_metrics.max_drawdown" for issue in result.issues)
    assert any("max drawdown exceeds 20.0%" in warning for warning in result.warnings)


def test_warns_for_sample_quality_and_risk_return_imbalance():
    result = audit_risk(
        base_qyir(),
        {
            "total_return": 0.8,
            "max_drawdown": -0.45,
            "sharpe_ratio": 0.2,
            "num_trades": 1,
        },
    )

    assert result.passed is True
    assert result.risk_level == "high"
    assert {
        "backtest_metrics.num_trades",
        "backtest_metrics.sharpe_ratio",
        "backtest_metrics.risk_return_balance",
    }.issubset({issue.path for issue in result.issues})


def test_to_dict_matches_phase_output_shape():
    qyir = base_qyir()
    qyir["risk_control"]["stop_loss"] = None

    payload = audit_risk(qyir).to_dict()

    assert set(payload) == {
        "risk_level",
        "passed",
        "warnings",
        "recommendations",
        "issues",
    }
    assert payload["risk_level"] == "medium"
    assert payload["passed"] is True
    assert payload["warnings"]
    assert payload["recommendations"]


def test_risk_verifier_cli_acceptance(tmp_path):
    qyir_path = tmp_path / "qyir.json"
    metrics_path = tmp_path / "metrics.json"
    qyir_path.write_text(json.dumps(base_qyir()), encoding="utf-8")
    metrics_path.write_text(
        json.dumps(
            {
                "total_return": 0.12,
                "max_drawdown": -0.08,
                "sharpe_ratio": 1.1,
                "num_trades": 8,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "verifier.risk_verifier",
            "--qyir",
            str(qyir_path),
            "--metrics",
            str(metrics_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Risk audit completed." in result.stdout
    assert '"risk_level": "low"' in result.stdout
