"""/api/execute SSE endpoint.

L5-execution lane: 流式返回 ExecuteEvent（start / progress / section_done / paper_ready / done / error）。
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from Product.backend.wrapper.execute_service import run_execute_stream
from Product.types.research import ExecuteRequest

router = APIRouter()

# 仓库根目录：Manuscripts / Results / Tasks 直接放在 repo 根
_REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPTS_ROOT = _REPO_ROOT / "Manuscripts"
RESULTS_ROOT = _REPO_ROOT / "Results"
TASKS_ROOT = _REPO_ROOT / "Tasks"


@router.post("/api/execute")
def post_execute(req: ExecuteRequest) -> StreamingResponse:
    """SSE 流式执行实验。"""

    def event_stream():
        for event in run_execute_stream(
            req,
            manuscripts_root=MANUSCRIPTS_ROOT,
            results_root=RESULTS_ROOT,
            tasks_root=TASKS_ROOT,
        ):
            yield f"data: {json.dumps(event.model_dump(), ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
