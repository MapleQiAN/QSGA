"""Run a no-oracle deterministic slot-extraction variant for QSI-Bench.

This experiment does not use benchmark expected_slots to construct QYIR.
It extracts a small set of explicit slots from user_query, builds QYIR from
those predicted slots, and evaluates the output against the original gold slots.
The goal is to quantify how much the prototype degrades without oracle slots.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pandas as pd

from backtester.simple_backtester import run_backtest
from compiler.qyir_compiler import compile_qyir
from experiments.baselines import (
    DEFAULT_BENCHMARK_PATH,
    DEFAULT_DATA_PATH,
    BenchmarkRecord,
    MethodResult,
    build_qyir_from_record,
    clarification_result,
    expected_slots_match,
    load_benchmark,
    query_needs_clarification,
    results_to_csv,
)
from qyir.validator import validate_qyir
from verifier.risk_verifier import audit_risk
from verifier.safe_rejection import should_reject
from verifier.semantic_verifier import semantic_verify


METHOD_NAME = "qsga_no_oracle_slots"


def extract_slots_from_query(record: BenchmarkRecord) -> dict[str, Any]:
    """Extract explicit slots from user_query without reading expected_slots."""
    query = str(record["user_query"])
    slots: dict[str, Any] = {"safe_action": "generate"}

    family = _strategy_family(query)
    if family is not None:
        slots["strategy_family"] = family
        if family in {"rsi_reversion", "mean_reversion"}:
            slots["strategy_type"] = "mean_reversion"
        elif family == "momentum_rotation":
            slots["strategy_type"] = "momentum"
        else:
            slots["strategy_type"] = "trend_following"

    windows = _extract_windows(query)
    if windows:
        slots["fast_window"] = windows[0]
    if len(windows) >= 2:
        slots["slow_window"] = windows[1]
    elif "lookback_window" not in slots and windows:
        slots["lookback_window"] = windows[0]

    if any(token in query for token in ("低风险", "稳健", "保守", "适合新手", "稳一点")):
        slots["risk_preference"] = "low"
    if any(token in query for token in ("不要杠杆", "不加杠杆", "不用杠杆", "无杠杆")):
        slots["allow_leverage"] = False
    if any(token in query for token in ("不要做空", "不做空", "只做多")):
        slots["allow_short"] = False
    if any(token in query for token in ("不要满仓", "仓位小", "仓位不要太高")):
        slots["position_size"] = "small"
    if any(token in query for token in ("止损", "止盈")):
        slots["stop_loss_required"] = "止损" in query

    drawdown = _extract_percent_after(query, "回撤")
    if drawdown is not None:
        slots["max_drawdown_limit"] = drawdown

    if "纳斯达克" in query:
        slots["asset_hint"] = "nasdaq"
    elif "黄金" in query:
        slots["asset_hint"] = "gold_etf"
    elif "SPY" in query.upper() or "标普" in query or "S&P" in query.upper():
        slots["asset_hint"] = "spy"

    if any(token in query for token in ("参数你自己看着办", "差不多", "不要太激进", "风险别太大")):
        slots["safe_action"] = "clarify"
    if query_needs_clarification(query):
        slots["safe_action"] = "clarify"

    return slots


def run_no_oracle_method(record: BenchmarkRecord, price_data: pd.DataFrame) -> MethodResult:
    """Run QSGA from extracted slots and evaluate against gold slots."""
    expected_reject = bool(record["should_reject"])
    query = str(record["user_query"])
    decision = should_reject(query)
    if decision.rejected:
        return _result(
            record,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            end_to_end_success=expected_reject,
            errors=[decision.reason or "safe rejection"],
        )

    if expected_reject:
        return _result(
            record,
            rejected=False,
            schema_valid=False,
            semantic_consistent=False,
            compile_success=False,
            backtest_success=False,
            risk_violation=True,
            end_to_end_success=False,
            errors=["unsafe request was not rejected by rules"],
        )

    predicted_record = dict(record)
    predicted_record["expected_slots"] = extract_slots_from_query(record)
    if dict(predicted_record["expected_slots"]).get("safe_action") == "clarify":
        return clarification_result(record, METHOD_NAME)
    qyir = build_qyir_from_record(predicted_record)

    validation = validate_qyir(qyir)
    errors = [f"{issue.path}: {issue.message}" for issue in validation.issues]
    schema_valid = validation.valid
    semantic_consistent = schema_valid and expected_slots_match(qyir, record)

    if schema_valid:
        semantic = semantic_verify(query, qyir)
        semantic_consistent = semantic_consistent and semantic.passed
        errors.extend(f"{issue.path}: {issue.message}" for issue in semantic.issues)

    compile_success = False
    backtest_success = False
    risk_violation = False
    if schema_valid:
        compilation = compile_qyir(qyir, price_data)
        compile_success = compilation.success
        errors.extend(compilation.errors)
        if compilation.success and compilation.signals is not None:
            backtest = run_backtest(compilation.signals, qyir.get("risk_control", {}))
            backtest_success = backtest.success
            errors.extend(backtest.errors)
            if backtest.success:
                risk = audit_risk(qyir, backtest.metrics)
                risk_violation = any(issue.severity == "rejected" for issue in risk.issues)

    e2e = schema_valid and semantic_consistent and compile_success and backtest_success and not risk_violation
    return _result(
        record,
        rejected=False,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        end_to_end_success=e2e,
        errors=errors,
    )


def run_no_oracle(
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[MethodResult]:
    """Run no-oracle QSGA on all benchmark records."""
    price_data = pd.read_csv(data_path)
    return [run_no_oracle_method(record, price_data) for record in load_benchmark(benchmark_path)]


def _strategy_family(query: str) -> str | None:
    upper = query.upper()
    if "RSI" in upper or "超卖" in query or "均值回归" in query:
        return "rsi_reversion"
    if "MACD" in upper:
        return "macd_cross"
    if "EMA" in upper:
        return "ema_cross"
    if "动量" in query or "涨幅最高" in query or "轮动" in query:
        return "momentum_rotation"
    if "均线" in query or "MA" in upper:
        return "ma_cross"
    if "布林" in query:
        return "bollinger_reversion"
    return None


def _extract_windows(query: str) -> list[int]:
    windows = [int(value) for value in re.findall(r"(\d+)\s*(?:日|周)?(?:均线|EMA|MA)", query, re.IGNORECASE)]
    if not windows:
        windows = [int(value) for value in re.findall(r"(\d+)\s*(?:日|周)", query)]
    unique: list[int] = []
    for window in windows:
        normalized = window * 5 if "周" in query and window < 100 else window
        if 2 <= normalized <= 500 and normalized not in unique:
            unique.append(normalized)
    return unique[:2]


def _extract_percent_after(query: str, anchor: str) -> float | None:
    pattern = rf"{anchor}[^0-9]{{0,8}}(\d+(?:\.\d+)?)\s*%"
    match = re.search(pattern, query)
    if not match:
        return None
    return float(match.group(1)) / 100.0


def _result(
    record: BenchmarkRecord,
    *,
    rejected: bool,
    schema_valid: bool,
    semantic_consistent: bool,
    compile_success: bool,
    backtest_success: bool,
    risk_violation: bool,
    end_to_end_success: bool,
    errors: list[str],
) -> MethodResult:
    should_reject = bool(record["should_reject"])
    return MethodResult(
        case_id=str(record["id"]),
        category=str(record["category"]),
        method=METHOD_NAME,
        should_reject=should_reject,
        rejected=rejected,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=False,
        repair_success=False,
        safe_rejection_correct=(rejected == should_reject) if should_reject else not rejected,
        clarification_requested=False,
        clarification_correct=False,
        end_to_end_success=end_to_end_success,
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run no-oracle QSGA slot extraction experiment.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--output", default="experiments/results/no_oracle_results.csv")
    args = parser.parse_args(argv)

    results = run_no_oracle(args.benchmark, args.data)
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} no-oracle rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
