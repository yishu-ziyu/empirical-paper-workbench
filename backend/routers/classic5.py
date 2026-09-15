"""TITLE/TOPIC → classic-5 candidate ranking (DC-BE-suggest).

Read-only: ranks catalog entries and returns a non-catalog own-file
action. Does not attach, admit uploads, or write ``dataAttached``.
Formal econpaper path only — not ``/demos/card``.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_optional_user, require_auth_unless_debug
from models.user import User
from schemas.responses import Classic5SuggestResponse
from services.classic5_catalog import suggest_candidates

router = APIRouter()


class Classic5SuggestRequest(BaseModel):
    """POST /classic-5/suggest 请求体：TITLE/TOPIC 文本。"""

    title: str = ""
    topic: str = ""


@router.post(
    "/classic-5/suggest",
    response_model=Classic5SuggestResponse,
    summary="Rank classic-5 candidates from TITLE/TOPIC",
)
async def suggest_classic5(
    body: Classic5SuggestRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> Classic5SuggestResponse:
    """Rank built-in classic-5 catalog entries for a title/topic.

    Returns ranked candidates plus a non-catalog own-file action.
    Does not attach, admit an upload, or write ``dataAttached``.
    """
    require_auth_unless_debug(current_user)
    title = (body.title or "").strip()
    topic = (body.topic or "").strip()
    if not title and not topic:
        raise HTTPException(status_code=400, detail="title or topic is required")
    return Classic5SuggestResponse.model_validate(suggest_candidates(title, topic))
