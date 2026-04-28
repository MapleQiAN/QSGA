"""Simple backtester — run backtest on compiled signals DataFrame.

Input: signals DataFrame from compiler (must have date, close, position columns).
Output: BacktestResult with equity curve, trade list, and metrics.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from backtester.data_loader import load_price_data
from backtester.metrics import compute_all_metrics
from compiler.qyir_compiler import compile_qyir_file, CompilationResult


@dataclass
class TradeRecord:
    """Single round-trip trade."""

    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    return_pct: float
    exit_reason: str  # "signal" | "stop_loss" | "take_profit"


@dataclass
class BacktestResult:
    """Complete backtest output."""

    success: bool = True
    equity_curve: pd.Series | None = None
    strategy_returns: pd.Series | None = None
    trades: list[TradeRecord] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.success = False
        self.errors.append(msg)


def run_backtest(
    signals: pd.DataFrame,
    risk_control: dict | None = None,
    initial_capital: float = 100_000.0,
    periods_per_year: int = 252,
) -> BacktestResult:
    """Run backtest on a signals DataFrame.

    signals must contain: date, close, position.
    risk_control dict may contain: position_size, stop_loss, take_profit.
    """
    result = BacktestResult()

    required = {"date", "close", "position"}
    missing = required - set(signals.columns)
    if missing:
        result.add_error(f"Signals DataFrame missing columns: {missing}")
        return result

    risk = risk_control or {}
    position_size = risk.get("position_size", 1.0)
    stop_loss_pct = risk.get("stop_loss")
    take_profit_pct = risk.get("take_profit")

    df = signals.copy().reset_index(drop=True)
    simulation = _simulate_positions_and_equity(
        df=df,
        position_size=position_size,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        initial_capital=initial_capital,
    )

    trade_returns = [t.return_pct for t in simulation["trades"]]

    # --- Compute metrics ---
    result.equity_curve = simulation["equity_curve"]
    result.strategy_returns = simulation["strategy_returns"]
    result.trades = simulation["trades"]
    result.metrics = compute_all_metrics(
        equity_curve=simulation["equity_curve"],
        strategy_returns=simulation["strategy_returns"],
        position=simulation["actual_position"],
        trade_returns=trade_returns,
        periods_per_year=periods_per_year,
    )

    return result


def _simulate_positions_and_equity(
    df: pd.DataFrame,
    position_size: float,
    stop_loss_pct: float | None,
    take_profit_pct: float | None,
    initial_capital: float,
) -> dict[str, Any]:
    """Simulate close-to-close returns using the previous day's active position."""
    close = df["close"].to_numpy(dtype=float)
    desired_positions = df["position"].to_numpy(dtype=int)
    n = len(df)

    equity = np.zeros(n)
    strategy_returns = np.zeros(n)
    actual_positions = np.zeros(n, dtype=int)
    trades: list[TradeRecord] = []

    equity[0] = initial_capital
    current_pos = 0
    entry_idx: int | None = None
    entry_price: float = 0.0

    for i in range(n):
        if i > 0:
            asset_return = (close[i] - close[i - 1]) / close[i - 1]
            strategy_returns[i] = current_pos * asset_return * position_size
            equity[i] = equity[i - 1] * (1 + strategy_returns[i])

        risk_exit = False
        if entry_idx is not None and current_pos != 0:
            pnl = _trade_return(current_pos, entry_price, close[i])
            if stop_loss_pct is not None:
                if pnl <= -stop_loss_pct:
                    trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "stop_loss"))
                    entry_idx = None
                    current_pos = 0
                    risk_exit = True
            if not risk_exit and take_profit_pct is not None:
                if pnl >= take_profit_pct:
                    trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "take_profit"))
                    entry_idx = None
                    current_pos = 0
                    risk_exit = True

        target_pos = desired_positions[i]
        if risk_exit:
            target_pos = 0

        if target_pos != current_pos:
            if entry_idx is not None and current_pos != 0:
                pnl = _trade_return(current_pos, entry_price, close[i])
                trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "signal"))
                entry_idx = None

            current_pos = target_pos
            if current_pos != 0:
                entry_idx = i
                entry_price = close[i]

        actual_positions[i] = current_pos

    equity_series = pd.Series(equity, index=df.index)
    returns_series = pd.Series(strategy_returns, index=df.index)
    position_series = pd.Series(actual_positions, index=df.index)

    return {
        "equity_curve": equity_series,
        "strategy_returns": returns_series,
        "actual_position": position_series,
        "trades": trades,
    }


def _trade_return(position: int, entry_price: float, exit_price: float) -> float:
    if position > 0:
        return (exit_price - entry_price) / entry_price
    return (entry_price - exit_price) / entry_price


def _make_trade_record(
    df: pd.DataFrame,
    entry_idx: int,
    exit_idx: int,
    entry_price: float,
    exit_price: float,
    return_pct: float,
    exit_reason: str,
) -> TradeRecord:
    return TradeRecord(
        entry_date=str(df["date"].iloc[entry_idx]),
        entry_price=round(entry_price, 4),
        exit_date=str(df["date"].iloc[exit_idx]),
        exit_price=round(exit_price, 4),
        return_pct=round(return_pct, 6),
        exit_reason=exit_reason,
    )


def _extract_trades(
    df: pd.DataFrame,
    close: np.ndarray,
    positions: np.ndarray,
    stop_loss_pct: float | None,
    take_profit_pct: float | None,
) -> list[TradeRecord]:
    """Deprecated compatibility helper; prefer _simulate_positions_and_equity."""
    trades: list[TradeRecord] = []
    entry_idx: int | None = None
    entry_price: float = 0.0
    entry_pos = 0

    n = len(positions)

    for i in range(n):
        pos = positions[i]

        if entry_idx is None and pos != 0:
            entry_idx = i
            entry_price = close[i]
            entry_pos = int(pos)
            continue

        if entry_idx is not None and pos != 0:
            pnl = _trade_return(entry_pos, entry_price, close[i])
            if stop_loss_pct is not None and pnl <= -stop_loss_pct:
                trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "stop_loss"))
                entry_idx = None
                continue

            if take_profit_pct is not None and pnl >= take_profit_pct:
                trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "take_profit"))
                entry_idx = None
                continue

        if entry_idx is not None and pos == 0:
            pnl = _trade_return(entry_pos, entry_price, close[i])
            trades.append(_make_trade_record(df, entry_idx, i, entry_price, close[i], pnl, "signal"))
            entry_idx = None

    return trades


def run_backtest_pipeline(
    qyir_path: str | Path,
    data_path: str | Path,
    initial_capital: float = 100_000.0,
) -> BacktestResult:
    """Full pipeline: load QYIR + data → compile → backtest."""

    # Compile QYIR to signals
    compilation = compile_qyir_file(qyir_path, data_path)
    if not compilation.success:
        result = BacktestResult()
        for err in compilation.errors:
            result.add_error(err)
        return result

    # Extract risk_control from QYIR
    qyir_path = Path(qyir_path)
    qyir_data = json.loads(qyir_path.read_text(encoding="utf-8"))
    risk_control = qyir_data.get("risk_control", {})

    # Run backtest
    return run_backtest(
        signals=compilation.signals,
        risk_control=risk_control,
        initial_capital=initial_capital,
    )


def format_backtest_summary(result: BacktestResult) -> str:
    """Format backtest result as readable summary."""
    if not result.success:
        return "Backtest failed:\n" + "\n".join(f"  - {e}" for e in result.errors)

    m = result.metrics
    lines = [
        "Backtest completed.",
        f"Total Return: {m['total_return']:.1%}",
        f"Annualized Return: {m['annualized_return']:.1%}",
        f"Sharpe Ratio: {m['sharpe_ratio']:.2f}",
        f"Max Drawdown: {m['max_drawdown']:.1%}",
        f"Volatility: {m['volatility']:.1%}",
        f"Win Rate: {m['win_rate']:.1%}",
        f"Number of Trades: {m['num_trades']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for `python -m backtester.simple_backtester`."""
    parser = argparse.ArgumentParser(description="Run a simple QYIR backtest.")
    parser.add_argument("--qyir", required=True, help="Path to QYIR JSON file.")
    parser.add_argument("--data", required=True, help="Path to price CSV file.")
    parser.add_argument("--initial-capital", type=float, default=100_000.0)
    parser.add_argument("--output-json", help="Optional path to save metrics as JSON.")
    parser.add_argument("--output-csv", help="Optional path to save metrics as CSV.")
    args = parser.parse_args(argv)

    result = run_backtest_pipeline(args.qyir, args.data, args.initial_capital)
    print(format_backtest_summary(result))

    if not result.success:
        return 1

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result.metrics, indent=2), encoding="utf-8")

    if args.output_csv:
        output_path = Path(args.output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([result.metrics]).to_csv(output_path, index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
