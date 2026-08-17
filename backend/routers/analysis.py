"""识别验真 / 稳健性：页面上能点的两个入口。"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from facade import facade

router = APIRouter()


class IdentificationResponse(BaseModel):
    passed: bool
    star_rating: Optional[int] = None
    identification_failed: bool = False
    diagnosis: Dict[str, Any] = Field(default_factory=dict)


class RobustnessResponse(BaseModel):
    robustness_results: Dict[str, Any] = Field(default_factory=dict)
    spec_curve: Optional[Dict[str, Any]] = None


@router.post(
    "/sessions/{session_id}/identification",
    response_model=IdentificationResponse,
)
async def run_identification(session_id: str) -> IdentificationResponse:
    result = facade.run_identification_verify(session_id)
    return IdentificationResponse(
        passed=bool(result.get("passed")),
        star_rating=result.get("star_rating"),
        identification_failed=bool(result.get("identification_failed")),
        diagnosis=result.get("diagnosis") or {},
    )


@router.post(
    "/sessions/{session_id}/robustness",
    response_model=RobustnessResponse,
)
async def run_robustness(session_id: str) -> RobustnessResponse:
    result = facade.run_robustness_check(session_id)
    return RobustnessResponse(
        robustness_results=result.get("robustness_results") or {},
        spec_curve=result.get("spec_curve"),
    )
