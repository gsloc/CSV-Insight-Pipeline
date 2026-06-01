"""End-to-end API tests exercising the full pipeline via FastAPI's TestClient."""
import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _csv() -> bytes:
    return (
        b"name,age,city,score\n"
        b"Alice,30,NYC,9.5\n"
        b"Bob,25,LA,8.1\n"
        b"Alice,30,NYC,9.5\n"
        b"Carol,,SF,7.2\n"
        b"Dave,40,NYC,100.0\n"
    )


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "median" in body["missing_strategies"]


def test_analyze_end_to_end():
    r = client.post(
        "/api/v1/analyze",
        files={"file": ("data.csv", _csv(), "text/csv")},
        data={"missing_strategy": "median", "outlier_method": "iqr"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("meta", "schema", "data_quality", "cleaning", "analysis", "insights", "preview"):
        assert key in body
    # duplicate Alice row detected
    assert body["data_quality"]["duplicate_rows"] >= 1
    # cleaning produced fewer rows than raw (dedupe)
    assert body["cleaning"]["rows_after"] < body["cleaning"]["rows_before"]
    # response must be strictly valid JSON (no NaN tokens)
    json.dumps(body)  # raises if any non-serialisable / NaN leaked through


def test_analyze_empty_returns_400():
    r = client.post("/api/v1/analyze", files={"file": ("empty.csv", b"   ", "text/csv")})
    assert r.status_code == 400


def test_analyze_invalid_strategy_returns_422():
    r = client.post(
        "/api/v1/analyze",
        files={"file": ("data.csv", _csv(), "text/csv")},
        data={"missing_strategy": "bogus"},
    )
    assert r.status_code == 422


def test_analyze_single_column_skips_correlation():
    csv = b"value\n1\n2\n3\n4\n5\n"
    r = client.post("/api/v1/analyze", files={"file": ("one.csv", csv, "text/csv")})
    assert r.status_code == 200
    body = r.json()
    assert body["analysis"]["has_correlation"] is False
    assert body["analysis"]["correlation"] is None
