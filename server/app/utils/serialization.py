"""Recursively convert pandas/numpy structures into JSON-safe Python natives.

FastAPI's default encoder will happily emit ``NaN``/``Infinity`` tokens (invalid
JSON that crashes ``JSON.parse`` in the browser) and chokes on ``np.int64`` /
``np.float64`` / ``pd.Timestamp``. Routing every response through
:func:`to_jsonable` guarantees a clean, strictly-valid JSON payload.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def to_jsonable(obj: Any) -> Any:
    # Primitives (bool must be checked before int via isinstance ordering below)
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, str):
        return obj

    # numpy scalars
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        f = float(obj)
        return f if math.isfinite(f) else None

    # datetimes
    if isinstance(obj, pd.Timestamp):
        return None if pd.isna(obj) else obj.isoformat()
    if isinstance(obj, np.datetime64):
        ts = pd.Timestamp(obj)
        return None if pd.isna(ts) else ts.isoformat()

    # containers
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [to_jsonable(v) for v in obj.tolist()]
    if isinstance(obj, pd.Series):
        return [to_jsonable(v) for v in obj.tolist()]

    # Any remaining scalar NaN/NaT
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return obj
