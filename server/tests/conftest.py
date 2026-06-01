"""Shared pytest fixtures."""
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def mixed_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "score": [9.5, 8.1, 7.2, 100.0, 8.0],   # 100.0 is an outlier
        "category": ["A", "B", "A", "C", "B"],
        "age": [30.0, np.nan, 25.0, 40.0, 35.0],  # has a missing value
    })


@pytest.fixture
def sample_csv_bytes() -> bytes:
    return (
        b"name,age,city,score\n"
        b"Alice,30,NYC,9.5\n"
        b"Bob,25,LA,8.1\n"
        b"Alice,30,NYC,9.5\n"      # exact duplicate row
        b"Carol,,SF,7.2\n"         # missing age
        b"Dave,40,NYC,100.0\n"      # score outlier
    )
