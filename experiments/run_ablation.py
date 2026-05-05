"""Run QSGA ablation variants on QSI-Bench."""

from __future__ import annotations

import argparse

from experiments.baselines import DEFAULT_BENCHMARK_PATH, DEFAULT_DATA_PATH, load_benchmark, results_to_csv, run_methods


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run QSGA ablation experiments.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--output", default="experiments/results/ablation_results.csv")
    args = parser.parse_args(argv)

    records = load_benchmark(args.benchmark)
    results = run_methods(
        records,
        ["qsga_full", "wo_qyir", "wo_semantic_verification", "wo_risk_audit", "wo_repair", "wo_safe_rejection"],
        data_path=args.data,
    )
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} ablation rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
