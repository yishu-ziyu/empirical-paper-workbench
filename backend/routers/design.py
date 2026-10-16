"""Infer-design: title/question → draft, then human confirm locks it.

POST /sessions/{id}/design/propose writes ``status=draft``.
POST /sessions/{id}/design/confirm is the only transition that sets
``status=confirmed``. Neither attaches data, suggests catalog rows, or
writes chapters.
"""
from __future__ import annotations

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionDesignConfirmResponse, SessionDesignResponse
from services.formal_binding import supersede_design

from agent.design.propose import propose_design
from agent.norms.loader import assert_propose_gates
from agent.design.propose_data import apply_design_overrides, map_design_to_data

router = APIRouter()


class DesignOverrides(BaseModel):
    """User edits to the draft. Column names must exist in the attached data."""

    method: Optional[str] = None
    outcome: Optional[str] = None
    treatment: Optional[str] = None
    controls: Optional[List[str]] = None
    heterogeneity_groups: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    group: Optional[str] = None
    treated: Optional[str] = None
    period: Optional[str] = None
    time_col: Optional[str] = None
    id_col: Optional[str] = None
    qType: Optional[str] = None


class ProposeDesignRequest(BaseModel):
    """POST /sessions/{id}/design/propose 请求体。

    With a dataset already on the session, the draft's variable slots are
    mapped to real columns (generate model + schema validation). ``overrides``
    is the user's own edit of the draft and wins over the proposal.
    """

    title: str
    question: str = ""
    overrides: Optional[DesignOverrides] = None


def _session_dataset(session_id: str) -> dict:
    try:
        entry = facade.get_session_entry(session_id) or {}
    except Exception:
        return {}
    keys = ("name", "rows", "columns", "dtypes", "variable_labels", "value_labels")
    return {key: entry.get(key) for key in keys if entry.get(key) is not None}


class ConfirmDesignRequest(BaseModel):
    """POST /sessions/{id}/design/confirm 请求体（可选）。

    ``expectedRevision`` 是客户端确认时看到的草稿版本（``design.revision``）。
    另一窗口替换草稿后，确认明确冲突，而不是确认一份用户没看过的草稿。
    """

    expectedRevision: Optional[str] = None


@router.post(
    "/sessions/{session_id}/design/propose",
    response_model=SessionDesignResponse,
)
async def propose_design_endpoint(
    session_id: str,
    payload: ProposeDesignRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionDesignResponse:
    """Propose a research-design draft from the session title (+ optional RQ).

    A new draft supersedes the previous approved version: its approvals and the
    preview built for it stop counting (the archived copy stays readable), so a
    re-proposed design never runs behind the old confirmation.
    """
    require_session_ownership(session_id, current_user)
    title = payload.title.strip()
    question = payload.question.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title required")
    try:
        draft = propose_design(title, question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    dataset = await run_in_threadpool(_session_dataset, session_id)
    if dataset.get("columns"):
        draft = await run_in_threadpool(
            lambda: map_design_to_data(draft, dataset, title=title, question=question)
        )
    if payload.overrides is not None:
        try:
            draft = apply_design_overrides(
                draft,
                payload.overrides.model_dump(exclude_none=True),
                dataset.get("columns") or [],
            )
        except ValueError as exc:
            code, _, column = str(exc).partition(":")
            raise HTTPException(
                status_code=400,
                detail={"code": code, "column": column} if column else {"code": code},
            ) from exc
    if dataset.get("columns") or payload.overrides is not None:
        try:
            assert_propose_gates(draft)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={"code": str(exc), "proposal": draft.get("proposal") or {}},
            ) from exc
    draft["revision"] = str(uuid4())
    await run_in_threadpool(
        facade.mutate_state, session_id,
        lambda state: supersede_design(state, draft),
    )
    return SessionDesignResponse.model_validate(draft)


@router.post(
    "/sessions/{session_id}/design/confirm",
    response_model=SessionDesignConfirmResponse,
)
async def confirm_design_endpoint(
    session_id: str,
    payload: Optional[ConfirmDesignRequest] = None,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionDesignConfirmResponse:
    """Lock the current session.design draft. Fail closed if none exists.

    Formal sessions must name the observed revision. Comparison and lock are
    performed together in the session store; only legacy callers may omit it.
    """
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    expected = (payload.expectedRevision or "").strip() if payload else None
    design = await run_in_threadpool(facade.confirm_design, session_id, expected)
    return SessionDesignConfirmResponse(ok=True, design=design)
