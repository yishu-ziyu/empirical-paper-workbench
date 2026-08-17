"""ADR-0010: Crossref is a first-class literature source with mock fallback."""
from nodes.search_literature import search_literature


def test_crossref_source_maps_entries(monkeypatch):
    fake = [
        {
            "title": "Returns to Schooling",
            "authors": ["Card, David"],
            "year": 1999,
            "abstract": "handbook chapter",
            "doi": "10.1016/s1573-4463(99)03011-4",
            "source": "crossref",
            "relevance_score": 1.0,
        }
    ]
    monkeypatch.setattr(
        "nodes.literature_sources.crossref.crossref_search",
        lambda query, **kwargs: fake,
    )
    result = search_literature(
        {"research_direction": "education wages", "literature_source": "crossref"}
    )
    assert result["literature_source"] == "crossref"
    assert result["literature_entries"][0]["doi"] == fake[0]["doi"]
    assert result["literature_entries"][0]["source"] == "crossref"


def test_crossref_error_degrades_to_mock(monkeypatch):
    def _boom(query, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(
        "nodes.literature_sources.crossref.crossref_search",
        _boom,
    )
    result = search_literature(
        {"research_direction": "劳动 教育", "literature_source": "crossref"}
    )
    assert result["literature_source"] == "mock_degraded"
    assert result["literature_source"] != "crossref"
    assert result["literature_produced_by"] == "search_literature"
    assert isinstance(result["literature_entries"], list)
    assert result["literature_entries"]
    for e in result["literature_entries"]:
        assert e["source"] == "mock"
