"""FL V1 search: OpenAlex + Crossref + S2, DOI dedupe, checkbox cards. No chapter write."""
from __future__ import annotations

from typing import Any, Callable, Iterable

from .cards import MIN_CARDS, has_min_cards, hits_to_cards
from .dedupe import dedupe_hits, normalize_doi
from .export import export_checked
from .polite_pool import polite_pool_note
from .query import build_query, design_is_confirmed, session_design

Searcher = Callable[[str], list[dict[str, Any]]]

SOURCE_OPENALEX = "openalex"
SOURCE_CROSSREF = "crossref"
SOURCE_S2 = "semantic_scholar"


def empty_find_lit(*, query: str = "", reason: str = "") -> dict[str, Any]:
    return {
        "hits": [],
        "cards": [],
        "checked_ids": [],
        "export": {"refs_bib": "", "csl_json": []},
        "polite_pool": polite_pool_note(),
        "query": query,
        "source_status": {},
        "shown_count": 0,
        "chapter_written": False,
        "reason": reason,
    }


def _as_hit(entry: dict[str, Any], source: str) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    title = str(entry.get("title") or "").strip()
    if not title:
        return None
    authors = entry.get("authors") if isinstance(entry.get("authors"), list) else []
    authors = [str(a).strip() for a in authors if str(a).strip()]
    doi = normalize_doi(entry.get("doi")) or None
    url = str(entry.get("url") or "").strip()
    if not url and doi:
        url = f"https://doi.org/{doi}"
    try:
        year = int(entry.get("year") or 0)
    except (TypeError, ValueError):
        year = 0
    return {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "url": url or None,
        "source": source,
        "abstract": str(entry.get("abstract") or ""),
    }


def _search_openalex(query: str) -> list[dict[str, Any]]:
    from ..nodes.literature_sources.openalex import openalex_search

    return [
        hit
        for hit in (_as_hit(e, SOURCE_OPENALEX) for e in openalex_search(query))
        if hit
    ]


def _search_crossref(query: str) -> list[dict[str, Any]]:
    from ..nodes.literature_sources.crossref import crossref_search

    return [
        hit
        for hit in (_as_hit(e, SOURCE_CROSSREF) for e in crossref_search(query))
        if hit
    ]


def _search_s2(query: str) -> list[dict[str, Any]]:
    from ..nodes.literature_sources.semantic_scholar import (
        get_api_key_from_env,
        semantic_scholar_search,
    )

    api_key = get_api_key_from_env() or None
    return [
        hit
        for hit in (
            _as_hit(e, SOURCE_S2) for e in semantic_scholar_search(query, api_key)
        )
        if hit
    ]


def default_searchers() -> list[tuple[str, Searcher]]:
    return [
        (SOURCE_OPENALEX, _search_openalex),
        (SOURCE_CROSSREF, _search_crossref),
        (SOURCE_S2, _search_s2),
    ]


def _run_searchers(
    query: str,
    searchers: Iterable[tuple[str, Searcher]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    hits: list[dict[str, Any]] = []
    status: dict[str, str] = {}
    for name, fn in searchers:
        try:
            batch = fn(query) or []
            status[name] = "ok"
            hits.extend(item for item in batch if isinstance(item, dict))
        except Exception as exc:
            status[name] = f"degraded:{type(exc).__name__}"
    return hits, status


def search_find_lit(
    state: dict[str, Any] | None = None,
    *,
    design: dict[str, Any] | None = None,
    searchers: Iterable[tuple[str, Searcher]] | None = None,
) -> dict[str, Any]:
    """Search three sources from confirmed design. Never writes chapters."""
    design = design if isinstance(design, dict) else session_design(state or {})
    if not design_is_confirmed(design):
        return empty_find_lit(reason="design_unconfirmed")
    query = build_query(design)
    if not query:
        return empty_find_lit(reason="empty_query")
    raw, source_status = _run_searchers(query, searchers or default_searchers())
    hits = dedupe_hits(raw)
    cards = hits_to_cards(hits)
    rec = empty_find_lit(query=query)
    rec.update(
        {
            "hits": hits,
            "cards": cards,
            "source_status": source_status,
            "shown_count": len(cards),
            "reason": "" if has_min_cards(cards) else "need_5_cards",
        }
    )
    rec["chapter_written"] = False
    return rec


def check_cards(find_lit: dict[str, Any], checked_ids: list[str]) -> dict[str, Any]:
    """Human check. Unchecked cards stay out of export. No chapter write."""
    rec = dict(find_lit or empty_find_lit())
    known = {str(c.get("id")) for c in (rec.get("cards") or []) if isinstance(c, dict)}
    ids = [str(i) for i in (checked_ids or []) if str(i) in known]
    cards = []
    for card in rec.get("cards") or []:
        if not isinstance(card, dict):
            continue
        item = dict(card)
        item["checked"] = str(item.get("id")) in ids
        cards.append(item)
    rec["cards"] = cards
    rec["checked_ids"] = ids
    rec["export"] = export_checked(cards, ids)
    rec["chapter_written"] = False
    rec["shown_count"] = len(cards)
    if len(cards) < MIN_CARDS:
        rec["reason"] = "need_5_cards"
    return rec
