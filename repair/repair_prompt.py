"""Prompt construction for LLM-based QYIR repair."""

from __future__ import annotations

import json
from typing import Any


def build_repair_prompt(
    user_query: str,
    qyir: dict[str, Any],
    violations: list[dict[str, Any]],
) -> str:
    """Build a repair prompt that asks the LLM for corrected QYIR JSON only."""
    qyir_json = json.dumps(qyir, ensure_ascii=False, indent=2)
    violations_json = json.dumps(violations, ensure_ascii=False, indent=2)
    return (
        "The generated QYIR failed verification.\n\n"
        "Original user query:\n"
        f"{user_query}\n\n"
        "Current QYIR:\n"
        f"{qyir_json}\n\n"
        "Violations:\n"
        f"{violations_json}\n\n"
        "Please repair the QYIR while preserving the user's original intent.\n\n"
        "Requirements:\n"
        "1. Output valid JSON only.\n"
        "2. Do not output Python code.\n"
        "3. Fix all listed violations.\n"
        "4. Keep the strategy within supported QYIR schema."
    )

