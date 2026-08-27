"""EDA sidebar endpoint (T-03).

POST /sessions/{session_id}/eda accepts {action: ...} and runs the
corresponding exploratory data analysis on the session's uploaded CSV.

StatsPAI integration (per T-03 验收项):
- ``sp.describe(df)`` provides per-variable metadata (type / n / n_missing).
  Used for the missing-count column and to exercise the StatsPAI surface.
- ``sp.pwcorr`` returns a formatted text string (not a clean numeric
  matrix), so the Pearson matrix is computed via ``pandas df.corr()``.
  The ticket explicitly allows the pandas fallback when StatsPAI's output
  is not suitable for the JSON contract.

Session state is read from ``AgentFacade`` (which owns the in-memory
session store). The CSV path is stored at the top level of the session
entry by the upload handler (``sessions.py``).

The router is registered in ``main.py`` via ``app.include_router(eda_router)``.
"""
from __future__ import annotations

import math
from typing import Any, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import EdaResponse

router = APIRouter()

_VALID_ACTIONS = {"describe", "corr", "plot", "scatter", "regression", "missing"}


class EdaRequest(BaseModel):
    """POST /sessions/{id}/eda 请求体。"""

    action: str
    model_config = {"extra": "allow"}


def _get_csv_path(session_id: str) -> str:
    """Look up the session's CSV path via the facade."""
    return facade.get_csv_path(session_id)


def _load_df(session_id: str) -> pd.DataFrame:
    """Read the session's CSV into a DataFrame."""
    return pd.read_csv(_get_csv_path(session_id))


def _to_jsonable(value: Any) -> Any:
    """Convert pandas/numpy scalars to JSON-friendly Python scalars (None for NaN)."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return value


def _run_describe(df: pd.DataFrame) -> dict:
    """Per-variable statistics table.

    StatsPAI ``sp.describe(df)`` supplies n / n_missing metadata;
    pandas ``df.describe()`` supplies the statistical moments
    (mean / std / min / max). Falls back to pandas for missing count
    if StatsPAI is unavailable on the session's data.
    """
    missing_by_col: dict[str, int] = {}
    try:
        import statspai as sp  # StatsPAI integration per T-03 验收项

        meta = sp.describe(df)  # DataFrame[variable, type, n, n_missing, label]
        for _, row in meta.iterrows():
            missing_by_col[str(row["variable"])] = int(row["n_missing"])
    except Exception:
        # Fallback: compute missing counts from pandas if StatsPAI is unavailable.
        missing_by_col = {str(col): int(df[col].isna().sum()) for col in df.columns}

    columns = ["variable", "count", "mean", "std", "min", "max", "missing"]
    rows: list[dict[str, Any]] = []
    for col in df.columns:
        s = df[col]
        is_numeric = pd.api.types.is_numeric_dtype(s)
        has_values = s.count() > 0
        rows.append(
            {
                "variable": str(col),
                "count": int(s.count()),
                "mean": _to_jsonable(float(s.mean()) if is_numeric and has_values else None),
                "std": _to_jsonable(
                    float(s.std()) if is_numeric and s.count() > 1 else None
                ),
                "min": _to_jsonable(
                    float(s.min()) if is_numeric and has_values
                    else (s.min() if has_values else None)
                ),
                "max": _to_jsonable(
                    float(s.max()) if is_numeric and has_values
                    else (s.max() if has_values else None)
                ),
                "missing": int(missing_by_col.get(str(col), int(s.isna().sum()))),
            }
        )
    return {"columns": columns, "rows": rows}


def _run_corr(df: pd.DataFrame) -> dict:
    """Pearson correlation matrix over numeric columns."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return {"variables": [], "matrix": []}
    corr = numeric_df.corr(method="pearson")
    variables = [str(c) for c in corr.columns]
    matrix = [[_to_jsonable(v) for v in row] for row in corr.values.tolist()]
    return {"variables": variables, "matrix": matrix}


def _run_missing(df: pd.DataFrame) -> dict:
    """Per-variable missing-value report."""
    n = len(df)
    columns = ["variable", "missing_count", "missing_pct"]
    rows = [
        {
            "variable": str(col),
            "missing_count": int(df[col].isna().sum()),
            "missing_pct": float(df[col].isna().sum() / n) if n else 0.0,
        }
        for col in df.columns
    ]
    return {"columns": columns, "rows": rows}


@router.post(
    "/sessions/{session_id}/eda",
    response_model=EdaResponse,
)
async def run_eda(
    session_id: str,
    payload: EdaRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> EdaResponse:
    """Run an EDA action on the session's dataset.

    Request body: ``{"action": "describe"|"corr"|"plot"|"scatter"|"regression"|"missing"}``.
    - ``describe`` → ``{columns, rows}`` per-variable stats table.
    - ``corr``     → ``{variables, matrix}`` Pearson correlation matrix.
    - ``missing``  → ``{columns, rows}`` missing-value report.
    - ``plot`` / ``scatter`` / ``regression`` → placeholder (later tickets).

    Stage D：返回 ``EdaResponse``（``action`` + ``result``，``result`` 承载
    各 action 的具体 shape；``EdaResponse`` 用 ``extra="allow"`` 保留
    describe / corr / missing 的原始字段）。
    """
    require_session_ownership(session_id, current_user)
    action = payload.action
    if action not in _VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action!r}")

    df = await run_in_threadpool(_load_df, session_id)

    if action == "describe":
        result = await run_in_threadpool(_run_describe, df)
        return EdaResponse(action=action, result=result, **result)
    if action == "corr":
        result = await run_in_threadpool(_run_corr, df)
        return EdaResponse(action=action, result=result, **result)
    if action == "missing":
        result = await run_in_threadpool(_run_missing, df)
        return EdaResponse(action=action, result=result, **result)
    # plot / scatter / regression: T-03 returns a placeholder; later tickets implement.
    placeholder = {
        "message": "Not implemented yet",
        "placeholder": True,
    }
    return EdaResponse(action=action, result=placeholder, **placeholder)


# Router is registered in main.py via app.include_router(eda_router).
# No self-registration needed.
