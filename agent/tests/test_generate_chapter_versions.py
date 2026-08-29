"""T-08a RED tests for generate_chapter 版本历史.

契约：
1. generate_chapter 用 state['current_chapter_index'] 从 outline 取章节 type
2. 生成内容后，把新版本 prepend 到 chapter['versions']（versions[0] 是最新）
3. chapter['content'] = 新生成的内容
4. chapter['status'] = "generated"
5. chapter['chapter_index'] = 当前索引（0-5）
6. state['current_chapter_index'] += 1（推进到下一章）
7. 重跑同一章（regenerate）时，新版本 prepend 到已有 versions 前面
"""
from __future__ import annotations

import pytest

from agent.nodes.generate_chapter import generate_chapter

from conftest import make_write_ready_state


@pytest.fixture
def recorder(mock_llm_for):
    """generate_chapter LLM recorder（基于根 conftest mock_llm_for 工厂）。"""
    return mock_llm_for("generate_chapter", return_value="MOCK CHAPTER CONTENT")


# ---------------------------------------------------------------------------
# 版本历史写入
# ---------------------------------------------------------------------------
def test_generate_chapter_writes_versions_list(recorder, six_chapter_outline):
    """generate_chapter 用索引流时，chapter 带 versions 列表，versions[0] 是最新内容。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="Q",
        data_summary="D",
    )
    result = generate_chapter(state)

    assert "body_chapters" in result
    ch = result["body_chapters"][0]
    assert "versions" in ch, "chapter 缺少 versions 字段"
    assert isinstance(ch["versions"], list)
    assert len(ch["versions"]) == 1
    # versions[0] 是最新
    assert ch["versions"][0] == "MOCK CHAPTER CONTENT"
    # content 也是最新
    assert ch["content"] == "MOCK CHAPTER CONTENT"
    assert ch["status"] == "generated"


def test_generate_chapter_sets_chapter_index(recorder, six_chapter_outline):
    """chapter 带 chapter_index 字段，0-5 对应 6 章。"""
    state = make_write_ready_state(
        current_chapter_index=2,
        outline=six_chapter_outline,
        data_summary="D",
        eda_results="EDA",
    )
    result = generate_chapter(state)
    ch = result["body_chapters"][2]
    assert ch["chapter_index"] == 2
    assert ch["type"] == "data_desc"


def test_generate_chapter_advances_current_index(recorder, six_chapter_outline):
    """generate_chapter 后 current_chapter_index += 1。"""
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="Q",
        data_summary="D",
    )
    result = generate_chapter(state)
    assert result["current_chapter_index"] == 1


# ---------------------------------------------------------------------------
# regenerate：重跑同一章，新版本 prepend
# ---------------------------------------------------------------------------
def test_regenerate_prepends_new_version(recorder, six_chapter_outline):
    """重跑同一章：已有 versions 不丢，新版本 prepend 到 versions[0]。"""
    # 第一章已有 1 个版本
    existing_chapter = {
        "type": "intro",
        "title": "引言",
        "content": "OLD CONTENT",
        "status": "generated",
        "versions": ["OLD CONTENT"],
        "chapter_index": 0,
    }
    state = make_write_ready_state(
        current_chapter_index=0,  # 重跑第 0 章
        outline=six_chapter_outline,
        body_chapters=[existing_chapter],
        research_question="Q",
        data_summary="D",
    )
    # 第一次生成返回 OLD，现在 mock 返回 NEW
    recorder.return_value = "NEW CONTENT"
    result = generate_chapter(state)

    ch = result["body_chapters"][0]
    assert len(ch["versions"]) == 2
    # versions[0] 是最新（NEW），versions[1] 是旧（OLD）
    assert ch["versions"][0] == "NEW CONTENT"
    assert ch["versions"][1] == "OLD CONTENT"
    assert ch["content"] == "NEW CONTENT"
    assert ch["status"] == "generated"


def test_regenerate_keeps_chapter_index(recorder, six_chapter_outline):
    """regenerate 后 chapter_index 不变。"""
    existing = {
        "type": "methods",
        "title": "方法",
        "content": "v1",
        "status": "generated",
        "versions": ["v1"],
        "chapter_index": 3,
    }
    # 占位前 3 章
    body_chapters = [{}, {}, {}, existing]
    state = make_write_ready_state(
        current_chapter_index=3,
        outline=six_chapter_outline,
        body_chapters=body_chapters,
        method="OLS",
        research_question="Q",
    )
    recorder.return_value = "v2"
    result = generate_chapter(state)
    ch = result["body_chapters"][3]
    assert ch["chapter_index"] == 3
    assert ch["versions"] == ["v2", "v1"]


# ---------------------------------------------------------------------------
# 索引流从 outline 取 type 正确
# ---------------------------------------------------------------------------
def test_results_regenerate_splices_current_table(recorder):
    """regenerate 重新 call_llm，再拼当前 state.results；旧 versions 已含当时的表。"""
    old_table = (
        "# 主结果\n\n| 变量 | 系数 | SE | p |\n"
        "|------|------|----|---|\n"
        "| age | 0.1111 | 0.0100 | 0.0100 |"
    )
    new_table = (
        "# 主结果\n\n| 变量 | 系数 | SE | p |\n"
        "|------|------|----|---|\n"
        "| age | 0.9999 | 0.0200 | 0.0010 |"
    )
    old_content = "OLD PROSE\n\n" + old_table
    existing = {
        "type": "results",
        "title": "结果",
        "content": old_content,
        "status": "generated",
        "versions": [old_content],
        "chapter_index": 0,
    }
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
        body_chapters=[existing],
        results=new_table,
    )
    recorder.return_value = "NEW PROSE"
    result = generate_chapter(state)
    ch = result["body_chapters"][0]
    expected = "NEW PROSE\n\n" + new_table
    assert ch["content"] == expected
    assert ch["versions"][0] == expected
    assert ch["versions"][1] == old_content
    assert "0.1111" in ch["versions"][1]
    assert "0.9999" in ch["versions"][0]
    assert len(recorder.calls) == 1


def test_index_flow_picks_type_from_outline(recorder, six_chapter_outline):
    """current_chapter_index=3 时生成 methods 章（type 来自 outline[3]）。"""
    state = make_write_ready_state(
        current_chapter_index=3,
        outline=six_chapter_outline,
        method="OLS",
        research_question="Q",
    )
    result = generate_chapter(state)
    ch = result["body_chapters"][3]
    assert ch["type"] == "methods"
    assert ch["title"] == "方法"
