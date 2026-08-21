"""Sample construction endpoints (T-05).

Three POST endpoints for the back-half of the clean_data pipeline:
- ``/sessions/{id}/transform`` -- variable recoding & construction (sub-step 5)
- ``/sessions/{id}/filter``     -- sample filtering (sub-step 6)
- ``/sessions/{id}/balance``    -- panel balance check (sub-step 7)

Each endpoint delegates to ``AgentFacade``, which reads the session's CSV
path from its in-memory session store, runs the corresponding cleaning
module, and returns the report. The cleaning modules live in
``agent/cleaning/`` and are imported by the facade (routers no longer
import ``cleaning.X`` directly).

Router self-registration: ``_self_register()`` attaches the router to
``main.app`` on import, matching the ``eda.py`` pattern so ``main.py``
does not need to be modified (T-05 file-boundary constraint).
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import (
    BalanceResponse,
    FilterResultResponse,
    TransformResponse,
)

router = APIRouter()
_REGISTERED = False


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class TransformRequest(BaseModel):
    """POST /sessions/{id}/transform 请求体（flat form）。"""

    type: str = "log_transform"
    column: str = ""
    # 其它字段按 vtype 透传到 _build_transform_config
    model_config = {"extra": "allow"}


class FilterConditionItem(BaseModel):
    """filter 条件项。"""

    col: str
    op: str
    val: object = None

    model_config = {"extra": "allow"}


class FilterRequest(BaseModel):
    """POST /sessions/{id}/filter 请求体。"""

    conditions: list[FilterConditionItem] = Field(default_factory=list)


class BalanceRequest(BaseModel):
    """POST /sessions/{id}/balance 请求体。"""

    panel_id: str = ""
    time_col: str = ""


# --------------------------------------------------------------------------- #
# Sub-step 5: transform
# --------------------------------------------------------------------------- #

@router.post(
    "/sessions/{session_id}/transform",
    response_model=TransformResponse,
)
async def run_transform(
    session_id: str,
    payload: TransformRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> TransformResponse:
    """Apply variable recoding & construction (sub-step 5).

    Request body (flat form, matching the frontend VariableConstructor):
    ``{"type": "log_transform"|"onehot"|"label"|"bin"|"interaction"|"policy_dummy",
       "column": str, ...}``

    The flat ``type``/``column`` is translated into the nested config that
    ``cleaning.transform.transform`` expects.
    """
    require_session_ownership(session_id, current_user)
    vtype = payload.type
    column = payload.column
    # 透传 extra 字段（method / n / other_column / treat_col / post_col / name）
    extra = payload.model_dump(exclude={"type", "column"})

    config = _build_transform_config(vtype, column, extra)
    datasets = await run_in_threadpool(
        facade.transform_variables, session_id, config
    )

    constructed = datasets[0].get("constructed_vars", []) if datasets else []
    return TransformResponse(constructed_vars=constructed)


def _build_transform_config(vtype: str, column: str, payload: dict) -> dict:
    """Translate the flat frontend payload into the nested transform config."""
    config: dict = {}
    if vtype == "log_transform":
        config["log_transform"] = [column]
    elif vtype == "onehot":
        config["encodings"] = {column: "onehot"}
    elif vtype == "label":
        config["encodings"] = {column: "label"}
    elif vtype == "bin":
        method = payload.get("method", "equal_width")
        n = int(payload.get("n", 5))
        config["bins"] = {column: {"method": method, "n": n}}
    elif vtype == "interaction":
        other = payload.get("other_column", "")
        if other:
            config["interactions"] = [[column, other]]
    elif vtype == "policy_dummy":
        treat = payload.get("treat_col", column)
        post = payload.get("post_col", "")
        name = payload.get("name", "treat_post")
        if post:
            config["policy_dummies"] = {name: {"treat": treat, "post": post}}
    return config


# --------------------------------------------------------------------------- #
# Sub-step 6: filter
# --------------------------------------------------------------------------- #

@router.post(
    "/sessions/{session_id}/filter",
    response_model=FilterResultResponse,
)
async def run_filter(
    session_id: str,
    payload: FilterRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> FilterResultResponse:
    """Apply sample filtering (sub-step 6).

    Request body: ``{"conditions": [{"col": str, "op": str, "val": Any}, ...]}``
    """
    require_session_ownership(session_id, current_user)
    conditions = [c.model_dump() for c in payload.conditions]
    datasets = await run_in_threadpool(
        facade.filter_sample, session_id, conditions
    )

    if not datasets:
        return FilterResultResponse(
            n_before=0, n_after=0, conditions=conditions
        )
    report = datasets[0].get("filter", {})
    return FilterResultResponse(
        n_before=report.get("n_before", 0),
        n_after=report.get("n_after", 0),
        conditions=report.get("conditions", conditions),
    )


# --------------------------------------------------------------------------- #
# Sub-step 7: balance
# --------------------------------------------------------------------------- #

@router.post(
    "/sessions/{session_id}/balance",
    response_model=BalanceResponse,
)
async def run_balance(
    session_id: str,
    payload: BalanceRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> BalanceResponse:
    """Check panel balance (sub-step 7).

    Request body: ``{"panel_id": str, "time_col": str}``

    Stage D 修复漂移 1：返回 ``BalanceResponse``（4 字段：
    ``balanced`` / ``unbalanced`` / ``n_periods`` / ``attrition_rate``），
    不再直接透传 step report。``unbalanced`` 在 router 层补算
    （总 panel 数 - balanced 数），因为 BalanceStep 的 step report 不含
    ``unbalanced`` 字段（只有 ``balanced`` / ``n_periods`` /
    ``attrition_rate``）。
    """
    require_session_ownership(session_id, current_user)
    if not payload.panel_id or not payload.time_col:
        raise HTTPException(
            status_code=400, detail="panel_id and time_col are required"
        )
    report = await run_in_threadpool(
        facade.balance_panel,
        session_id,
        payload.panel_id,
        payload.time_col,
    )
    # 补算 unbalanced：总 panel 数 - balanced 数
    unbalanced = _compute_unbalanced(session_id, payload.panel_id, report)
    return BalanceResponse(
        balanced=int(report.get("balanced", 0)),
        unbalanced=unbalanced,
        n_periods=int(report.get("n_periods", 0)),
        attrition_rate=float(report.get("attrition_rate", 0.0)),
    )


def _compute_unbalanced(session_id: str, panel_id: str, report: dict) -> int:
    """Compute ``unbalanced`` = total_panels - balanced.

    Defensive: any failure (CSV missing, column missing, etc.) → 0.
    """
    try:
        import pandas as pd

        csv_path = facade.get_csv_path(session_id)
        df = pd.read_csv(csv_path)
        if panel_id not in df.columns:
            return 0
        total_panels = int(df[panel_id].nunique())
        balanced = int(report.get("balanced", 0))
        return max(0, total_panels - balanced)
    except Exception:
        return 0


# --------------------------------------------------------------------------- #
# Self-registration
# --------------------------------------------------------------------------- #

def _self_register() -> None:
    """Attach this router to the FastAPI app on import (eda.py pattern)."""
    global _REGISTERED
    if _REGISTERED:
        return
    try:
        from main import app  # noqa: PLC0415

        app.include_router(router)
        _REGISTERED = True
    except Exception:
        # main not importable yet (e.g. during partial builds) -- skip silently.
        pass


_self_register()
