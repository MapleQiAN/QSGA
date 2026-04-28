"""Verification-guided repair loop for QYIR dictionaries."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from generator.llm_client import LLMClient
from repair.repair_operators import apply_rule_based_repairs
from repair.repair_prompt import build_repair_prompt


@dataclass(frozen=True)
class RepairTraceEntry:
    """One repair attempt and its verification outcome."""

    round: int
    violations_before: list[str]
    repair_action: str
    passed_after_repair: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "round": self.round,
            "violations_before": self.violations_before,
            "repair_action": self.repair_action,
            "passed_after_repair": self.passed_after_repair,
        }


@dataclass(frozen=True)
class RepairResult:
    """Result of a bounded QYIR repair loop."""

    success: bool
    qyir: dict[str, Any] | None
    errors: list[dict[str, str]] = field(default_factory=list)
    trace: list[RepairTraceEntry] = field(default_factory=list)

    def trace_dicts(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self.trace]


def repair_qyir(
    user_query: str,
    qyir: dict[str, Any],
    *,
    validator: Callable[[dict[str, Any]], Any],
    semantic_validator: Callable[[str, dict[str, Any]], Any],
    client: LLMClient | None = None,
    max_rounds: int = 2,
) -> RepairResult:
    """Repair QYIR with deterministic operators first, then optional LLM repair."""
    current = qyir
    trace: list[RepairTraceEntry] = []
    errors: list[dict[str, str]] = []

    for round_number in range(1, max_rounds + 1):
        violations = _collect_violations(user_query, current, validator, semantic_validator)
        if not violations:
            return RepairResult(success=True, qyir=current, trace=trace)

        candidate, actions = apply_rule_based_repairs(user_query, current, violations)
        if actions:
            action = " ".join(actions)
        elif client is not None:
            prompt = build_repair_prompt(user_query, current, violations)
            raw = client.generate(prompt)
            candidate, parse_error = _parse_json(raw)
            if parse_error is not None:
                errors = [parse_error]
                trace.append(
                    RepairTraceEntry(
                        round=round_number,
                        violations_before=_violation_messages(violations),
                        repair_action=parse_error["message"],
                        passed_after_repair=False,
                    )
                )
                current = current
                continue
            action = "LLM repaired QYIR from verification feedback."
        else:
            errors = _violations_to_errors(violations)
            break

        after_violations = _collect_violations(user_query, candidate, validator, semantic_validator)
        passed = not after_violations
        trace.append(
            RepairTraceEntry(
                round=round_number,
                violations_before=_violation_messages(violations),
                repair_action=action,
                passed_after_repair=passed,
            )
        )
        current = candidate
        errors = _violations_to_errors(after_violations)
        if passed:
            return RepairResult(success=True, qyir=current, trace=trace)

    return RepairResult(success=False, qyir=current, errors=errors, trace=trace)


def _collect_violations(
    user_query: str,
    qyir: dict[str, Any],
    validator: Callable[[dict[str, Any]], Any],
    semantic_validator: Callable[[str, dict[str, Any]], Any],
) -> list[dict[str, str]]:
    validation = validator(qyir)
    if not validation.valid:
        return _issues_to_violations(validation.issues)

    semantic_validation = semantic_validator(user_query, qyir)
    if not semantic_validation.valid:
        return _issues_to_violations(semantic_validation.issues)

    return []


def _issues_to_violations(issues: list[Any]) -> list[dict[str, str]]:
    return [
        {
            "path": str(getattr(issue, "path", "unknown")),
            "message": str(getattr(issue, "message", issue)),
        }
        for issue in issues
    ]


def _violation_messages(violations: list[dict[str, str]]) -> list[str]:
    return [violation["message"] for violation in violations]


def _violations_to_errors(violations: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{"path": violation["path"], "message": violation["message"]} for violation in violations]


def _parse_json(raw: str) -> tuple[dict[str, Any], dict[str, str] | None]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {}, {"path": "json", "message": f"Invalid JSON from repair LLM: {exc}"}

    if not isinstance(data, dict):
        return {}, {"path": "json", "message": "Repair LLM output must be a JSON object"}
    return data, None

