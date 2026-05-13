"""Mocked tests for Route B slot extraction and construction pipeline."""

from __future__ import annotations

import json

from qsgi.construction import construct_qyir_from_query, detect_ambiguous_intent, detect_unsupported_semantics, extract_slots
from experiments.run_live_route_b import (
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODELS,
    _normalize_deepseek_model_name,
    _read_api_key_file_first,
)


def _slot_payload() -> dict:
    return {
        "strategy_family": "trend_following",
        "market_scope": {"symbol": "SPY", "asset_type": "etf", "timeframe": "daily"},
        "indicators": [
            {"name": "SMA", "window": 20, "role": "fast"},
            {"name": "SMA", "window": 60, "role": "slow"},
        ],
        "entry_logic": {"operator": "cross_over", "left": "sma20", "right": "sma60"},
        "exit_logic": {"operator": "cross_under", "left": "sma20", "right": "sma60"},
        "risk_constraints": {"position_size": 0.5, "max_drawdown_limit": 0.2, "allow_short": False, "leverage": 1.0},
        "ambiguity": {"requires_clarification": False, "missing_slots": [], "ambiguous_phrases": []},
        "safe_action": "construct",
    }


class FakeClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.outputs.pop(0)


def test_extract_slots_retries_invalid_json_then_succeeds():
    client = FakeClient(["not json", json.dumps(_slot_payload())])

    result = extract_slots("双均线", client=client, max_retries=1)

    assert result.success is True
    assert result.attempts == 2
    assert "Previous slot JSON failed validation" in client.prompts[1]


def test_construct_qyir_from_query_builds_valid_qyir():
    client = FakeClient([json.dumps(_slot_payload())])

    result = construct_qyir_from_query("20日均线上穿60日均线买入，不要杠杆", client=client)

    assert result.success is True
    assert result.qyir is not None
    assert result.qyir["entry_rules"][0]["left"] == "sma_20"


def test_construct_qyir_from_query_rejects_before_llm():
    client = FakeClient([])

    result = construct_qyir_from_query("帮我生成稳赚不赔的策略", client=client)

    assert result.rejected is True
    assert result.rejection_reason is not None
    assert client.prompts == []


def test_construct_qyir_from_query_handles_clarification():
    payload = _slot_payload()
    payload["safe_action"] = "clarify"
    payload["ambiguity"] = {
        "requires_clarification": True,
        "missing_slots": ["entry_logic"],
        "ambiguous_phrases": ["稳一点"],
    }
    client = FakeClient([json.dumps(payload)])

    result = construct_qyir_from_query("稳一点", client=client)

    assert result.success is False
    assert result.clarification_requested is True
    assert "Clarification required" in result.errors[0]["message"]


def test_construct_qyir_from_query_clarifies_vague_intent_before_llm():
    client = FakeClient([])

    result = construct_qyir_from_query("帮我做一个稳一点的策略。", client=client)

    assert result.success is False
    assert result.clarification_requested is True
    assert result.errors[0]["path"] == "ambiguity_guard"
    assert client.prompts == []


def test_ambiguity_guard_allows_concrete_rules():
    result = detect_ambiguous_intent("做一个稳健的20日均线上穿60日均线买入策略")

    assert result.clarify is False


def test_ambiguity_guard_does_not_block_risk_constrained_defaults():
    result = detect_ambiguous_intent("我不要满仓，也不要杠杆，给我一个稳健的ETF策略。")

    assert result.clarify is False


def test_construct_qyir_from_query_defaults_non_core_clarification_slots():
    payload = _slot_payload()
    payload["safe_action"] = "clarify"
    payload["market_scope"]["symbol"] = "UNKNOWN"
    payload["ambiguity"] = {
        "requires_clarification": True,
        "missing_slots": ["symbol", "risk_constraints"],
        "ambiguous_phrases": ["asset omitted"],
    }
    client = FakeClient([json.dumps(payload)])

    result = construct_qyir_from_query("20日均线上穿60日均线买入", client=client)

    assert result.success is True
    assert result.clarification_requested is False
    assert result.slots is not None
    assert result.slots.safe_action == "construct"


def test_construct_qyir_from_query_defaults_ma_deviation_threshold():
    payload = _slot_payload()
    payload["strategy_family"] = "mean_reversion"
    payload["indicators"] = [{"name": "SMA", "window": 50, "role": "fast"}]
    payload["entry_logic"] = {
        "operator": "greater_than",
        "left": "price",
        "right": "sma50",
        "natural_language": "price deviates too much above 50-day SMA",
    }
    payload["exit_logic"] = {
        "operator": "less_than",
        "left": "price",
        "right": "sma50",
        "natural_language": "price returns to 50-day SMA",
    }
    payload["safe_action"] = "clarify"
    payload["ambiguity"] = {
        "requires_clarification": True,
        "missing_slots": ["entry_threshold"],
        "ambiguous_phrases": ["价格偏离50日均线太多时买入"],
    }
    client = FakeClient([json.dumps(payload)])

    result = construct_qyir_from_query("价格偏离50日均线太多时买入，回归均线后卖出", client=client)

    assert result.success is True
    assert result.clarification_requested is False
    assert result.qyir is not None
    assert {indicator["alias"] for indicator in result.qyir["indicators"]} == {"sma_20", "sma_50"}


def test_construct_qyir_from_query_blocks_unsupported_rotation_before_llm():
    client = FakeClient([])

    result = construct_qyir_from_query("每月买入过去60天涨幅最高的3个ETF", client=client)

    assert result.success is False
    assert result.clarification_requested is True
    assert result.errors[0]["path"] == "unsupported_semantics"
    assert client.prompts == []


def test_unsupported_semantics_guard_allows_single_asset_momentum_proxy():
    result = detect_unsupported_semantics("根据过去20个交易日涨幅做短周期动量策略，但不要满仓。")

    assert result.unsupported is False


def test_live_route_b_prefers_explicit_key_file(tmp_path, monkeypatch):
    key_file = tmp_path / "key.txt"
    key_file.write_text("file-key", encoding="utf-8")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "env-key")

    assert _read_api_key_file_first(key_file) == "file-key"


def test_live_route_b_uses_official_deepseek_defaults_and_aliases():
    assert DEFAULT_DEEPSEEK_BASE_URL == "https://api.deepseek.com"
    assert DEFAULT_DEEPSEEK_MODELS == ["deepseek-v4-flash"]
    assert _normalize_deepseek_model_name("deepseek-v4-flash") == "deepseek-v4-flash"
    assert _normalize_deepseek_model_name("deepseek-v4-pro") == "deepseek-v4-pro"
    assert _normalize_deepseek_model_name("deepseek-chat") == "deepseek-v4-flash"
    assert _normalize_deepseek_model_name("deepseek-reasoner") == "deepseek-v4-pro"
