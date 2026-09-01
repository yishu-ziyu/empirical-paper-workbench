"""REST endpoints for T-11: CHARLS dataset native wizard.

- GET  /sessions/{id}/charls/detect  — run the profiling detection on the
  session's uploaded CSV and return ``{dataset_type, charls_config?}``. The
  frontend uses this to decide whether to open the CharlsWizard modal.
- POST /sessions/{id}/charls/confirm  — accept the user-confirmed wizard
  payload (variable mapping + selected waves + applied filter presets) and
  persist it into the session state under ``charls_config``. Subsequent
  nodes then read readable variable names from this state slot.

Self-registration: ``_self_register()`` is invoked at module import to
attach this router to ``main.app`` (mirrors the eda.py pattern in T-03).
``main.py`` is not modified (T-11 file-boundary constraint).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import CharlsConfirmResponse, CharlsDetectResponse

router = APIRouter()


@router.get(
    "/sessions/{session_id}/charls/detect",
    response_model=CharlsDetectResponse,
)
async def detect_charls(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> CharlsDetectResponse:
    """Run the profiling dataset-type detector on the session CSV.

    Returns ``{dataset_type, charls_config?}``. ``charls_config`` is the
    parsed ``charls.yaml`` and is only included when the dataset is
    detected as CHARLS.
    """
    require_session_ownership(session_id, current_user)
    data = facade.detect_charls(session_id)
    return CharlsDetectResponse(**data)


class CharlsConfirmRequest(BaseModel):
    """POST /sessions/{id}/charls/confirm request body."""

    variable_mapping: Dict[str, str] = Field(default_factory=dict)
    waves: List[int] = Field(default_factory=list)
    filter_presets: List[Dict[str, Any]] = Field(default_factory=list)


@router.post(
    "/sessions/{session_id}/charls/confirm",
    response_model=CharlsConfirmResponse,
)
async def confirm_charls(
    session_id: str,
    payload: CharlsConfirmRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> CharlsConfirmResponse:
    """Persist the user-confirmed CHARLS wizard config into session state.

    The wizard payload is written to ``state["charls_config"]`` so
    downstream nodes (clean_data sub-steps, eda, outline) can read
    readable variable names instead of raw CHARLS codes.
    """
    require_session_ownership(session_id, current_user)
    charls_config = facade.confirm_charls(
        session_id,
        variable_mapping=payload.variable_mapping,
        waves=payload.waves,
        filter_presets=payload.filter_presets,
    )
    return CharlsConfirmResponse(ok=True, charls_config=charls_config)
