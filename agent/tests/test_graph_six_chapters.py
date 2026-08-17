"""T-08a RED tests for graph 6 章条件边循环.

契约：
1. graph 用条件边循环 generate_chapter（current_chapter_index < 6 → 继续）
2. 6 章全部生成后进入 translate_code（T-09 返回 4 条翻译：py/do/R/m）
3. 6 章 type 顺序：intro / lit_review / data_desc / methods / results / conclusion
4. 每章带 versions 历史
5. current_chapter_index 最终 = 6
6. route_after_chapter 路由函数：< 6 → "generate_chapter"，>= 6 → "translate_code"

测试策略：build_graph() 从 upload_data 开始，端到端跑需要真实数据过重；
改用最小测试 graph（generate_chapter + translate_code + 条件边）验证循环逻辑，
再单独测 route_after_chapter 路由函数。
"""
from __future__ import annotations

import pytest
from langgraph.graph import END, START, StateGraph

from nodes.generate_chapter import generate_chapter
from nodes.translate_code import translate_code
from state import EconPaperState

from conftest import make_write_ready_state


@pytest.fixture
def recorder(mock_llm_for):
    """generate_chapter LLM recorder（基于根 conftest mock_llm_for 工厂）。"""
    return mock_llm_for("generate_chapter", return_value="MOCK CONTENT")


# ---------------------------------------------------------------------------
# route_after_chapter 路由函数
# ---------------------------------------------------------------------------
def test_route_after_chapter_continues_when_below_six():
    """current_chapter_index < 6 → "generate_chapter"（继续循环）。"""
    from graph import route_after_chapter

    base = {"outline": [{"type": "intro"}]}
    assert route_after_chapter({**base, "current_chapter_index": 0}) == "generate_chapter"
    assert route_after_chapter({**base, "current_chapter_index": 3}) == "generate_chapter"
    assert route_after_chapter({**base, "current_chapter_index": 5}) == "generate_chapter"


def test_route_after_chapter_goes_to_translate_when_six():
    """current_chapter_index >= 6 → "translate_code"。"""
    from graph import route_after_chapter

    base = {"outline": [{"type": "intro"}]}
    assert route_after_chapter({**base, "current_chapter_index": 6}) == "translate_code"
    assert route_after_chapter({**base, "current_chapter_index": 7}) == "translate_code"


def test_route_after_chapter_defaults_to_translate_when_no_index():
    """无 current_chapter_index（legacy 流）→ translate_code（不循环）。"""
    from graph import route_after_chapter

    assert route_after_chapter({}) == "translate_code"
    assert route_after_chapter({"outline": []}) == "translate_code"


# ---------------------------------------------------------------------------
# 最小 graph 循环测试
# ---------------------------------------------------------------------------
def _build_chapter_loop_graph():
    """构建只含 generate_chapter + translate_code 的最小循环 graph。

    复用 graph.route_after_chapter 路由函数，与 build_graph() 一致。
    """
    from graph import route_after_chapter

    builder = StateGraph(EconPaperState)
    builder.add_node("generate_chapter", generate_chapter)
    builder.add_node("translate_code", translate_code)
    builder.add_edge(START, "generate_chapter")
    builder.add_conditional_edges(
        "generate_chapter",
        route_after_chapter,
        {"generate_chapter": "generate_chapter", "translate_code": "translate_code"},
    )
    builder.add_edge("translate_code", END)
    return builder.compile()


def _loop_state(six_chapter_outline):
    """构造循环 graph 需要的 state。"""
    return make_write_ready_state(
        current_chapter_index=0,
        outline=six_chapter_outline,
        body_chapters=[],
        research_question="Q",
        data_summary="D",
        key_references="REF",
        eda_results="EDA",
        method="OLS",
    )


def test_graph_loops_six_chapters(recorder, six_chapter_outline):
    """graph 从 chapter 0 循环到 chapter 5，生成 6 章。"""
    graph = _build_chapter_loop_graph()
    state = _loop_state(six_chapter_outline)
    result = graph.invoke(
        state, config={"configurable": {"thread_id": "test"}, "recursion_limit": 50}
    )

    assert len(result["body_chapters"]) == 6
    # current_chapter_index 推进到 6
    assert result["current_chapter_index"] == 6
    # 6 章 type 顺序正确
    expected_types = [
        "intro",
        "lit_review",
        "data_desc",
        "methods",
        "results",
        "conclusion",
    ]
    actual_types = [ch["type"] for ch in result["body_chapters"]]
    assert actual_types == expected_types


def test_graph_reaches_translate_code(recorder, six_chapter_outline):
    """6 章生成后进入 translate_code，返回 4 条翻译（T-09 实现）。

    T-08a 时 translate_code 是占位（返回 []）；T-09 把它扩展为真正的
    翻译节点，固定返回 4 条（py / stata / r / eviews）。
    """
    graph = _build_chapter_loop_graph()
    state = _loop_state(six_chapter_outline)
    result = graph.invoke(
        state, config={"configurable": {"thread_id": "test"}, "recursion_limit": 50}
    )
    translations = result.get("code_translations")
    assert isinstance(translations, list)
    assert len(translations) == 4
    langs = {t["lang"] for t in translations}
    assert langs == {"py", "stata", "r", "eviews"}


def test_graph_each_chapter_has_versions(recorder, six_chapter_outline):
    """每章都带 versions 列表，versions[0] 是最新内容。"""
    graph = _build_chapter_loop_graph()
    state = _loop_state(six_chapter_outline)
    result = graph.invoke(
        state, config={"configurable": {"thread_id": "test"}, "recursion_limit": 50}
    )
    for i, ch in enumerate(result["body_chapters"]):
        assert "versions" in ch, f"chapter {i} 缺 versions"
        assert isinstance(ch["versions"], list)
        assert len(ch["versions"]) >= 1
        assert ch["versions"][0] == ch["content"]


def test_graph_llm_called_six_times(recorder, six_chapter_outline):
    """graph 循环调用 LLM 6 次（每章一次）。"""
    graph = _build_chapter_loop_graph()
    state = _loop_state(six_chapter_outline)
    graph.invoke(
        state, config={"configurable": {"thread_id": "test"}, "recursion_limit": 50}
    )
    assert len(recorder.calls) == 6


# ---------------------------------------------------------------------------
# build_graph() 结构：包含 translate_code 节点 + 条件边
# ---------------------------------------------------------------------------
def test_build_graph_compiles_with_translate_code():
    """build_graph() 能编译。章节节点不在预写图里。"""
    from graph import build_graph

    g = build_graph()
    assert g is not None
    node_ids = set(g.get_graph().nodes.keys())
    assert "generate_chapter" not in node_ids
    assert "run_estimate" in node_ids
    assert "search_literature" in node_ids


def test_route_after_identification_goes_to_estimate():
    from graph import route_after_identification

    assert route_after_identification({"star_rating": None}) == [
        "run_estimate",
        "search_literature",
    ]
    assert route_after_identification({"star_rating": 2}) == [
        "run_estimate",
        "search_literature",
    ]
    assert route_after_identification({"star_rating": 0}) == "hitl_pause"


def test_route_after_clean_stops_without_direction():
    from graph import route_after_clean
    from langgraph.graph import END

    assert route_after_clean({}) == END
    assert route_after_clean({"research_direction": {"question": "q"}}) == (
        "set_direction"
    )
