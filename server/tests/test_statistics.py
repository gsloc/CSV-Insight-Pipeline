"""Tests for summary statistics and correlation."""
import pandas as pd

from app.core.statistics import correlation_matrix, summary_statistics


def test_summary_basic_math():
    stats = summary_statistics(pd.DataFrame({"x": [1, 2, 3, 4, 5]}), ["x"])["x"]
    assert stats["mean"] == 3.0
    assert stats["median"] == 3.0
    assert stats["min"] == 1.0
    assert stats["max"] == 5.0
    assert abs(stats["variance"] - 2.5) < 1e-9       # sample variance (ddof=1)
    assert stats["percentiles"]["50"] == 3.0


def test_correlation_perfect_positive():
    corr = correlation_matrix(pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [2, 4, 6, 8, 10]}), ["a", "b"])
    assert corr is not None
    assert abs(corr["pairs"][0]["corr"] - 1.0) < 1e-9


def test_correlation_perfect_negative():
    corr = correlation_matrix(pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [5, 4, 3, 2, 1]}), ["a", "b"])
    assert abs(corr["pairs"][0]["corr"] + 1.0) < 1e-9


def test_correlation_single_column_returns_none():
    assert correlation_matrix(pd.DataFrame({"a": [1, 2, 3]}), ["a"]) is None


def test_summary_handles_empty_column():
    stats = summary_statistics(pd.DataFrame({"x": [None, None]}), ["x"])["x"]
    assert stats["count"] == 0
