"""ADR-0009 Stage 2: citation_graph edges 构建测试。

通过 monkeypatch semantic_scholar_references 验证：
- 真实 references API 返回的 DOI 列表被正确转成 edges
- 图谱外的 cited_doi 被过滤掉
- 自环被排除（source_doi == cited_doi）
- API 失败时该 entry 降级为无出边
- 无 DOI 的 entry 不触发 API 调用
- 单次构建 API 调用数受 MAX_API_CALL_ENTRIES 限制
"""
from __future__ import annotations

from typing import List

import pytest

from nodes.citation_graph import build_citation_graph, MAX_API_CALL_ENTRIES


def _patch_references(monkeypatch, mapping: dict[str, List[str]]):
    """把 semantic_scholar_references 替换为按 mapping 返回的 fake。

    mapping: {source_doi: [cited_doi, ...]}
    未在 mapping 中的 doi 返回空列表。
    """
    from nodes.literature_sources import semantic_scholar

    def _fake(doi, api_key=None, max_results=20):
        return mapping.get(doi, [])

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _fake
    )


def test_edges_built_from_references_api(monkeypatch):
    """references API 返回的 DOI 列表被正确转成 edges。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
        {"title": "C", "year": 2022, "doi": "10.1/c"},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.1/b", "10.1/c"],  # A 引用 B 和 C
        "10.1/b": ["10.1/c"],            # B 引用 C
        "10.1/c": [],
    })

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]

    assert {"from": "10.1/a", "to": "10.1/b"} in edges
    assert {"from": "10.1/a", "to": "10.1/c"} in edges
    assert {"from": "10.1/b", "to": "10.1/c"} in edges
    assert len(edges) == 3


def test_edges_filter_out_dois_outside_graph(monkeypatch):
    """图谱外的 cited_doi 先写进文献集，再留边（#8 被引跳）。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.1/b", "10.99/external"],  # external 原本不在图谱内
    })

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]
    dois = [e.get("doi") for e in result["literature_entries"]]

    assert "10.99/external" in dois
    assert {"from": "10.1/a", "to": "10.1/b"} in edges
    assert {"from": "10.1/a", "to": "10.99/external"} in edges
    assert len(result["literature_entries"]) <= 20
    assert "10.99/external" in result["citation_indices"]


def test_self_loop_excluded(monkeypatch):
    """source_doi == cited_doi 时排除（避免自环）。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.1/a"],  # 自引
    })

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]

    assert edges == []


def test_api_failure_degrades_to_empty_edges(monkeypatch):
    """API 调用失败时该 entry 降级为无出边，不抛异常。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]

    from nodes.literature_sources import semantic_scholar

    def _flaky(doi, api_key=None, max_results=20):
        if doi == "10.1/a":
            raise RuntimeError("network timeout")
        return ["10.1/a"]  # B 引用 A

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _flaky
    )

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]

    # A 的 API 失败 → A 无出边；B 的 API 成功 → B → A
    assert {"from": "10.1/b", "to": "10.1/a"} in edges
    assert all(e["from"] != "10.1/a" for e in edges)
    assert len(edges) == 1


def test_no_doi_entry_skips_api(monkeypatch):
    """无 DOI 的 entry 不触发 API 调用。"""
    entries = [
        {"title": "No DOI", "year": 2020},  # 无 doi 字段
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]

    call_count = {"n": 0}

    from nodes.literature_sources import semantic_scholar

    def _counter(doi, api_key=None, max_results=20):
        call_count["n"] += 1
        return []

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _counter
    )

    build_citation_graph({"literature_entries": entries})

    # 只有 B（有 DOI）触发 API
    assert call_count["n"] == 1


def test_api_call_count_capped(monkeypatch):
    """单次构建 API 调用数受 MAX_API_CALL_ENTRIES 限制。"""
    # 10 条有 DOI 的文献
    entries = [
        {"title": f"P{i}", "year": 2000 + i, "doi": f"10.1/p{i}"}
        for i in range(10)
    ]

    call_count = {"n": 0}

    from nodes.literature_sources import semantic_scholar

    def _counter(doi, api_key=None, max_results=20):
        call_count["n"] += 1
        return []

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _counter
    )

    build_citation_graph({"literature_entries": entries})

    assert call_count["n"] == MAX_API_CALL_ENTRIES


def test_empty_entries_skips_api_entirely(monkeypatch):
    """空 literature_entries 时完全不调 API。"""
    call_count = {"n": 0}

    from nodes.literature_sources import semantic_scholar

    def _counter(doi, api_key=None, max_results=20):
        call_count["n"] += 1
        return []

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _counter
    )

    result = build_citation_graph({})

    assert call_count["n"] == 0
    assert result["citation_graph"]["edges"] == []


def test_edges_shape_is_from_to_dict(monkeypatch):
    """每条 edge 是 {from: doi, to: doi} 结构。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]
    _patch_references(monkeypatch, {"10.1/a": ["10.1/b"]})

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]

    assert len(edges) == 1
    edge = edges[0]
    assert set(edge.keys()) == {"from", "to"}
    assert edge["from"] == "10.1/a"
    assert edge["to"] == "10.1/b"


def test_fitness_function_edge_endpoints_in_indices(monkeypatch):
    """Fitness Function: edges 两端 DOI 都在 citation_indices 内。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
        {"title": "C", "year": 2022, "doi": "10.1/c"},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.1/b", "10.1/c"],
        "10.1/b": ["10.1/c"],
    })

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]
    indices = result["citation_indices"]

    for edge in edges:
        assert edge["from"] in indices, f"from DOI {edge['from']} 不在 indices"
        assert edge["to"] in indices, f"to DOI {edge['to']} 不在 indices"


def test_citation_hop_adds_out_of_set_doi_and_keeps_cap(monkeypatch):
    """有被引跳时集外 DOI 进 literature_entries，总长 <= 20。"""
    from nodes.search_literature import MAX_LITERATURE_ENTRIES

    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a", "citation_count": 99},
        {"title": "B", "year": 2021, "doi": "10.1/b", "citation_count": 1},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.99/external"],
    })
    result = build_citation_graph({"literature_entries": entries})
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert "10.99/external" in dois
    assert len(result["literature_entries"]) <= MAX_LITERATURE_ENTRIES
    assert {"from": "10.1/a", "to": "10.99/external"} in result["citation_graph"]["edges"]


def test_citation_hop_does_not_exceed_max_when_l0_full(monkeypatch):
    """L0 已 20 条时，集外 DOI 不能再进，边仍滤掉。"""
    from nodes.search_literature import MAX_LITERATURE_ENTRIES

    entries = [
        {"title": f"P{i}", "year": 2000 + i, "doi": f"10.1/p{i}", "citation_count": i}
        for i in range(MAX_LITERATURE_ENTRIES)
    ]
    # citation_count 最高的是 p19
    _patch_references(monkeypatch, {
        "10.1/p19": ["10.99/external"],
    })
    result = build_citation_graph({"literature_entries": entries})
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert len(result["literature_entries"]) == MAX_LITERATURE_ENTRIES
    assert "10.99/external" not in dois
    assert all(e["to"] != "10.99/external" for e in result["citation_graph"]["edges"])


def test_citation_hop_api_failure_does_not_crash(monkeypatch):
    """无 key / API 失败时不崩，文献集保持 L0。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a", "citation_count": 10},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]
    from nodes.literature_sources import semantic_scholar

    def _boom(doi, api_key=None, max_results=20):
        raise RuntimeError("network down")

    monkeypatch.setattr(semantic_scholar, "semantic_scholar_references", _boom)
    result = build_citation_graph({"literature_entries": entries})
    assert len(result["literature_entries"]) == 2
    assert result["citation_graph"]["edges"] == []
    assert result["citation_indices"]["10.1/a"] == 1


def test_citation_hop_only_queries_top_three(monkeypatch):
    """被引跳只打 citation 最高的 3 条。"""
    entries = [
        {"title": f"P{i}", "year": 2000, "doi": f"10.1/p{i}", "citation_count": i}
        for i in range(6)
    ]
    called: list[str] = []
    from nodes.literature_sources import semantic_scholar

    def _counter(doi, api_key=None, max_results=20):
        called.append(doi)
        return []

    monkeypatch.setattr(semantic_scholar, "semantic_scholar_references", _counter)
    build_citation_graph({"literature_entries": entries})
    # 先 hop 最高 3：p5 p4 p3；剩余预算再补 p0 p1（MAX_API_CALL_ENTRIES=5）
    assert called[:3] == ["10.1/p5", "10.1/p4", "10.1/p3"]
    assert len(called) == MAX_API_CALL_ENTRIES

