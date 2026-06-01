"""Summary statistics and correlation. Pure functions on (cleaned) data."""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd

PERCENTILES = [5, 25, 50, 75, 90, 95]


def summary_statistics(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for col in numeric_cols:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if s.empty:
            out[col] = {"count": 0}
            continue
        out[col] = {
            "count": int(s.count()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
            "variance": float(s.var(ddof=1)) if len(s) > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
            "range": float(s.max() - s.min()),
            "skew": float(s.skew()) if len(s) > 2 else 0.0,
            "percentiles": {str(p): float(np.percentile(s, p)) for p in PERCENTILES},
        }
    return out


def categorical_summaries(df: pd.DataFrame, categorical_cols: List[str], top_n: int = 10) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for col in categorical_cols:
        vc = df[col].astype(str).value_counts().head(top_n)
        out[col] = {
            "unique": int(df[col].nunique()),
            "top": [{"value": str(k), "count": int(v)} for k, v in vc.items()],
        }
    return out


def correlation_matrix(df: pd.DataFrame, numeric_cols: List[str], method: str = "pearson") -> Optional[dict]:
    """Return a serialisable correlation matrix, or ``None`` if < 2 numeric cols."""
    cols = list(numeric_cols)
    if len(cols) < 2:
        return None
    numeric_df = df[cols].apply(pd.to_numeric, errors="coerce")
    corr = numeric_df.corr(method=method)
    columns = [str(c) for c in corr.columns]
    matrix = [[None if pd.isna(v) else round(float(v), 6) for v in row] for row in corr.to_numpy()]
    pairs = []
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            v = corr.iloc[i, j]
            if pd.notna(v):
                pairs.append({"x": columns[i], "y": columns[j], "corr": round(float(v), 6)})
    pairs.sort(key=lambda p: abs(p["corr"]), reverse=True)
    return {"method": method, "columns": columns, "matrix": matrix, "pairs": pairs}
