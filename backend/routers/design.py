"""INF-BE-propose: title/question → ``session.design`` draft.

Does not confirm, attach data, or project onto ``research_direction``.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionDesignResponse

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
