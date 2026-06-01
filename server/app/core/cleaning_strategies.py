"""Strategy Pattern for missing-value handling.

Each strategy encapsulates one approach to missing values. The factory
:func:`get_missing_value_strategy` resolves a strategy by name, so new strategies
can be registered without touching the calling service (Open/Closed Principle).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Type

import pandas as pd


# --------------------------------------------------------------------------- #
# Low-level column imputers (pure, individually unit-testable)
# --------------------------------------------------------------------------- #
def impute_mean(series: pd.Series) -> Tuple[pd.Series, Optional[float]]:
    numeric = pd.to_numeric(series, errors="coerce")
    fill = float(numeric.mean()) if numeric.notna().any() else None
    return (numeric.fillna(fill) if fill is not None else numeric, fill)


def impute_median(series: pd.Series) -> Tuple[pd.Series, Optional[float]]:
    numeric = pd.to_numeric(series, errors="coerce")
    fill = float(numeric.median()) if numeric.notna().any() else None
    return (numeric.fillna(fill) if fill is not None else numeric, fill)


def impute_mode(series: pd.Series) -> Tuple[pd.Series, Optional[object]]:
    modes = series.mode(dropna=True)
    fill = modes.iloc[0] if not modes.empty else None
    return (series.fillna(fill) if fill is not None else series, fill)


# --------------------------------------------------------------------------- #
# Transformation logging + result wrapper
# --------------------------------------------------------------------------- #
@dataclass
class Transformation:
    column: str
    action: str
    detail: str = ""
    count: int = 0

    def to_dict(self) -> dict:
        return {"column": self.column, "action": self.action,
                "detail": self.detail, "count": self.count}


@dataclass
class CleaningResult:
    df: pd.DataFrame
    transformations: List[Transformation] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #
class MissingValueStrategy(ABC):
    name: str = "base"

    @abstractmethod
    def apply(self, df: pd.DataFrame, numeric_cols: List[str]) -> CleaningResult:
        ...


class _NumericImputationStrategy(MissingValueStrategy):
    """Impute numeric columns with a numeric statistic, others with the mode."""

    numeric_action = ""

    def _numeric_fill(self, series: pd.Series) -> Tuple[pd.Series, Optional[float]]:
        raise NotImplementedError

    def apply(self, df: pd.DataFrame, numeric_cols: List[str]) -> CleaningResult:
        out = df.copy()
        tx: List[Transformation] = []
        for col in out.columns:
            n_missing = int(out[col].isna().sum())
            if n_missing == 0:
                continue
            if col in numeric_cols:
                out[col], fill = self._numeric_fill(out[col])
                fill_repr = round(fill, 4) if fill is not None else None
                tx.append(Transformation(col, self.numeric_action,
                                         f"filled {n_missing} nulls with {fill_repr}", n_missing))
            else:
                out[col], fill = impute_mode(out[col])
                tx.append(Transformation(col, "impute_mode",
                                         f"non-numeric column: filled {n_missing} nulls with mode={fill!r}",
                                         n_missing))
        return CleaningResult(out, tx)


class MeanImputationStrategy(_NumericImputationStrategy):
    name = "mean"
    numeric_action = "impute_mean"

    def _numeric_fill(self, series):
        return impute_mean(series)


class MedianImputationStrategy(_NumericImputationStrategy):
    name = "median"
    numeric_action = "impute_median"

    def _numeric_fill(self, series):
        return impute_median(series)


class ModeImputationStrategy(MissingValueStrategy):
    name = "mode"

    def apply(self, df: pd.DataFrame, numeric_cols: List[str]) -> CleaningResult:
        out = df.copy()
        tx: List[Transformation] = []
        for col in out.columns:
            n_missing = int(out[col].isna().sum())
            if n_missing == 0:
                continue
            out[col], fill = impute_mode(out[col])
            tx.append(Transformation(col, "impute_mode",
                                     f"filled {n_missing} nulls with mode={fill!r}", n_missing))
        return CleaningResult(out, tx)


class DropMissingStrategy(MissingValueStrategy):
    name = "drop"

    def apply(self, df: pd.DataFrame, numeric_cols: List[str]) -> CleaningResult:
        before = len(df)
        out = df.dropna(axis=0, how="any").reset_index(drop=True)
        removed = before - len(out)
        tx = [Transformation("*", "drop_missing_rows",
                             f"dropped {removed} rows containing missing values", removed)]
        return CleaningResult(out, tx)


_REGISTRY: Dict[str, Type[MissingValueStrategy]] = {
    MeanImputationStrategy.name: MeanImputationStrategy,
    MedianImputationStrategy.name: MedianImputationStrategy,
    ModeImputationStrategy.name: ModeImputationStrategy,
    DropMissingStrategy.name: DropMissingStrategy,
}


def get_missing_value_strategy(name: str) -> MissingValueStrategy:
    key = (name or "").strip().lower()
    if key not in _REGISTRY:
        raise ValueError(
            f"Unknown missing-value strategy '{name}'. Available: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[key]()


def available_strategies() -> List[str]:
    return sorted(_REGISTRY)
