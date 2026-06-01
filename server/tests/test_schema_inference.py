"""Tests for schema detection logic."""
import numpy as np
import pandas as pd

from app.core.schema_inference import (
    BOOLEAN,
    CATEGORICAL,
    DATETIME,
    EMPTY,
    FLOAT,
    INTEGER,
    TEXT,
    infer_schema,
    infer_series_type,
    numeric_columns,
)


def test_integer_native():
    assert infer_series_type(pd.Series([1, 2, 3, 4, 5])) == INTEGER


def test_integer_from_strings():
    assert infer_series_type(pd.Series(["1", "2", "3"])) == INTEGER


def test_float_native():
    assert infer_series_type(pd.Series([1.5, 2.5, 3.0])) == FLOAT


def test_float_from_strings():
    assert infer_series_type(pd.Series(["1.1", "2.2", "3.3"])) == FLOAT


def test_integer_with_thousands_separator():
    assert infer_series_type(pd.Series(["1,000", "2,500", "3,000"])) == INTEGER


def test_datetime_detection():
    assert infer_series_type(pd.Series(["2021-01-01", "2021-02-01", "2021-03-15"])) == DATETIME


def test_boolean_detection():
    assert infer_series_type(pd.Series(["true", "false", "true", "false"])) == BOOLEAN


def test_categorical_detection():
    assert infer_series_type(pd.Series(["red", "blue", "red", "green", "blue"] * 5)) == CATEGORICAL


def test_text_detection():
    values = [f"free form note number {i} about something" for i in range(100)]
    assert infer_series_type(pd.Series(values)) == TEXT


def test_empty_detection():
    assert infer_series_type(pd.Series([None, None, np.nan])) == EMPTY


def test_mostly_numeric_meets_threshold():
    # 9 numeric of 10 (>= 90%) -> still numeric (integer)
    series = pd.Series(["1", "2", "3", "4", "5", "6", "7", "8", "9", "junk"])
    assert infer_series_type(series) == INTEGER


def test_below_threshold_is_not_numeric():
    # only 5 of 10 numeric -> not numeric, falls back to categorical
    series = pd.Series(["1", "2", "3", "4", "5", "a", "b", "c", "d", "e"])
    assert infer_series_type(series) in (CATEGORICAL, TEXT)


def test_infer_schema_full():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"], "c": [1.5, 2.5, 3.5]})
    schema = infer_schema(df)
    types = {s.name: s.inferred_type for s in schema}
    assert types["a"] == INTEGER
    assert types["c"] == FLOAT
    assert set(numeric_columns(schema)) == {"a", "c"}


def test_schema_records_nulls():
    schema = infer_schema(pd.DataFrame({"a": [1.0, np.nan, 3.0]}))[0]
    assert schema.null_count == 1
    assert schema.non_null_count == 2
