"""预写流程双源收敛的一致性测试。

验证 ``agent.engine.prewrite.PRWRITE_SEQUENCE`` 是预写顺序的单一真相，且
graph（LangGraph 并行图）与 ``run_prewrite``（Facade HITL 串行路径）均由它派生、
对同一输入产出一致。
"""
from __future__ import annotations

import agent.graph as graph_module
from agent.engine.prewrite import PRWRITE_NODES, PRWRITE_SEQUENCE, run_prewrite
from agent.nodes.route_after_review import _advance  # noqa: F401  (route 收敛锚点)


def _panel_csv(tmp_path):
    import pandas as pd

    path = tmp_path / "panel.csv"
    pd.DataFrame(
        {
            "y": [1.0, 1.2, 2.0, 2.4, 1.1, 1.3, 2.1, 2.5],
            "treat": [0, 0, 1, 1, 0, 0, 1, 1],
            "year": [2000, 2001, 2000, 2001, 2000, 2001, 2000, 2001],
            "id": [1, 1, 2, 2, 3, 3, 4, 4],
            "group": [0, 0, 1, 1, 0, 0, 1, 1],
        }
    ).to_csv(path, index=False)
    return path


def _direction():
    return {
        "question": "treat on y",
        "dv": "y",
        "iv": "treat",
        "controls": [],
        "method": "did",
        "time_col": "year",
        "id_col": "id",
    }


def test_prwrite_sequence_is_single_source():
    """PRWRITE_SEQUENCE 是唯一预写顺序清单（节点 id——调用函数——前驱依赖）。"""
    ids = [node_id for node_id, _fn, _deps in PRWRITE_SEQUENCE]
    assert ids == [
        "set_direction",
        "identification_verify",
        "run_estimate",
        "robustness_check",
        "search_literature",
        "build_citation_graph",
        "generate_title",
        "generate_outline",
    ]
    # 8 个预写节点，id 唯一
    assert len(ids) == len(set(ids)) == 8
    assert set(ids) == set(PRWRITE_NODES.keys())
    # 每个前驱依赖都定义在清单里，且排在自身之前（合法拓扑序）
    declared = {node_id for node_id, _fn, _deps in PRWRITE_SEQUENCE}
    seen: set[str] = set()
    for node_id, _fn, deps in PRWRITE_SEQUENCE:
        for dep in deps:
            assert dep in declared, f"依赖 {dep!r} 不在清单中"
            assert dep in seen, f"依赖 {dep!r} 必须排在 {node_id!r} 之前"
        seen.add(node_id)


def test_id_node_reuse_in_nonzero_star():
    """run_prewrite 从清单串行走到 generate_outline（最后一个节点）→ outline 产出。"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        csv = _panel_csv(Path(td))
        state = run_prewrite({"csv_path": str(csv), "research_direction": _direction()})
    assert state.get("star_rating") not in (0, None)
    assert state.get("claim") in ("causal_with_caveat", "association", "blocked")
    outline = state.get("outline") or []
    assert len(outline) == 6
    assert {ch.get("type") for ch in outline} == {
        "intro", "lit_review", "data_desc", "methods", "results", "conclusion",
    }


def test_graph_edges_derived_from_prwrite_sequence():
    """graph 的预写普通边 == PRWRITE_SEQUENCE 派生的 (dep, node) 集合。

    identification_verify 的出边由条件路由表达、generate_title 入边合成等待边，
    其余依赖必须成为普通边——证明图拓扑来自同一清单。
    """
    compiled = graph_module.build_graph()
    builder = compiled.builder

    expected_regular = set()
    for node_id, _fn, deps in PRWRITE_SEQUENCE:
        for dep in deps:
            if dep == "identification_verify":
                continue  # 条件路由接管
            expected_regular.add((dep, node_id))
    # generate_title 为扇入，不入普通边集合
    expected_regular -= {
        ("robustness_check", "generate_title"),
        ("build_citation_graph", "generate_title"),
    }

    prewrite_ids = set(PRWRITE_NODES.keys())
    regular = set(builder.edges)
    actual = {e for e in regular if e[0] in prewrite_ids and e[1] in prewrite_ids}
    assert actual == expected_regular

    # generate_title 必须经等待边扇入，而非两条独立边
    assert ("robustness_check", "generate_title") not in regular
    assert ("build_citation_graph", "generate_title") not in regular
    assert (("robustness_check", "build_citation_graph"), "generate_title") in set(
        builder.waiting_edges
    )


def test_graph_and_run_prewrite_equivalent(monkeypatch, tmp_path):
    """同一输入下，并行 graph 与串行 run_prewrite 产出等价预写产物。"""
    # 让 graph 从 set_direction 开始（跳过 upload/clean），与 run_prewrite 同起点。
    monkeypatch.setattr("agent.graph.upload_data", lambda s: {})
    monkeypatch.setattr("agent.graph.clean_data", lambda s: {})
    monkeypatch.setattr(
        "agent.nodes.generate_outline.call_llm", lambda *a, **k: "outline-mock-text"
    )
    monkeypatch.setattr(
        "agent.nodes.generate_title.call_llm", lambda *a, **k: "title: 一致标题"
    )

    csv = _panel_csv(tmp_path)
    init = {
        "csv_path": str(csv),
        "uploaded_datasets": [{"path": str(csv), "format": "csv"}],
        "research_direction": _direction(),
    }

    from_graph = graph_module.build_graph().invoke(
        dict(init), config={"configurable": {"thread_id": "conv-equiv"}}
    )
    from_prewrite = run_prewrite(dict(init))

    # 同一结果集的最终产物一致（outline 结构、标题、估计与识别、文献源）
    g_outline = [ch["type"] for ch in (from_graph.get("outline") or [])]
    p_outline = [ch["type"] for ch in (from_prewrite.get("outline") or [])]
    assert g_outline == p_outline == [
        "intro", "lit_review", "data_desc", "methods", "results", "conclusion",
    ]
    assert from_graph.get("title_chapter") == from_prewrite.get("title_chapter")
    assert (from_graph.get("estimate") or {}).get("method") == (
        from_prewrite.get("estimate") or {}
    ).get("method")
    assert from_graph.get("star_rating") == from_prewrite.get("star_rating")
    assert from_graph.get("literature_source") == from_prewrite.get(
        "literature_source"
    )
    # 并行图与串行路径都走到 generate_title，且产出一致
    assert from_graph["title_chapter"]["status"] == from_prewrite["title_chapter"][
        "status"
    ] == "done"