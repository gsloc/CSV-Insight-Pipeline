"""Schema inference — classify each column into a logical type.

These are pure functions over pandas Series/DataFrame so they can be unit-tested
in complete isolation from the web layer (this is the "Core Data Logic" tier).
"""
from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass, field
from typing import Any, List

import numpy as np
import pandas as pd

# Logical column types
INTEGER = "integer"
FLOAT = "float"
DATETIME = "datetime"
BOOLEAN = "boolean"
CATEGORICAL = "categorical"
TEXT = "text"
EMPTY = "empty"

NUMERIC_TYPES = {INTEGER, FLOAT}

# Tunable thresholds
NUMERIC_PARSE_THRESHOLD = 0.90
DATETIME_PARSE_THRESHOLD = 0.90
CATEGORICAL_MAX_UNIQUE = 50
CATEGORICAL_MAX_UNIQUE_RATIO = 0.5

_BOOLEAN_TOKENS = {"true", "false", "yes", "no", "t", "f", "y", "n"}


@dataclass
class ColumnSchema:
    name: str
    inferred_type: str
    pandas_dtype: str
    non_null_count: int
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: List[Any] = field(default_factory=list)
    numeric_parse_ratio: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def _to_native(v: Any) -> Any:
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        f = float(v)
        return f if np.isfinite(f) else None
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.isoformat()
    return v


def _datetime_parse_ratio(values: pd.Series) -> float:
    if values.empty:
        return 0.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            parsed = pd.to_datetime(values, errors="coerce", format="mixed")
        except (ValueError, TypeError):
            try:
                parsed = pd.to_datetime(values, errors="coerce")
            except (ValueError, TypeError):
                return 0.0
    return float(parsed.notna().mean())


def _numeric_parse_ratio(values: pd.Series) -> float:
    cleaned = values.astype(str).str.replace(",", "", regex=False).str.strip()
    return float(pd.to_numeric(cleaned, errors="coerce").notna().mean())


def infer_series_type(series: pd.Series) -> str:
    """Classify a single column into a logical type. Pure + deterministic."""
    non_null = series.dropna()
    if len(non_null) == 0:
        return EMPTY

    # Fast paths for already-typed pandas columns.
    if pd.api.types.is_bool_dtype(series):
        return BOOLEAN
    if pd.api.types.is_datetime64_any_dtype(series):
        return DATETIME
    if pd.api.types.is_integer_dtype(series):
        return INTEGER
    if pd.api.types.is_float_dtype(series):
        return FLOAT

    # Object/string columns: normalise to trimmed strings for token tests.
    as_str = non_null.astype(str).str.strip()
    lowered = as_str.str.lower()

    # Boolean tokens (checked before numeric so they aren't treated as numbers).
    if set(lowered.unique()).issubset(_BOOLEAN_TOKENS):
        return BOOLEAN

    # Numeric? (tolerate thousands separators for detection)
    cleaned = as_str.str.replace(",", "", regex=False)
    numeric = pd.to_numeric(cleaned, errors="coerce")
    if numeric.notna().mean() >= NUMERIC_PARSE_THRESHOLD:
        valid = numeric.dropna()
        if not valid.empty and np.all(np.mod(valid.to_numpy(), 1) == 0):
            return INTEGER
        return FLOAT

    # Datetime? (only reached when not predominantly numeric)
    if _datetime_parse_ratio(as_str) >= DATETIME_PARSE_THRESHOLD:
        return DATETIME

    # Categorical vs free text based on cardinality.
    n_unique = non_null.nunique()
    ratio = n_unique / len(non_null)
    if n_unique <= CATEGORICAL_MAX_UNIQUE or ratio <= CATEGORICAL_MAX_UNIQUE_RATIO:
        return CATEGORICAL
    return TEXT


def infer_column_schema(series: pd.Series) -> ColumnSchema:
    inferred = infer_series_type(series)
    non_null = series.dropna()
    n = len(series)
    null_count = int(series.isna().sum())
    sample = [_to_native(v) for v in non_null.head(5).tolist()]
    parse_ratio = 0.0
    if inferred != DATETIME and len(non_null):
        parse_ratio = round(_numeric_parse_ratio(non_null), 4)
    return ColumnSchema(
        name=str(series.name),
        inferred_type=inferred,
        pandas_dtype=str(series.dtype),
        non_null_count=int(len(non_null)),
        null_count=null_count,
        null_pct=round(100.0 * null_count / n, 4) if n else 0.0,
        unique_count=int(non_null.nunique()),
        sample_values=sample,
        numeric_parse_ratio=parse_ratio,
    )


def infer_schema(df: pd.DataFrame) -> List[ColumnSchema]:
    return [infer_column_schema(df[col]) for col in df.columns]


def numeric_columns(schema: List[ColumnSchema]) -> List[str]:
    return [c.name for c in schema if c.inferred_type in NUMERIC_TYPES]


def categorical_columns(schema: List[ColumnSchema]) -> List[str]:
    return [c.name for c in schema if c.inferred_type == CATEGORICAL]


def datetime_columns(schema: List[ColumnSchema]) -> List[str]:
    return [c.name for c in schema if c.inferred_type == DATETIME]
