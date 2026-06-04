"""POST /api/brief endpoint.

参考 spec §6.1 row 1 + Product/api/openapi.yaml 的 /api/brief schema.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from Product.backend.wrapper.brief_service import run_brief
from Product.types.research import BriefRequest, BriefResponse

router = APIRouter()

# 落盘到 repo 根的 Tasks/ 目录
_TASKS_ROOT = Path(__file__).resolve().parents[2] / "Tasks"


@router.post("/api/brief", response_model=BriefResponse)
def post_brief(req: BriefRequest) -> BriefResponse:
    """任务书 LLM 扩写 + 落盘 + verdict gate。"""
    try:
        return run_brief(req, _TASKS_ROOT)
    except Exception as exc:  # noqa: BLE001 — endpoint boundary
        raise HTTPException(status_code=500, detail=f"brief failed: {exc}") from exc
