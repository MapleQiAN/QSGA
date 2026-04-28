"""Backtest performance metrics.

All functions accept standard pandas/numpy inputs and return scalars.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def total_return(equity_curve: pd.Series) -> float:
    """Total return from equity curve. E.g. 0.235 = +23.5%."""
    if len(equity_curve) < 2:
        return 0.0
    return float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1)


def annualized_return(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized return from equity curve."""
    if len(equity_curve) < 2:
        return 0.0
    total_ret = total_return(equity_curve)
    n_periods = len(equity_curve)
    if total_ret <= -1:
        return -1.0
    return float((1 + total_ret) ** (periods_per_year / n_periods) - 1)


def sharpe_ratio(
    strategy_returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """Annualized Sharpe ratio."""
    if len(strategy_returns) < 2:
        return 0.0
    excess = strategy_returns - risk_free_rate / periods_per_year
    std = excess.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float(np.sqrt(periods_per_year) * excess.mean() / std)


def max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum drawdown (negative value). E.g. -0.184 = -18.4%."""
    if len(equity_curve) < 2:
        return 0.0
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1
    return float(drawdown.min())


def volatility(strategy_returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized volatility."""
    if len(strategy_returns) < 2:
        return 0.0
    return float(strategy_returns.std() * np.sqrt(periods_per_year))


def win_rate(trade_returns: list[float]) -> float:
    """Fraction of profitable trades."""
    if not trade_returns:
        return 0.0
    wins = sum(1 for r in trade_returns if r > 0)
    return wins / len(trade_returns)


def num_trades(position: pd.Series) -> int:
    """Number of round-trip trades (long entry → flat)."""
    if len(position) < 2:
        return 0
    # Count transitions from non-zero to zero (closing a trade)
    prev_nonzero = position.shift(1).fillna(0) != 0
    curr_zero = position == 0
    closes = int((prev_nonzero & curr_zero).sum())
    return closes


def compute_all_metrics(
    equity_curve: pd.Series,
    strategy_returns: pd.Series,
    position: pd.Series,
    trade_returns: list[float],
    periods_per_year: int = 252,
) -> dict:
    """Compute all backtest metrics and return as dict."""
    return {
        "total_return": round(total_return(equity_curve), 6),
        "annualized_return": round(annualized_return(equity_curve, periods_per_year), 6),
        "sharpe_ratio": round(sharpe_ratio(strategy_returns, periods_per_year=periods_per_year), 4),
        "max_drawdown": round(max_drawdown(equity_curve), 6),
        "volatility": round(volatility(strategy_returns, periods_per_year), 6),
        "win_rate": round(win_rate(trade_returns), 4),
        "num_trades": num_trades(position),
    }
