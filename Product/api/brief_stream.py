"""POST /api/brief/stream + POST /api/brief/stream/resume — SSE endpoints.

返回 text/event-stream, 每个 event 是 `data: {BriefEvent JSON}\n\n`.
前端 BriefPanel.tsx 用 fetch + ReadableStream 消费.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

# Re-export event / request types from the wrapper so callers can
# `from Product.api.brief_stream import BriefEvent, BriefResumeRequest`.
from Product.backend.wrapper.brief_stream_service import (
    BriefEvent,
    BriefResumeRequest,
    resume_brief_stream,
    run_brief_stream,
)

# `BriefRequest` is the wire-format request model for the initial POST.
# It already exists in Product.types.research and matches the simple
# {"topic": str, "topic_slug"?: str} payload the stream endpoint needs.
from Product.types.research import BriefRequest

router = APIRouter()

# 落盘到 repo 根的 Tasks/ 目录 (与 /api/brief 保持一致)
_TASKS_ROOT = Path(__file__).resolve().parents[2] / "Tasks"


def _sse_format(event_dict: dict) -> str:
    """Format Pydantic model as `data: {...}\n\n`."""
    return f"data: {json.dumps(event_dict, ensure_ascii=False)}\n\n"


async def _stream_initial(req: BriefRequest) -> AsyncIterator[str]:
    for event in run_brief_stream(req.topic):
        yield _sse_format(event.model_dump())


async def _stream_resume(req: BriefResumeRequest) -> AsyncIterator[str]:
    for event in resume_brief_stream(
        topic=req.topic,
        action=req.action,
        prior_steps=req.prior_steps,
        user_input=req.user_input,
        tasks_root=_TASKS_ROOT,
    ):
        yield _sse_format(event.model_dump())


@router.post("/api/brief/stream")
async def post_brief_stream(req: BriefRequest) -> StreamingResponse:
    """SSE endpoint for the initial brief run (steps 1-3 → await_user)."""
    return StreamingResponse(
        _stream_initial(req),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@router.post("/api/brief/stream/resume")
async def post_brief_stream_resume(req: BriefResumeRequest) -> StreamingResponse:
    """SSE endpoint to resume after await_user (step 4 → final_brief → done)."""
    return StreamingResponse(
        _stream_resume(req),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
