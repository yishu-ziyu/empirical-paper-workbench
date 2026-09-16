"""Checkbox-ready FL cards. Verifiable title/author/year/DOI-or-link only."""
from __future__ import annotations

from typing import Any

from .dedupe import normalize_doi, work_key

MIN_CARDS = 5


def followable_url(hit: dict[str, Any]) -> str:
    doi = normalize_doi(hit.get("doi"))
    url = str(hit.get("url") or "").strip()
    if doi:
        return url or f"https://doi.org/{doi}"
    return url


def is_verifiable(hit: dict[str, Any]) -> bool:
    if not isinstance(hit, dict):
        return False
    title = str(hit.get("title") or "").strip()
    authors = hit.get("authors") if isinstance(hit.get("authors"), list) else []
    authors = [str(a).strip() for a in authors if str(a).strip()]
    try:
        year = int(hit.get("year") or 0)
    except (TypeError, ValueError):
        year = 0
    if not title or not authors or year <= 0:
        return False
    doi = normalize_doi(hit.get("doi"))
    url = followable_url({**hit, "authors": authors})
    return bool(doi or url)


def hit_to_card(hit: dict[str, Any]) -> dict[str, Any] | None:
    if not is_verifiable(hit):
        return None
    authors = [str(a).strip() for a in (hit.get("authors") or []) if str(a).strip()]
    doi = normalize_doi(hit.get("doi")) or None
    url = followable_url(hit)
    card_id = str(hit.get("id") or work_key(hit))
    return {
        "id": card_id,
        "title": str(hit.get("title") or "").strip(),
        "authors": authors,
        "year": int(hit.get("year") or 0),
        "doi": doi,
        "url": url,
        "sources": list(hit.get("sources") or ([hit.get("source")] if hit.get("source") else [])),
        "checked": False,
    }


def hits_to_cards(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for hit in hits:
        card = hit_to_card(hit)
        if card is None or card["id"] in seen:
            continue
        seen.add(card["id"])
        cards.append(card)
    return cards


def has_min_cards(cards: list[dict[str, Any]]) -> bool:
    return len(cards) >= MIN_CARDS
