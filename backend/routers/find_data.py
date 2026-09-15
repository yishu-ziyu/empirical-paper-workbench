"""FD-BE-plan + FD-BE-fetch-card: plan and Card zip staging after confirm.

Does not attach data, confirm a design, or search literature.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionFindDataResponse

from agent.find_data.card_zip import (
    CardZipNotApplicable,
    fetch_card_zip,
    merge_card_zip_candidate,
)
from agent.find_data.plan import (
    DesignUnconfirmed,
    build_find_data_plan,
    classify_route_family,
    is_confirmed_design,
    read_find_data,
)

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
    "/sessions/{session_id}/find-data/fetch-card",
    response_model=SessionFindDataResponse,
)
async def fetch_card_zip_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionFindDataResponse:
    """Download author-posted Card zip into session, or keep link + upload."""
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    design = state.get("design")
    if not is_confirmed_design(design):
        raise HTTPException(status_code=409, detail="design_unconfirmed")
    if classify_route_family(design) != "minwage":
        raise HTTPException(status_code=409, detail="not_minwage")
    workspace = Path(facade._workspace_dir(session_id))
    try:
        candidate = await run_in_threadpool(fetch_card_zip, design, workspace)
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except CardZipNotApplicable as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    record = read_find_data(state)
    if record.get("status") != "planned":
        record = build_find_data_plan(design)
    record = merge_card_zip_candidate(record, candidate)
    facade.update_state(session_id, find_data=record)
    return SessionFindDataResponse.model_validate(record)
