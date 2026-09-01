"""Run 工件查询端点：把磁盘上的 trace / checkpoints / outputs 暴露成 API。

北极星"每一步可查"的读侧：
- GET /sessions/{id}/artifacts  → manifest + 全部文件清单
- GET /sessions/{id}/trace      → trace.jsonl 尾部事件流

只读端点；写入由 facade 在各节点执行时完成（见 run_store.py）。
"""

from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import run_store
from auth import get_optional_user, require_session_ownership
from models.user import User

router = APIRouter()


class ArtifactFile(BaseModel):
    path: str
    bytes: int


class ArtifactsResponse(BaseModel):
    session_id: str
    exists: bool
    manifest: Optional[dict] = None
    files: List[ArtifactFile] = []


class TraceEvent(BaseModel):
    ts: str
    node: str
    status: str
    duration_ms: Optional[float] = None
    detail: Optional[dict] = None


class TraceResponse(BaseModel):
    session_id: str
    total_returned: int
    events: List[TraceEvent] = []


@router.get("/sessions/{session_id}/artifacts", response_model=ArtifactsResponse)
async def get_artifacts(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ArtifactsResponse:
    """列出某 session 的 run 目录：manifest + 文件树。

    会话不存在 → 404；会话存在但尚无 run 目录（还没跑过任何被追踪的
    步骤）→ exists=False + 空清单，前端渲染空态。
    鉴权：与其它 session 路由一致，校验 ownership（匿名会话仅 DEBUG 放行）。
    """
    require_session_ownership(session_id, current_user)
    files = run_store.list_files(session_id)
    return ArtifactsResponse(
        session_id=session_id,
        exists=bool(files),
        manifest=run_store.read_manifest(session_id),
        files=[ArtifactFile(**f) for f in files],
    )


@router.get("/sessions/{session_id}/trace", response_model=TraceResponse)
async def get_trace(
    session_id: str,
    limit: int = 50,
    current_user: Optional[User] = Depends(get_optional_user),
) -> TraceResponse:
    """返回 trace.jsonl 的尾部事件流（默认最近 50 条）。"""
    require_session_ownership(session_id, current_user)
    limit = max(1, min(limit, 500))
    events = run_store.tail_events(session_id, limit=limit)
    return TraceResponse(
        session_id=session_id,
        total_returned=len(events),
        events=[
            TraceEvent(
                ts=e.get("ts", ""),
                node=e.get("node", ""),
                status=e.get("status", "ok"),
                duration_ms=e.get("duration_ms"),
                detail=e.get("detail"),
            )
            for e in events
        ],
    )
