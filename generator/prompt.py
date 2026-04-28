"""Prompt construction for generating constrained QYIR JSON."""

from __future__ import annotations

from qyir.constants import IndicatorType, RuleType


def build_qyir_prompt(query: str, feedback: str | None = None) -> str:
    """Build a strict JSON-only prompt for QYIR generation."""
    indicators = ", ".join(indicator.value for indicator in IndicatorType)
    rules = ", ".join(rule.value for rule in RuleType)

    feedback_block = ""
    if feedback:
        feedback_block = (
            "\nPrevious output failed validation. Fix only the JSON and try again.\n"
            f"Validation feedback: {feedback}\n"
        )

    return f"""You generate QYIR v1 JSON for quantitative trading strategies.

User query:
{query}
{feedback_block}
Output rules:
- Return JSON only. Do not include markdown, code fences, comments, explanations, or prose.
- Do not output Python code or any executable code.
- Use only supported indicators: {indicators}.
- Use only supported rule types: {rules}.
- Include a risk_control object with position_size, stop_loss, take_profit, max_drawdown_limit, allow_short, and leverage.
- Use leverage 1.0. Do not promise profit, return, win rate, alpha, or guaranteed performance.
- Keep strategy_name lowercase snake_case.
- Use QYIR version "1.0" and timeframe "1d".
- Rule references must point to indicator aliases defined in indicators.

Required JSON shape:
{{
  "strategy_name": "lowercase_snake_case",
  "description": "short neutral description without return promises",
  "version": "1.0",
  "market": {{
    "symbol": "SPY",
    "timeframe": "1d",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31"
  }},
  "indicators": [
    {{"name": "SMA", "params": {{"window": 20}}, "alias": "sma_20"}}
  ],
  "entry_rules": [
    {{"type": "greater_than", "left": "sma_20", "right": 100}}
  ],
  "exit_rules": [
    {{"type": "less_than", "left": "sma_20", "right": 100}}
  ],
  "risk_control": {{
    "position_size": 0.5,
    "stop_loss": 0.1,
    "take_profit": null,
    "max_drawdown_limit": 0.2,
    "allow_short": false,
    "leverage": 1.0
  }}
}}"""
