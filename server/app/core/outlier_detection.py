"""Outlier detection via IQR and Z-score. Pure numeric functions."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd

IQR = "iqr"
ZSCORE = "zscore"


@dataclass
class OutlierResult:
    column: str
    method: str
    count: int
    pct: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    threshold: Optional[float] = None
    indices: List[int] = field(default_factory=list)
    sample_values: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").dropna()


def iqr_outliers(series: pd.Series, k: float = 1.5, column: str = "") -> OutlierResult:
    """Tukey's fences: flag values outside [Q1 - k*IQR, Q3 + k*IQR]."""
    s = _coerce_numeric(series)
    column = column or str(series.name or "")
    if s.empty:
        return OutlierResult(column=column, method=IQR, count=0, pct=0.0)
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    mask = (s < lower) | (s > upper)
    flagged = s[mask]
    return OutlierResult(
        column=column,
        method=IQR,
        count=int(mask.sum()),
        pct=round(100.0 * float(mask.mean()), 4),
        lower_bound=lower,
        upper_bound=upper,
        indices=[int(i) for i in flagged.index.tolist()[:100]],
        sample_values=[float(v) for v in flagged.tolist()[:20]],
    )


def zscore_outliers(series: pd.Series, threshold: float = 3.0, column: str = "") -> OutlierResult:
    """Flag values whose |z-score| exceeds ``threshold`` (population std)."""
    s = _coerce_numeric(series)
    column = column or str(series.name or "")
    if s.empty:
        return OutlierResult(column=column, method=ZSCORE, count=0, pct=0.0, threshold=threshold)
    mean = float(s.mean())
    std = float(s.std(ddof=0))
    if std == 0 or np.isnan(std):
        # No variance -> no outliers (and avoids divide-by-zero).
        return OutlierResult(column=column, method=ZSCORE, count=0, pct=0.0, threshold=threshold)
    z = (s - mean) / std
    mask = z.abs() > threshold
    flagged = s[mask]
    return OutlierResult(
        column=column,
        method=ZSCORE,
        count=int(mask.sum()),
        pct=round(100.0 * float(mask.mean()), 4),
        threshold=threshold,
        indices=[int(i) for i in flagged.index.tolist()[:100]],
        sample_values=[float(v) for v in flagged.tolist()[:20]],
    )


def detect_outliers(series: pd.Series, method: str = IQR, column: str = "", **kwargs) -> OutlierResult:
    if method == ZSCORE:
        return zscore_outliers(series, column=column, **kwargs)
    return iqr_outliers(series, column=column, **kwargs)
