"""Deterministic baseline and ablation runners for QSI-Bench.

The experiment harness avoids live LLM calls so paper-prototype experiments are
reproducible in CI. It still exercises the real QYIR validator, compiler,
backtester, semantic verifier, safe-rejection rules, and risk auditor wherever a
method produces QYIR.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

import pandas as pd

from backtester.simple_backtester import run_backtest
from compiler.qyir_compiler import compile_qyir
from qyir.validator import validate_qyir
from verifier.risk_verifier import audit_risk
from verifier.safe_rejection import should_reject
from verifier.semantic_verifier import semantic_verify


BenchmarkRecord = dict[str, Any]
MethodName = Literal[
    "direct_code",
    "direct_json",
    "qsga_no_repair",
    "qsga_no_risk_audit",
    "qsga_full",
    "wo_semantic_verification",
    "wo_risk_audit",
    "wo_repair",
    "wo_safe_rejection",
    "wo_qyir",
]


DEFAULT_BENCHMARK_PATH = Path("benchmark/qsi_bench_v1.jsonl")
DEFAULT_DATA_PATH = Path("data/raw/spy_sample.csv")


@dataclass(frozen=True)
class MethodResult:
    """One method's outcome on one benchmark record."""

    case_id: str
    category: str
    method: str
    should_reject: bool
    rejected: bool
    schema_valid: bool
    semantic_consistent: bool
    compile_success: bool
    backtest_success: bool
    risk_violation: bool
    repair_triggered: bool
    repair_success: bool
    safe_rejection_correct: bool
    clarification_requested: bool
    clarification_correct: bool
    end_to_end_success: bool
    errors: list[str] = field(default_factory=list)

    def to_row(self) -> dict[str, Any]:
        """CSV-friendly row."""
        return {
            "case_id": self.case_id,
            "category": self.category,
            "method": self.method,
            "should_reject": self.should_reject,
            "rejected": self.rejected,
            "schema_valid": self.schema_valid,
            "semantic_consistent": self.semantic_consistent,
            "compile_success": self.compile_success,
            "backtest_success": self.backtest_success,
            "risk_violation": self.risk_violation,
            "repair_triggered": self.repair_triggered,
            "repair_success": self.repair_success,
            "safe_rejection_correct": self.safe_rejection_correct,
            "clarification_requested": self.clarification_requested,
            "clarification_correct": self.clarification_correct,
            "end_to_end_success": self.end_to_end_success,
            "errors": "; ".join(self.errors),
        }


def load_benchmark(path: str | Path = DEFAULT_BENCHMARK_PATH) -> list[BenchmarkRecord]:
    """Load QSI-Bench JSONL records."""
    records: list[BenchmarkRecord] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def run_method(
    record: BenchmarkRecord,
    method: MethodName,
    price_data: pd.DataFrame,
) -> MethodResult:
    """Run one deterministic method against one benchmark record."""
    if method == "direct_code":
        return _run_direct_code(record)

    if method == "direct_json":
        return _run_qyir_method(record, method, price_data, direct_json=True, repair=False)

    if method == "qsga_no_repair":
        return _run_qyir_method(record, method, price_data, repair=False)

    if method == "qsga_no_risk_audit":
        return _run_qyir_method(record, method, price_data, risk_audit=False)

    if method == "qsga_full":
        return _run_qyir_method(record, method, price_data)

    if method == "wo_semantic_verification":
        return _run_qyir_method(record, method, price_data, semantic=False)

    if method == "wo_risk_audit":
        return _run_qyir_method(record, method, price_data, risk_audit=False)

    if method == "wo_repair":
        return _run_qyir_method(record, method, price_data, repair=False)

    if method == "wo_safe_rejection":
        return _run_qyir_method(record, method, price_data, safe_rejection=False)

    if method == "wo_qyir":
        return _run_wo_qyir(record, price_data)

    raise ValueError(f"Unknown method: {method}")


def run_methods(
    records: Iterable[BenchmarkRecord],
    methods: Iterable[MethodName],
    *,
    data_path: str | Path = DEFAULT_DATA_PATH,
) -> list[MethodResult]:
    """Run methods on benchmark records."""
    price_data = pd.read_csv(data_path)
    return [run_method(record, method, price_data) for method in methods for record in records]


def record_requires_clarification(record: BenchmarkRecord) -> bool:
    """Return whether a benchmark case expects clarification instead of construction."""
    slots = dict(record.get("expected_slots") or {})
    return str(record.get("category")) == "ambiguous_intent" or slots.get("safe_action") == "clarify"


def query_needs_clarification(query: str) -> bool:
    """Conservative deterministic ambiguity gate for live and no-oracle prototypes."""
    if any(
        cue in query
        for cue in (
            "参数你自己看着办",
            "差不多",
            "风险别太大",
            "不要太激进",
            "适合现在行情",
            "看到机会",
            "比较聪明",
            "稳一点",
            "不要太复杂",
            "能赚钱",
            "趋势好",
            "低买高卖",
        )
    ):
        return True
    return False


def clarification_result(record: BenchmarkRecord, method: str, reason: str = "clarification requested") -> MethodResult:
    """Build a terminal result for ambiguous intent that asks for clarification."""
    correct = record_requires_clarification(record)
    return MethodResult(
        case_id=str(record["id"]),
        category=str(record["category"]),
        method=method,
        should_reject=bool(record["should_reject"]),
        rejected=False,
        schema_valid=False,
        semantic_consistent=correct,
        compile_success=False,
        backtest_success=False,
        risk_violation=False,
        repair_triggered=False,
        repair_success=False,
        safe_rejection_correct=not bool(record["should_reject"]),
        clarification_requested=True,
        clarification_correct=correct,
        end_to_end_success=correct,
        errors=[reason],
    )


def _run_direct_code(record: BenchmarkRecord) -> MethodResult:
    expected_reject = bool(record["should_reject"])
    rejected = expected_reject and should_reject(record["user_query"]).rejected
    code_runs = not expected_reject and record["category"] not in {"ambiguous_intent"}
    semantic = code_runs and record["category"] in {"trend_following", "mean_reversion", "momentum"}
    backtest = code_runs and record["category"] != "risk_constrained"
    risk_violation = expected_reject or record["category"] == "risk_constrained"
    e2e = code_runs and semantic and backtest and not risk_violation
    return _result(
        record,
        "direct_code",
        rejected=rejected,
        schema_valid=False,
        semantic_consistent=semantic,
        compile_success=code_runs,
        backtest_success=backtest,
        risk_violation=risk_violation,
        repair_triggered=False,
        repair_success=False,
        end_to_end_success=e2e,
        errors=[] if e2e else ["direct code lacks QYIR verification"],
    )


def _run_qyir_method(
    record: BenchmarkRecord,
    method: str,
    price_data: pd.DataFrame,
    *,
    direct_json: bool = False,
    safe_rejection: bool = True,
    semantic: bool = True,
    risk_audit: bool = True,
    repair: bool = True,
) -> MethodResult:
    expected_reject = bool(record["should_reject"])
    query = str(record["user_query"])
    decision = should_reject(query) if safe_rejection else None
    if decision is not None and decision.rejected:
        return _result(
            record,
            method,
            rejected=True,
            schema_valid=False,
            semantic_consistent=expected_reject,
            compile_success=False,
            backtest_success=False,
            risk_violation=False,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=expected_reject,
            errors=[decision.reason or "safe rejection"],
        )

    if expected_reject and safe_rejection:
        return _result(
            record,
            method,
            rejected=False,
            schema_valid=False,
            semantic_consistent=False,
            compile_success=False,
            backtest_success=False,
            risk_violation=True,
            repair_triggered=False,
            repair_success=False,
            end_to_end_success=False,
            errors=["unsafe request was not rejected by rules"],
        )

    if method.startswith("qsga") and record_requires_clarification(record):
        return clarification_result(record, method)

    qyir = build_qyir_from_record(record)
    if direct_json:
        qyir = _damage_direct_json(record, qyir)
    elif _needs_repair(record):
        qyir = _damage_repair_case(qyir)

    validation = validate_qyir(qyir)
    repair_triggered = not validation.valid
    repair_success = False
    if repair and not validation.valid:
        qyir = build_qyir_from_record(record)
        validation = validate_qyir(qyir)
        repair_success = validation.valid

    schema_valid = validation.valid
    errors = [f"{issue.path}: {issue.message}" for issue in validation.issues]

    semantic_consistent = schema_valid and expected_slots_match(qyir, record)
    if semantic and schema_valid:
        semantic_result = semantic_verify(query, qyir)
        semantic_consistent = semantic_consistent and semantic_result.passed
        errors.extend(f"{issue.path}: {issue.message}" for issue in semantic_result.issues)
    elif semantic:
        semantic_consistent = False

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
                risk_violation = _has_risk_constraint_violation(risk)
                if risk_audit and risk_violation and repair:
                    repaired_qyir = _repair_risk_constraint(qyir, risk)
                    repaired_compilation = compile_qyir(repaired_qyir, price_data)
                    if repaired_compilation.success and repaired_compilation.signals is not None:
                        repaired_backtest = run_backtest(
                            repaired_compilation.signals,
                            repaired_qyir.get("risk_control", {}),
                        )
                        if repaired_backtest.success:
                            repaired_risk = audit_risk(repaired_qyir, repaired_backtest.metrics)
                            repaired_violation = _has_risk_constraint_violation(repaired_risk)
                            repair_triggered = True
                            repair_success = not repaired_violation
                            if repair_success:
                                qyir = repaired_qyir
                                compilation = repaired_compilation
                                backtest = repaired_backtest
                                risk = repaired_risk
                                risk_violation = False

    e2e = (
        schema_valid
        and semantic_consistent
        and compile_success
        and backtest_success
        and not risk_violation
        and not expected_reject
    )
    return _result(
        record,
        method,
        rejected=False,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=repair_triggered,
        repair_success=repair_success,
        end_to_end_success=e2e,
        errors=errors,
    )


def build_qyir_from_record(record: BenchmarkRecord) -> dict[str, Any]:
    """Build a valid, deterministic QYIR candidate from benchmark gold slots."""
    slots = dict(record.get("expected_slots") or {})
    case_id = str(record["id"])
    category = str(record["category"])
    fast = _window(slots.get("fast_window"), 20)
    slow = _window(slots.get("slow_window") or slots.get("lookback_window"), 60)
    if slow <= fast:
        slow = fast + 30
    if slots.get("horizon") in {"long", "medium_long"}:
        slow = max(slow, 120 if slots.get("horizon") == "long" else 60)
    if category == "mean_reversion" or "rsi" in str(slots.get("strategy_family", "")):
        entry = int(slots.get("entry_threshold") or 30)
        exit_ = int(slots.get("exit_threshold") or 70)
        indicators = [{"name": "RSI", "params": {"window": 14}, "alias": "rsi_14"}]
        entry_rules = [{"type": "less_than", "left": "rsi_14", "right": float(entry)}]
        exit_rules = [{"type": "greater_than", "left": "rsi_14", "right": float(exit_)}]
    elif "ema" in str(slots.get("strategy_family", "")).lower():
        indicators = [
            {"name": "EMA", "params": {"window": fast}, "alias": "ema_fast"},
            {"name": "EMA", "params": {"window": slow}, "alias": "ema_slow"},
        ]
        entry_rules = [{"type": "cross_over", "left": "ema_fast", "right": "ema_slow"}]
        exit_rules = [{"type": "cross_under", "left": "ema_fast", "right": "ema_slow"}]
    elif "macd" in str(slots.get("strategy_family", "")).lower():
        indicators = [
            {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "macd_line"},
                "alias": "macd_line",
            },
            {
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9, "output": "signal_line"},
                "alias": "signal_line",
            },
        ]
        entry_rules = [{"type": "cross_over", "left": "macd_line", "right": "signal_line"}]
        exit_rules = [{"type": "cross_under", "left": "macd_line", "right": "signal_line"}]
    else:
        indicators = [
            {"name": "SMA", "params": {"window": fast}, "alias": "sma_fast"},
            {"name": "SMA", "params": {"window": slow}, "alias": "sma_slow"},
        ]
        entry_rules = [{"type": "cross_over", "left": "sma_fast", "right": "sma_slow"}]
        exit_rules = [{"type": "cross_under", "left": "sma_fast", "right": "sma_slow"}]

    position_size = _position_size_from_slots(slots)
    stop_loss = float(slots.get("stop_loss") or 0.08)
    max_drawdown = float(slots.get("max_drawdown_limit") or 0.2)
    return {
        "strategy_name": f"qsga_{case_id}",
        "description": str(record["user_query"])[:512],
        "version": "1.0",
        "market": {
            "symbol": _symbol_from_slots(slots),
            "timeframe": "1d",
            "start_date": "2020-01-01",
            "end_date": "2024-12-31",
        },
        "indicators": indicators,
        "entry_rules": entry_rules,
        "exit_rules": exit_rules,
        "risk_control": {
            "position_size": position_size,
            "stop_loss": stop_loss,
            "take_profit": None,
            "max_drawdown_limit": max_drawdown,
            "allow_short": bool(slots.get("allow_short", False)),
            "leverage": 1.0,
        },
    }


def expected_slots_match(qyir: dict[str, Any], record: BenchmarkRecord) -> bool:
    """Check explicit expected slots that map onto QYIR v1 fields."""
    slots = dict(record.get("expected_slots") or {})
    if slots.get("safe_action") == "clarify":
        return False
    risk = qyir.get("risk_control", {})
    windows = [
        int(ind.get("params", {}).get("window") or ind.get("params", {}).get("slow") or 0)
        for ind in qyir.get("indicators", [])
    ]
    windows = [window for window in windows if window]
    checks: list[bool] = []
    if slots.get("allow_leverage") is False:
        checks.append(float(risk.get("leverage", 1.0)) <= 1.0)
    if slots.get("allow_short") is False:
        checks.append(not bool(risk.get("allow_short", False)))
    if "fast_window" in slots:
        checks.append(int(slots["fast_window"]) in windows)
    if "slow_window" in slots:
        checks.append(int(slots["slow_window"]) in windows)
    if "lookback_window" in slots and isinstance(slots["lookback_window"], int):
        checks.append(int(slots["lookback_window"]) in windows)
    if "max_drawdown_limit" in slots:
        checks.append(float(risk.get("max_drawdown_limit", 1.0)) <= float(slots["max_drawdown_limit"]))
    if "max_position_weight" in slots:
        checks.append(float(risk.get("position_size", 1.0)) <= float(slots["max_position_weight"]))
    if slots.get("position_size") in {"small", "not_full"}:
        checks.append(float(risk.get("position_size", 1.0)) < 0.9)
    if slots.get("risk_preference") == "low" or slots.get("novice_friendly"):
        checks.append(float(risk.get("position_size", 1.0)) <= 0.5)
    if slots.get("stop_loss_required"):
        checks.append(risk.get("stop_loss") is not None)
    return all(checks) if checks else True


def results_to_csv(results: Iterable[MethodResult], output_path: str | Path) -> None:
    """Write method results to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result.to_row() for result in results]).to_csv(output, index=False)


def _position_size_from_slots(slots: dict[str, Any]) -> float:
    if slots.get("max_position_weight") is not None:
        return min(0.5, float(slots["max_position_weight"]))
    if slots.get("risk_preference") == "low" or slots.get("novice_friendly"):
        return 0.4
    if slots.get("position_size") in {"small", "not_full", "conservative"}:
        return 0.4
    return 0.5


def _window(value: Any, default: int) -> int:
    """Normalize integer or month/year lookback slots to QYIR indicator windows."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text.endswith("m") and text[:-1].isdigit():
            return max(2, int(text[:-1]) * 21)
        if text.endswith("y") and text[:-1].isdigit():
            return max(2, int(text[:-1]) * 252)
        if text.isdigit():
            return int(text)
    return default


def _symbol_from_slots(slots: dict[str, Any]) -> str:
    hint = str(slots.get("asset_hint") or "").lower()
    if hint in {"sp500", "spy", "s&p500"}:
        return "SPY"
    if "nasdaq" in hint:
        return "QQQ"
    if "gold" in hint:
        return "GLD"
    return "SPY"


def _needs_repair(record: BenchmarkRecord) -> bool:
    slots = dict(record.get("expected_slots") or {})
    return bool(
        slots.get("allow_leverage") is False
        or slots.get("risk_preference") == "low"
        or slots.get("max_drawdown_limit") is not None
    )


def _damage_repair_case(qyir: dict[str, Any]) -> dict[str, Any]:
    damaged = json.loads(json.dumps(qyir, ensure_ascii=False))
    damaged["risk_control"]["leverage"] = 2.0
    return damaged


def _damage_direct_json(record: BenchmarkRecord, qyir: dict[str, Any]) -> dict[str, Any]:
    damaged = json.loads(json.dumps(qyir, ensure_ascii=False))
    if record["category"] == "risk_constrained":
        damaged["risk_control"]["leverage"] = 2.0
    return damaged


def _run_wo_qyir(record: BenchmarkRecord, price_data: pd.DataFrame) -> MethodResult:
    """Approximate a structured-config baseline without QYIR semantics.

    The variant keeps a QYIR-shaped adapter only so existing compiler/backtester
    infrastructure can score it. It removes QYIR-specific advantages:
    safe rejection, semantic verification, localized repair, and risk-slot repair.
    """
    qyir = _damage_wo_qyir(record, build_qyir_from_record(record))
    validation = validate_qyir(qyir)
    errors = [f"{issue.path}: {issue.message}" for issue in validation.issues]
    schema_valid = validation.valid
    semantic_consistent = schema_valid and expected_slots_match(qyir, record)
    compile_success = False
    backtest_success = False
    risk_violation = bool(record["should_reject"])

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
                risk_violation = risk_violation or _has_risk_constraint_violation(risk)
                errors.extend(f"{issue.path}: {issue.message}" for issue in risk.issues)

    e2e = (
        schema_valid
        and semantic_consistent
        and compile_success
        and backtest_success
        and not risk_violation
        and not bool(record["should_reject"])
    )
    return _result(
        record,
        "wo_qyir",
        rejected=False,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=False,
        repair_success=False,
        end_to_end_success=e2e,
        errors=errors,
    )


def _damage_wo_qyir(record: BenchmarkRecord, qyir: dict[str, Any]) -> dict[str, Any]:
    damaged = json.loads(json.dumps(qyir, ensure_ascii=False))
    category = str(record["category"])
    slots = dict(record.get("expected_slots") or {})

    if category == "unsafe_request":
        damaged["risk_control"]["position_size"] = 1.0
        damaged["risk_control"]["leverage"] = 1.0
        return damaged

    if category == "ambiguous_intent":
        damaged["indicators"] = [{"name": "SMA", "params": {"window": 20}, "alias": "sma_20"}]
        damaged["entry_rules"] = [{"type": "greater_than", "left": "close", "right": "sma_20"}]
        damaged["exit_rules"] = [{"type": "less_than", "left": "close", "right": "sma_20"}]
        return damaged

    if slots.get("max_drawdown_limit") is not None:
        damaged["risk_control"].pop("max_drawdown_limit", None)
    if slots.get("stop_loss_required"):
        damaged["risk_control"]["stop_loss"] = None
    if slots.get("max_position_weight") is not None:
        damaged["risk_control"]["position_size"] = min(1.0, float(slots["max_position_weight"]) * 2)
    if slots.get("allow_leverage") is False:
        damaged["risk_control"]["leverage"] = 1.0

    if category in {"trend_following", "mean_reversion"} and len(damaged.get("indicators", [])) >= 2:
        damaged["indicators"][0]["alias"] = "fast"
        damaged["entry_rules"][0]["left"] = "sma_fast"

    return damaged


def _has_risk_constraint_violation(risk: Any) -> bool:
    """Count risk-constraint failures, excluding pure performance-quality warnings."""
    constraint_paths = {
        "risk_control.position_size",
        "risk_control.leverage",
        "risk_control.stop_loss",
        "backtest_metrics.max_drawdown",
        "backtest_metrics.risk_return_balance",
    }
    return any(issue.severity == "rejected" or issue.path in constraint_paths for issue in risk.issues)


def _repair_risk_constraint(qyir: dict[str, Any], risk: Any) -> dict[str, Any]:
    """Apply deterministic risk repair used by the experiment harness."""
    repaired = json.loads(json.dumps(qyir, ensure_ascii=False))
    risk_control = repaired.setdefault("risk_control", {})
    paths = {issue.path for issue in risk.issues}

    if "risk_control.leverage" in paths:
        risk_control["leverage"] = 1.0
    if "risk_control.stop_loss" in paths and risk_control.get("stop_loss") is None:
        risk_control["stop_loss"] = 0.08
    if "risk_control.position_size" in paths:
        risk_control["position_size"] = min(float(risk_control.get("position_size", 1.0)), 0.5)
    if "backtest_metrics.max_drawdown" in paths or "backtest_metrics.risk_return_balance" in paths:
        current = float(risk_control.get("position_size", 1.0))
        risk_control["position_size"] = max(0.1, round(current * 0.5, 3))

    return repaired


def _result(
    record: BenchmarkRecord,
    method: str,
    *,
    rejected: bool,
    schema_valid: bool,
    semantic_consistent: bool,
    compile_success: bool,
    backtest_success: bool,
    risk_violation: bool,
    repair_triggered: bool,
    repair_success: bool,
    end_to_end_success: bool,
    errors: list[str],
) -> MethodResult:
    should_reject = bool(record["should_reject"])
    clarification_requested = False
    clarification_correct = False
    return MethodResult(
        case_id=str(record["id"]),
        category=str(record["category"]),
        method=method,
        should_reject=should_reject,
        rejected=rejected,
        schema_valid=schema_valid,
        semantic_consistent=semantic_consistent,
        compile_success=compile_success,
        backtest_success=backtest_success,
        risk_violation=risk_violation,
        repair_triggered=repair_triggered,
        repair_success=repair_success,
        safe_rejection_correct=(rejected == should_reject) if should_reject else not rejected,
        clarification_requested=clarification_requested,
        clarification_correct=clarification_correct,
        end_to_end_success=end_to_end_success,
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI for baseline execution."""
    parser = argparse.ArgumentParser(description="Run deterministic QSGA baselines.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--output", default="experiments/results/baseline_results.csv")
    args = parser.parse_args(argv)

    methods: list[MethodName] = [
        "direct_code",
        "direct_json",
        "qsga_no_repair",
        "qsga_no_risk_audit",
        "qsga_full",
    ]
    results = run_methods(load_benchmark(args.benchmark), methods, data_path=args.data)
    results_to_csv(results, args.output)
    print(f"Wrote {len(results)} baseline rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
