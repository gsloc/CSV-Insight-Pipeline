"""Ingestion & analysis routes."""
from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from app.controllers.analysis_controller import run_analysis_pipeline
from app.core.cleaning_strategies import available_strategies
from app.utils.exceptions import PipelineError
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

_ALLOWED_EXT = {".csv", ".txt", ".tsv"}
_OUTLIER_METHODS = {"iqr", "zscore"}


async def _read_limited(file: UploadFile) -> bytes:
    """Stream the upload in chunks, enforcing the size cap to protect memory."""
    max_bytes = settings.max_upload_bytes
    chunks = []
    total = 0
    while True:
        chunk = await file.read(settings.chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the maximum size of {settings.max_upload_mb} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/analyze", tags=["analysis"])
async def analyze(
    file: UploadFile = File(..., description="CSV file (multipart/form-data)"),
    missing_strategy: str = Form(settings.default_missing_strategy),
    outlier_method: str = Form(settings.default_outlier_method),
):
    name = file.filename or "upload.csv"
    ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext and ext not in _ALLOWED_EXT:
        raise HTTPException(status_code=415,
                            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(_ALLOWED_EXT)}")
    if missing_strategy not in available_strategies():
        raise HTTPException(status_code=422,
                            detail=f"Invalid missing_strategy. Allowed: {available_strategies()}")
    if outlier_method not in _OUTLIER_METHODS:
        raise HTTPException(status_code=422,
                            detail=f"Invalid outlier_method. Allowed: {sorted(_OUTLIER_METHODS)}")

    try:
        content = await _read_limited(file)
    finally:
        await file.close()

    try:
        return run_analysis_pipeline(content, name, missing_strategy, outlier_method)
    except PipelineError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed for %s", name)
        raise HTTPException(status_code=500, detail=f"Internal analysis error: {exc}")
