"""Infer-design: title/question → draft, then human confirm locks it.

POST /sessions/{id}/design/propose writes ``status=draft``.
POST /sessions/{id}/design/confirm is the only transition that sets
``status=confirmed``. Neither attaches data, suggests catalog rows, or
writes chapters.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionDesignConfirmResponse, SessionDesignResponse

from agent.design.propose import propose_design

router = APIRouter()


class ProposeDesignRequest(BaseModel):
    """POST /sessions/{id}/design/propose 请求体。"""

    title: str
    question: str = ""


@router.post(
    "/sessions/{session_id}/design/propose",
    response_model=SessionDesignResponse,
)
async def propose_design_endpoint(
    session_id: str,
    payload: ProposeDesignRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionDesignResponse:
    """Propose a research-design draft from the session title (+ optional RQ)."""
    require_session_ownership(session_id, current_user)
    title = payload.title.strip()
    question = payload.question.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title required")
    try:
        draft = propose_design(title, question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    facade.update_state(session_id, design=draft)
    return SessionDesignResponse.model_validate(draft)


@router.post(
    "/sessions/{session_id}/design/confirm",
    response_model=SessionDesignConfirmResponse,
)
async def confirm_design_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionDesignConfirmResponse:
    """Lock the current session.design draft. Fail closed if none exists."""
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    design = await run_in_threadpool(facade.confirm_design, session_id)
    return SessionDesignConfirmResponse(ok=True, design=design)
