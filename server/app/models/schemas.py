"""API contract: request enums and (documentation) response models.

Input validation is enforced via these enums; the response is assembled as a
sanitised dict (see ``utils.serialization``) so the heavy/variable analysis
payload is never blocked by over-strict output validation.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MissingStrategy(str, Enum):
    mean = "mean"
    median = "median"
    mode = "mode"
    drop = "drop"


class OutlierMethod(str, Enum):
    iqr = "iqr"
    zscore = "zscore"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str
    max_upload_mb: int
    missing_strategies: List[str]
    outlier_methods: List[str]


# --- Documentation models (shape of the /analyze response) ---
class ColumnSchemaModel(BaseModel):
    name: str
    inferred_type: str
    pandas_dtype: str
    non_null_count: int
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: List[Any] = Field(default_factory=list)
    numeric_parse_ratio: float = 0.0


class AnalyzeResponse(BaseModel):
    meta: Dict[str, Any]
    schema_: List[ColumnSchemaModel] = Field(alias="schema")
    data_quality: Dict[str, Any]
    cleaning: Dict[str, Any]
    analysis: Dict[str, Any]
    insights: Dict[str, Any]
    preview: Dict[str, Any]

    model_config = {"populate_by_name": True}
