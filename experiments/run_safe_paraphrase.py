"""Evaluate safe-rejection rules on unsafe paraphrases and boundary-safe requests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from verifier.safe_rejection import should_reject


DEFAULT_BENCHMARK = Path("benchmark/unsafe_paraphrase_bench.jsonl")
DEFAULT_RESULTS = Path("experiments/results/safe_paraphrase_results.csv")
DEFAULT_METRICS = Path("experiments/results/safe_paraphrase_metrics.csv")


def load_cases(path: str | Path = DEFAULT_BENCHMARK) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_cases(cases: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for case in cases:
        decision = should_reject(str(case["user_query"]))
        expected = bool(case["should_reject"])
        actual = bool(decision.rejected)
        rows.append(
            {
                "id": case["id"],
                "category": case["category"],
                "user_query": case["user_query"],
                "should_reject": expected,
                "rejected": actual,
                "correct": expected == actual,
                "false_positive": actual and not expected,
                "false_negative": expected and not actual,
                "detected_category": decision.category,
                "pattern": decision.pattern,
                "reason": decision.reason,
            }
        )
    return pd.DataFrame(rows)


def compute_metrics(results: pd.DataFrame) -> pd.DataFrame:
    unsafe = results[results["should_reject"] == True]  # noqa: E712
    safe = results[results["should_reject"] == False]  # noqa: E712
    rows = [
        {
            "metric": "total",
            "value": float(len(results)),
        },
        {
            "metric": "accuracy",
            "value": float(results["correct"].astype(bool).mean()) if len(results) else 0.0,
        },
        {
            "metric": "false_positive_rate",
            "value": float(safe["false_positive"].astype(bool).mean()) if len(safe) else 0.0,
        },
        {
            "metric": "false_negative_rate",
            "value": float(unsafe["false_negative"].astype(bool).mean()) if len(unsafe) else 0.0,
        },
        {
            "metric": "unsafe_acceptance_rate",
            "value": float((unsafe["rejected"] == False).mean()) if len(unsafe) else 0.0,  # noqa: E712
        },
    ]
    return pd.DataFrame(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate safe-rejection paraphrase coverage.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK))
    parser.add_argument("--output", default=str(DEFAULT_RESULTS))
    parser.add_argument("--metrics-output", default=str(DEFAULT_METRICS))
    args = parser.parse_args(argv)

    results = evaluate_cases(load_cases(args.benchmark))
    metrics = compute_metrics(results)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    metrics.to_csv(args.metrics_output, index=False)
    print(metrics.to_string(index=False))
    print(f"Wrote results to {args.output}")
    print(f"Wrote metrics to {args.metrics_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
