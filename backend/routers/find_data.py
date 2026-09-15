"""FD-BE-plan + FD-BE-fetch-wdi.

Plan: confirmed session.design → session.find_data plan.
WDI fetch: confirmed growth design → session download or honest link.

Does not attach data, confirm a design, or search literature.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionFindDataResponse, WdiFetchResponse

from agent.find_data.fetch_wdi import WdiFetchNotApplicable, fetch_wdi
from agent.find_data.plan import DesignUnconfirmed, build_find_data_plan, read_find_data

router = APIRouter()


@router.get(
    "/sessions/{session_id}/find-data",
    response_model=SessionFindDataResponse,
)
async def get_find_data_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionFindDataResponse:
    """Read stored find-data plan. Empty unless design is confirmed."""
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    return SessionFindDataResponse.model_validate(read_find_data(state))


@router.post(
    "/sessions/{session_id}/find-data/plan",
    response_model=SessionFindDataResponse,
)
async def plan_find_data_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionFindDataResponse:
    """Emit where/how plan from confirmed design facets + R-sources."""
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    try:
        record = build_find_data_plan(state.get("design"))
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    facade.update_state(session_id, find_data=record)
    return SessionFindDataResponse.model_validate(record)


@router.post(
    "/sessions/{session_id}/find-data/fetch-wdi",
    response_model=WdiFetchResponse,
)
async def fetch_wdi_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> WdiFetchResponse:
    """Download WDI into the session workspace, or return the WDI link.

    Confirm-design required. Growth family only. Never copies the Barro
    fixture. Does not set dataAttached.
    """
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    workspace = Path(facade._workspace_dir(session_id))
    try:
        row = fetch_wdi(state.get("design"), workspace=workspace)
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except WdiFetchNotApplicable as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    stored = state.get("find_data")
    updated = dict(stored) if isinstance(stored, dict) else {}
    updated["wdi_fetch"] = row
    facade.update_state(session_id, find_data=updated)
    return WdiFetchResponse.model_validate(row)
