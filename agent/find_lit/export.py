"""Checked cards → refs.bib and CSL-JSON. Empty checked_ids → empty export."""
from __future__ import annotations

import re
from typing import Any


def _bib_escape(value: str) -> str:
    return (
        (value or "")
        .replace("\\", "\\textbackslash{}")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def _citekey(card: dict[str, Any], used: set[str]) -> str:
    authors = card.get("authors") or []
    first = str(authors[0] if authors else "anon")
    family = first.split(",")[0].strip()
    token = re.sub(r"[^A-Za-z0-9]+", "", family) or "anon"
    year = card.get("year") or "nd"
    doi = str(card.get("doi") or card.get("id") or "x")
    tail = re.sub(r"[^A-Za-z0-9]+", "", doi)[-8:] or "x"
    base = f"{token}{year}{tail}"
    key = base
    n = 2
    while key in used:
        key = f"{base}{n}"
        n += 1
    used.add(key)
    return key


def _author_csl(name: str) -> dict[str, str]:
    raw = str(name or "").strip()
    if "," in raw:
        family, given = [p.strip() for p in raw.split(",", 1)]
        out: dict[str, str] = {"family": family}
        if given:
            out["given"] = given
        return out
    parts = raw.split()
    if len(parts) >= 2:
        return {"family": parts[-1], "given": " ".join(parts[:-1])}
    return {"family": raw or "Unknown"}


def card_to_bibtex(card: dict[str, Any], citekey: str) -> str:
    authors = " and ".join(str(a) for a in (card.get("authors") or []))
    fields = [
        f"  title = {{{_bib_escape(str(card.get('title') or ''))}}}",
        f"  author = {{{_bib_escape(authors)}}}",
        f"  year = {{{card.get('year') or ''}}}",
    ]
    if card.get("doi"):
        fields.append(f"  doi = {{{_bib_escape(str(card['doi']))}}}")
    if card.get("url"):
        fields.append(f"  url = {{{_bib_escape(str(card['url']))}}}")
    return "@article{" + citekey + ",\n" + ",\n".join(fields) + "\n}"


def card_to_csl(card: dict[str, Any]) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": card.get("id"),
        "type": "article-journal",
        "title": card.get("title") or "",
        "author": [_author_csl(a) for a in (card.get("authors") or [])],
        "issued": {"date-parts": [[int(card.get("year") or 0)]]},
    }
    if card.get("doi"):
        item["DOI"] = card["doi"]
    if card.get("url"):
        item["URL"] = card["url"]
    return item


def cards_by_id(cards: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(c.get("id")): c for c in cards if isinstance(c, dict) and c.get("id")}


def export_checked(cards: list[dict[str, Any]], checked_ids: list[str]) -> dict[str, Any]:
    known = cards_by_id(cards)
    used: set[str] = set()
    bib_parts: list[str] = []
    csl: list[dict[str, Any]] = []
    for cid in checked_ids or []:
        card = known.get(str(cid))
        if not card:
            continue
        citekey = _citekey(card, used)
        bib_parts.append(card_to_bibtex(card, citekey))
        csl.append(card_to_csl(card))
    return {
        "refs_bib": "\n\n".join(bib_parts),
        "csl_json": csl,
    }
