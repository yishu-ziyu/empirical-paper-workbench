"""T-07 / T-08a RED tests for generate_chapter node.

契约：
1. generate_chapter(state) 读 state['current_chapter_index'] + state['outline']
2. 从 outline[idx] 取章节 type，加载模板
3. render(state) 用 state 字段填充模板占位符
4. 调 call_llm(system, user)（注意是 system+user 两参数，不是单 prompt）
5. 写回 state['body_chapters'][idx]，新章节含 {**chapter_spec, content, status: "generated"}
6. call_llm 是模块级函数，测试 monkeypatch 它
7. intro 端到端：mock LLM 返回含"研究背景"的内容，断言 body_chapters[0].content 含"研究背景"
"""
from __future__ import annotations

import pytest

from nodes.generate_chapter import generate_chapter

from conftest import make_state


@pytest.fixture
def recorder(mock_llm_for):
    """generate_chapter LLM recorder（基于根 conftest mock_llm_for 工厂）。"""
    return mock_llm_for("generate_chapter", return_value="MOCK CHAPTER CONTENT")


# ---------------------------------------------------------------------------
# 基本契约
# ---------------------------------------------------------------------------
def test_generate_chapter_writes_to_body_chapters(recorder, six_chapter_outline):
    """generate_chapter 把生成的章节写到 state['body_chapters'][idx]。"""
    state = make_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="教育对收入的影响",
        data_summary="5 行 3 列",
    )
    result = generate_chapter(state)

    assert "body_chapters" in result
    out = result["body_chapters"][0]
    assert out["type"] == "intro"
    assert out["title"] == "引言"
    assert out["content"] == "MOCK CHAPTER CONTENT"
    assert out["status"] == "generated"


def test_generate_chapter_preserves_other_body_chapters(
    recorder, six_chapter_outline
):
    """generate_chapter 写 body_chapters[idx] 时，其他位置的已有章节保留。"""
    existing = {
        "type": "intro",
        "title": "引言",
        "content": "OLD INTRO",
        "status": "approved",
        "versions": ["OLD INTRO"],
        "chapter_index": 0,
    }
    state = make_state(
        current_chapter_index=1,  # 写第 1 章
        outline=six_chapter_outline,
        body_chapters=[existing],
        research_question="Q",
        key_references="REF",
    )
    result = generate_chapter(state)
    # chapter 0 保留
    assert result["body_chapters"][0]["content"] == "OLD INTRO"
    assert result["body_chapters"][0]["status"] == "approved"
    # chapter 1 新生成
    assert result["body_chapters"][1]["type"] == "lit_review"
    assert result["body_chapters"][1]["status"] == "generated"


def test_generate_chapter_calls_llm_with_system_and_user(
    recorder, six_chapter_outline
):
    """generate_chapter 必须调 call_llm(system, user) 两参数（不是单 prompt）。"""
    state = make_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="RQ",
        data_summary="DS",
    )
    generate_chapter(state)
    assert len(recorder.calls) == 1, "generate_chapter did not call LLM"
    system, user = recorder.calls[0]["args"]
    assert isinstance(system, str) and len(system) > 0
    assert isinstance(user, str) and len(user) > 0
    # user prompt 必须含被替换的研究问题
    assert "RQ" in user
    assert "DS" in user


def test_generate_chapter_no_index_returns_empty(recorder):
    """无 current_chapter_index 时返回空 dict（no-op）。"""
    state = make_state(
        research_question="q",
        data_summary="d",
    )
    result = generate_chapter(state)
    assert result == {}


def test_generate_chapter_unknown_type_raises(recorder):
    """未知 chapter_type 抛错（不要 silent fallback 成 intro，掩盖 bug）。"""
    outline = [{"type": "unknown_xyz", "title": "x"}]
    state = make_state(
        current_chapter_index=0,
        outline=outline,
    )
    with pytest.raises(ValueError):
        generate_chapter(state)


# ---------------------------------------------------------------------------
# 6 种 chapter_type 都能跑通
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "chapter_type, required_fields",
    [
        ("intro", {"research_question": "Q", "data_summary": "D"}),
        ("lit_review", {"research_question": "Q", "key_references": "REF"}),
        ("data_desc", {"data_summary": "D", "eda_results": "EDA"}),
        ("methods", {"method": "OLS", "research_question": "Q"}),
        ("results", {"results": "R", "method": "OLS"}),
        ("conclusion", {"results": "R", "research_question": "Q"}),
    ],
)
def test_generate_chapter_all_six_types(
    recorder, chapter_type, required_fields
):
    """6 种 chapter_type 都能加载模板 + render + 调 LLM + 写回 body_chapters。"""
    outline = [{"type": chapter_type, "title": chapter_type}]
    state = make_state(
        current_chapter_index=0,
        outline=outline,
        **required_fields,
    )
    result = generate_chapter(state)
    out = result["body_chapters"][0]
    assert out["type"] == chapter_type
    assert out["status"] == "generated"
    assert out["content"] == "MOCK CHAPTER CONTENT"
    # 检查 LLM 被调用且 user prompt 含所有占位符的值
    assert len(recorder.calls) == 1
    _, user = recorder.calls[0]["args"]
    for v in required_fields.values():
        assert v in user, f"{chapter_type}: user prompt missing value {v!r}"


# ---------------------------------------------------------------------------
# intro 端到端：mock LLM 返回含"研究背景"的内容，验证写回 body_chapters
# ---------------------------------------------------------------------------
def test_intro_end_to_end_contains_required_section(
    recorder, six_chapter_outline
):
    """intro 端到端：mock LLM 返回含"研究背景"的内容，body_chapters[0].content 含"研究背景"。

    这是 T-07 验收的"intro 端到端跑通"在 agent 层的等价测试。
    前端 ChapterWriter.test.tsx 测 UI 渲染；这里测 agent 节点 → LLM → 写回链路。
    """
    recorder.return_value = (
        "# 引言\n\n## 研究背景\n教育回报是劳动经济学的经典议题...\n\n"
        "## 研究问题\n本文研究教育对收入的影响。\n\n"
        "## 贡献\n使用 CHARLS 数据...\n\n"
        "## 论文结构\n..."
    )
    state = make_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        research_question="教育对收入的影响",
        data_summary="CHARLS 2018，5 列 1000 行",
    )
    result = generate_chapter(state)
    content = result["body_chapters"][0]["content"]
    assert "研究背景" in content
    assert "研究问题" in content
    assert "贡献" in content
