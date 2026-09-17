"""Contract method-literature-check: purpose-driven retrieval + source honesty.

C1 purpose decides query & order (not a post-hoc label)
C2 method_check accepts draft design; topic positioning still requires confirmed
C3 no mock/synthetic in production path; mock anchors never pollute real sources
C4 must-check threats are not truncated by MAX_LITERATURE_ENTRIES
C5 every evidence record carries provenance + reading level (metadata/abstract/fulltext)
C6 a failed source keeps degraded:<Exc> and contributes no hits
"""
from __future__ import annotations

import pytest

from agent.find_lit import (
    READING_LEVELS,
    annotate_evidence,
    build_method_check_query,
    check_method_literature,
    fetch_papers,
)
from agent.find_lit.search import search_find_lit
from agent.nodes.search_literature import (
    MAX_LITERATURE_ENTRIES,
    _merge_unique,
    _method_anchors,
    search_literature,
)

CALLAWAY_DOI = "10.1016/j.jeconom.2022.019"


def _design(**overrides):
    design = {
        "status": "draft",
        "confirmed": False,
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


def _confirmed(design):
    return {**design, "status": "confirmed", "confirmed": True}


def _hit(i, *, source="openalex", doi=None, abstract="", **extra):
    rec = {
        "title": f"Paper {i}",
        "authors": [f"Author {i}"],
        "year": 2000 + i,
        "doi": doi if doi is not None else f"10.1000/p.{i}",
        "url": f"https://doi.org/10.1000/p.{i}",
        "source": source,
        "abstract": abstract,
    }
    rec.update(extra)
    return rec


def _five(source="openalex"):
    return [_hit(i, source=source, abstract="abs") for i in range(1, 6)]


def _unrelated(n):
    return [
        {
            "title": f"Unrelated {i}",
            "authors": ["A"],
            "year": 2020,
            "abstract": " unrelated ",
            "doi": f"10.1/u{i}",
            "source": "mock",
            "relevance_score": 0.5,
        }
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# C1
# ---------------------------------------------------------------------------
def test_c1_purpose_selects_query_not_a_posthoc_label():
    seen = []

    def searcher(query):
        seen.append(query)
        hits = [
            _hit(1, doi="10.1/alpha", title="Alpha", abstract="a"),
            _hit(2, doi="10.1/beta", title="Beta", abstract="b"),
        ]
        # Only the method_check query contains failure-mode words: prove the
        # different order comes from the *query the searcher received*.
        if "parallel trends" in query:
            return list(reversed(hits))
        return hits

    topic = search_find_lit(
        {"design": _confirmed(_design())}, searchers=[("openalex", searcher)]
    )
    method = check_method_literature(design=_design(), searchers=[("openalex", searcher)])

    assert topic["query"] != method["query"]
    assert "did" in method["query"]
    assert any(
        token in method["query"]
        for token in ("parallel trends", "staggered", "negative weights")
    )
    assert "最低工资对就业的影响" in topic["query"]
    assert "employment" in topic["query"]
    assert "min_wage" in topic["query"]
    # The fake searcher saw the purpose-specific queries, not a relabeled result.
    assert method["query"] in seen
    assert topic["query"] in seen
    assert [h["title"] for h in method["hits"]] == ["Beta", "Alpha"]
    assert [c["title"] for c in topic["cards"]] == ["Alpha", "Beta"]


def test_c1_fetch_papers_records_purpose_without_reordering():
    rec = fetch_papers(
        "did assumptions",
        purpose="method_check",
        searchers=[("openalex", lambda q: _five())],
    )
    assert rec["purpose"] == "method_check"
    assert [h["title"] for h in rec["hits"]] == [f"Paper {i}" for i in range(1, 6)]


# ---------------------------------------------------------------------------
# C2
# ---------------------------------------------------------------------------
def test_c2_method_check_accepts_draft_topic_still_requires_confirmed():
    called = []

    def boom(_q):
        called.append(True)
        raise AssertionError("unconfirmed topic positioning must not search")

    draft = _design()
    rec = check_method_literature(design=draft, searchers=[("openalex", lambda q: _five())])
    assert rec["hits"]
    assert rec["reason"] == ""
    assert rec["chapter_written"] is False

    refused = search_find_lit({"design": draft}, searchers=[("openalex", boom)])
    assert refused["reason"] == "design_unconfirmed"
    assert refused["hits"] == []
    assert called == []

    ok = search_find_lit(
        {"design": _confirmed(_design())}, searchers=[("openalex", lambda q: _five())]
    )
    assert ok["reason"] == ""
    assert ok["shown_count"] == 5


# ---------------------------------------------------------------------------
# C3
# ---------------------------------------------------------------------------
def test_c3_1_fetch_papers_drops_mock_and_synthetic_hits():
    rec = fetch_papers(
        "did employment",
        searchers=[
            (
                "openalex",
                lambda q: [
                    _hit(1),
                    {"title": "Mock", "authors": ["M"], "year": 2020, "doi": "10.9/m", "url": "u", "source": "mock"},
                    {"title": "Syn", "authors": ["S"], "year": 2020, "doi": "10.9/s", "url": "u", "sources": ["mock_degraded"]},
                ],
            )
        ],
    )
    assert all(h.get("source") != "mock" for h in rec["hits"])
    assert all("mock_degraded" not in (h.get("sources") or []) for h in rec["hits"])
    assert [h["title"] for h in rec["hits"]] == ["Paper 1"]


def test_c3_2_real_source_branch_drops_mock_anchor(monkeypatch):
    real = [_hit(i, source="crossref", abstract="real") for i in range(1, 4)]
    monkeypatch.setattr(
        "agent.nodes.literature_sources.crossref.crossref_search",
        lambda q, **k: real,
    )
    result = search_literature(
        {
            "research_direction": {"question": "养老金", "method": "DID"},
            "literature_source": "crossref",
        }
    )
    assert result["literature_source"] == "crossref"
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert CALLAWAY_DOI not in dois
    assert all(e.get("source") != "mock" for e in result["literature_entries"])


def test_c3_2_old_call_order_would_have_injected_mock_anchor():
    """Reproduces the pre-fix inputs: anchors were taken unconditionally and
    merged ahead of real entries, so a mock DOI appeared on a real branch."""
    real = [_hit(i, source="crossref", abstract="real") for i in range(1, 4)]
    old_anchors = _method_anchors("did")  # old code called this on every branch
    assert old_anchors and old_anchors[0]["doi"] == CALLAWAY_DOI
    old_result = _merge_unique(old_anchors, real, [])
    assert CALLAWAY_DOI in [e.get("doi") for e in old_result]


def test_c3_2b_real_branch_threat_fallback_does_not_inject_mock(monkeypatch):
    real = [_hit(i, source="crossref", abstract="real") for i in range(1, 4)]

    def flaky(query, **kwargs):
        if "交错" in query or "staggered" in query:
            raise RuntimeError("threat search down")
        return real

    monkeypatch.setattr(
        "agent.nodes.literature_sources.crossref.crossref_search", flaky
    )
    result = search_literature(
        {
            "research_direction": {"question": "养老金", "method": "DID"},
            "literature_source": "crossref",
        }
    )
    assert result["literature_source"] == "crossref"
    assert result["literature_entries"]
    assert all(e.get("source") == "crossref" for e in result["literature_entries"])
    assert "threat" not in result["literature_actions"]


def test_c3_3_all_sources_fail_no_mock_fallback():
    def boom(_q):
        raise TimeoutError("down")

    searchers = [
        ("openalex", boom),
        ("crossref", boom),
        ("semantic_scholar", boom),
    ]
    rec = fetch_papers("did employment", searchers=searchers)
    assert rec["hits"] == []
    assert rec["source_status"] == {
        "openalex": "degraded:TimeoutError",
        "crossref": "degraded:TimeoutError",
        "semantic_scholar": "degraded:TimeoutError",
    }

    mc = check_method_literature(design=_design(), searchers=searchers)
    assert mc["hits"] == []
    assert mc["evidence"] == []
    assert mc["reason"] == "no_hits"
    assert mc["source_status"]["openalex"] == "degraded:TimeoutError"


# ---------------------------------------------------------------------------
# C4
# ---------------------------------------------------------------------------
def test_c4_threat_survives_entry_cap(monkeypatch):
    def fake(query):
        if "交错" in query or "staggered" in query:
            return [
                {
                    "title": "Staggered treatment bias",
                    "authors": ["X"],
                    "year": 2021,
                    "abstract": "交错 DID 威胁",
                    "doi": "10.9/threat",
                    "source": "mock",
                    "relevance_score": 0.6,
                }
            ]
        return _unrelated(25)

    monkeypatch.setattr("agent.nodes.search_literature._mock_search", fake)
    result = search_literature(
        {"research_direction": {"question": "养老金", "method": "DID"}}
    )
    dois = [e.get("doi") for e in result["literature_entries"]]
    assert "10.9/threat" in dois
    assert CALLAWAY_DOI in dois
    assert len(result["literature_entries"]) <= MAX_LITERATURE_ENTRIES


def test_c4_old_merge_order_dropped_the_threat():
    """Pre-fix order (anchors, entries, threat) truncates the threat at 20."""
    anchors = _method_anchors("did")
    entries = _unrelated(25)
    threat = [
        {"title": "Staggered treatment bias", "doi": "10.9/threat", "authors": ["X"], "year": 2021, "source": "mock"}
    ]
    old_result = _merge_unique(anchors, entries, threat)
    assert len(old_result) == MAX_LITERATURE_ENTRIES
    assert "10.9/threat" not in [e.get("doi") for e in old_result]

    new_result = _merge_unique(anchors, threat, entries)
    assert "10.9/threat" in [e.get("doi") for e in new_result]
    assert len(new_result) <= MAX_LITERATURE_ENTRIES


# ---------------------------------------------------------------------------
# C5
# ---------------------------------------------------------------------------
def test_c5_evidence_has_provenance_and_reading_level():
    hits = [
        _hit(1, doi="10.1/wa", url="https://doi.org/10.1/wa", source="openalex", abstract="real abstract"),
        {
            "title": "Meta only",
            "authors": ["B"],
            "year": 2019,
            "doi": None,
            "url": "https://example.org/meta",
            "source": "crossref",
        },
    ]
    rec = check_method_literature(
        design=_design(),
        searchers=[
            ("openalex", lambda q: [hits[0]]),
            ("crossref", lambda q: [hits[1]]),
        ],
    )
    assert rec["evidence"]
    ev = rec["evidence"][0]
    for key in ("title", "doi", "url", "source", "year", "reading_level", "source_status"):
        assert key in ev
    assert ev["reading_level"] in READING_LEVELS
    with_abs = next(e for e in rec["evidence"] if e["title"] == "Paper 1")
    meta = next(e for e in rec["evidence"] if e["title"] == "Meta only")
    assert meta["doi"] is None
    assert with_abs["reading_level"] == "abstract"
    assert meta["reading_level"] == "metadata"
    assert all(e["reading_level"] != "fulltext" for e in rec["evidence"])
    assert all(e["source_status"] == "ok" for e in rec["evidence"])


def test_c5_missing_risk_says_not_found_not_absence():
    def searcher(query):
        if query == "iv weak instruments":
            return []
        return [_hit(1, abstract="x")]

    rec = check_method_literature(design=_design(method="iv"), searchers=[("openalex", searcher)])
    missing = [r for r in rec["risk_coverage"] if r["status"] == "not_found"]
    assert missing, rec["risk_coverage"]
    assert all(r["statement"] == "未找到" for r in missing)
    assert all("不存在" not in (r.get("statement") or "") for r in rec["risk_coverage"])
    assert any(r["status"] == "covered" for r in rec["risk_coverage"])


def test_c5_default_reading_level_is_metadata_not_fulltext():
    ev = annotate_evidence([_hit(1, abstract="")], {"openalex": "ok"})
    assert ev[0]["reading_level"] == "metadata"


# ---------------------------------------------------------------------------
# C6
# ---------------------------------------------------------------------------
def test_c6_failed_source_keeps_status_and_only_ok_source_contributes():
    def boom(_q):
        raise RuntimeError("network down")

    rec = check_method_literature(
        design=_design(),
        searchers=[
            ("openalex", lambda q: _five("openalex")),
            ("crossref", boom),
            ("semantic_scholar", boom),
        ],
    )
    assert rec["source_status"]["openalex"] == "ok"
    assert rec["source_status"]["crossref"] == "degraded:RuntimeError"
    assert rec["source_status"]["semantic_scholar"] == "degraded:RuntimeError"
    assert rec["hits"]
    assert all(h["source"] == "openalex" for h in rec["hits"])
    assert all(e["source_status"] == "ok" for e in rec["evidence"])
