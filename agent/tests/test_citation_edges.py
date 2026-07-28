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
    """图谱外的 cited_doi 被过滤掉（去噪）。"""
    entries = [
        {"title": "A", "year": 2020, "doi": "10.1/a"},
        {"title": "B", "year": 2021, "doi": "10.1/b"},
    ]
    _patch_references(monkeypatch, {
        "10.1/a": ["10.1/b", "10.99/external"],  # external 不在图谱内
    })

    result = build_citation_graph({"literature_entries": entries})
    edges = result["citation_graph"]["edges"]

    assert {"from": "10.1/a", "to": "10.1/b"} in edges
    assert all(e["to"] != "10.99/external" for e in edges)
    assert len(edges) == 1


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
