"""Tests for QYIR v1 validator module."""

import json
import tempfile
from pathlib import Path

from qyir.validator import validate_qyir, validate_qyir_file


class TestValidateQyir:
    """Test dict-based validator."""

    def test_valid_qyir(self):
        data = {
            "strategy_name": "test",
            "version": "1.0",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [{"name": "SMA", "params": {"window": 20}, "alias": "sma"}],
            "entry_rules": [{"type": "greater_than", "left": "sma", "right": 100}],
            "exit_rules": [{"type": "less_than", "left": "sma", "right": 50}],
            "risk_control": {"position_size": 0.5, "leverage": 1.0},
        }
        result = validate_qyir(data)
        assert result.valid is True
        assert len(result.issues) == 0

    def test_missing_fields(self):
        result = validate_qyir({"strategy_name": "x"})
        assert result.valid is False
        paths = [i.path for i in result.issues]
        assert any("entry_rules" in p for p in paths)
        assert any("risk_control" in p for p in paths)

    def test_bad_indicator(self):
        data = {
            "strategy_name": "test",
            "version": "1.0",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [{"name": "ICHIMOKU", "params": {}, "alias": "bad"}],
            "entry_rules": [{"type": "greater_than", "left": "bad", "right": 100}],
            "exit_rules": [{"type": "less_than", "left": "bad", "right": 50}],
            "risk_control": {"position_size": 0.5, "leverage": 1.0},
        }
        result = validate_qyir(data)
        assert result.valid is False
        assert any("indicators" in i.path for i in result.issues)

    def test_leverage_rejected(self):
        data = {
            "strategy_name": "test",
            "version": "1.0",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [{"name": "SMA", "params": {"window": 20}, "alias": "sma"}],
            "entry_rules": [{"type": "greater_than", "left": "sma", "right": 100}],
            "exit_rules": [{"type": "less_than", "left": "sma", "right": 50}],
            "risk_control": {"position_size": 0.5, "leverage": 2.0},
        }
        result = validate_qyir(data)
        assert result.valid is False
        assert any("leverage" in i.message for i in result.issues)

    def test_bad_alias_ref(self):
        data = {
            "strategy_name": "test",
            "version": "1.0",
            "market": {"symbol": "SPY", "timeframe": "1d", "start_date": "2020-01-01", "end_date": "2024-12-31"},
            "indicators": [{"name": "SMA", "params": {"window": 20}, "alias": "sma"}],
            "entry_rules": [{"type": "cross_over", "left": "sma", "right": "ema_50"}],
            "exit_rules": [{"type": "cross_under", "left": "sma", "right": "ema_50"}],
            "risk_control": {"position_size": 0.5, "leverage": 1.0},
        }
        result = validate_qyir(data)
        assert result.valid is False
        assert any("unknown alias" in i.message for i in result.issues)

    def test_summary_on_pass(self):
        result = validate_qyir({"strategy_name": "x"})
        result.valid = True
        assert "passed" in result.summary.lower()

    def test_summary_on_fail(self):
        result = validate_qyir({"strategy_name": "x"})
        assert "failed" in result.summary.lower()


class TestValidateQyirFile:
    """Test file-based validator."""

    def test_valid_file(self):
        result = validate_qyir_file("qyir/examples/ma_cross.json")
        assert result.valid is True

    def test_invalid_file(self):
        result = validate_qyir_file("qyir/examples/invalid/bad_leverage.json")
        assert result.valid is False

    def test_file_not_found(self):
        result = validate_qyir_file("nonexistent.json")
        assert result.valid is False
        assert "not found" in result.issues[0].message

    def test_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json}", encoding="utf-8")
        result = validate_qyir_file(bad)
        assert result.valid is False
        assert "Invalid JSON" in result.issues[0].message

    def test_non_dict_json(self, tmp_path):
        bad = tmp_path / "array.json"
        bad.write_text("[1,2,3]", encoding="utf-8")
        result = validate_qyir_file(bad)
        assert result.valid is False
        assert "must be a JSON object" in result.issues[0].message
