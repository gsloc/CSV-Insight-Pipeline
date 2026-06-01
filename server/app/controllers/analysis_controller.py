"""Controller: orchestrates the full ingest -> validate -> clean -> analyse run.

Kept free of HTTP concerns so it can be reused from a CLI or async worker.
"""
from __future__ import annotations

import time

import pandas as pd

from app.config import settings
from app.core.insights import generate_insights
from app.core.schema_inference import infer_schema
from app.services.analysis_service import analyze_dataframe
from app.services.cleaning_service import clean_dataframe
from app.services.ingestion_service import read_csv
from app.services.validation_service import build_data_quality_report
from app.utils.serialization import to_jsonable


def _preview(df: pd.DataFrame, n: int) -> dict:
    head = df.head(n)
    return {
        "columns": [str(c) for c in head.columns],
        "rows": [{str(c): row[c] for c in head.columns} for _, row in head.iterrows()],
        "total_rows": int(len(df)),
    }


def run_analysis_pipeline(content: bytes, filename: str, missing_strategy: str,
                          outlier_method: str) -> dict:
    t0 = time.perf_counter()

    # 1. Ingest
    df, ingest_meta = read_csv(content, filename)

    # 2. Infer schema (on the raw data, so the quality report reflects reality)
    schema = infer_schema(df)
    schema_dicts = [s.to_dict() for s in schema]

    # 3. Data quality report (raw)
    data_quality = build_data_quality_report(df, schema, outlier_method=outlier_method)

    # 4. Clean
    clean_df, cleaning_log = clean_dataframe(df, schema, missing_strategy=missing_strategy)

    # 5. Analyse (cleaned)
    analysis = analyze_dataframe(clean_df, schema)

    # 6. Executive insights
    meta = {
        "filename": filename,
        "rows": ingest_meta.rows_raw,
        "rows_clean": cleaning_log["rows_after"],
        "columns": ingest_meta.columns,
        "encoding": ingest_meta.detected_encoding,
        "encoding_confidence": ingest_meta.encoding_confidence,
        "header_generated": ingest_meta.header_generated,
        "skipped_bad_rows": ingest_meta.skipped_bad_rows,
        "missing_strategy": missing_strategy,
        "outlier_method": outlier_method,
        "warnings": ingest_meta.warnings,
    }
    insights = generate_insights(meta=meta, schema=schema_dicts,
                                 data_quality=data_quality, analysis=analysis)

    # 7. Preview of the cleaned data
    preview = _preview(clean_df, settings.max_preview_rows)

    meta["processing_ms"] = round((time.perf_counter() - t0) * 1000, 2)

    response = {
        "meta": meta,
        "schema": schema_dicts,
        "data_quality": data_quality,
        "cleaning": cleaning_log,
        "analysis": analysis,
        "insights": insights,
        "preview": preview,
    }
    return to_jsonable(response)
