"""Continuous-only winsorization with explicit cuts.

Product contract: ``clean_winsor`` always passes ``cuts=(1, 99)`` and
``replace=True`` into pywinsor2. That is not Stata ``winsor2``'s default
call (implicit cuts, ``replace=False``, ``_w`` suffix columns).
"""
from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

logger = logging.getLogger(__name__)

WINSOR_CUTS = (1, 99)
ENGINE_PYWINSOR2 = "pywinsor2"
ENGINE_PANDAS = "pandas"


def is_continuous_column(series: pd.Series) -> bool:
    """Numeric with more than two distinct values (excludes binary / constants)."""
    if not pd.api.types.is_numeric_dtype(series):
        return False
    return int(series.nunique(dropna=True)) > 2


def _normalized_cuts(cuts: Sequence[float] | None) -> tuple[int, int]:
    if cuts is None:
        return WINSOR_CUTS
    return (int(cuts[0]), int(cuts[1]))


def _skip_reason(
    column: str,
    series: pd.Series,
    protected: set[str],
) -> str | None:
    if column in protected:
        return "protected"
    if not pd.api.types.is_numeric_dtype(series):
        return "non_numeric"
    if not is_continuous_column(series):
        return "not_continuous"
    return None


def _n_changed(before: pd.Series, after: pd.Series) -> int:
    unchanged = before.eq(after) | (before.isna() & after.isna())
    return int((~unchanged).sum())


def _winsorize_pandas(
    df: pd.DataFrame, cols: list[str], cuts: tuple[int, int]
) -> pd.DataFrame:
    out = df.copy()
    lo, hi = cuts[0] / 100.0, cuts[1] / 100.0
    for col in cols:
        series = out[col]
        non_nan = series.dropna()
        if non_nan.empty:
            continue
        lower = non_nan.quantile(lo)
        upper = non_nan.quantile(hi)
        out[col] = series.clip(lower=lower, upper=upper)
    return out


def _apply_pywinsor2(
    df: pd.DataFrame, cols: list[str], cuts: tuple[int, int]
) -> pd.DataFrame:
    import pywinsor2 as pw2

    # cuts and replace are always explicit: never inherit Stata/library defaults.
    result = pw2.winsor2(
        df,
        cols,
        cuts=cuts,
        replace=True,
        trim=False,
        copy=True,
    )
    if isinstance(result, tuple):
        return result[0]
    return result


def clean_winsor(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    *,
    cuts: Sequence[float] | None = WINSOR_CUTS,
    protected_columns: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Winsorize continuous columns at explicit percentile cuts.

    Args:
        df: Input frame. The original is not mutated when the engine copies.
        columns: Candidate columns. ``None`` means every column in ``df``.
        cuts: Inclusive percentile bounds. ``None`` falls back to ``(1, 99)``;
            the value is always passed through to the engine.
        protected_columns: Design columns that must not be clipped (ids, treat).

    Returns:
        ``(frame, audit)`` where ``audit`` records engine, cuts, columns, and
        how many cells changed. ``stata_default`` is always False.
    """
    cuts_t = _normalized_cuts(cuts)
    protected = {str(name) for name in (protected_columns or ())}
    candidates = list(columns) if columns is not None else list(df.columns)

    winsor_cols: list[str] = []
    skipped: dict[str, str] = {}
    seen: set[str] = set()
    for column in candidates:
        if column in seen or column not in df.columns:
            continue
        seen.add(column)
        reason = _skip_reason(column, df[column], protected)
        if reason is not None:
            skipped[column] = reason
            continue
        winsor_cols.append(column)

    audit: dict[str, Any] = {
        "cuts": [cuts_t[0], cuts_t[1]],
        "engine": None,
        "columns": list(winsor_cols),
        "skipped": skipped,
        "n_changed": {},
        "stata_default": False,
        "replace": True,
    }
    if not winsor_cols:
        return df, audit

    before = {col: df[col].copy() for col in winsor_cols}
    try:
        out = _apply_pywinsor2(df, winsor_cols, cuts_t)
        engine = ENGINE_PYWINSOR2
    except ImportError:
        logger.warning("pywinsor2 not available; falling back to pandas")
        out = _winsorize_pandas(df, winsor_cols, cuts_t)
        engine = ENGINE_PANDAS
    except Exception:
        logger.warning(
            "pywinsor2.winsor2 failed; falling back to pandas",
            exc_info=True,
        )
        out = _winsorize_pandas(df, winsor_cols, cuts_t)
        engine = ENGINE_PANDAS

    audit["engine"] = engine
    audit["n_changed"] = {
        col: _n_changed(before[col], out[col]) for col in winsor_cols
    }
    return out, audit


def winsor_audit_row(
    audit: Mapping[str, Any],
    *,
    before: dict,
    after: dict,
    iqr_outliers: dict,
) -> dict[str, Any]:
    """Dataset-level outliers payload: existing keys plus the winsor audit."""
    columns = list(audit.get("columns") or [])
    return {
        "before": before,
        "after": after,
        "iqr_outliers": iqr_outliers,
        "winsorized": bool(columns),
        "cuts": list(audit.get("cuts") or list(WINSOR_CUTS)),
        "engine": audit.get("engine"),
        "columns": columns,
        "skipped": dict(audit.get("skipped") or {}),
        "n_changed": dict(audit.get("n_changed") or {}),
        "stata_default": False,
        "replace": True,
    }
