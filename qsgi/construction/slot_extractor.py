"""Structured slot extraction for Route B NL-to-QYIR construction."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from generator.llm_client import LLMClient
from qsgi.construction.slot_schema import StrategySlotSpec


SLOT_SYSTEM_PROMPT = (
    "You are a quantitative strategy slot extractor. "
    "Extract strict json slots only. Do not write QYIR, code, markdown, or prose."
)


@dataclass(frozen=True)
class SlotExtractionResult:
    """Result of structured slot extraction."""

    success: bool
    slots: StrategySlotSpec | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    attempts: int = 0
    raw_outputs: list[str] = field(default_factory=list)


def build_slot_extraction_prompt(query: str, feedback: str | None = None) -> str:
    """Build a JSON-only prompt for StrategySlotSpec extraction."""
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\nPrevious slot JSON failed validation. Fix only invalid fields.\n"
            f"Validation feedback: {feedback}\n"
        )
    return f"""Extract explicit strategy slots from the user request.

User request:
{query}
{feedback_block}
Rules:
- Return one strict JSON object only.
- Do not output QYIR.
- Do not output Python or markdown.
- Use strategy_family: trend_following, mean_reversion, momentum, breakout, risk_controlled, or unknown.
- Use indicators only from: SMA, EMA, RSI, MACD, BOLLINGER, UNKNOWN.
- Use operators only from: cross_over, cross_under, greater_than, less_than, between, stop_loss, take_profit, unknown.
- If the request is ambiguous, set safe_action to "clarify" and fill ambiguity.
- If the request is unsafe or unsupported, set safe_action to "reject".
- Do not clarify only because symbol, timeframe, exit logic, or risk constraints are omitted.
- Use defaults for omitted symbol/timeframe/risk: SPY, daily, position_size 0.5, leverage 1.0, allow_short false.
- Map common asset hints: 黄金ETF/gold ETF to GLD, 标普/S&P/SPY to SPY, 纳指/Nasdaq/QQQ to QQQ.
- For RSI mean reversion with no exit threshold, use exit_logic greater_than RSI 70.
- If an explicit risk phrase says no leverage, set risk_constraints.leverage to 1.0.
- If an explicit risk phrase says no short selling, set risk_constraints.allow_short to false.

Required JSON shape:
{{
  "strategy_family": "trend_following",
  "market_scope": {{
    "symbol": "SPY",
    "asset_type": "etf",
    "timeframe": "daily"
  }},
  "indicators": [
    {{"name": "SMA", "window": 20, "role": "fast"}},
    {{"name": "SMA", "window": 60, "role": "slow"}}
  ],
  "entry_logic": {{
    "operator": "cross_over",
    "left": "sma20",
    "right": "sma60",
    "natural_language": "20-day SMA crosses above 60-day SMA"
  }},
  "exit_logic": {{
    "operator": "cross_under",
    "left": "sma20",
    "right": "sma60",
    "natural_language": "20-day SMA crosses below 60-day SMA"
  }},
  "risk_constraints": {{
    "position_size": 0.5,
    "max_drawdown_limit": 0.2,
    "stop_loss": 0.1,
    "take_profit": null,
    "allow_short": false,
    "leverage": 1.0
  }},
  "ambiguity": {{
    "requires_clarification": false,
    "missing_slots": [],
    "ambiguous_phrases": []
  }},
  "safe_action": "construct"
}}"""


def extract_slots(
    query: str,
    *,
    client: LLMClient,
    max_retries: int = 1,
) -> SlotExtractionResult:
    """Extract StrategySlotSpec using an LLM client and Pydantic validation."""
    if not query.strip():
        return SlotExtractionResult(
            success=False,
            errors=[{"path": "query", "message": "Query must not be empty."}],
            attempts=0,
        )

    raw_outputs: list[str] = []
    errors: list[dict[str, str]] = []
    feedback: str | None = None
    for attempt in range(1, max_retries + 2):
        raw = client.generate(build_slot_extraction_prompt(query, feedback=feedback))
        raw_outputs.append(raw)
        data, parse_error = _parse_json(raw)
        if parse_error is not None:
            errors = [parse_error]
            feedback = parse_error["message"]
            continue
        try:
            slots = StrategySlotSpec.model_validate(data)
        except Exception as exc:
            errors = [{"path": "slot_schema", "message": str(exc)}]
            feedback = str(exc)
            continue
        return SlotExtractionResult(
            success=True,
            slots=slots,
            attempts=attempt,
            raw_outputs=raw_outputs,
        )

    return SlotExtractionResult(
        success=False,
        errors=errors,
        attempts=max_retries + 1,
        raw_outputs=raw_outputs,
    )


def _parse_json(raw: str) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, {"path": "json", "message": f"Invalid slot JSON from LLM: {exc}"}
    if not isinstance(parsed, dict):
        return None, {"path": "json", "message": "Slot extractor output must be a JSON object."}
    return parsed, None
