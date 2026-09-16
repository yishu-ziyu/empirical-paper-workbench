"""DOI-first merge of OpenAlex + Crossref + S2 hits."""
from __future__ import annotations

import re
from typing import Any

_DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)


def normalize_doi(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    lowered = raw.lower()
    for prefix in _DOI_PREFIXES:
        if lowered.startswith(prefix):
            raw = raw[len(prefix) :]
            lowered = raw.lower()
            break
    return lowered.strip().strip("/")


def _norm_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def fallback_key(title: Any, year: Any, authors: Any) -> str:
    first = ""
    if isinstance(authors, list) and authors:
        first = _norm_text(authors[0])
    elif authors:
        first = _norm_text(authors)
    try:
        year_n = int(year or 0)
    except (TypeError, ValueError):
        year_n = 0
    return f"{_norm_text(title)}|{year_n}|{first}"


def work_key(hit: dict[str, Any]) -> str:
    doi = normalize_doi(hit.get("doi"))
    if doi:
        return f"doi:{doi}"
    return f"key:{fallback_key(hit.get('title'), hit.get('year'), hit.get('authors'))}"


def _year(hit: dict[str, Any]) -> int:
    try:
        return int(hit.get("year") or 0)
    except (TypeError, ValueError):
        return 0


def fullness(hit: dict[str, Any]) -> tuple[int, int, int, int]:
    authors = hit.get("authors") if isinstance(hit.get("authors"), list) else []
    title = str(hit.get("title") or "")
    return (
        1 if normalize_doi(hit.get("doi")) else 0,
        1 if _year(hit) else 0,
        len(authors),
        len(title),
    )


def _merge_pair(kept: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    if fullness(other) > fullness(kept):
        kept, other = dict(other), kept
    else:
        kept = dict(kept)
    if not normalize_doi(kept.get("doi")) and normalize_doi(other.get("doi")):
        kept["doi"] = other.get("doi")
    if not str(kept.get("title") or "").strip() and other.get("title"):
        kept["title"] = other.get("title")
    if not (kept.get("authors") or []) and other.get("authors"):
        kept["authors"] = other.get("authors")
    if not _year(kept) and _year(other):
        kept["year"] = other.get("year")
    if not str(kept.get("url") or "").strip() and other.get("url"):
        kept["url"] = other.get("url")
    sources: list[str] = []
    for src in (kept.get("sources"), other.get("sources"), [kept.get("source")], [other.get("source")]):
        for item in src or []:
            if item and item not in sources:
                sources.append(str(item))
    kept["sources"] = sources
    if sources:
        kept["source"] = sources[0]
    return kept


def dedupe_hits(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Same DOI → one hit. No DOI → title+year+first author. Keep fullest record."""
    order: list[str] = []
    by_key: dict[str, dict[str, Any]] = {}
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        key = work_key(hit)
        if not key or key in {"doi:", "key:|0|"}:
            continue
        if key not in by_key:
            by_key[key] = dict(hit)
            sources = list(hit.get("sources") or [])
            src = hit.get("source")
            if src and src not in sources:
                sources.append(str(src))
            by_key[key]["sources"] = sources
            by_key[key]["id"] = key
            order.append(key)
        else:
            by_key[key] = _merge_pair(by_key[key], hit)
            by_key[key]["id"] = key
    return [by_key[key] for key in order]
