"""FD-BE-plan / FD-BE-honesty: confirmed session.design → session.find_data.

Does not attach data, confirm a design, search literature, or download
Card/Dataverse/WDI bytes.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionFindDataResponse

from agent.find_data.candidates import apply_find_data_suggest
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
    prior = state.get("find_data") if isinstance(state.get("find_data"), dict) else None
    try:
        record = build_find_data_plan(state.get("design"), prior=prior)
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    facade.update_state(session_id, find_data=record)
    return SessionFindDataResponse.model_validate(record)


@router.post(
    "/sessions/{session_id}/find-data/suggest",
    response_model=SessionFindDataResponse,
)
async def suggest_find_data_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionFindDataResponse:
    """Label discovered / external_link candidates and optional teaching shelf."""
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    try:
        record = apply_find_data_suggest(state)
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    facade.update_state(session_id, find_data=record)
    return SessionFindDataResponse.model_validate(record)
