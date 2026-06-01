"""Tests for the file ingestion layer (encoding, headers, malformed rows)."""
import pytest

from app.services.ingestion_service import detect_encoding, read_csv
from app.utils.exceptions import EmptyDataError


def test_basic_csv():
    df, meta = read_csv(b"a,b,c\n1,2,3\n4,5,6\n", "t.csv")
    assert list(df.columns) == ["a", "b", "c"]
    assert df.shape == (2, 3)
    assert meta.header_generated is False


def test_empty_file_raises():
    with pytest.raises(EmptyDataError):
        read_csv(b"   ", "t.csv")


def test_iso8859_1_encoding_decodes():
    content = "name,city\nJose,Malaga\nRene,Munchen\n".replace("o", "\xf3").encode("ISO-8859-1")
    df, meta = read_csv(content, "t.csv")
    assert df.shape[0] == 2
    assert "name" in df.columns


def test_headerless_generates_headers():
    df, meta = read_csv(b"1,2,3\n4,5,6\n7,8,9\n", "t.csv")
    assert meta.header_generated is True
    assert df.columns[0] == "column_1"


def test_malformed_rows_are_skipped():
    df, meta = read_csv(b"a,b\n1,2\n1,2,3,4\n5,6\n", "t.csv")
    assert df.shape[0] == 2          # the 4-field bad row is skipped
    assert meta.skipped_bad_rows >= 1


def test_detect_encoding_returns_tuple():
    enc, conf = detect_encoding("hello,world\n1,2\n".encode("utf-8"))
    assert isinstance(enc, str)
    assert 0.0 <= conf <= 1.0
