"""Application settings, sourced from environment variables with sane defaults."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


def _origins() -> List[str]:
    # Frontend defaults to port 3100 (chosen to avoid the common :3000 clash);
    # :3000 is also allowed so a frontend started there still works out of the box.
    raw = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3100,http://127.0.0.1:3100,http://localhost:3000,http://127.0.0.1:3000",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass
class Settings:
    app_name: str = "CSV Insight Pipeline API"
    version: str = "1.0.0"
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8100"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "50"))
    chunk_size: int = int(os.getenv("UPLOAD_CHUNK_SIZE", str(1024 * 1024)))  # 1 MiB
    allowed_origins: List[str] = field(default_factory=_origins)
    default_missing_strategy: str = os.getenv("DEFAULT_MISSING_STRATEGY", "median")
    default_outlier_method: str = os.getenv("DEFAULT_OUTLIER_METHOD", "iqr")
    max_preview_rows: int = int(os.getenv("MAX_PREVIEW_ROWS", "50"))

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
