"""Backend-generated chart specifications.

Heavy binning/sampling is done server-side (Pandas/NumPy) so the frontend only
renders pre-computed, lightweight specs — keeping the presentation tier thin.
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd


def histogram_spec(series: pd.Series, column: str, bins: int = 20) -> Optional[dict]:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    if len(s) >= 5:
        n_bins = int(min(bins, max(5, int(np.sqrt(len(s))))))
    else:
        n_bins = max(1, len(s))
    counts, edges = np.histogram(s.to_numpy(), bins=n_bins)
    buckets = []
    for i in range(len(counts)):
        x0, x1 = float(edges[i]), float(edges[i + 1])
        buckets.append({
            "x0": round(x0, 4), "x1": round(x1, 4),
            "label": f"{round(x0, 2)}–{round(x1, 2)}",
            "count": int(counts[i]),
        })
    return {"type": "histogram", "column": column, "bins": buckets}


def bar_spec(series: pd.Series, column: str, top_n: int = 12) -> dict:
    vc = series.astype(str).value_counts().head(top_n)
    data = [{"category": str(k), "count": int(v)} for k, v in vc.items()]
    return {"type": "bar", "column": column, "data": data}


def scatter_spec(df: pd.DataFrame, x: str, y: str, max_points: int = 500) -> Optional[dict]:
    sub = df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()
    if sub.empty:
        return None
    if len(sub) > max_points:
        sub = sub.sample(max_points, random_state=42)
    points = [{"x": round(float(a), 4), "y": round(float(b), 4)}
              for a, b in zip(sub[x], sub[y])]
    return {"type": "scatter", "x": x, "y": y, "points": points}


def build_chart_specs(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str],
                      correlation: Optional[dict], max_charts: int = 12) -> List[dict]:
    specs: List[dict] = []
    for col in numeric_cols:
        spec = histogram_spec(df[col], col)
        if spec:
            specs.append(spec)
    for col in categorical_cols:
        if df[col].nunique() <= 30:
            specs.append(bar_spec(df[col], col))
    if correlation and correlation.get("pairs"):
        for p in correlation["pairs"][:2]:
            if abs(p["corr"]) >= 0.3:
                spec = scatter_spec(df, p["x"], p["y"])
                if spec:
                    spec["corr"] = p["corr"]
                    specs.append(spec)
    return specs[:max_charts]
