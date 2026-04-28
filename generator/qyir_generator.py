"""Chinese query to validated QYIR generation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from generator.llm_client import LLMClient, OpenAILLMClient
from generator.prompt import build_qyir_prompt


@dataclass
class GenerationResult:
    """Structured result for QYIR generation."""

    success: bool
    qyir: dict[str, Any] | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    attempts: int = 0


def _issue(path: str, message: str) -> dict[str, str]:
    return {"path": path, "message": message}


def _parse_json(raw: str) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, _issue("json", f"Invalid JSON from LLM: {exc}")

    if not isinstance(data, dict):
        return None, _issue("json", "LLM output must be a JSON object")
    return data, None


def generate_qyir(
    query: str,
    client: LLMClient | None = None,
    max_retries: int = 2,
    validator: Callable[[dict[str, Any]], Any] | None = None,
) -> GenerationResult:
    """Generate, parse, and validate QYIR from a Chinese natural-language query."""
    if not query.strip():
        return GenerationResult(
            success=False,
            errors=[_issue("query", "Query must not be empty")],
            attempts=0,
        )

    llm = client if client is not None else OpenAILLMClient()
    validate = validator if validator is not None else _load_qyir_validator()
    last_errors: list[dict[str, str]] = []
    feedback: str | None = None

    for attempt in range(1, max_retries + 2):
        prompt = build_qyir_prompt(query, feedback=feedback)
        raw = llm.generate(prompt)
        data, parse_error = _parse_json(raw)
        if parse_error is not None:
            last_errors = [parse_error]
            feedback = parse_error["message"]
            continue

        validation = validate(data)
        if validation.valid:
            return GenerationResult(success=True, qyir=data, attempts=attempt)

        last_errors = [_issue(issue.path, issue.message) for issue in validation.issues]
        feedback = "; ".join(f"{error['path']}: {error['message']}" for error in last_errors)

    return GenerationResult(success=False, errors=last_errors, attempts=max_retries + 1)


def _load_qyir_validator() -> Callable[[dict[str, Any]], Any]:
    from qyir.validator import validate_qyir

    return validate_qyir
