"""FL-BE-reuse: fetch_papers thin wrap inside find_lit. No parallel lit stack."""
from __future__ import annotations

from agent.find_lit.fetch_papers import (
    V1_SOURCES,
    default_searchers,
    fetch_papers,
    is_found_hit,
)
from agent.find_lit.search import search_find_lit


def _hit(i: int, *, source: str = "openalex", doi: str | None = None, **extra):
    rec = {
        "title": f"Paper {i} on minimum wages",
        "authors": [f"Author {i}"],
        "year": 2000 + i,
        "doi": doi if doi is not None else f"10.1000/fl.{i}",
        "url": f"https://doi.org/10.1000/fl.{i}" if doi is None else extra.get("url"),
        "source": source,
    }
    rec.update(extra)
    if rec.get("url") is None and rec.get("doi"):
        rec["url"] = f"https://doi.org/{rec['doi']}"
    return rec


def test_v1_sources_are_openalex_crossref_s2_only():
    assert V1_SOURCES == ("openalex", "crossref", "semantic_scholar")
    names = [name for name, _ in default_searchers()]
    assert names == list(V1_SOURCES)
    for banned in ("pubmed", "europepmc", "arxiv", "elicit", "cnki", "consensus"):
        assert banned not in names


def test_fetch_papers_merges_three_sources_and_doi_dedupes():
    def oa(_q):
        return [_hit(1, source="openalex", doi="10.1000/FL.1", title="Short")]

    def cr(_q):
        return [
            _hit(
                1,
                source="crossref",
                doi="https://doi.org/10.1000/FL.1",
                title="Fuller Minimum Wage Title",
                authors=["Author 1", "Second"],
            ),
            _hit(2, source="crossref"),
        ]

    def s2(_q):
        return [
            _hit(1, source="semantic_scholar", doi="10.1000/fl.1"),
            {
                "title": "Link only work",
                "authors": ["Solo"],
                "year": 2011,
                "doi": None,
                "url": "https://www.semanticscholar.org/paper/abc",
                "source": "semantic_scholar",
            },
        ]

    rec = fetch_papers(
        "did employment min_wage",
        searchers=[
            ("openalex", oa),
            ("crossref", cr),
            ("semantic_scholar", s2),
        ],
    )
    assert rec["chapter_written"] is False
    assert "cards" not in rec
    assert "checked_ids" not in rec
    assert "literature_entries" not in rec
    assert rec["source_status"] == {
        "openalex": "ok",
        "crossref": "ok",
        "semantic_scholar": "ok",
    }
    dois = [h["doi"] for h in rec["hits"] if h.get("doi")]
    assert dois.count("10.1000/fl.1") == 1
    winner = next(h for h in rec["hits"] if h.get("doi") == "10.1000/fl.1")
    assert winner["title"] == "Fuller Minimum Wage Title"
    assert "Second" in winner["authors"]
    assert set(winner["sources"]) >= {"openalex", "crossref", "semantic_scholar"}
    link_only = next(h for h in rec["hits"] if h["title"] == "Link only work")
    assert not link_only.get("doi")
    assert str(link_only.get("url") or "").startswith("https://")


def test_fetch_papers_one_source_failure_does_not_mock_fill(monkeypatch):
    from agent.nodes.literature_sources import mock_corpus as mc

    corpus_calls = []
    monkeypatch.setattr(
        mc, "mock_literature_corpus", lambda: corpus_calls.append(True) or []
    )

    def oa(_q):
        return [_hit(i) for i in range(1, 4)]

    def boom(_q):
        raise RuntimeError("network down")

    rec = fetch_papers(
        "did employment",
        searchers=[
            ("openalex", oa),
            ("crossref", boom),
            ("semantic_scholar", boom),
        ],
    )
    assert rec["source_status"]["openalex"] == "ok"
    assert rec["source_status"]["crossref"].startswith("degraded:")
    assert rec["source_status"]["semantic_scholar"].startswith("degraded:")
    assert all(h.get("source") != "mock" for h in rec["hits"])
    assert rec["chapter_written"] is False
    assert corpus_calls == []


def test_fetch_papers_empty_query_does_not_search():
    called = []

    rec = fetch_papers(
        "  ",
        searchers=[("openalex", lambda q: called.append(q) or [_hit(1)])],
    )
    assert rec["hits"] == []
    assert rec["source_status"] == {}
    assert called == []


def test_fetch_papers_is_not_a_chapter_or_biblio_writer(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rec = fetch_papers(
        "did employment",
        searchers=[("openalex", lambda q: [_hit(1)])],
    )
    assert rec["hits"]
    assert not (tmp_path / "results.json").exists()
    assert not (tmp_path / "refs.bib").exists()
    assert not (tmp_path / "manifest.json").exists()
    assert "literature_entries" not in rec
    assert "cards" not in rec


def test_fetch_papers_drops_synthetic_and_mock_as_not_found():
    rec = fetch_papers(
        "did employment",
        searchers=[
            (
                "openalex",
                lambda q: [
                    _hit(1, source="openalex"),
                    _hit(2, source="mock"),
                    _hit(3, source="synthetic"),
                    _hit(4, source="mock_degraded"),
                    _hit(1, source="gold", doi="10.1000/fl.1", title="Gold paste"),
                ],
            )
        ],
    )
    sources = {h.get("source") for h in rec["hits"]}
    titles = [h.get("title") for h in rec["hits"]]
    assert sources == {"openalex"}
    assert "Gold paste" not in titles
    assert all(is_found_hit(h) for h in rec["hits"])
    assert any(h["doi"] == "10.1000/fl.1" for h in rec["hits"])
    assert rec["chapter_written"] is False


def test_search_find_lit_calls_fetch_papers_after_confirm(monkeypatch):
    called = []

    def fake_fetch(query, searchers=None):
        called.append({"query": query, "searchers": searchers})
        return {
            "hits": [_hit(i) for i in range(1, 6)],
            "source_status": {"openalex": "ok"},
            "query": query,
            "chapter_written": False,
        }

    monkeypatch.setattr("agent.find_lit.search.fetch_papers", fake_fetch)
    rec = search_find_lit(
        {
            "design": {
                "status": "confirmed",
                "confirmed": True,
                "source": {"title": "最低工资对就业的影响", "question": "q"},
                "method": "did",
                "outcome": "employment",
                "treatment": "min_wage",
            }
        }
    )
    assert len(called) == 1
    assert "did" in called[0]["query"]
    assert rec["shown_count"] >= 5
    assert rec["checked_ids"] == []
    assert rec["export"]["refs_bib"] == ""
    assert rec["chapter_written"] is False
    assert "literature_entries" not in rec


def test_unconfirmed_design_does_not_call_fetch_papers(monkeypatch):
    called = []

    def boom(query, searchers=None):
        called.append(True)
        raise AssertionError("must not fetch")

    monkeypatch.setattr("agent.find_lit.search.fetch_papers", boom)
    rec = search_find_lit({"design": {"status": "draft", "source": {"title": "x"}}})
    assert called == []
    assert rec["reason"] == "design_unconfirmed"
    assert rec["cards"] == []
    assert rec["chapter_written"] is False
