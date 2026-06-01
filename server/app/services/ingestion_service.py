"""File Ingestion Layer.

Responsibilities:
  * detect text encoding (UTF-8 vs ISO-8859-1 / Windows-1252) via ``chardet``
  * decode with a robust fallback chain
  * auto-generate headers when the file is headerless
  * skip malformed rows gracefully (and count them)
  * raise clear, typed errors for empty/unparseable input
"""
from __future__ import annotations

import csv
import io
import warnings
from dataclasses import dataclass, field
from typing import List, Tuple

import chardet
import pandas as pd

from app.utils.exceptions import EmptyDataError, MalformedDataError
from app.utils.logging import get_logger

logger = get_logger(__name__)

ENCODING_SAMPLE_BYTES = 64 * 1024


@dataclass
class IngestionMeta:
    filename: str
    detected_encoding: str
    encoding_confidence: float
    rows_raw: int
    columns: int
    skipped_bad_rows: int
    header_generated: bool
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def detect_encoding(content: bytes) -> Tuple[str, float]:
    if not content:
        return ("utf-8", 0.0)
    result = chardet.detect(content[:ENCODING_SAMPLE_BYTES])
    encoding = (result.get("encoding") or "utf-8")
    confidence = float(result.get("confidence") or 0.0)
    if encoding.lower() in ("ascii", "us-ascii"):
        encoding = "utf-8"
    return (encoding, confidence)


def _decode(content: bytes, encoding: str) -> str:
    for enc in (encoding, "utf-8", "ISO-8859-1"):
        try:
            return content.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return content.decode("utf-8", errors="replace")


def _numeric_fraction(cells: List[str]) -> float:
    non_empty = [c for c in cells if c.strip() != ""]
    if not non_empty:
        return 0.0
    parsed = 0
    for value in non_empty:
        try:
            float(value.strip().replace(",", ""))
            parsed += 1
        except ValueError:
            pass
    return parsed / len(non_empty)


def _looks_headerless(sample_text: str) -> bool:
    """Heuristic: a header row is usually non-numeric while data rows are numeric."""
    try:
        rows = [row for _, row in zip(range(6), csv.reader(io.StringIO(sample_text)))]
    except csv.Error:
        return False
    rows = [r for r in rows if r]
    if len(rows) < 2:
        return False
    first_numeric = _numeric_fraction(rows[0])
    rest = rows[1:]
    rest_numeric = sum(_numeric_fraction(r) for r in rest) / max(1, len(rest))
    return first_numeric >= 0.6 and first_numeric >= rest_numeric


def read_csv(content: bytes, filename: str) -> Tuple[pd.DataFrame, IngestionMeta]:
    if content is None or len(content.strip()) == 0:
        raise EmptyDataError("Uploaded file is empty.")

    encoding, confidence = detect_encoding(content)
    text = _decode(content, encoding)
    sample_text = "\n".join(text.splitlines()[:10])
    headerless = _looks_headerless(sample_text)

    warns: List[str] = []
    header_generated = False

    # Use the C parser: it is fast and, crucially, *skips* over-long rows rather
    # than mis-interpreting their leading fields as an index (which the python
    # engine does). Capturing its "Skipping line N" warnings lets us count the
    # malformed rows precisely.
    read_kwargs = dict(skip_blank_lines=True, on_bad_lines="warn", engine="c")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            if headerless:
                df = pd.read_csv(io.StringIO(text), header=None, **read_kwargs)
                df.columns = [f"column_{i + 1}" for i in range(df.shape[1])]
                header_generated = True
            else:
                df = pd.read_csv(io.StringIO(text), **read_kwargs)
        except pd.errors.EmptyDataError:
            raise EmptyDataError("No columns to parse from file.")
        except Exception as exc:  # noqa: BLE001 - surfaced as a typed pipeline error
            raise MalformedDataError(f"Failed to parse CSV: {exc}")

    skipped = sum(
        1 for w in caught
        if "skip" in str(w.message).lower() or "bad line" in str(w.message).lower()
    )

    # Drop entirely-empty columns and normalise unnamed/blank headers.
    df = df.dropna(axis=1, how="all")
    normalised_cols = []
    for i, col in enumerate(df.columns):
        name = str(col)
        if name.startswith("Unnamed") or name.strip() == "" or name == "nan":
            normalised_cols.append(f"column_{i + 1}")
            header_generated = True
        else:
            normalised_cols.append(name)
    df.columns = normalised_cols

    if df.shape[0] == 0 or df.shape[1] == 0:
        raise EmptyDataError("CSV contains no data rows after parsing.")

    if confidence and confidence < 0.5:
        warns.append(f"Low confidence ({confidence:.2f}) in detected encoding '{encoding}'.")
    if skipped:
        warns.append(f"Skipped {skipped} malformed row(s) during parsing.")
    if header_generated:
        warns.append("Header row missing or unnamed — generated column names automatically.")

    meta = IngestionMeta(
        filename=filename,
        detected_encoding=encoding,
        encoding_confidence=round(confidence, 4),
        rows_raw=int(df.shape[0]),
        columns=int(df.shape[1]),
        skipped_bad_rows=int(skipped),
        header_generated=header_generated,
        warnings=warns,
    )
    logger.info("Ingested %s: %d rows x %d cols (enc=%s, skipped=%d)",
                filename, df.shape[0], df.shape[1], encoding, skipped)
    return df, meta
