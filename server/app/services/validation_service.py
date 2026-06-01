"""Schema & Data Validation — produces the Data Quality JSON report."""
from __future__ import annotations

from typing import List

import pandas as pd

from app.core.outlier_detection import detect_outliers
from app.core.schema_inference import ColumnSchema, numeric_columns


def build_data_quality_report(df: pd.DataFrame, schema: List[ColumnSchema],
                              outlier_method: str = "iqr") -> dict:
    n_rows, n_cols = int(df.shape[0]), int(df.shape[1])
    total_cells = n_rows * n_cols

    columns_detail = []
    total_missing = 0
    for c in schema:
        series = df[c.name]
        missing = int(series.isna().sum())
        total_missing += missing
        constant = c.unique_count <= 1 and c.non_null_count > 0
        high_card = (
            c.inferred_type in ("categorical", "text")
            and c.non_null_count > 0
            and (c.unique_count / max(1, c.non_null_count)) > 0.9
        )
        mixed = c.inferred_type in ("integer", "float") and 0.0 < c.numeric_parse_ratio < 1.0
        columns_detail.append({
            "column": c.name,
            "inferred_type": c.inferred_type,
            "null_count": missing,
            "null_pct": round(100.0 * missing / n_rows, 4) if n_rows else 0.0,
            "unique_count": c.unique_count,
            "constant": bool(constant),
            "high_cardinality": bool(high_card),
            "mixed_type": bool(mixed),
        })

    duplicate_rows = int(df.duplicated(keep="first").sum())

    outliers = []
    for name in numeric_columns(schema):
        res = detect_outliers(df[name], method=outlier_method, column=name)
        if res.count > 0:
            outliers.append(res.to_dict())

    warnings_list: List[str] = []
    if duplicate_rows:
        warnings_list.append(f"{duplicate_rows} duplicate row(s) detected.")
    for cr in columns_detail:
        if cr["null_pct"] >= 20:
            warnings_list.append(f"Column '{cr['column']}' is {cr['null_pct']:.1f}% missing.")
        if cr["constant"]:
            warnings_list.append(f"Column '{cr['column']}' has a single constant value.")
        if cr["mixed_type"]:
            warnings_list.append(f"Column '{cr['column']}' has mixed/inconsistent value types.")

    missing_ratio = total_missing / total_cells if total_cells else 0.0
    dup_ratio = duplicate_rows / n_rows if n_rows else 0.0
    outlier_cells = sum(o["count"] for o in outliers)
    outlier_ratio = outlier_cells / total_cells if total_cells else 0.0
    score = 100.0 * (1 - missing_ratio) * (1 - dup_ratio) * (1 - min(0.5, outlier_ratio))
    quality_score = round(max(0.0, min(100.0, score)), 2)

    return {
        "rows": n_rows,
        "n_columns": n_cols,
        "total_cells": total_cells,
        "total_missing": total_missing,
        "missing_pct": round(100.0 * missing_ratio, 4),
        "duplicate_rows": duplicate_rows,
        "columns": columns_detail,
        "outliers": outliers,
        "outlier_method": outlier_method,
        "warnings": warnings_list,
        "quality_score": quality_score,
    }
