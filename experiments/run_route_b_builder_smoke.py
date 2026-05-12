"""Offline Route B builder smoke test using QSI-Bench expected slots.

This script intentionally uses benchmark expected_slots. It tests deterministic
builder coverage only; it is not evidence of live natural-language slot
extraction capability.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.baselines import DEFAULT_BENCHMARK_PATH, load_benchmark
from qsgi.construction import StrategySlotSpec, build_qyir_from_slots


def expected_slots_to_spec(record: dict[str, Any]) -> StrategySlotSpec:
    """Convert benchmark expected_slots into a Route B slot spec."""
    slots = dict(record.get("expected_slots") or {})
    if bool(record.get("should_reject")):
        return StrategySlotSpec(safe_action="reject")
    if slots.get("safe_action") == "clarify" or str(record.get("category")) == "ambiguous_intent":
        return StrategySlotSpec(
            strategy_family="unknown",
            safe_action="clarify",
            ambiguity={
                "requires_clarification": True,
                "missing_slots": ["entry_logic", "exit_logic"],
                "ambiguous_phrases": [str(record.get("user_query", ""))[:120]],
            },
        )

    family = _strategy_family(record, slots)
    indicators = _indicator_slots(family, slots)
    entry_logic, exit_logic = _logic_slots(indicators, slots)
    risk_constraints = _risk_constraints(slots)
    return StrategySlotSpec.model_validate(
        {
            "strategy_family": family,
            "market_scope": {
                "symbol": _symbol(slots),
                "asset_type": "etf",
                "timeframe": "daily",
            },
            "indicators": indicators,
            "entry_logic": entry_logic,
            "exit_logic": exit_logic,
            "risk_constraints": risk_constraints,
            "safe_action": "construct",
        }
    )


def run_builder_smoke(
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    *,
    output: str | Path = "experiments/results/route_b_builder_smoke.csv",
    table_output: str | Path = "experiments/tables/route_b_builder_smoke.md",
) -> pd.DataFrame:
    """Run deterministic builder smoke over QSI-Bench expected slots."""
    rows: list[dict[str, Any]] = []
    for record in load_benchmark(benchmark_path):
        spec = expected_slots_to_spec(record)
        result = build_qyir_from_slots(
            spec,
            strategy_name=f"route_b_{record['id']}",
            description=str(record.get("user_query", "")),
        )
        expected_action = spec.safe_action
        terminal_correct = (
            (expected_action == "construct" and result.success)
            or (expected_action in {"reject", "clarify"} and not result.success)
        )
        rows.append(
            {
                "case_id": str(record["id"]),
                "category": str(record["category"]),
                "expected_action": expected_action,
                "builder_success": result.success,
                "terminal_correct": terminal_correct,
                "indicator_count": len(result.qyir.get("indicators", [])) if result.qyir else 0,
                "entry_rule_count": len(result.qyir.get("entry_rules", [])) if result.qyir else 0,
                "exit_rule_count": len(result.qyir.get("exit_rules", [])) if result.qyir else 0,
                "canonicalization_events": len(result.canonicalization_log),
                "errors": "; ".join(f"{error['path']}: {error['message']}" for error in result.errors),
            }
        )

    frame = pd.DataFrame(rows)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)

    summary = summarize_builder_smoke(frame)
    table_path = Path(table_output)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(_to_markdown(summary), encoding="utf-8")
    return frame


def summarize_builder_smoke(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize builder smoke by expected terminal action."""
    rows: list[dict[str, Any]] = []
    for action, group in frame.groupby("expected_action", sort=False):
        rows.append(
            {
                "Expected Action": action,
                "Cases": int(len(group)),
                "Builder Success": int(group["builder_success"].astype(bool).sum()),
                "Terminal Correct": int(group["terminal_correct"].astype(bool).sum()),
                "Terminal Correct Rate": float(group["terminal_correct"].astype(bool).mean()),
            }
        )
    rows.append(
        {
            "Expected Action": "all",
            "Cases": int(len(frame)),
            "Builder Success": int(frame["builder_success"].astype(bool).sum()),
            "Terminal Correct": int(frame["terminal_correct"].astype(bool).sum()),
            "Terminal Correct Rate": float(frame["terminal_correct"].astype(bool).mean()),
        }
    )
    return pd.DataFrame(rows)


def _strategy_family(record: dict[str, Any], slots: dict[str, Any]) -> str:
    category = str(record.get("category", ""))
    family = str(slots.get("strategy_family") or slots.get("strategy_type") or "").lower()
    if "rsi" in family or category == "mean_reversion":
        return "mean_reversion"
    if "momentum" in family or category == "momentum":
        return "momentum"
    if category == "risk_constrained":
        return "risk_controlled"
    if category == "breakout":
        return "breakout"
    return "trend_following"


def _indicator_slots(family: str, slots: dict[str, Any]) -> list[dict[str, Any]]:
    strategy_family = str(slots.get("strategy_family") or "").lower()
    if "macd" in strategy_family:
        return [{"name": "MACD", "role": "signal"}]
    if "rsi" in strategy_family or family == "mean_reversion":
        return [{"name": "RSI", "window": int(slots.get("lookback_window") or 14), "role": "threshold"}]
    if "ema" in strategy_family:
        fast, slow = _fast_slow_windows(slots)
        return [{"name": "EMA", "window": fast, "role": "fast"}, {"name": "EMA", "window": slow, "role": "slow"}]
    if "boll" in strategy_family:
        return [{"name": "BOLLINGER", "window": int(slots.get("lookback_window") or 20), "role": "threshold"}]

    fast, slow = _fast_slow_windows(slots)
    return [{"name": "SMA", "window": fast, "role": "fast"}, {"name": "SMA", "window": slow, "role": "slow"}]


def _fast_slow_windows(slots: dict[str, Any]) -> tuple[int, int]:
    fast = _window(slots.get("fast_window"), 20)
    slow = _window(slots.get("slow_window") or slots.get("lookback_window"), 60)
    if slow <= fast:
        slow = min(500, max(fast + 1, fast + 30))
    return fast, slow


def _logic_slots(indicators: list[dict[str, Any]], slots: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    first_name = indicators[0]["name"] if indicators else "SMA"
    if first_name == "RSI":
        left = f"rsi{indicators[0].get('window') or 14}"
        return (
            {"operator": "less_than", "left": left, "right": float(slots.get("entry_threshold") or 30)},
            {"operator": "greater_than", "left": left, "right": float(slots.get("exit_threshold") or 70)},
        )
    if first_name == "MACD":
        return (
            {"operator": "cross_over", "left": "macd_line", "right": "signal_line"},
            {"operator": "cross_under", "left": "macd_line", "right": "signal_line"},
        )
    if len(indicators) >= 2:
        left = f"{indicators[0]['name'].lower()}{indicators[0]['window']}"
        right = f"{indicators[1]['name'].lower()}{indicators[1]['window']}"
        return (
            {"operator": "cross_over", "left": left, "right": right},
            {"operator": "cross_under", "left": left, "right": right},
        )
    return ({}, {})


def _risk_constraints(slots: dict[str, Any]) -> dict[str, Any]:
    position_size = slots.get("max_position_weight")
    if position_size is None:
        if slots.get("risk_preference") == "low" or slots.get("novice_friendly"):
            position_size = 0.4
        elif slots.get("position_size") in {"small", "not_full", "conservative"}:
            position_size = 0.4
        else:
            position_size = 0.5
    stop_loss = slots.get("stop_loss")
    if stop_loss is None and slots.get("stop_loss_required"):
        stop_loss = 0.08
    return {
        "position_size": min(1.0, float(position_size)),
        "max_drawdown_limit": float(slots.get("max_drawdown_limit") or 0.2),
        "stop_loss": float(stop_loss) if stop_loss is not None else None,
        "take_profit": float(slots["take_profit"]) if slots.get("take_profit") is not None else None,
        "allow_short": bool(slots.get("allow_short", False)),
        "leverage": 1.0,
    }


def _symbol(slots: dict[str, Any]) -> str:
    hint = str(slots.get("asset_hint") or "").lower()
    if "nasdaq" in hint or hint == "qqq":
        return "QQQ"
    if "gold" in hint:
        return "GLD"
    return "SPY"


def _window(value: Any, default: int) -> int:
    if isinstance(value, int):
        return max(2, min(500, value))
    if isinstance(value, str) and value.isdigit():
        return max(2, min(500, int(value)))
    return default


def _to_markdown(frame: pd.DataFrame) -> str:
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = []
        for column in frame.columns:
            value = row[column]
            values.append(f"{value:.3f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run offline Route B builder smoke over expected slots.")
    parser.add_argument("--benchmark", default=str(DEFAULT_BENCHMARK_PATH))
    parser.add_argument("--output", default="experiments/results/route_b_builder_smoke.csv")
    parser.add_argument("--table-output", default="experiments/tables/route_b_builder_smoke.md")
    args = parser.parse_args(argv)

    frame = run_builder_smoke(args.benchmark, output=args.output, table_output=args.table_output)
    print(f"Wrote {len(frame)} builder smoke rows to {args.output}")
    print(f"Wrote builder smoke summary to {args.table_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
