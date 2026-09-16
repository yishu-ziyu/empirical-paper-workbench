"""Confirmed ``session.design`` → classic-5 candidate ranking (DC-BE-suggest).

Read-only: ranks catalog entries that match a confirmed design and returns
a non-catalog own-file action. Does not attach, admit uploads, write
``dataAttached``, lock spec, or set ``allow_did``. Formal econpaper path
only — not ``/demos/card``.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_optional_user, require_auth_unless_debug
from facade import facade
from models.user import User
from schemas.responses import Classic5SuggestResponse
from services.classic5_catalog import suggest_candidates

router = APIRouter()


class Classic5SuggestRequest(BaseModel):
    """POST /classic-5/suggest 请求体：session + optional TITLE/TOPIC 文本。"""

    session_id: Optional[str] = None
    title: str = ""
    topic: str = ""


def _session_design(session_id: str | None) -> object:
    """Stub-read ``session.design``. Missing session → 404; missing design → None."""
    if not session_id or not session_id.strip():
        return None
    state = facade.get_state(session_id.strip())
    design = state.get("design")
    return design if isinstance(design, dict) else None


@router.post(
    "/classic-5/suggest",
    response_model=Classic5SuggestResponse,
    summary="Rank classic-5 candidates from a confirmed design",
)
async def suggest_classic5(
    body: Classic5SuggestRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> Classic5SuggestResponse:
    """Rank built-in classic-5 catalog entries for a confirmed design.

    Returns ranked candidates plus a non-catalog own-file action.
    Without a confirmed design, candidates are empty (not a catalog success).
    Does not attach, admit an upload, write ``dataAttached``, or lock spec.
    """
    require_auth_unless_debug(current_user)
    title = (body.title or "").strip()
    topic = (body.topic or "").strip()
    session_id = (body.session_id or "").strip() or None
    if not session_id and not title and not topic:
        raise HTTPException(
            status_code=400, detail="session_id or title or topic is required"
        )
    design = _session_design(session_id)
    return Classic5SuggestResponse.model_validate(
        suggest_candidates(title, topic, design=design)
    )
