"""Evaluate the deterministic Route B ambiguity guard on QSI-Bench."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qsgi.construction import detect_ambiguous_intent


DEFAULT_BENCHMARK_PATH = ROOT / "benchmark" / "qsi_bench_v1.jsonl"


def evaluate_ambiguity_guard(benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH) -> pd.DataFrame:
    """Return per-case ambiguity-guard decisions."""
    rows = []
    for line in Path(benchmark_path).read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        result = detect_ambiguous_intent(str(record["user_query"]))
        expected = str(record["category"]) == "ambiguous_intent"
        rows.append(
            {
                "case_id": record["id"],
                "category": record["category"],
                "expected_clarify": expected,
                "guard_clarify": result.clarify,
                "correct": result.clarify == expected,
                "missing_slots": ",".join(result.missing_slots),
                "reason": result.reason,
            }
        )
    return pd.DataFrame(rows)


def write_summary(results: pd.DataFrame, output_path: str | Path) -> None:
    """Write a compact markdown summary table."""
    total = len(results)
    ambiguous = results[results["expected_clarify"]]
    non_ambiguous = results[~results["expected_clarify"]]
    true_positive = int((ambiguous["guard_clarify"] == True).sum())  # noqa: E712
    false_positive = int((non_ambiguous["guard_clarify"] == True).sum())  # noqa: E712
    rows = [
        ["ambiguous_recall", f"{true_positive}/{len(ambiguous)}", true_positive / len(ambiguous) if len(ambiguous) else 0.0],
        ["non_ambiguous_false_positive", f"{false_positive}/{len(non_ambiguous)}", false_positive / len(non_ambiguous) if len(non_ambiguous) else 0.0],
        ["overall_accuracy", f"{int(results['correct'].sum())}/{total}", float(results["correct"].mean()) if total else 0.0],
    ]
    lines = ["| Metric | Count | Rate |", "|---|---:|---:|"]
    for metric, count, rate in rows:
        lines.append(f"| {metric} | {count} | {rate:.3f} |")
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Route B ambiguity guard.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--output", default="experiments/results/route_b_ambiguity_guard_check.csv")
    parser.add_argument("--table-output", default="experiments/tables/route_b_ambiguity_guard_check.md")
    args = parser.parse_args(argv)

    results = evaluate_ambiguity_guard(args.benchmark)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output, index=False)
    write_summary(results, args.table_output)
    print(f"Wrote {len(results)} ambiguity-guard rows to {args.output}")
    print(f"Wrote ambiguity-guard summary to {args.table_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

