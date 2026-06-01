"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, ingestion
from app.config import settings
from app.utils.exceptions import PipelineError
from app.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("app")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Ingest, validate, clean, and analyse CSV files, returning a Data Quality "
        "report, summary statistics, correlations, auto-generated chart specs, and "
        "an executive insight summary."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PipelineError)
async def pipeline_error_handler(request: Request, exc: PipelineError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(health.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")


@app.get("/", tags=["system"])
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/api/v1/health",
        "analyze": "POST /api/v1/analyze",
    }
