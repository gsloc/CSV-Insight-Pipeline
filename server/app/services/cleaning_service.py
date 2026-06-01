"""Data Cleaning Layer.

Pipeline order (each step is fully logged):
  1. coerce dtypes to match the inferred schema (numeric / datetime)
  2. normalise string/categorical values (trim + lowercase)
  3. drop exact duplicate rows
  4. handle missing values via the configured Strategy Pattern strategy
"""
from __future__ import annotations

import warnings
from typing import List, Tuple

import pandas as pd

from app.core.cleaning_strategies import Transformation, get_missing_value_strategy
from app.core.schema_inference import (
    CATEGORICAL,
    DATETIME,
    FLOAT,
    INTEGER,
    TEXT,
    ColumnSchema,
    numeric_columns,
)


def _coerce_types(df: pd.DataFrame, schema: List[ColumnSchema]) -> Tuple[pd.DataFrame, List[Transformation]]:
    out = df.copy()
    tx: List[Transformation] = []
    for c in schema:
        col = c.name
        if c.inferred_type in (INTEGER, FLOAT):
            cleaned = out[col].astype(str).str.replace(",", "", regex=False).str.strip()
            coerced = pd.to_numeric(cleaned, errors="coerce")
            out[col] = coerced
            tx.append(Transformation(col, "coerce_numeric",
                                     f"standardised to numeric ({c.inferred_type})",
                                     int(coerced.notna().sum())))
        elif c.inferred_type == DATETIME:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                out[col] = pd.to_datetime(out[col], errors="coerce", format="mixed")
            tx.append(Transformation(col, "coerce_datetime", "parsed to datetime",
                                     int(out[col].notna().sum())))
    return out, tx


def _normalize_strings(df: pd.DataFrame, schema: List[ColumnSchema]) -> Tuple[pd.DataFrame, List[Transformation]]:
    out = df.copy()
    tx: List[Transformation] = []
    for c in schema:
        if c.inferred_type in (CATEGORICAL, TEXT):
            col = c.name
            before = out[col].astype("object")
            normalized = before.where(before.isna(), before.astype(str).str.strip().str.lower())
            changed = int((normalized.fillna("\x00") != before.fillna("\x00")).sum())
            out[col] = normalized
            if changed:
                tx.append(Transformation(col, "normalize_text",
                                         f"trimmed + lowercased {changed} value(s)", changed))
    return out, tx


def clean_dataframe(df: pd.DataFrame, schema: List[ColumnSchema],
                    missing_strategy: str = "median", normalize: bool = True) -> Tuple[pd.DataFrame, dict]:
    log = {"strategy": missing_strategy, "rows_before": int(len(df)), "transformations": []}
    work = df

    work, tx_types = _coerce_types(work, schema)
    tx_norm: List[Transformation] = []
    if normalize:
        work, tx_norm = _normalize_strings(work, schema)

    before = len(work)
    work = work.drop_duplicates().reset_index(drop=True)
    removed = before - len(work)
    tx_dupes = ([Transformation("*", "drop_duplicates", f"removed {removed} duplicate row(s)", removed)]
                if removed else [])

    strategy = get_missing_value_strategy(missing_strategy)
    result = strategy.apply(work, numeric_columns(schema))
    work = result.df

    all_tx = tx_types + tx_norm + tx_dupes + result.transformations
    log["transformations"] = [t.to_dict() for t in all_tx]
    log["rows_after"] = int(len(work))
    log["columns_after"] = int(work.shape[1])
    log["duplicates_removed"] = removed
    return work, log
