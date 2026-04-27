"""Generate synthetic SPY-like daily OHLCV data for testing."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


def generate_spy_sample(
    start: str = "2019-06-01",
    end: str = "2024-12-31",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate synthetic daily OHLCV data resembling SPY.

    Returns DataFrame with columns: date, open, high, low, close, volume.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)

    n = len(dates)
    # Start around $300, daily return ~0.03% with ~1.2% vol
    daily_returns = rng.normal(0.0003, 0.012, n)
    close = 300.0 * np.cumprod(1 + daily_returns)

    # Generate OHLC from close
    intra_range = rng.uniform(0.002, 0.015, n)
    high = close * (1 + intra_range)
    low = close * (1 - intra_range)
    open_price = close * (1 + rng.normal(0, 0.005, n))
    # Ensure OHLC consistency: low <= open,close <= high
    low = np.minimum(low, np.minimum(open_price, close))
    high = np.maximum(high, np.maximum(open_price, close))

    volume = rng.integers(50_000_000, 150_000_000, n)

    df = pd.DataFrame({
        "date": dates,
        "open": np.round(open_price, 2),
        "high": np.round(high, 2),
        "low": np.round(low, 2),
        "close": np.round(close, 2),
        "volume": volume,
    })

    return df


if __name__ == "__main__":
    output = Path(__file__).resolve().parent.parent / "data" / "raw" / "spy_sample.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    df = generate_spy_sample()
    df.to_csv(output, index=False)
    print(f"Generated {len(df)} rows → {output}")
