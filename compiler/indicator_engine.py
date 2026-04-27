"""Indicator engine — compute technical indicators from price Series.

Supported: SMA, EMA, RSI, MACD, BOLLINGER.
All functions accept a pd.Series and return a pd.Series (or tuple for multi-output).
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def compute_sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def compute_ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=window, min_periods=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window, min_periods=window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def compute_macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (macd_line, signal_line, histogram)."""
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_bollinger(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (upper, middle, lower)."""
    middle = compute_sma(series, window)
    std = series.rolling(window=window, min_periods=window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_INDICATOR_FNS = {
    "SMA": lambda series, p: compute_sma(series, p["window"]),
    "EMA": lambda series, p: compute_ema(series, p["window"]),
    "RSI": lambda series, p: compute_rsi(series, p.get("window", 14)),
}


def compute_indicator(
    name: str,
    series: pd.Series,
    params: dict,
) -> pd.Series:
    """Compute a single indicator and return the requested output as a Series.

    For multi-output indicators (MACD, BOLLINGER), the `output` param selects
    which component to return.
    """
    if name == "MACD":
        macd_line, signal_line, histogram = compute_macd(
            series,
            fast=params.get("fast", 12),
            slow=params.get("slow", 26),
            signal=params.get("signal", 9),
        )
        output_map = {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram,
        }
        return output_map[params["output"]]

    if name == "BOLLINGER":
        upper, middle, lower = compute_bollinger(
            series,
            window=params.get("window", 20),
            num_std=params.get("num_std", 2.0),
        )
        output_map = {
            "upper": upper,
            "middle": middle,
            "lower": lower,
        }
        return output_map[params["output"]]

    fn = _INDICATOR_FNS.get(name)
    if fn is None:
        raise ValueError(f"Unsupported indicator: {name}")
    return fn(series, params)
