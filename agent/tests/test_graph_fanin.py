"""批次 6：识别后估计∥文献，扇入 generate_title 只跑一次。"""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.types import interrupt

from agent.graph import (
    route_after_identification,
    wire_prewrite_edges,
)
from agent.state import EconPaperState

from conftest import make_state, make_write_ready_state


def _stub_prewrite_graph(
    calls: list[str],
    *,
    pause_interrupts: bool = True,
    title_fn=None,
):
    """与 build_graph 同一套边，节点只记账。"""

    # 并行步里两个节点不能写同一个 LastValue 键。
    _writes = {
        "upload_data": lambda s: {"csv_path": s.get("csv_path")},
        "clean_data": lambda s: {"workspace": s.get("workspace")},
        "set_direction": lambda s: {"claim": s.get("claim")},
        "identification_verify": lambda s: {"star_rating": s.get("star_rating")},
        "run_estimate": lambda s: {"estimate": s.get("estimate")},
        "robustness_check": lambda s: {
            "robustness_results": s.get("robustness_results")
        },
        "search_literature": lambda s: {
            "literature_query": s.get("literature_query") or "q"
        },
        "build_citation_graph": lambda s: {
            "citation_indices": s.get("citation_indices") or {}
        },
        "generate_outline": lambda s: {"outline": s.get("outline") or []},
    }

    def _mark(name: str):
        def node(state):
            calls.append(name)
            return _writes[name](state)

        return node

    def pause(state):
        calls.append("hitl_pause")
        if pause_interrupts:
            interrupt({"reason": "identification_0star"})
        return {"hitl_pause_reason": "identification_0star"}

    def title(state):
        calls.append("generate_title")
        return {"title_chapter": {"type": "title", "content": "T", "status": "generated"}}

    title_node = title_fn or title

    builder = StateGraph(EconPaperState)
    builder.add_node("upload_data", _mark("upload_data"))
    builder.add_node("clean_data", _mark("clean_data"))
    builder.add_node("set_direction", _mark("set_direction"))
    builder.add_node("identification_verify", _mark("identification_verify"))
    builder.add_node("hitl_pause", pause)
    builder.add_node("run_estimate", _mark("run_estimate"))
    builder.add_node("robustness_check", _mark("robustness_check"))
    builder.add_node("search_literature", _mark("search_literature"))
    builder.add_node("build_citation_graph", _mark("build_citation_graph"))
    builder.add_node("generate_title", title_node)
    builder.add_node("generate_outline", _mark("generate_outline"))
    wire_prewrite_edges(builder)
    return builder.compile(checkpointer=MemorySaver())


def test_generate_title_runs_once_after_fanin(monkeypatch):
    """带方向、非 0 星：估计与文献都走，generate_title 恰好 1 次。"""
    calls: list[str] = []

    def fake_title(state):
        calls.append("generate_title")
        return {
            "title_chapter": {
                "type": "title",
                "content": "T",
                "status": "generated",
            }
        }

    monkeypatch.setattr("agent.graph.generate_title", fake_title)
    import agent.graph as graph_mod

    graph = _stub_prewrite_graph(calls, title_fn=graph_mod.generate_title)
    state = make_write_ready_state(star_rating=2)
    graph.invoke(
        state,
        config={"configurable": {"thread_id": "fanin-title-once"}},
    )
    assert calls.count("generate_title") == 1
    assert "run_estimate" in calls
    assert "search_literature" in calls
    assert "robustness_check" in calls
    assert "build_citation_graph" in calls
    assert "generate_outline" in calls


def test_no_direction_does_not_enter_prewrite():
    """无方向时清洗后停，不进标题。"""
    calls: list[str] = []
    graph = _stub_prewrite_graph(calls)
    state = make_state(session_id="no-dir", uploaded_datasets=[])
    graph.invoke(
        state,
        config={"configurable": {"thread_id": "fanin-no-dir"}},
    )
    assert "set_direction" not in calls
    assert "run_estimate" not in calls
    assert "search_literature" not in calls
    assert "generate_title" not in calls


def test_zero_star_goes_to_hitl_not_estimate_or_literature():
    """0 星进 hitl_pause，不进估计、不进文献。"""
    assert route_after_identification({"star_rating": 0}) == "hitl_pause"
    calls: list[str] = []
    graph = _stub_prewrite_graph(calls)
    state = make_write_ready_state(star_rating=0)
    graph.invoke(
        state,
        config={"configurable": {"thread_id": "fanin-zero-star"}},
    )
    assert "hitl_pause" in calls
    assert "run_estimate" not in calls
    assert "search_literature" not in calls
    assert "generate_title" not in calls


def test_production_graph_waiting_edge_joins_title():
    """生产图用 waiting_edges 扇入 generate_title，不是两条独立边。"""
    from agent.graph import build_graph

    compiled = build_graph()
    waiting = compiled.builder.waiting_edges
    assert (
        (("robustness_check", "build_citation_graph"), "generate_title") in waiting
    )
    regular = compiled.builder.edges
    assert ("robustness_check", "generate_title") not in regular
    assert ("build_citation_graph", "generate_title") not in regular
