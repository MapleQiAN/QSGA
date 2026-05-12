"""Analyze live QYIR failure types for Route B failure-reduction tables."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


FAILURE_TYPES = [
    "success",
    "parse_failure",
    "schema_failure",
    "unsupported_indicator",
    "alias_failure",
    "type_error",
    "semantic_mismatch",
    "risk_slot_missing",
    "compilation_failure",
    "execution_failure",
    "risk_violation",
    "unsafe_intent_failure",
    "clarification_failure",
    "unknown_failure",
]


@dataclass(frozen=True)
class FailureClassification:
    """Primary failure label plus a concise reason."""

    failure_type: str
    stage: str
    reason: str


def classify_failure(row: pd.Series) -> FailureClassification:
    """Classify one MethodResult row into the Route B failure taxonomy."""
    errors = str(row.get("errors", "") or "")
    errors_lower = errors.lower()
    should_reject = _bool(row.get("should_reject"))
    rejected = _bool(row.get("rejected"))
    schema_valid = _bool(row.get("schema_valid"))
    semantic_consistent = _bool(row.get("semantic_consistent"))
    compile_success = _bool(row.get("compile_success"))
    backtest_success = _bool(row.get("backtest_success"))
    risk_violation = _bool(row.get("risk_violation"))
    clarification_requested = _bool(row.get("clarification_requested"))
    clarification_correct = _bool(row.get("clarification_correct"))
    end_to_end_success = _bool(row.get("end_to_end_success"))

    if end_to_end_success:
        return FailureClassification("success", "success", "end_to_end_success=true")
    if should_reject and not rejected:
        return FailureClassification("unsafe_intent_failure", "safety", _reason(errors, "unsafe request was not rejected"))
    if clarification_requested and not clarification_correct:
        return FailureClassification("clarification_failure", "clarification", _reason(errors, "clarification was incorrect"))
    if _contains_any(errors_lower, ("invalid json", "json:", "must be a json object")):
        return FailureClassification("parse_failure", "parse", _reason(errors, "invalid or non-object JSON"))
    if _contains_any(errors_lower, ("unsupported indicator", "unsupported or unknown indicator", "stochastic", "kdj", "atr", "obv")):
        return FailureClassification("unsupported_indicator", "schema", _reason(errors, "unsupported indicator"))
    if _contains_any(errors_lower, ("unknown alias", "references unknown alias", "unknown alias in rule operand")):
        return FailureClassification("alias_failure", "reference", _reason(errors, "unresolved alias reference"))
    if _contains_any(errors_lower, ("invalid rule operand", "requires 'right'", "requires both", "does not use", "must be int", "must be float")):
        return FailureClassification("type_error", "type", _reason(errors, "invalid rule or parameter type"))
    if _contains_any(errors_lower, ("risk_control.stop_loss", "stop_loss_required", "does not set stop_loss")):
        return FailureClassification("risk_slot_missing", "risk", _reason(errors, "explicit risk slot missing"))
    if not schema_valid:
        return FailureClassification("schema_failure", "schema", _reason(errors, "schema validation failed"))
    if not semantic_consistent:
        return FailureClassification("semantic_mismatch", "semantic", _reason(errors, "semantic consistency failed"))
    if not compile_success:
        return FailureClassification("compilation_failure", "compile", _reason(errors, "compilation failed"))
    if not backtest_success:
        return FailureClassification("execution_failure", "execution", _reason(errors, "backtest execution failed"))
    if risk_violation:
        return FailureClassification("risk_violation", "risk", _reason(errors, "risk audit violation"))
    return FailureClassification("unknown_failure", "unknown", _reason(errors, "failure did not match known taxonomy"))


def analyze_failures(
    results_csv: str | Path,
    *,
    output_csv: str | Path,
    table_output: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Write per-row failure classifications and markdown summary table."""
    results = pd.read_csv(results_csv)
    classified_rows = []
    for _, row in results.iterrows():
        classification = classify_failure(row)
        classified = row.to_dict()
        classified.update(
            {
                "failure_type": classification.failure_type,
                "failure_stage": classification.stage,
                "failure_reason": classification.reason,
            }
        )
        classified_rows.append(classified)

    breakdown = pd.DataFrame(classified_rows)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    breakdown.to_csv(output_path, index=False)

    summary = summarize_breakdown(breakdown)
    table_path = Path(table_output)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(_summary_to_markdown(summary), encoding="utf-8")
    return breakdown, summary


def summarize_breakdown(breakdown: pd.DataFrame) -> pd.DataFrame:
    """Aggregate failure counts by method and failure type."""
    rows = []
    total_by_method = breakdown.groupby("method").size().to_dict()
    for (method, failure_type), group in breakdown.groupby(["method", "failure_type"], sort=False):
        total = int(total_by_method[method])
        example = group.iloc[0]
        rows.append(
            {
                "Method": method,
                "Failure Type": failure_type,
                "Count": int(len(group)),
                "Percentage": len(group) / total if total else 0.0,
                "Representative Case": str(example.get("case_id", "")),
                "Representative Reason": str(example.get("failure_reason", ""))[:120],
            }
        )
    order = {failure_type: index for index, failure_type in enumerate(FAILURE_TYPES)}
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary["_order"] = summary["Failure Type"].map(order).fillna(len(order))
        summary = summary.sort_values(["Method", "_order", "Failure Type"]).drop(columns=["_order"])
    return summary


def _summary_to_markdown(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "| Method | Failure Type | Count | Percentage | Representative Case | Representative Reason |\n| --- | --- | ---: | ---: | --- | --- |\n"
    columns = ["Method", "Failure Type", "Count", "Percentage", "Representative Case", "Representative Reason"]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for _, row in summary[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if column == "Percentage":
                values.append(f"{float(value):.3f}")
            else:
                values.append(str(value).replace("\n", " ").replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    if pd.isna(value):
        return False
    return bool(value)


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)


def _reason(errors: str, fallback: str) -> str:
    text = str(errors or "").strip()
    return text if text else fallback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze Route B live QYIR failure breakdown.")
    parser.add_argument("--results", default="experiments/results/live_qyir_80_results.csv")
    parser.add_argument("--output", default="experiments/results/live_failure_breakdown.csv")
    parser.add_argument("--table-output", default="experiments/tables/live_failure_breakdown.md")
    args = parser.parse_args(argv)

    breakdown, summary = analyze_failures(args.results, output_csv=args.output, table_output=args.table_output)
    print(f"Wrote {len(breakdown)} classified rows to {args.output}")
    print(f"Wrote {len(summary)} summary rows to {args.table_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
