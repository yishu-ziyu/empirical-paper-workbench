"""ADR-0009: generate_references 节点测试。"""
from nodes.generate_references import generate_references, _format_apa


def test_empty_graph_returns_empty_list():
    result = generate_references({})
    assert result["references_list"] == []


def test_apa_format_single_author():
    entry = {"authors": ["Smith"], "year": 2023, "title": "Test", "doi": "10.1/x"}
    ref = _format_apa(entry)
    assert "Smith" in ref
    assert "2023" in ref
    assert "Test" in ref
    assert "10.1/x" in ref


def test_apa_format_many_authors_et_al():
    entry = {"authors": ["A", "B", "C", "D"], "year": 2023, "title": "T"}
    ref = _format_apa(entry)
    assert "et al." in ref


def test_references_ordered_by_index():
    entries = [
        {"authors": ["A"], "year": 2023, "title": "A", "doi": "10.1/a"},
        {"authors": ["B"], "year": 2022, "title": "B", "doi": "10.1/b"},
    ]
    state = {"citation_graph": {"entries": entries, "edges": [], "indices": {}}}
    result = generate_references(state)
    refs = result["references_list"]
    assert len(refs) == 2
    # 按年份排序后 B 在前
    assert refs[0]["entry"]["title"] == "B"
    assert refs[0]["index"] == 1
    assert refs[1]["index"] == 2


def test_apa_format_no_doi_omits_url():
    """无 DOI 时不输出 https://doi.org/..."""
    entry = {"authors": ["Smith"], "year": 2023, "title": "No DOI"}
    ref = _format_apa(entry)
    assert "https://doi.org" not in ref


def test_apa_format_no_authors_uses_unknown():
    """作者缺失时用 Unknown 占位。"""
    entry = {"year": 2023, "title": "Anon"}
    ref = _format_apa(entry)
    assert "Unknown" in ref


def test_apa_format_no_year_uses_nd():
    """年份缺失时用 n.d.（no date）占位。"""
    entry = {"authors": ["Smith"], "title": "T"}
    ref = _format_apa(entry)
    assert "n.d." in ref


def test_references_each_has_index_text_doi_entry():
    """每条 reference 含 index / text / doi / entry 四字段。"""
    entries = [
        {"authors": ["A"], "year": 2022, "title": "A", "doi": "10.1/a"},
        {"authors": ["B"], "year": 2023, "title": "B"},  # 无 DOI
    ]
    state = {"citation_graph": {"entries": entries, "edges": [], "indices": {}}}
    result = generate_references(state)
    for ref in result["references_list"]:
        assert "index" in ref
        assert "text" in ref
        assert "doi" in ref
        assert "entry" in ref


def test_doi_field_propagated_from_entry():
    """DOI 可追溯: references_list 每项 doi 与 entry.doi 一致。"""
    entries = [
        {"authors": ["A"], "year": 2022, "title": "A", "doi": "10.1/xyz"},
    ]
    state = {"citation_graph": {"entries": entries, "edges": [], "indices": {}}}
    result = generate_references(state)
    assert result["references_list"][0]["doi"] == "10.1/xyz"
    assert "10.1/xyz" in result["references_list"][0]["text"]


def test_citation_graph_missing_returns_empty():
    """citation_graph 缺失时返回空列表。"""
    result = generate_references({"citation_graph": None})
    assert result["references_list"] == []


def test_citation_graph_not_dict_returns_empty():
    """citation_graph 不是 dict 时返回空列表（防御性）。"""
    result = generate_references({"citation_graph": "not a dict"})
    assert result["references_list"] == []


def test_return_type_annotation_is_references_output():
    """NodeResult 协议: 返回类型注解为 ReferencesOutput。"""
    from typing import get_type_hints
    from nodes.generate_references import generate_references as fn
    from protocols import ReferencesOutput

    hints = get_type_hints(fn)
    assert hints.get("return") is ReferencesOutput
