"""Infer-design: title/question → draft, then human confirm locks it.

POST /sessions/{id}/design/propose writes ``status=draft``.
POST /sessions/{id}/design/confirm is the only transition that sets
``status=confirmed``. Neither attaches data, suggests catalog rows, or
writes chapters.
"""
from __future__ import annotations

from typing import Optional
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

router = APIRouter()


class ProposeDesignRequest(BaseModel):
    """POST /sessions/{id}/design/propose 请求体。"""

    title: str
    question: str = ""


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
