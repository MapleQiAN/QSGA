"""Run the full QSGA method on QSI-Bench and save per-case results."""

from __future__ import annotations

import argparse

from experiments.baselines import DEFAULT_BENCHMARK_PATH, DEFAULT_DATA_PATH, load_benchmark, results_to_csv, run_methods


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run QSGA-Full on QSI-Bench.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--output", default="experiments/results/full_results.csv")
    args = parser.parse_args(argv)

    records = load_benchmark(args.benchmark)
    results = run_methods(records, ["qsga_full"], data_path=args.data)
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} benchmark rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

