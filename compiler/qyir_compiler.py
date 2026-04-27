"""QYIR compiler — compile a validated QYIR into a signals DataFrame.

Pipeline:
  1. Load price data (OHLCV DataFrame).
  2. Compute each indicator → store as column named by alias.
  3. Evaluate entry rules → entry_signal.
  4. Evaluate exit rules → exit_signal.
  5. Generate position series from signals.

Output DataFrame columns:
  date, open, high, low, close, volume, [indicator aliases...],
  entry_signal, exit_signal, position
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compiler.indicator_engine import compute_indicator
from compiler.rule_engine import evaluate_rule


@dataclass
class CompilationResult:
    """Result of QYIR compilation."""

    success: bool = True
    signals: pd.DataFrame | None = None
    errors: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.success = False
        self.errors.append(msg)


def _resolve_operand(
    value: Any,
    indicator_columns: dict[str, pd.Series],
) -> pd.Series | float:
    """Resolve a rule operand: alias string → Series, numeric → float."""
    if isinstance(value, str):
        if value in indicator_columns:
            return indicator_columns[value]
        raise ValueError(f"Unknown alias in rule operand: '{value}'")
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(f"Invalid rule operand type: {type(value)} for {value}")


def compile_qyir(
    qyir_data: dict,
    price_data: pd.DataFrame,
) -> CompilationResult:
    """Compile a QYIR dict against price data. Returns CompilationResult.

    price_data must have columns: date, open, high, low, close, volume.
    date column should be parseable as datetime.
    """
    result = CompilationResult()

    # --- Validate price data ---
    required_cols = {"date", "close"}
    missing = required_cols - set(price_data.columns)
    if missing:
        result.add_error(f"Price data missing columns: {missing}")
        return result

    df = price_data.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # --- Filter by date range ---
    market = qyir_data.get("market", {})
    start_date = market.get("start_date")
    end_date = market.get("end_date")
    if start_date and end_date:
        start_dt = pd.Timestamp(start_date)
        end_dt = pd.Timestamp(end_date)
        mask = (df["date"] >= start_dt) & (df["date"] <= end_dt)
        df = df.loc[mask].reset_index(drop=True)
        if len(df) == 0:
            result.add_error(
                f"No price data in range {start_date} to {end_date}"
            )
            return result

    # --- Compute indicators ---
    indicators = qyir_data.get("indicators", [])
    indicator_columns: dict[str, pd.Series] = {}

    for ind in indicators:
        name = ind["name"]
        params = ind.get("params", {})
        alias = ind["alias"]

        try:
            series = compute_indicator(name, df["close"], params)
            indicator_columns[alias] = series
            df[alias] = series
        except Exception as e:
            result.add_error(f"Indicator '{alias}' ({name}) failed: {e}")
            return result

    # --- Evaluate entry rules ---
    entry_rules = qyir_data.get("entry_rules", [])
    if not entry_rules:
        result.add_error("No entry rules defined")
        return result

    entry_signals = []
    for i, rule in enumerate(entry_rules):
        try:
            left = _resolve_operand(rule["left"], indicator_columns)
            right = _resolve_operand(rule.get("right"), indicator_columns) if rule.get("right") is not None else None
            lower = _resolve_operand(rule.get("lower"), indicator_columns) if rule.get("lower") is not None else None
            upper = _resolve_operand(rule.get("upper"), indicator_columns) if rule.get("upper") is not None else None

            sig = evaluate_rule(rule["type"], left, right=right, lower=lower, upper=upper)
            entry_signals.append(sig.fillna(False))
        except Exception as e:
            result.add_error(f"Entry rule {i} failed: {e}")
            return result

    # AND all entry signals
    combined_entry = entry_signals[0]
    for sig in entry_signals[1:]:
        combined_entry = combined_entry & sig
    df["entry_signal"] = combined_entry

    # --- Evaluate exit rules ---
    exit_rules = qyir_data.get("exit_rules", [])
    if not exit_rules:
        result.add_error("No exit rules defined")
        return result

    exit_signals = []
    for i, rule in enumerate(exit_rules):
        try:
            left = _resolve_operand(rule["left"], indicator_columns)
            right = _resolve_operand(rule.get("right"), indicator_columns) if rule.get("right") is not None else None
            lower = _resolve_operand(rule.get("lower"), indicator_columns) if rule.get("lower") is not None else None
            upper = _resolve_operand(rule.get("upper"), indicator_columns) if rule.get("upper") is not None else None

            sig = evaluate_rule(rule["type"], left, right=right, lower=lower, upper=upper)
            exit_signals.append(sig.fillna(False))
        except Exception as e:
            result.add_error(f"Exit rule {i} failed: {e}")
            return result

    combined_exit = exit_signals[0]
    for sig in exit_signals[1:]:
        combined_exit = combined_exit & sig
    df["exit_signal"] = combined_exit

    # --- Generate position series ---
    risk = qyir_data.get("risk_control", {})
    allow_short = risk.get("allow_short", False)

    df["position"] = _generate_positions(
        df["entry_signal"],
        df["exit_signal"],
        allow_short=allow_short,
    )

    result.signals = df
    return result


def _generate_positions(
    entry: pd.Series,
    exit_sig: pd.Series,
    allow_short: bool = False,
) -> pd.Series:
    """Generate position series from entry/exit boolean signals.

    Logic:
    - Start flat (0).
    - On entry signal → go long (1).
    - On exit signal → go flat (0).
    - If allow_short, exit while long → go short (-1), entry while short → go flat.
    """
    n = len(entry)
    positions = np.zeros(n, dtype=int)

    current_pos = 0
    for i in range(n):
        if current_pos == 0:
            if entry.iloc[i]:
                current_pos = 1
            elif allow_short and exit_sig.iloc[i]:
                current_pos = -1
        elif current_pos == 1:
            if exit_sig.iloc[i]:
                current_pos = 0
        elif current_pos == -1:
            if entry.iloc[i]:
                current_pos = 0

        positions[i] = current_pos

    return pd.Series(positions, index=entry.index)


def compile_qyir_file(
    qyir_path: str | Path,
    data_path: str | Path,
) -> CompilationResult:
    """Load QYIR JSON + price CSV, compile, return result."""
    qyir_path = Path(qyir_path)
    data_path = Path(data_path)

    result = CompilationResult()

    # Load QYIR
    try:
        qyir_data = json.loads(qyir_path.read_text(encoding="utf-8"))
    except Exception as e:
        result.add_error(f"Cannot load QYIR: {e}")
        return result

    # Load price data
    try:
        price_data = pd.read_csv(data_path)
    except Exception as e:
        result.add_error(f"Cannot load price data: {e}")
        return result

    return compile_qyir(qyir_data, price_data)
