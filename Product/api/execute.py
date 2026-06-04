"""/api/execute SSE endpoint.

L5-execution lane: 流式返回 ExecuteEvent（start / progress / section_done / paper_ready / done / error）。

失败模式 (spec §6.3, DoD #3):
- LLM 超时 / 数据缺失 / schema 异常 — 包在 try/except 里转成 error SSE 事件
- request 本身无效 (空 topic_slug / 缺路径) — 起点就 raise HTTPException 400
- 中途异常不会让连接 hang: 一个 error event 后 generator 正常结束
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from Product.backend.wrapper.execute_service import run_execute_stream
from Product.types.research import ExecuteEvent, ExecuteRequest

router = APIRouter()

log = logging.getLogger(__name__)

# 仓库根目录：Manuscripts / Results / Tasks 直接放在 repo 根
_REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPTS_ROOT = _REPO_ROOT / "Manuscripts"
RESULTS_ROOT = _REPO_ROOT / "Results"
TASKS_ROOT = _REPO_ROOT / "Tasks"


@router.post("/api/execute")
def post_execute(req: ExecuteRequest) -> StreamingResponse:
    """SSE 流式执行实验。失败 → error event 串到客户端。"""

    # 1. request 入口校验: 缺关键字段直接 HTTPException (还没进流, 可以正常抛)
    if not req.topic_slug or not req.topic_slug.strip():
        raise HTTPException(status_code=400, detail="topic_slug is required")
    if not req.brief_path or not req.variables_path or not req.design_path:
        raise HTTPException(
            status_code=400,
            detail="brief_path / variables_path / design_path are all required",
        )

    def event_stream():
        # 2. 流中途异常: 兜底 try/except 转 error event (SSE 不能 raise, 否则连接挂)
        try:
            for event in run_execute_stream(
                req,
                manuscripts_root=MANUSCRIPTS_ROOT,
                results_root=RESULTS_ROOT,
                tasks_root=TASKS_ROOT,
            ):
                yield f"data: {json.dumps(event.model_dump(), ensure_ascii=False)}\n\n"
        except Exception as exc:  # noqa: BLE001 — endpoint boundary
            log.exception("execute stream failed for %s", req.topic_slug)
            err = ExecuteEvent(
                event="error",
                stage="execute",
                message=f"execute failed: {exc}",
            )
            yield f"data: {json.dumps(err.model_dump(), ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
