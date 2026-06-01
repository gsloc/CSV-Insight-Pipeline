"""Tests for outlier detection math (IQR and Z-score)."""
import pandas as pd

from app.core.outlier_detection import (
    IQR,
    ZSCORE,
    detect_outliers,
    iqr_outliers,
    zscore_outliers,
)


def test_iqr_flags_extreme_value():
    res = iqr_outliers(pd.Series([10, 10, 11, 11, 12, 12, 12, 13, 100]))
    assert res.count == 1
    assert 100 in res.sample_values
    assert res.method == IQR


def test_iqr_no_outliers_in_uniform_range():
    res = iqr_outliers(pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    assert res.count == 0


def test_iqr_bounds_are_sane():
    res = iqr_outliers(pd.Series([10, 10, 11, 11, 12, 12, 12, 13, 100]))
    assert res.lower_bound is not None and res.upper_bound is not None
    assert res.upper_bound < 100


def test_zscore_flags_outlier():
    res = zscore_outliers(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1, 20]), threshold=2.0)
    assert res.count == 1
    assert 20 in res.sample_values
    assert res.method == ZSCORE


def test_zscore_constant_series_no_division_error():
    res = zscore_outliers(pd.Series([5, 5, 5, 5, 5]))
    assert res.count == 0  # std == 0 handled gracefully


def test_iqr_coerces_and_ignores_nonnumeric():
    res = iqr_outliers(pd.Series(["1", "2", "3", "x", "100", "12", "11", "10", "13", "12"]))
    assert res.count >= 1   # 100 still flagged after coercion


def test_detect_dispatch():
    s = pd.Series([10, 10, 11, 11, 12, 12, 12, 13, 100])
    assert detect_outliers(s, method="zscore").method == ZSCORE
    assert detect_outliers(s, method="iqr").method == IQR


def test_empty_series_safe():
    res = iqr_outliers(pd.Series([], dtype="float64"))
    assert res.count == 0
