"""FIND-DATA: plan + Dataverse fetch after confirmed session.design.

Does not attach data, confirm a design, or search literature.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionFindDataResponse

from agent.find_data.dataverse import apply_dataverse_fetch
from agent.find_data.plan import DesignUnconfirmed, build_find_data_plan, read_find_data

router = APIRouter()


class DataverseFetchRequest(BaseModel):
    """Optional chosen Dataverse dataset / file. Empty body searches then fetches."""

    source_id: Optional[str] = None
    file_id: Optional[str] = None


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
    "/sessions/{session_id}/find-data/fetch-dataverse",
    response_model=SessionFindDataResponse,
)
async def fetch_dataverse_endpoint(
    session_id: str,
    payload: DataverseFetchRequest = DataverseFetchRequest(),
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionFindDataResponse:
    """Search Dataverse and download a public file, else keep the URL."""
    require_session_ownership(session_id, current_user)
    record = await run_in_threadpool(_fetch_dataverse, session_id, payload)
    return SessionFindDataResponse.model_validate(record)


def _fetch_dataverse(session_id: str, payload: DataverseFetchRequest) -> dict:
    state = facade.get_state(session_id)
    workspace = Path(facade._workspace_dir(session_id))
    try:
        record = apply_dataverse_fetch(
            state,
            workspace=workspace,
            source_id=payload.source_id,
            file_id=payload.file_id,
        )
    except DesignUnconfirmed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    facade.update_state(session_id, find_data=record)
    return record
