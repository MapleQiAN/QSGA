"""Route B construction pipeline from natural-language query to QYIR."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from generator.llm_client import LLMClient
from qsgi.construction.ambiguity_guard import detect_ambiguous_intent
from qsgi.construction.canonicalizer import CanonicalizationEvent
from qsgi.construction.qyir_builder import build_qyir_from_slots
from qsgi.construction.slot_extractor import SlotExtractionResult, extract_slots
from qsgi.construction.slot_schema import StrategySlotSpec
from qsgi.construction.unsupported_semantics import detect_unsupported_semantics
from verifier.safe_rejection import should_reject


@dataclass(frozen=True)
class RouteBConstructionResult:
    """End-to-end Route B construction result before backend scoring."""

    success: bool
    qyir: dict[str, Any] | None = None
    slots: StrategySlotSpec | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    attempts: int = 0
    rejected: bool = False
    rejection_reason: str | None = None
    clarification_requested: bool = False
    canonicalization_log: list[CanonicalizationEvent] = field(default_factory=list)
    extraction: SlotExtractionResult | None = None


def construct_qyir_from_query(
    query: str,
    *,
    client: LLMClient,
    max_retries: int = 1,
) -> RouteBConstructionResult:
    """Run safe rejection, slot extraction, deterministic builder, and validation."""
    rejection = should_reject(query)
    if rejection.rejected:
        reason = rejection.reason or "Unsafe request detected."
        return RouteBConstructionResult(
            success=False,
            rejected=True,
            rejection_reason=reason,
            errors=[{"path": "safe_rejection", "message": reason}],
        )

    unsupported = detect_unsupported_semantics(query)
    if unsupported.unsupported:
        return RouteBConstructionResult(
            success=False,
            clarification_requested=True,
            errors=[{"path": "unsupported_semantics", "message": unsupported.reason}],
        )

    ambiguity = detect_ambiguous_intent(query)
    if ambiguity.clarify:
        missing = ", ".join(ambiguity.missing_slots)
        return RouteBConstructionResult(
            success=False,
            clarification_requested=True,
            errors=[{"path": "ambiguity_guard", "message": f"Clarification required: {missing}."}],
        )

    extraction = extract_slots(query, client=client, max_retries=max_retries)
    if not extraction.success or extraction.slots is None:
        return RouteBConstructionResult(
            success=False,
            errors=extraction.errors,
            attempts=extraction.attempts,
            extraction=extraction,
        )

    slots = extraction.slots
    if slots.safe_action == "reject":
        return RouteBConstructionResult(
            success=False,
            slots=slots,
            rejected=True,
            rejection_reason="Slot extractor requested rejection.",
            attempts=extraction.attempts,
            errors=[{"path": "safe_action", "message": "Slot extractor requested rejection."}],
            extraction=extraction,
        )
    defaulted_clarification = slots.safe_action == "clarify" and _clarification_can_be_defaulted(slots)
    if slots.safe_action == "clarify" and not defaulted_clarification:
        missing = ", ".join(slots.ambiguity.missing_slots) or "missing or ambiguous slots"
        return RouteBConstructionResult(
            success=False,
            slots=slots,
            clarification_requested=True,
            attempts=extraction.attempts,
            errors=[{"path": "safe_action", "message": f"Clarification required: {missing}."}],
            extraction=extraction,
        )

    builder_slots = slots.model_copy(update={"safe_action": "construct"}) if defaulted_clarification else slots
    built = build_qyir_from_slots(builder_slots)
    return RouteBConstructionResult(
        success=built.success,
        qyir=built.qyir,
        slots=builder_slots,
        errors=built.errors,
        attempts=extraction.attempts,
        canonicalization_log=built.canonicalization_log,
        extraction=extraction,
    )


def _clarification_can_be_defaulted(slots: StrategySlotSpec) -> bool:
    defaultable = {
        "symbol",
        "asset_type",
        "timeframe",
        "market_scope",
        "market_scope.symbol",
        "market_scope.asset_type",
        "market_scope.timeframe",
        "exit_logic",
        "risk_constraints",
    }
    missing = {item.strip() for item in slots.ambiguity.missing_slots}
    if missing == {"entry_threshold"}:
        return _can_default_entry_threshold(slots)
    if not missing or not missing.issubset(defaultable):
        return False
    if slots.strategy_family not in {"trend_following", "mean_reversion"}:
        return False
    has_supported_indicator = any(indicator.name != "UNKNOWN" for indicator in slots.indicators)
    has_entry = slots.entry_logic.operator not in {None, "unknown"} and slots.entry_logic.left is not None
    has_strategy_default = slots.strategy_family in {"trend_following", "mean_reversion"}
    return has_supported_indicator and (has_entry or has_strategy_default)


def _can_default_entry_threshold(slots: StrategySlotSpec) -> bool:
    """Allow MA-deviation style requests to use builder-level v1 approximation."""
    has_supported_indicator = any(indicator.name != "UNKNOWN" for indicator in slots.indicators)
    has_entry = (
        slots.entry_logic.operator not in {None, "unknown"}
        and slots.entry_logic.left is not None
        and slots.entry_logic.right is not None
    )
    has_exit = (
        slots.exit_logic.operator not in {None, "unknown"}
        and slots.exit_logic.left is not None
        and slots.exit_logic.right is not None
    )
    return slots.strategy_family == "mean_reversion" and has_supported_indicator and has_entry and has_exit
