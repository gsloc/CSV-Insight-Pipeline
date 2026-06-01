"""Tests for missing-value handling and imputation strategies (Strategy Pattern)."""
import numpy as np
import pandas as pd
import pytest

from app.core.cleaning_strategies import (
    DropMissingStrategy,
    MeanImputationStrategy,
    MedianImputationStrategy,
    ModeImputationStrategy,
    available_strategies,
    get_missing_value_strategy,
    impute_mean,
    impute_median,
    impute_mode,
)


def test_impute_mean():
    out, fill = impute_mean(pd.Series([2.0, 4.0, np.nan, 6.0]))
    assert fill == 4.0
    assert out.isna().sum() == 0
    assert out.iloc[2] == 4.0


def test_impute_median():
    out, fill = impute_median(pd.Series([1.0, 2.0, 4.0, np.nan]))
    assert fill == 2.0
    assert out.isna().sum() == 0


def test_impute_mode_categorical():
    out, fill = impute_mode(pd.Series(["a", "b", "a", None]))
    assert fill == "a"
    assert (out == "a").sum() == 3


def test_factory_resolves_by_name():
    assert isinstance(get_missing_value_strategy("mean"), MeanImputationStrategy)
    assert isinstance(get_missing_value_strategy("MEDIAN"), MedianImputationStrategy)
    assert isinstance(get_missing_value_strategy("mode"), ModeImputationStrategy)
    assert isinstance(get_missing_value_strategy("drop"), DropMissingStrategy)


def test_factory_rejects_unknown():
    with pytest.raises(ValueError):
        get_missing_value_strategy("does-not-exist")


def test_mean_strategy_mixed_frame():
    df = pd.DataFrame({"num": [1.0, 2.0, np.nan, 4.0], "cat": ["x", "x", None, "y"]})
    result = get_missing_value_strategy("mean").apply(df, ["num"])
    assert result.df["num"].isna().sum() == 0
    assert result.df["cat"].isna().sum() == 0
    assert abs(result.df["num"].iloc[2] - (7.0 / 3.0)) < 1e-9   # mean of [1,2,4]
    assert result.df["cat"].iloc[2] == "x"                       # mode of categorical
    assert any(t.action == "impute_mean" for t in result.transformations)


def test_median_strategy_uses_median():
    df = pd.DataFrame({"num": [1.0, 2.0, 4.0, np.nan]})
    result = get_missing_value_strategy("median").apply(df, ["num"])
    assert result.df["num"].iloc[3] == 2.0


def test_drop_strategy_removes_rows():
    df = pd.DataFrame({"a": [1, 2, np.nan], "b": [4, np.nan, 6]})
    result = get_missing_value_strategy("drop").apply(df, ["a", "b"])
    assert len(result.df) == 1
    assert result.transformations[0].action == "drop_missing_rows"


def test_registry_contains_all_strategies():
    assert set(available_strategies()) >= {"mean", "median", "mode", "drop"}
