"""Rule engine — evaluate trading rules on indicator Series.

Supported: cross_over, cross_under, greater_than, less_than, between.
"""

from __future__ import annotations

import pandas as pd


def cross_over(left: pd.Series, right: pd.Series) -> pd.Series:
    """True when left crosses above right (was <=, now >)."""
    return (left.shift(1) <= right.shift(1)) & (left > right)


def cross_under(left: pd.Series, right: pd.Series) -> pd.Series:
    """True when left crosses below right (was >=, now <)."""
    return (left.shift(1) >= right.shift(1)) & (left < right)


def greater_than(left: pd.Series, right: pd.Series) -> pd.Series:
    return left > right


def less_than(left: pd.Series, right: pd.Series) -> pd.Series:
    return left < right


def between(value: pd.Series, lower: pd.Series, upper: pd.Series) -> pd.Series:
    return (value >= lower) & (value <= upper)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_RULE_FNS = {
    "cross_over": cross_over,
    "cross_under": cross_under,
    "greater_than": greater_than,
    "less_than": less_than,
}


def evaluate_rule(
    rule_type: str,
    left: pd.Series,
    right: pd.Series | None = None,
    lower: pd.Series | None = None,
    upper: pd.Series | None = None,
) -> pd.Series:
    """Evaluate a rule and return boolean Series."""
    if rule_type == "between":
        if lower is None or upper is None:
            raise ValueError("Rule 'between' requires lower and upper")
        return between(left, lower, upper)

    fn = _RULE_FNS.get(rule_type)
    if fn is None:
        raise ValueError(f"Unsupported rule type: {rule_type}")
    if right is None:
        raise ValueError(f"Rule '{rule_type}' requires right")
    return fn(left, right)
