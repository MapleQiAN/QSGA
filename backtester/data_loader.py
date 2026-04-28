"""Data loader — load and validate OHLCV price data from CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"date", "close"}


def load_price_data(path: str | Path) -> pd.DataFrame:
    """Load CSV price data, validate columns, parse dates.

    Required columns: date, close.
    Optional columns: open, high, low, volume.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Price data file not found: {path}")

    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Price data missing required columns: {missing}")

    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)
    return df
