"""T-08a RED tests for approve_chapter 节点.

契约：
1. approve_chapter(state) 把 body_chapters[chapter_index] 的 status 设为 "approved"
2. 更新 chapter_statuses[chapter_index] = "approved"
3. 返回 {"body_chapters": [...], "chapter_statuses": [...]}
4. 不改 content / versions
5. 缺 chapter_index 时报错
"""
from __future__ import annotations

import pytest

from nodes.approve_chapter import approve_chapter

from conftest import make_state, make_body_chapters


@pytest.fixture
def approve_chapters():
    """审批用章节列表（基于根 conftest make_body_chapters 定制）。

    approve 测试需要断言 content / versions 不被修改，这里固定其值。
    """
    chapters = make_body_chapters(n=2)
    chapters[0]["content"] = "intro content"
    chapters[0]["versions"] = ["intro content"]
    chapters[1]["content"] = "lit content"
    chapters[1]["versions"] = ["lit content"]
    return chapters


# ---------------------------------------------------------------------------
# 基本审批
# ---------------------------------------------------------------------------
def test_approve_sets_chapter_status_approved(approve_chapters):
    """approve chapter 0 → body_chapters[0].status = "approved"。"""
    state = make_state(body_chapters=approve_chapters, chapter_index=0)
    result = approve_chapter(state)

    assert "body_chapters" in result
    assert result["body_chapters"][0]["status"] == "approved"


def test_approve_updates_chapter_statuses(approve_chapters):
    """approve chapter 1 → chapter_statuses[1] = "approved"。"""
    state = make_state(
        body_chapters=approve_chapters,
        chapter_index=1,
        chapter_statuses=["", ""],
    )
    result = approve_chapter(state)

    assert "chapter_statuses" in result
    assert result["chapter_statuses"][1] == "approved"


def test_approve_initializes_chapter_statuses_if_absent(approve_chapters):
    """无 chapter_statuses 时，approve 初始化 6 元素列表。"""
    state = make_state(body_chapters=approve_chapters, chapter_index=0)
    result = approve_chapter(state)

    assert "chapter_statuses" in result
    assert len(result["chapter_statuses"]) == 6
    assert result["chapter_statuses"][0] == "approved"


def test_approve_does_not_touch_content_or_versions(approve_chapters):
    """approve 不改 content 和 versions。"""
    state = make_state(body_chapters=approve_chapters, chapter_index=0)
    result = approve_chapter(state)
    ch = result["body_chapters"][0]
    assert ch["content"] == "intro content"
    assert ch["versions"] == ["intro content"]


def test_approve_preserves_other_chapters(approve_chapters):
    """approve chapter 0 不影响 chapter 1。"""
    state = make_state(body_chapters=approve_chapters, chapter_index=0)
    result = approve_chapter(state)
    assert result["body_chapters"][1]["status"] == "generated"


def test_approve_second_chapter(approve_chapters):
    """approve chapter 1。"""
    state = make_state(
        body_chapters=approve_chapters,
        chapter_index=1,
        chapter_statuses=["approved", ""],
    )
    result = approve_chapter(state)
    assert result["body_chapters"][1]["status"] == "approved"
    assert result["chapter_statuses"][0] == "approved"
    assert result["chapter_statuses"][1] == "approved"


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------
def test_approve_missing_chapter_index_raises(approve_chapters):
    """缺 chapter_index 报错。"""
    state = make_state(body_chapters=approve_chapters)
    with pytest.raises((KeyError, ValueError)):
        approve_chapter(state)
