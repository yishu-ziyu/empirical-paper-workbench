"""FL-BE-search / R-lit-bar: OpenAlex + Crossref + S2, DOI dedupe, cards, bib export."""
from __future__ import annotations

from agent.find_lit import (
    MIN_CARDS,
    V1_SOURCES,
    build_query,
    check_cards,
    dedupe_hits,
    design_is_confirmed,
    export_checked,
    fetch_papers,
    literature_write_allowed,
    literature_write_blockers,
    mailto,
    normalize_doi,
    search_find_lit,
    user_agent,
)
from agent.nodes.generate_chapter import generate_chapter
from agent.nodes.search_literature import search_literature
from conftest import make_write_ready_state, make_six_chapter_outline


def _confirmed_design(**overrides):
    design = {
        "status": "confirmed",
        "confirmed": True,
        "source": {
            "title": "最低工资对就业的影响",
            "question": "提高最低工资是否减少就业",
        },
        "method": "did",
        "outcome": "employment",
        "treatment": "min_wage",
    }
    design.update(overrides)
    return design


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


def _five_hits(source: str = "openalex"):
    return [_hit(i, source=source) for i in range(1, 6)]


def test_query_from_confirmed_design_facets_not_free_write():
    q = build_query(_confirmed_design())
    assert "最低工资对就业的影响" in q
    assert "did" in q
    assert "employment" in q
    assert "min_wage" in q


def test_unconfirmed_design_does_not_search():
    called = []

    def boom(_query):
        called.append(True)
        raise AssertionError("must not search")

    rec = search_find_lit(
        {"design": {"status": "draft", "source": {"title": "x"}}},
        searchers=[("openalex", boom)],
    )
    assert rec["cards"] == []
    assert rec["reason"] == "design_unconfirmed"
    assert rec["chapter_written"] is False
    assert called == []
    assert design_is_confirmed({"design": {"status": "draft"}}) is False
    assert design_is_confirmed({"design": {"status": "confirmed"}}) is False


def test_search_merges_three_sources_and_doi_dedupes():
    def oa(_q):
        return _five_hits("openalex") + [
            _hit(1, source="openalex", doi="10.1000/FL.1", title="Short")
        ]

    def cr(_q):
        return [
            _hit(
                1,
                source="crossref",
                doi="https://doi.org/10.1000/FL.1",
                title="Fuller Minimum Wage Title",
                authors=["Author 1", "Second"],
            ),
            _hit(9, source="crossref"),
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

    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[
            ("openalex", oa),
            ("crossref", cr),
            ("semantic_scholar", s2),
        ],
    )
    assert rec["chapter_written"] is False
    assert rec["checked_ids"] == []
    assert rec["source_status"] == {
        "openalex": "ok",
        "crossref": "ok",
        "semantic_scholar": "ok",
    }
    assert rec["shown_count"] >= MIN_CARDS
    cards = rec["cards"]
    dois = [c["doi"] for c in cards if c.get("doi")]
    assert dois.count("10.1000/fl.1") == 1
    winner = next(c for c in cards if c["doi"] == "10.1000/fl.1")
    assert winner["title"] == "Fuller Minimum Wage Title"
    assert "Second" in winner["authors"]
    assert set(winner["sources"]) >= {"openalex", "crossref", "semantic_scholar"}
    link_only = next(c for c in cards if c["title"] == "Link only work")
    assert link_only["doi"] is None
    assert link_only["url"].startswith("https://")
    for card in cards:
        assert card["title"]
        assert card["authors"]
        assert card["year"]
        assert card["doi"] or card["url"]
        assert card["checked"] is False


def test_one_source_failure_does_not_invent_or_mock_fill():
    def oa(_q):
        return _five_hits("openalex")

    def boom(_q):
        raise RuntimeError("network down")

    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[
            ("openalex", oa),
            ("crossref", boom),
            ("semantic_scholar", boom),
        ],
    )
    assert rec["source_status"]["openalex"] == "ok"
    assert rec["source_status"]["crossref"].startswith("degraded:")
    assert rec["source_status"]["semantic_scholar"].startswith("degraded:")
    assert all(c["source"] != "mock" for c in rec["hits"])
    assert rec["shown_count"] >= MIN_CARDS
    assert rec["chapter_written"] is False


def test_fewer_than_five_cards_fail_closed():
    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[
            ("openalex", lambda q: [_hit(1)]),
            ("crossref", lambda q: []),
            ("semantic_scholar", lambda q: []),
        ],
    )
    assert rec["shown_count"] < MIN_CARDS
    assert rec["reason"] == "need_5_cards"
    assert literature_write_allowed({"design": _confirmed_design(), "find_lit": rec}) is False
    assert "r_lit_bar_need_5_cards" in literature_write_blockers(
        {"design": _confirmed_design(), "find_lit": rec}
    )


def test_drop_unverified_title_only_hits():
    merged = dedupe_hits(
        [
            {
                "title": "No identifiers",
                "authors": ["A"],
                "year": 2001,
                "doi": None,
                "url": None,
                "source": "openalex",
            },
            _hit(2),
        ]
    )
    from agent.find_lit.cards import hits_to_cards

    cards = hits_to_cards(merged)
    assert all(c["doi"] or c["url"] for c in cards)
    assert "No identifiers" not in [c["title"] for c in cards]


def test_normalize_doi_strips_url_prefix():
    assert normalize_doi("https://doi.org/10.1000/ABC") == "10.1000/abc"
    assert normalize_doi("DOI:10.1000/abc") == "10.1000/abc"


def test_checked_export_only_checked_cards():
    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[
            ("openalex", lambda q: _five_hits()),
            ("crossref", lambda q: []),
            ("semantic_scholar", lambda q: []),
        ],
    )
    empty = export_checked(rec["cards"], [])
    assert empty["refs_bib"] == ""
    assert empty["csl_json"] == []

    chosen = [rec["cards"][0]["id"], rec["cards"][1]["id"]]
    checked = check_cards(rec, chosen)
    assert checked["checked_ids"] == chosen
    assert checked["chapter_written"] is False
    assert "Paper 1" in checked["export"]["refs_bib"]
    assert "Paper 2" in checked["export"]["refs_bib"]
    assert "Paper 3" not in checked["export"]["refs_bib"]
    assert len(checked["export"]["csl_json"]) == 2
    assert checked["export"]["csl_json"][0]["DOI"] == "10.1000/fl.1"
    assert checked["export"]["csl_json"][0]["title"]
    unchecked_still = [c for c in checked["cards"] if not c["checked"]]
    assert len(unchecked_still) == 3


def test_chapter_write_requires_confirmed_five_cards_and_checks():
    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[("openalex", lambda q: _five_hits())],
    )
    state = {"design": _confirmed_design(), "find_lit": rec}
    assert literature_write_allowed(state) is False
    assert "r_lit_bar_no_checked" in literature_write_blockers(state)

    state["find_lit"] = check_cards(rec, [rec["cards"][0]["id"]])
    assert literature_write_allowed(state) is True
    assert literature_write_blockers(state) == []

    assert literature_write_allowed({"research_direction": "x"}) is True


def test_fetch_papers_wrap_keeps_checkbox_bib_on_find_lit():
    assert V1_SOURCES == ("openalex", "crossref", "semantic_scholar")
    fetched = fetch_papers(
        "did employment min_wage",
        searchers=[("openalex", lambda q: _five_hits())],
    )
    assert "export" not in fetched
    assert "checked_ids" not in fetched
    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[("openalex", lambda q: _five_hits())],
    )
    assert rec["checked_ids"] == []
    assert rec["export"]["refs_bib"] == ""
    chosen = [rec["cards"][0]["id"]]
    checked = check_cards(rec, chosen)
    assert checked["checked_ids"] == chosen
    assert "Paper 1" in checked["export"]["refs_bib"]
    assert checked["chapter_written"] is False
    state = {"design": _confirmed_design(), "find_lit": rec}
    assert literature_write_allowed(state) is False
    assert literature_write_allowed({"design": _confirmed_design(), "find_lit": checked}) is True


def test_search_find_lit_does_not_show_synthetic_as_found():
    rec = search_find_lit(
        {"design": _confirmed_design()},
        searchers=[
            (
                "openalex",
                lambda q: _five_hits() + [_hit(99, source="synthetic")],
            )
        ],
    )
    assert all("synthetic" not in (h.get("sources") or [h.get("source")]) for h in rec["hits"])
    assert "Paper 99" not in [c["title"] for c in rec["cards"]]
    assert rec["shown_count"] >= MIN_CARDS
    assert rec["chapter_written"] is False


def test_mailto_polite_pool_stub_and_env(monkeypatch):
    assert mailto() == "dev@local"
    assert "mailto:dev@local" in user_agent()
    monkeypatch.setenv("ECONPAPER_POLITE_MAILTO", "papers@example.org")
    assert mailto() == "papers@example.org"
    assert "mailto:papers@example.org" in user_agent()


def test_search_literature_confirmed_skips_mock_generate_as_lit(monkeypatch):
    def fake_search(state, **kwargs):
        return {
            "hits": _five_hits(),
            "cards": [],
            "checked_ids": [],
            "query": "did employment",
            "chapter_written": False,
        }

    monkeypatch.setattr("agent.find_lit.search.search_find_lit", fake_search)
    result = search_literature(
        {
            "research_direction": {"question": "养老金", "method": "DID"},
            "design": _confirmed_design(),
        }
    )
    assert result["literature_entries"] == []
    assert result["literature_source"] == "r_lit_bar"
    assert result["literature_actions"] == ["fl_search"]
    assert result["find_lit"]["chapter_written"] is False


def test_generate_chapter_blocks_lit_review_without_r_lit_bar():
    state = make_write_ready_state(
        current_chapter_index=1,
        outline=make_six_chapter_outline(),
        design=_confirmed_design(),
        key_references="GOLD BIBLIO PASTE",
        research_question="Q",
    )
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert "r_lit_bar_need_5_cards" in result.get("write_blockers", [])
    assert "body_chapters" not in result
