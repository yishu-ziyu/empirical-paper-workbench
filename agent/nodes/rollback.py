"""rollback_chapter 节点 (T-08a).

从 ``state['chapter_index']`` + ``state['version_index']`` 恢复指定章节到
历史版本。回滚只改 ``content`` 和 ``status``，不改 ``versions`` 列表本身
（版本历史是只追加的审计记录）。

此节点不在 LangGraph 主循环里——它由 backend
``POST /sessions/{id}/rollback-chapter`` 触发，单独调用，故不接 graph 边。
HITL 策略同 T-04/T-06/T-07：state-driven，不调 interrupt()。
"""
from __future__ import annotations

from protocols import RollbackOutput
from state import EconPaperState


def rollback_chapter(state: EconPaperState) -> RollbackOutput:
    """回滚到指定版本。

    读 ``state['chapter_index']``（0-5）定位章节，
    读 ``state['version_index']`` 定位 versions 列表里的历史版本，
    把该版本内容写回 ``content``，``status`` 设为 ``"rolled_back"``。

    缺参数或越界时抛错（不 silent fallback，防止 bug 被掩盖）。
    """
    chapter_index = state.get("chapter_index")
    if chapter_index is None:
        raise ValueError("rollback 需要 state['chapter_index']")

    version_index = state.get("version_index")
    if version_index is None:
        raise ValueError("rollback 需要 state['version_index']")

    body_chapters: list = list(state.get("body_chapters", []) or [])
    if chapter_index >= len(body_chapters):
        raise IndexError(
            f"chapter_index {chapter_index} 越界（body_chapters 长度 {len(body_chapters)}）"
        )

    chapter = dict(body_chapters[chapter_index])
    versions = chapter.get("versions", []) or []
    if version_index >= len(versions):
        raise IndexError(
            f"version_index {version_index} 越界（versions 长度 {len(versions)}）"
        )

    chapter["content"] = versions[version_index]
    chapter["status"] = "rolled_back"
    body_chapters[chapter_index] = chapter

    return {"body_chapters": body_chapters}
