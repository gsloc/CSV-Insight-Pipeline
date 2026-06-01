"""System / health routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.core.cleaning_strategies import available_strategies
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.version,
        max_upload_mb=settings.max_upload_mb,
        missing_strategies=available_strategies(),
        outlier_methods=["iqr", "zscore"],
    )
