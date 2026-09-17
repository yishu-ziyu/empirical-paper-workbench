"""FL-BE-reuse: thin wrap of fetch_papers into existing find_lit.

OpenAlex + Crossref + S2, DOI dedupe. HTTP stays in literature_sources.
Cards, checkbox, bib export, and the chapter write gate stay in find_lit.
Confirmed-design is enforced by search_find_lit, not here.

V1 sources are the FL three only. PubMed / Europe PMC / arXiv, outdir dumps,
PDF harvest, mock/synthetic "found" hits, and a standalone fetch-papers
product path are out. DATA-RIGOR: mock/synthetic never count as found.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

from .dedupe import dedupe_hits, normalize_doi

Searcher = Callable[[str], list[dict[str, Any]]]

SOURCE_OPENALEX = "openalex"
SOURCE_CROSSREF = "crossref"
SOURCE_S2 = "semantic_scholar"
V1_SOURCES = (SOURCE_OPENALEX, SOURCE_CROSSREF, SOURCE_S2)

# Same three sources, two jobs. `purpose` selects *how the caller planned the
# query* (and what evidence artifact it builds), not an after-the-fact label:
# fetch_papers never reorders or rewrites hits by purpose.
PURPOSE_METHOD_CHECK = "method_check"
PURPOSE_TOPIC_POSITIONING = "topic_positioning"
VALID_PURPOSES = (PURPOSE_METHOD_CHECK, PURPOSE_TOPIC_POSITIONING)
DEFAULT_PURPOSE = PURPOSE_TOPIC_POSITIONING

# Analog of DATA-RIGOR "no synthetic as found": these are not FL hits.
_NOT_FOUND_SOURCES = frozenset(
    {"mock", "synthetic", "mock_degraded", "mock_corpus", "gold"}
)


def _source_names(hit: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for src in (hit.get("sources"), [hit.get("source")]):
        for item in src or []:
            token = str(item).strip().lower()
            if token and token not in names:
                names.append(token)
    return names


def is_found_hit(hit: dict[str, Any]) -> bool:
    if not isinstance(hit, dict):
        return False
    return not any(name in _NOT_FOUND_SOURCES for name in _source_names(hit))


def _prepare_hit(hit: Any) -> dict[str, Any] | None:
    if not isinstance(hit, dict) or not is_found_hit(hit):
        return None
    out = dict(hit)
    doi = normalize_doi(out.get("doi"))
    out["doi"] = doi or None
    return out


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
            hits.extend(
                item for item in (_prepare_hit(h) for h in batch) if item
            )
        except Exception as exc:
            status[name] = f"degraded:{type(exc).__name__}"
    return hits, status


def empty_fetch(*, query: str = "", purpose: str = DEFAULT_PURPOSE) -> dict[str, Any]:
    return {
        "hits": [],
        "source_status": {},
        "query": query,
        "purpose": purpose,
        "chapter_written": False,
    }


def fetch_papers(
    query: str,
    *,
    purpose: str = DEFAULT_PURPOSE,
    searchers: Iterable[tuple[str, Searcher]] | None = None,
) -> dict[str, Any]:
    """Three-source search + DOI dedupe. No cards, no chapter, no literature_entries.

    `purpose` is method_check | topic_positioning. It records *why* the caller
    planned this query (method-applicability vs who-did-similar-work); it does
    not reorder or rewrite hits, so topic positioning keeps its old behaviour.
    """
    resolved = str(purpose or DEFAULT_PURPOSE).strip() or DEFAULT_PURPOSE
    if resolved not in VALID_PURPOSES:
        resolved = DEFAULT_PURPOSE
    q = str(query or "").strip()
    if not q:
        return empty_fetch(purpose=resolved)
    raw, source_status = _run_searchers(q, searchers or default_searchers())
    return {
        "hits": dedupe_hits(raw),
        "source_status": source_status,
        "query": q,
        "purpose": resolved,
        "chapter_written": False,
    }
