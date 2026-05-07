"""Compute slot-level diagnostics for the deterministic no-oracle extractor."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from experiments.baselines import DEFAULT_BENCHMARK_PATH
from experiments.run_no_oracle import extract_slots_from_query


SLOT_GROUPS: dict[str, set[str]] = {
    "market": {"frequency", "asset_hint"},
    "indicators": {
        "strategy_type",
        "strategy_family",
        "fast_window",
        "slow_window",
        "lookback_window",
        "window",
        "num_std",
    },
    "entry_rules": {
        "entry_signal",
        "entry_condition",
        "entry_threshold",
        "down_days",
        "deviation_threshold",
    },
    "exit_rules": {
        "exit_signal",
        "exit_condition",
        "exit_threshold",
        "take_profit",
    },
    "risk_control": {
        "risk_preference",
        "allow_leverage",
        "allow_short",
        "position_size",
        "max_position_weight",
        "stop_loss_required",
        "stop_loss",
        "max_drawdown_limit",
        "novice_friendly",
        "cash_when_no_signal",
    },
}


def load_records(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def slot_pairs(slots: dict[str, Any], keys: set[str]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for key in keys:
        if key in slots:
            pairs.add((key, _normalize(slots[key])))
    return pairs


def _normalize(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value).lower()


def compute_slot_diagnostics(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for record in records:
        expected = dict(record.get("expected_slots") or {})
        if bool(record.get("should_reject")) or expected.get("safe_action") != "generate":
            continue

        predicted = extract_slots_from_query(record)
        for group, keys in SLOT_GROUPS.items():
            expected_pairs = slot_pairs(expected, keys)
            predicted_pairs = slot_pairs(predicted, keys)
            counts[group]["tp"] += len(expected_pairs & predicted_pairs)
            counts[group]["fp"] += len(predicted_pairs - expected_pairs)
            counts[group]["fn"] += len(expected_pairs - predicted_pairs)

    rows: list[dict[str, Any]] = []
    for group in SLOT_GROUPS:
        tp = counts[group]["tp"]
        fp = counts[group]["fp"]
        fn = counts[group]["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append(
            {
                "slot_group": group,
                "true_positive": tp,
                "false_positive": fp,
                "false_negative": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# No-Oracle Slot Diagnostics",
        "",
        "Computed over constructible QSI-Bench v1 records whose expected `safe_action` is `generate`.",
        "",
        "| Slot Group | TP | FP | FN | Precision | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {slot_group} | {true_positive} | {false_positive} | {false_negative} | "
            "{precision:.3f} | {recall:.3f} | {f1:.3f} |".format(**row)
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute no-oracle slot-level diagnostics.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--csv-output", default="experiments/results/no_oracle_slot_diagnostics.csv")
    parser.add_argument("--md-output", default="experiments/tables/no_oracle_slot_diagnostics.md")
    args = parser.parse_args(argv)

    rows = compute_slot_diagnostics(load_records(args.benchmark))
    write_csv(rows, args.csv_output)
    write_markdown(rows, args.md_output)
    print(f"Wrote {len(rows)} slot-diagnostic rows to {args.csv_output} and {args.md_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
