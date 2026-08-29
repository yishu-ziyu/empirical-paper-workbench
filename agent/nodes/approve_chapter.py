"""approve_chapter 节点 (T-08a).

用户审批当前章节：``status`` 设为 ``"approved"``，并在 ``chapter_statuses``
列表里记录该章已通过。推进到下一章由 backend 调用 generate_chapter
（``current_chapter_index`` 在 generate_chapter 里自增）完成。

此节点不在 LangGraph 主循环里——它由 backend
``POST /sessions/{id}/approve-chapter`` 触发，单独调用。HITL 策略同
T-04/T-06/T-07：state-driven，不调 interrupt()。
"""
from __future__ import annotations

from ..protocols import ApproveChapterOutput
from ..state import EconPaperState

_NUM_CHAPTERS = 6


def approve_chapter(state: EconPaperState) -> ApproveChapterOutput:
    """审批指定章节。

    读 ``state['chapter_index']``（0-5）定位要审批的章节，设其
    ``status = "approved"``，并在 ``chapter_statuses`` 列表对应位置记
    ``"approved"``。``chapter_statuses`` 不存在时初始化为 6 元空串列表。

    不改 ``content`` / ``versions``。缺 ``chapter_index`` 时抛错。
    """
    chapter_index = state.get("chapter_index")
    if chapter_index is None:
        raise ValueError("approve 需要 state['chapter_index']")

    body_chapters: list = list(state.get("body_chapters", []) or [])
    if chapter_index < len(body_chapters):
        chapter = dict(body_chapters[chapter_index])
        chapter["status"] = "approved"
        body_chapters[chapter_index] = chapter

    # 初始化 / 更新 chapter_statuses（6 元素）
    statuses: list = list(state.get("chapter_statuses", []) or [])
    while len(statuses) < _NUM_CHAPTERS:
        statuses.append("")
    statuses[chapter_index] = "approved"

    return {"body_chapters": body_chapters, "chapter_statuses": statuses}
