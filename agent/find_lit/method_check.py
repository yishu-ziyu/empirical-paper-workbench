"""FL method-check entry: reuse the three sources for a *tentative* design.

Method check happens before the method is frozen, so it must NOT go through
`search_find_lit`'s confirmed-design gate (that would be a circular dependency).
It calls `fetch_papers(..., purpose="method_check")` directly and builds an
evidence artifact where every record says how deep it was read
(metadata / abstract / fulltext) and what each source did.

Honesty rules (DATA-RIGOR):
- mock / synthetic hits never count as found (fetch_papers drops them).
- All three sources failing => empty hits, every source `degraded:<Exc>`, and
  no fallback to the mock corpus.
- A risk with no hit is recorded as "未找到" (not searched-and-found-absent);
  it is never written as "does not exist".
"""
from __future__ import annotations

from typing import Any, Iterable

from .cards import hits_to_cards
from .dedupe import dedupe_hits
from .fetch_papers import PURPOSE_METHOD_CHECK, Searcher, fetch_papers
from .query import build_method_check_query, build_risk_queries, session_design

# How deep the evidence was actually read. Default is the shallowest, never
# "fulltext": an unread abstract must not be stamped as read fulltext.
READING_LEVELS = ("metadata", "abstract", "fulltext")

NOT_FOUND_STATEMENT = "未找到"


def reading_level_of(hit: dict[str, Any]) -> str:
    if not isinstance(hit, dict):
        return "metadata"
    if hit.get("fulltext"):
        return "fulltext"
    if str(hit.get("abstract") or "").strip():
        return "abstract"
    return "metadata"


def source_status_for(hit: dict[str, Any], source_status: dict[str, str]) -> str:
    status = source_status or {}
    names: list[str] = []
    for src in (hit.get("sources"), [hit.get("source")]):
        for item in src or []:
            token = str(item or "").strip()
            if token and token not in names:
                names.append(token)
    for name in names:
        if name in status:
            return status[name]
    return status.get(str(hit.get("source") or ""), "")


def annotate_evidence(
    hits: Iterable[dict[str, Any]],
    source_status: dict[str, str],
) -> list[dict[str, Any]]:
    """Attach reading level + per-record source status to each hit."""
    evidence: list[dict[str, Any]] = []
    for hit in hits or []:
        if not isinstance(hit, dict):
            continue
        rec = dict(hit)
        rec["reading_level"] = reading_level_of(rec)
        rec["source_status"] = source_status_for(rec, source_status)
        rec["found"] = True
        evidence.append(rec)
    return evidence


def empty_method_check(*, query: str = "", reason: str = "") -> dict[str, Any]:
    return {
        "purpose": PURPOSE_METHOD_CHECK,
        "query": query,
        "queries": [],
        "hits": [],
        "evidence": [],
        "cards": [],
        "risk_coverage": [],
        "source_status": {},
        "reason": reason,
        "chapter_written": False,
    }


def check_method_literature(
    state: dict[str, Any] | None = None,
    *,
    design: dict[str, Any] | None = None,
    searchers: Iterable[tuple[str, Searcher]] | None = None,
) -> dict[str, Any]:
    """Method check on a tentative (draft) design. No confirmed-design gate."""
    design = design if isinstance(design, dict) else session_design(state or {})
    query = build_method_check_query(design)
    if not query:
        return empty_method_check(reason="empty_query")

    pool: list[tuple[str, Searcher]] | None
    pool = list(searchers) if searchers is not None else None

    main = fetch_papers(query, purpose=PURPOSE_METHOD_CHECK, searchers=pool)
    raw_hits: list[dict[str, Any]] = list(main.get("hits") or [])
    source_status: dict[str, str] = dict(main.get("source_status") or {})
    queries: list[str] = [query]

    risk_coverage: list[dict[str, Any]] = []
    for risk_query in build_risk_queries(design):
        fetched = fetch_papers(
            risk_query, purpose=PURPOSE_METHOD_CHECK, searchers=pool
        )
        queries.append(risk_query)
        source_status.update(fetched.get("source_status") or {})
        found = list(fetched.get("hits") or [])
        raw_hits.extend(found)
        risk_coverage.append(
            {
                "query": risk_query,
                "status": "covered" if found else "not_found",
                "statement": "" if found else NOT_FOUND_STATEMENT,
                "hits": len(found),
            }
        )

    hits = dedupe_hits(raw_hits)
    return {
        "purpose": PURPOSE_METHOD_CHECK,
        "query": query,
        "queries": queries,
        "hits": hits,
        "evidence": annotate_evidence(hits, source_status),
        "cards": hits_to_cards(hits),
        "risk_coverage": risk_coverage,
        "source_status": source_status,
        "reason": "" if hits else "no_hits",
        "chapter_written": False,
    }
