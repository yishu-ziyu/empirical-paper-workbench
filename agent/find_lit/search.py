"""FL V1 search: confirmed design → fetch_papers → checkbox cards. No chapter write."""
from __future__ import annotations

from typing import Any, Iterable

from .cards import MIN_CARDS, has_min_cards, hits_to_cards
from .export import export_checked
from .fetch_papers import Searcher, fetch_papers
from .polite_pool import polite_pool_note
from .query import build_query, design_is_confirmed, session_design


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
    fetched = fetch_papers(query, searchers=searchers)
    hits = fetched.get("hits") or []
    cards = hits_to_cards(hits)
    rec = empty_find_lit(query=query)
    rec.update(
        {
            "hits": hits,
            "cards": cards,
            "source_status": fetched.get("source_status") or {},
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
