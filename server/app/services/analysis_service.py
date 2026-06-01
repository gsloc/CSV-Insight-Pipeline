"""Analysis & Insight Engine orchestration (statistics, correlation, charts)."""
from __future__ import annotations

from typing import List

import pandas as pd

from app.core.chart_specs import build_chart_specs
from app.core.schema_inference import ColumnSchema, categorical_columns, numeric_columns
from app.core.statistics import categorical_summaries, correlation_matrix, summary_statistics


def analyze_dataframe(df: pd.DataFrame, schema: List[ColumnSchema]) -> dict:
    num = numeric_columns(schema)
    cat = categorical_columns(schema)

    summary = summary_statistics(df, num)
    cats = categorical_summaries(df, cat)
    corr = correlation_matrix(df, num)
    charts = build_chart_specs(df, num, cat, corr)

    return {
        "numeric_columns": num,
        "categorical_columns": cat,
        "summary_statistics": summary,
        "categorical_summaries": cats,
        "correlation": corr,
        "charts": charts,
        "single_column": df.shape[1] <= 1,
        "has_correlation": corr is not None,
    }
