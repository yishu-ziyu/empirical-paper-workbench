"""ADR-0009: build_citation_graph 节点测试。

Stage 2 (ADR-0009 §9): edges 由 Semantic Scholar references API 填充。
为保持 Stage 1 测试稳定性，本文件默认 monkeypatch
semantic_scholar_references 返回空列表（等价于无引用关系）。
真实 API 行为由 test_citation_edges.py 覆盖。
"""
import pytest

from agent.nodes.citation_graph import build_citation_graph


@pytest.fixture(autouse=True)
def _stub_empty_references(monkeypatch):
    """默认 stub：semantic_scholar_references 返回空列表。

    本文件只测编号分配 / 排序 / 降级行为；
    真实 edges 构建逻辑在 test_citation_edges.py 验证。
    """
    from agent.nodes.literature_sources import semantic_scholar

    def _fake_references(doi, api_key=None, max_results=20):
        return []

    monkeypatch.setattr(
        semantic_scholar, "semantic_scholar_references", _fake_references
    )


def test_empty_entries_returns_empty_graph():
    result = build_citation_graph({})
    assert result["citation_graph"]["entries"] == []
    assert result["citation_indices"] == {}


def test_entries_sorted_by_year_then_title():
    entries = [
        {"title": "B", "year": 2023, "doi": "10.1/b"},
        {"title": "A", "year": 2022, "doi": "10.1/a"},
        {"title": "C", "year": 2022, "doi": "10.1/c"},
    ]
    result = build_citation_graph({"literature_entries": entries})
    graph = result["citation_graph"]
    assert graph["entries"][0]["title"] == "A"
    assert graph["entries"][1]["title"] == "C"
    assert graph["entries"][2]["title"] == "B"
    assert result["citation_indices"]["10.1/a"] == 1


def test_doi_none_falls_back_to_title():
    entries = [{"title": "No DOI Paper", "year": 2023}]
    result = build_citation_graph({"literature_entries": entries})
    assert "No DOI Paper" in result["citation_indices"]


def test_citation_indices_values_are_contiguous():
    """Fitness Function: 编号连续 {1, 2, ..., N} 无间断。"""
    entries = [
        {"title": f"P{i}", "year": 2000 + i, "doi": f"10.1/p{i}"}
        for i in range(5)
    ]
    result = build_citation_graph({"literature_entries": entries})
    values = sorted(result["citation_indices"].values())
    assert values == [1, 2, 3, 4, 5]


def test_graph_has_entries_edges_indices_keys():
    """citation_graph schema 含 entries / edges / indices 三键。"""
    entries = [{"title": "X", "year": 2020, "doi": "10.1/x"}]
    result = build_citation_graph({"literature_entries": entries})
    graph = result["citation_graph"]
    assert "entries" in graph
    assert "edges" in graph
    assert "indices" in graph
    # 默认 stub 返回空列表 → edges 为空（等价 Stage 1 行为）
    assert graph["edges"] == []


def test_literature_entries_none_treated_as_empty():
    """literature_entries 缺失时返回空图谱。"""
    result = build_citation_graph({"literature_entries": None})
    assert result["citation_graph"]["entries"] == []
    assert result["citation_indices"] == {}


def test_same_year_sorted_by_title():
    """同年按 title 字母序排序。"""
    entries = [
        {"title": "Zebra", "year": 2020, "doi": "10.1/z"},
        {"title": "Apple", "year": 2020, "doi": "10.1/a"},
        {"title": "Mango", "year": 2020, "doi": "10.1/m"},
    ]
    result = build_citation_graph({"literature_entries": entries})
    titles = [e["title"] for e in result["citation_graph"]["entries"]]
    assert titles == ["Apple", "Mango", "Zebra"]


def test_return_type_annotation_is_citation_graph_output():
    """NodeResult 协议: 返回类型注解为 CitationGraphOutput。"""
    from typing import get_type_hints
    from agent.nodes.citation_graph import build_citation_graph as fn
    from agent.protocols import CitationGraphOutput

    hints = get_type_hints(fn)
    assert hints.get("return") is CitationGraphOutput
