"""FD-BE-plan / honesty / Card / Dataverse / WDI: confirmed design → find_data.

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
from schemas.responses import SessionFindDataResponse, WdiFetchResponse

from agent.find_data.candidates import apply_find_data_suggest
from agent.find_data.card_zip import (
    CardZipNotApplicable,
    fetch_card_zip,
    merge_card_zip_candidate,
)
from agent.find_data.dataverse import apply_dataverse_fetch
from agent.find_data.fetch_wdi import WdiFetchNotApplicable, fetch_wdi
from agent.find_data.honesty import project_honest_find_data
from agent.find_data.plan import (
    DesignUnconfirmed,
    build_find_data_plan,
    classify_route_family,
    is_confirmed_design,
    read_find_data,
)

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
    record = project_honest_find_data(merge_card_zip_candidate(record, candidate))
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
    record = project_honest_find_data(record)
    facade.update_state(session_id, find_data=record)
    return record


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
