"""/api/system/status — Task 41 行为 3.

聚合 11 个 backend service 的状态, 状态条 (SystemStatusBar) 一次 fetch 拿全部.
Spec: ui-gap-fill-bdd-2026-06-05.md Task 41 行为 3.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from Product.api._paths import REPO_ROOT
from Product.backend.system_status_service import aggregate


router = APIRouter()


class SystemStatusRequest(BaseModel):
    """请求体。project_id 必填; topic_slug 可选, 仅用于显示."""

    project_id: str = Field(min_length=1)
    topic_slug: str = ""


@router.post("/api/system/status")
def post_system_status(req: SystemStatusRequest) -> dict:
    """聚合 11 service, 返回状态条所需的 4 项 (cap_count, cost_total, artifact_count, obs_status).

    单 service 失败不抛 — 字段为 null, UI graceful degradation.
    """
    # Note: product_root = repo_root for this status endpoint because the
    # system status is product-wide (not per-managed-project). The
    # product_root argument is required by `aggregate` to walk state/runs/
    # and state/product/ for cost events.
    return aggregate(REPO_ROOT, REPO_ROOT, req.project_id, req.topic_slug)
