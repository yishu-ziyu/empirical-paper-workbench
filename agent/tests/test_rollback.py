"""T-08a RED tests for rollback_chapter 节点.

契约：
1. rollback_chapter(state) 从 body_chapters[chapter_index]['versions'][version_index] 恢复 content
2. 恢复后 status = "rolled_back"
3. versions 列表本身不变（只读不写）
4. 缺少 chapter_index / version_index 时给清晰错误
5. version_index 越界时报错
"""
from __future__ import annotations

import pytest

from nodes.rollback import rollback_chapter

from conftest import make_state, make_body_chapters


@pytest.fixture
def rollback_chapters():
    """带多版本的章节列表（基于根 conftest make_body_chapters 定制）。

    rollback 需要章节 0 含 3 个版本以测试版本回滚；章节 1 保留单版本 + approved 状态。
    """
    chapters = make_body_chapters(n=2)
    chapters[0]["content"] = "v0_content"
    chapters[0]["versions"] = ["v0_content", "v1_content", "v2_content"]
    chapters[1]["content"] = "lit_v0"
    chapters[1]["versions"] = ["lit_v0"]
    chapters[1]["status"] = "approved"
    return chapters


# ---------------------------------------------------------------------------
# 基本回滚
# ---------------------------------------------------------------------------
def test_rollback_restores_content_from_version_index(rollback_chapters):
    """rollback 到 versions[1]，content 恢复为 v1_content。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=0,
        version_index=1,
    )
    result = rollback_chapter(state)

    assert "body_chapters" in result
    ch = result["body_chapters"][0]
    assert ch["content"] == "v1_content"
    assert ch["status"] == "rolled_back"


def test_rollback_to_oldest_version(rollback_chapters):
    """rollback 到 versions[-1]（最旧版本）。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=0,
        version_index=2,  # 最旧
    )
    result = rollback_chapter(state)
    ch = result["body_chapters"][0]
    assert ch["content"] == "v2_content"
    assert ch["status"] == "rolled_back"


def test_rollback_does_not_mutate_versions(rollback_chapters):
    """rollback 不改 versions 列表本身。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=0,
        version_index=1,
    )
    original_versions = list(state["body_chapters"][0]["versions"])
    result = rollback_chapter(state)
    assert result["body_chapters"][0]["versions"] == original_versions


def test_rollback_preserves_other_chapters(rollback_chapters):
    """rollback chapter 0 不影响 chapter 1。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=0,
        version_index=1,
    )
    result = rollback_chapter(state)
    assert result["body_chapters"][1]["content"] == "lit_v0"
    assert result["body_chapters"][1]["status"] == "approved"


def test_rollback_second_chapter(rollback_chapters):
    """rollback chapter 1。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=1,
        version_index=0,
    )
    result = rollback_chapter(state)
    ch = result["body_chapters"][1]
    assert ch["content"] == "lit_v0"
    assert ch["status"] == "rolled_back"


# ---------------------------------------------------------------------------
# 错误处理
# ---------------------------------------------------------------------------
def test_rollback_missing_chapter_index_raises(rollback_chapters):
    """缺 chapter_index 报错（不要 silent fallback）。"""
    state = make_state(body_chapters=rollback_chapters, version_index=0)
    with pytest.raises((KeyError, ValueError)):
        rollback_chapter(state)


def test_rollback_missing_version_index_raises(rollback_chapters):
    """缺 version_index 报错。"""
    state = make_state(body_chapters=rollback_chapters, chapter_index=0)
    with pytest.raises((KeyError, ValueError)):
        rollback_chapter(state)


def test_rollback_version_index_out_of_range_raises(rollback_chapters):
    """version_index 越界报错。"""
    state = make_state(
        body_chapters=rollback_chapters,
        chapter_index=0,
        version_index=99,
    )
    with pytest.raises((IndexError, ValueError)):
        rollback_chapter(state)
