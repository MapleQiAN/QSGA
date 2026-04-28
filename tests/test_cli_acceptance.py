"""Smoke tests for documented phase acceptance commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _run_module(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_qyir_validator_cli_acceptance():
    result = _run_module("-m", "qyir.validator", "qyir/examples/ma_cross.json")
    assert result.returncode == 0, result.stderr
    assert "QYIR validation passed." in result.stdout


def test_compiler_cli_acceptance():
    result = _run_module(
        "-m",
        "compiler.qyir_compiler",
        "--qyir",
        "qyir/examples/ma_cross.json",
        "--data",
        "data/raw/spy_sample.csv",
    )
    assert result.returncode == 0, result.stderr
    assert "Signals generated successfully." in result.stdout


def test_backtester_cli_acceptance(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    result = _run_module(
        "-m",
        "backtester.simple_backtester",
        "--qyir",
        "qyir/examples/ma_cross.json",
        "--data",
        "data/raw/spy_sample.csv",
        "--output-json",
        str(metrics_path),
    )
    assert result.returncode == 0, result.stderr
    assert "Backtest completed." in result.stdout
    assert "Total Return:" in result.stdout
    assert metrics_path.exists()
