"""POST /api/brief endpoint.

参考 spec §6.1 row 1 + Product/api/openapi.yaml 的 /api/brief schema.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from Product.api._paths import TASKS_ROOT
from Product.backend.wrapper.brief_service import run_brief
from Product.types.research import BriefRequest, BriefResponse

router = APIRouter()


@router.post("/api/brief", response_model=BriefResponse)
def post_brief(req: BriefRequest) -> BriefResponse:
    """任务书 LLM 扩写 + 落盘 + verdict gate。"""
    try:
        return run_brief(req, TASKS_ROOT)
    except Exception as exc:  # noqa: BLE001 — endpoint boundary
        raise HTTPException(status_code=500, detail=f"brief failed: {exc}") from exc
