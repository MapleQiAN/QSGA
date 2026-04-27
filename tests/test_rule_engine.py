"""Tests for compiler/rule_engine.py"""

import pandas as pd
import numpy as np
import pytest

from compiler.rule_engine import (
    between,
    cross_over,
    cross_under,
    evaluate_rule,
    greater_than,
    less_than,
)


@pytest.fixture
def series_pair():
    """Two simple series for cross/compare tests."""
    left = pd.Series([1, 2, 3, 2, 1, 2, 3, 4], dtype=float)
    right = pd.Series([2, 2, 2, 2, 2, 2, 2, 2], dtype=float)
    return left, right


class TestCrossOver:
    def test_detects_cross(self, series_pair):
        left, right = series_pair
        result = cross_over(left, right)
        # idx 1: left=2, right=2, prev left=1 <= prev right=2, now 2 > 2? No (equal)
        # idx 2: left=3, right=2, prev left=2 <= prev right=2, now 3 > 2? Yes
        assert result.iloc[2] == True
        # idx 5: left=2, right=2, prev left=1 <= prev right=2, now 2 > 2? No
        assert result.iloc[5] == False
        # idx 6: left=3, right=2, prev left=2 <= prev right=2, now 3 > 2? Yes
        assert result.iloc[6] == True

    def test_no_false_positives_at_start(self, series_pair):
        left, right = series_pair
        result = cross_over(left, right)
        assert result.iloc[0] == False


class TestCrossUnder:
    def test_detects_cross(self, series_pair):
        left, right = series_pair
        result = cross_under(left, right)
        # idx 3: left=2, right=2, prev left=3 >= prev right=2, now 2 < 2? No
        # idx 4: left=1, right=2, prev left=2 >= prev right=2, now 1 < 2? Yes
        assert result.iloc[4] == True


class TestGreaterThan:
    def test_basic(self):
        left = pd.Series([1, 2, 3])
        right = pd.Series([2, 2, 2])
        result = greater_than(left, right)
        assert list(result) == [False, False, True]


class TestLessThan:
    def test_basic(self):
        left = pd.Series([1, 2, 3])
        right = pd.Series([2, 2, 2])
        result = less_than(left, right)
        assert list(result) == [True, False, False]


class TestBetween:
    def test_basic(self):
        value = pd.Series([20, 30, 40, 50, 60])
        lower = pd.Series([25, 25, 25, 25, 25])
        upper = pd.Series([55, 55, 55, 55, 55])
        result = between(value, lower, upper)
        assert list(result) == [False, True, True, True, False]


class TestEvaluateRule:
    def test_dispatch_cross_over(self, series_pair):
        left, right = series_pair
        result = evaluate_rule("cross_over", left, right=right)
        assert result.iloc[2] == True

    def test_dispatch_between(self):
        value = pd.Series([30, 50, 70])
        lower = pd.Series([25, 25, 25])
        upper = pd.Series([75, 75, 75])
        result = evaluate_rule("between", value, lower=lower, upper=upper)
        assert list(result) == [True, True, True]

    def test_unsupported_type(self, series_pair):
        left, _ = series_pair
        with pytest.raises(ValueError, match="Unsupported"):
            evaluate_rule("rank_top_k", left, right=left)

    def test_between_missing_bounds(self):
        value = pd.Series([30])
        with pytest.raises(ValueError, match="requires lower and upper"):
            evaluate_rule("between", value)

    def test_missing_right(self):
        value = pd.Series([30])
        with pytest.raises(ValueError, match="requires right"):
            evaluate_rule("cross_over", value)
