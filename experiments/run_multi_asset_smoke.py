"""Run synthetic multi-asset and multi-period smoke checks.

This is an execution-robustness check only. It does not claim market
performance, cross-market profitability, or portfolio support.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from backtester.simple_backtester import run_backtest
from compiler.generate_sample_data import generate_spy_sample
from compiler.qyir_compiler import compile_qyir
from experiments.baselines import build_qyir_from_record, load_benchmark
from verifier.risk_verifier import audit_risk


DEFAULT_OUTPUT = Path("experiments/results/multi_asset_smoke_results.csv")


@dataclass(frozen=True)
class SmokeResult:
    case_id: str
    symbol: str
    period: str
    compile_success: bool
    backtest_success: bool
    risk_audit_runnable: bool
    end_to_end_success: bool
    errors: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "symbol": self.symbol,
            "period": self.period,
            "compile_success": self.compile_success,
            "backtest_success": self.backtest_success,
            "risk_audit_runnable": self.risk_audit_runnable,
            "end_to_end_success": self.end_to_end_success,
            "errors": "; ".join(self.errors),
        }


def run_multi_asset_smoke(
    *,
    benchmark_path: str | Path = "benchmark/qsi_bench_v1.jsonl",
    case_id: str = "qsi_001",
) -> list[SmokeResult]:
    records = {str(record["id"]): record for record in load_benchmark(benchmark_path)}
    if case_id not in records:
        raise ValueError(f"Unknown case_id: {case_id}")
    base_qyir = build_qyir_from_record(records[case_id])
    specs = [
        ("SPY", "2020-2024", "2019-06-01", "2024-12-31", 42),
        ("QQQ", "2020-2024", "2019-06-01", "2024-12-31", 84),
        ("GLD", "2020-2024", "2019-06-01", "2024-12-31", 126),
        ("SPY", "2021-2023", "2020-06-01", "2023-12-31", 43),
        ("QQQ", "2021-2023", "2020-06-01", "2023-12-31", 85),
    ]
    results: list[SmokeResult] = []
    for symbol, period, start, end, seed in specs:
        qyir = json.loads(json.dumps(base_qyir, ensure_ascii=False))
        qyir["market"]["symbol"] = symbol
        qyir["market"]["start_date"] = "2020-01-01" if period == "2020-2024" else "2021-01-01"
        qyir["market"]["end_date"] = "2024-12-31" if period == "2020-2024" else "2023-12-31"
        data = generate_spy_sample(start=start, end=end, seed=seed)
        results.append(_run_one(case_id, symbol, period, qyir, data))
    return results


def write_smoke_results(results: list[SmokeResult], output_path: str | Path = DEFAULT_OUTPUT) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result.to_row() for result in results]).to_csv(output, index=False)


def _run_one(case_id: str, symbol: str, period: str, qyir: dict[str, Any], data: pd.DataFrame) -> SmokeResult:
    errors: list[str] = []
    compilation = compile_qyir(qyir, data)
    compile_success = compilation.success
    errors.extend(compilation.errors)
    backtest_success = False
    risk_audit_runnable = False

    if compilation.success and compilation.signals is not None:
        backtest = run_backtest(compilation.signals, qyir.get("risk_control", {}))
        backtest_success = backtest.success
        errors.extend(backtest.errors)
        if backtest.success:
            try:
                audit_risk(qyir, backtest.metrics)
                risk_audit_runnable = True
            except Exception as exc:
                errors.append(f"risk_audit_error: {type(exc).__name__}: {exc}")

    return SmokeResult(
        case_id=case_id,
        symbol=symbol,
        period=period,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_audit_runnable=risk_audit_runnable,
        end_to_end_success=compile_success and backtest_success and risk_audit_runnable,
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run synthetic multi-asset smoke checks.")
    parser.add_argument("--benchmark", default="benchmark/qsi_bench_v1.jsonl")
    parser.add_argument("--case-id", default="qsi_001")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)

    results = run_multi_asset_smoke(benchmark_path=args.benchmark, case_id=args.case_id)
    write_smoke_results(results, args.output)
    print(f"Wrote {len(results)} smoke rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
