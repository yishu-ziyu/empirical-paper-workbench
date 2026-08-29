"""ADR-0009 Stage 3: 正文引用标记 [1][2] 自动插入测试。

验证：
- _format_citation_indices 把 dict 格式化为 LLM 可读的引用编号表
- lit_review SYSTEM_PROMPT 含 [N] 标记指引
- lit_review USER_TEMPLATE 含 {citation_indices} 占位符
- render() 把 citation_indices 注入 user prompt
- generate_chapter 的 lit_review 流程把 state["citation_indices"] 透传到 prompt
"""
from __future__ import annotations

import re
from string import Formatter

import pytest

from agent.prompts import get_prompt
from agent.prompts.lit_review import (
    _format_citation_indices,
    SYSTEM_PROMPT,
    USER_TEMPLATE,
    render,
)


# ---------------------------------------------------------------------------
# _format_citation_indices
# ---------------------------------------------------------------------------
def test_format_empty_dict_returns_placeholder_text():
    assert _format_citation_indices({}) == "（暂无引用编号）"


def test_format_none_returns_placeholder_text():
    assert _format_citation_indices(None) == "（暂无引用编号）"


def test_format_non_dict_returns_placeholder_text():
    assert _format_citation_indices("not a dict") == "（暂无引用编号）"


def test_format_dict_with_dois():
    indices = {"10.1/a": 1, "10.1/b": 2}
    text = _format_citation_indices(indices)
    assert "[1] DOI: 10.1/a" in text
    assert "[2] DOI: 10.1/b" in text


def test_format_dict_with_titles():
    indices = {"Some Paper": 1, "Another Paper": 2}
    text = _format_citation_indices(indices)
    assert "[1] Title: Some Paper" in text
    assert "[2] Title: Another Paper" in text


def test_format_dict_mixed_dois_and_titles():
    indices = {"10.1/a": 1, "Some Paper": 2}
    text = _format_citation_indices(indices)
    assert "[1] DOI: 10.1/a" in text
    assert "[2] Title: Some Paper" in text


def test_format_dict_sorted_by_number_ascending():
    """输出按 [N] 升序排列，与 dict 插入顺序无关。"""
    indices = {"10.1/c": 3, "10.1/a": 1, "10.1/b": 2}
    text = _format_citation_indices(indices)
    lines = text.split("\n")
    assert lines[0] == "[1] DOI: 10.1/a"
    assert lines[1] == "[2] DOI: 10.1/b"
    assert lines[2] == "[3] DOI: 10.1/c"


# ---------------------------------------------------------------------------
# lit_review prompt 契约
# ---------------------------------------------------------------------------
def test_system_prompt_mentions_citation_markers():
    """SYSTEM_PROMPT 必须包含 [N] 引用标记规则指引。"""
    assert "[1]" in SYSTEM_PROMPT or "[N]" in SYSTEM_PROMPT, (
        "SYSTEM_PROMPT 缺少引用标记 [N] 指引"
    )
    assert "引用编号" in SYSTEM_PROMPT or "引用标记" in SYSTEM_PROMPT, (
        "SYSTEM_PROMPT 缺少引用编号/标记关键词"
    )


def test_user_template_has_citation_indices_placeholder():
    """USER_TEMPLATE 必须含 {citation_indices} 占位符。"""
    placeholders = {
        fname for _, fname, _, _ in Formatter().parse(USER_TEMPLATE) if fname
    }
    assert "citation_indices" in placeholders, (
        "USER_TEMPLATE 缺少 {citation_indices} 占位符"
    )


def test_render_with_dict_formats_indices():
    """render 把 dict 形式的 citation_indices 格式化为可读文本。"""
    system, user = render(
        research_question="X 对 Y 的影响",
        key_references="Smith (2020). Some Paper.",
        citation_indices={"10.1/a": 1, "10.1/b": 2},
    )
    assert "[1] DOI: 10.1/a" in user
    assert "[2] DOI: 10.1/b" in user
    assert "{citation_indices}" not in user  # 占位符已替换


def test_render_with_empty_dict_shows_placeholder_text():
    """render 把空 dict 替换为占位提示文本。"""
    system, user = render(
        research_question="X 对 Y 的影响",
        key_references="Smith (2020). Some Paper.",
        citation_indices={},
    )
    assert "（暂无引用编号）" in user
    assert "{citation_indices}" not in user


def test_render_with_none_citation_indices():
    """render 把 None 替换为占位提示文本。"""
    system, user = render(
        research_question="X",
        key_references="refs",
        citation_indices=None,
    )
    assert "（暂无引用编号）" in user


def test_render_with_preformatted_string_passes_through():
    """render 把已格式化的字符串原样传递（不二次处理）。"""
    preformatted = "[1] DOI: 10.1/custom"
    system, user = render(
        research_question="X",
        key_references="refs",
        citation_indices=preformatted,
    )
    assert preformatted in user


# ---------------------------------------------------------------------------
# generate_chapter 集成：state["citation_indices"] 透传到 prompt
# ---------------------------------------------------------------------------
def test_generate_chapter_passes_citation_indices_to_lit_review_prompt(monkeypatch):
    """generate_chapter 对 lit_review 章节把 state["citation_indices"] 透传到 prompt。

    通过 capture call_llm 的 (system, user) 参数，断言 user 含 [1] DOI: ...
    """
    captured = {}

    def fake_call_llm(system: str, user: str) -> str:
        captured["system"] = system
        captured["user"] = user
        return "文献综述正文...Smith (2020) [1] 指出..."

    monkeypatch.setattr("agent.nodes.generate_chapter.call_llm", fake_call_llm)

    from agent.nodes.generate_chapter import generate_chapter

    from conftest import make_write_ready_state

    state = make_write_ready_state(
        current_chapter_index=1,  # 第 2 章 = lit_review
        outline=[
            {"type": "intro", "title": "引言"},
            {"type": "lit_review", "title": "文献综述"},
        ],
        research_question="X 对 Y 的影响",
        key_references="Smith (2020). Some Paper.",
        citation_indices={"10.1/a": 1, "10.1/b": 2},
    )

    result = generate_chapter(state)

    # 断言 prompt 含格式化后的引用编号表
    assert "[1] DOI: 10.1/a" in captured["user"]
    assert "[2] DOI: 10.1/b" in captured["user"]
    # 断言 SYSTEM_PROMPT 含 [N] 引用标记规则
    assert "[1]" in captured["system"] or "[N]" in captured["system"]
    # 断言 LLM 输出（含 [1] 标记）写回 body_chapters
    chapter = result["body_chapters"][1]
    assert "[1]" in chapter["content"]


def test_generate_chapter_no_citation_indices_does_not_crash(monkeypatch):
    """state 无 citation_indices 时 generate_chapter 不崩溃。"""
    monkeypatch.setattr(
        "agent.nodes.generate_chapter.call_llm",
        lambda system, user: "文献综述正文，无引用标记",
    )

    from agent.nodes.generate_chapter import generate_chapter

    from conftest import make_write_ready_state

    state = make_write_ready_state(
        current_chapter_index=1,
        outline=[
            {"type": "intro", "title": "引言"},
            {"type": "lit_review", "title": "文献综述"},
        ],
        research_question="X",
        key_references="refs",
    )
    state.pop("citation_indices", None)

    result = generate_chapter(state)
    chapter = result["body_chapters"][1]
    assert chapter["content"] == "文献综述正文，无引用标记"


# ---------------------------------------------------------------------------
# Fitness Function: 引用标记格式
# ---------------------------------------------------------------------------
def test_fitness_function_citation_marker_pattern():
    """Fitness Function: 引用标记必须匹配 [N] 格式（N 为正整数）。

    此测试不验证 LLM 输出（LLM 可能不遵守），而是验证
    SYSTEM_PROMPT 中的示例标记格式正确。
    """
    # 找 SYSTEM_PROMPT 中所有 [N] 形式的标记
    markers = re.findall(r"\[(\d+)\]", SYSTEM_PROMPT)
    assert len(markers) >= 1, "SYSTEM_PROMPT 应含至少一个 [N] 示例标记"
    # 所有 N 应为正整数
    for n in markers:
        assert int(n) >= 1
