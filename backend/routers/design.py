"""Confirm-design: lock session.design (INF-BE-confirm).

POST /sessions/{id}/design/confirm is the only transition that sets
``status=confirmed``. It does not propose, attach, suggest, or write chapters.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import SessionDesignConfirmResponse

router = APIRouter()


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
