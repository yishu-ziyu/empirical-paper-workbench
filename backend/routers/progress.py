"""整体进度端点 (T-08b).

GET /sessions/{session_id}/progress 返回 6 章完成进度：

    {
      "total": 6,
      "completed": <status=="approved" 的章节数>,
      "current": <state['current_chapter_index']，缺省取 len(body_chapters)>,
      "body_chapters": [{"type":..., "title":..., "status":...}, ...]
    }

Router self-registration: 与 eda.py / chapter.py 一致，import 时自动 attach
到 ``main.app``，不改 ``main.py``（T-08b file-boundary 约束）。
"""
from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter

from facade import facade
from schemas.responses import ProgressChapterSummary, ProgressResponse

router = APIRouter()
_REGISTERED = False

_TOTAL_CHAPTERS = 6


@router.get(
    "/sessions/{session_id}/progress",
    response_model=ProgressResponse,
)
async def get_progress(session_id: str) -> ProgressResponse:
    """返回 6 章完成进度。"""
    state = facade.get_state(session_id)
    body_chapters: List[Any] = list(state.get("body_chapters", []) or [])

    completed = sum(
        1
        for c in body_chapters
        if isinstance(c, dict) and c.get("status") == "approved"
    )

    current = state.get("current_chapter_index")
    if current is None:
        current = len(body_chapters)

    summary = [
        ProgressChapterSummary(
            type=c.get("type") if isinstance(c, dict) else None,
            title=c.get("title") if isinstance(c, dict) else None,
            status=c.get("status") if isinstance(c, dict) else None,
        )
        for c in body_chapters
    ]
    return ProgressResponse(
        total=_TOTAL_CHAPTERS,
        completed=completed,
        current=current,
        body_chapters=summary,
    )


def _self_register() -> None:
    """Attach this router to the FastAPI app on import.

    与 eda.py / chapter.py 模式一致：idempotent via ``_REGISTERED`` flag。
    """
    global _REGISTERED
    if _REGISTERED:
        return
    try:
        from main import app  # noqa: PLC0415

        app.include_router(router)
        _REGISTERED = True
    except Exception:
        # main not importable yet (e.g. during partial builds) — skip silently.
        pass


_self_register()
