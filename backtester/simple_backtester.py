"""Simple backtester — run backtest on compiled signals DataFrame.

Input: signals DataFrame from compiler (must have date, close, position columns).
Output: BacktestResult with equity curve, trade list, and metrics.
"""

from __future__ import annotations

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

    df = signals.copy()
    close = df["close"].values
    positions = df["position"].values
    n = len(df)

    # --- Compute strategy returns ---
    # Daily return of the asset
    asset_returns = np.zeros(n)
    asset_returns[1:] = (close[1:] - close[:-1]) / close[:-1]

    # Strategy return = position * asset return * position_size
    strat_returns = positions * asset_returns * position_size
    strat_returns[0] = 0.0  # No return on first day

    # --- Compute equity curve ---
    equity = np.zeros(n)
    equity[0] = initial_capital
    for i in range(1, n):
        equity[i] = equity[i - 1] * (1 + strat_returns[i])

    equity_series = pd.Series(equity, index=df.index)
    returns_series = pd.Series(strat_returns, index=df.index)
    position_series = df["position"]

    # --- Extract individual trades with stop_loss / take_profit ---
    trades = _extract_trades(
        df, close, positions, stop_loss_pct, take_profit_pct
    )

    trade_returns = [t.return_pct for t in trades]

    # --- Compute metrics ---
    result.equity_curve = equity_series
    result.strategy_returns = returns_series
    result.trades = trades
    result.metrics = compute_all_metrics(
        equity_curve=equity_series,
        strategy_returns=returns_series,
        position=position_series,
        trade_returns=trade_returns,
        periods_per_year=periods_per_year,
    )

    return result


def _extract_trades(
    df: pd.DataFrame,
    close: np.ndarray,
    positions: np.ndarray,
    stop_loss_pct: float | None,
    take_profit_pct: float | None,
) -> list[TradeRecord]:
    """Extract individual round-trip trades from position series.

    Applies stop-loss and take-profit at the trade level.
    """
    trades: list[TradeRecord] = []
    entry_idx: int | None = None
    entry_price: float = 0.0

    n = len(positions)

    for i in range(n):
        pos = positions[i]

        # Entering a position
        if entry_idx is None and pos != 0:
            entry_idx = i
            entry_price = close[i]
            continue

        # In a position, check stop_loss / take_profit
        if entry_idx is not None and pos != 0:
            if stop_loss_pct is not None:
                pnl = (close[i] - entry_price) / entry_price
                if pnl <= -stop_loss_pct:
                    trades.append(TradeRecord(
                        entry_date=str(df["date"].iloc[entry_idx]),
                        entry_price=round(entry_price, 4),
                        exit_date=str(df["date"].iloc[i]),
                        exit_price=round(close[i], 4),
                        return_pct=round(pnl, 6),
                        exit_reason="stop_loss",
                    ))
                    entry_idx = None
                    continue

            if take_profit_pct is not None:
                pnl = (close[i] - entry_price) / entry_price
                if pnl >= take_profit_pct:
                    trades.append(TradeRecord(
                        entry_date=str(df["date"].iloc[entry_idx]),
                        entry_price=round(entry_price, 4),
                        exit_date=str(df["date"].iloc[i]),
                        exit_price=round(close[i], 4),
                        return_pct=round(pnl, 6),
                        exit_reason="take_profit",
                    ))
                    entry_idx = None
                    continue

        # Exiting position (position goes to 0 or reverses)
        if entry_idx is not None and pos == 0:
            pnl = (close[i] - entry_price) / entry_price
            trades.append(TradeRecord(
                entry_date=str(df["date"].iloc[entry_idx]),
                entry_price=round(entry_price, 4),
                exit_date=str(df["date"].iloc[i]),
                exit_price=round(close[i], 4),
                return_pct=round(pnl, 6),
                exit_reason="signal",
            ))
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
