"""Crossref works search + DOI resolve.

Extracted from empirical-paper-workbench `runtime/literature_search.py`
and `runtime/literature_pack.py`. Stdlib only. Failures raise RuntimeError
so `search_literature` can degrade to mock.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, List

from ...protocols import LiteratureEntry

CROSSREF = "https://api.crossref.org/works"
UA = "econpaper/1.0 (literature-search; mailto:dev@local)"
HTTP_TIMEOUT_SECONDS = 10
MAX_RESULTS = 20


def _http_get_json(url: str, timeout: float = HTTP_TIMEOUT_SECONDS) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _authors_list(authors: list[dict[str, Any]] | None) -> List[str]:
    if not authors:
        return []
    parts: List[str] = []
    for a in authors[:8]:
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        if family and given:
            parts.append(f"{family}, {given}")
        elif family:
            parts.append(family)
        elif given:
            parts.append(given)
    return parts


def _year_from_message(msg: dict[str, Any]) -> int:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                continue
    return 0


def resolve_doi(doi: str) -> dict[str, Any]:
    """Resolve a single DOI. Raises RuntimeError on network / parse failure."""
    url = f"{CROSSREF}/{urllib.parse.quote(doi.strip())}"
    try:
        data = _http_get_json(url)
        return data["message"]
    except Exception as exc:
        raise RuntimeError(f"Crossref DOI resolve failed: {exc}") from exc


def crossref_search(
    query: str,
    *,
    max_results: int = MAX_RESULTS,
) -> List[LiteratureEntry]:
    """Query Crossref works search. Keep journal articles that have a DOI."""
    if not query or not query.strip():
        return []
    params = urllib.parse.urlencode(
        {
            "query": query,
            "rows": str(min(max_results, MAX_RESULTS)),
            "filter": "type:journal-article,from-pub-date:1980",
        }
    )
    url = f"{CROSSREF}?{params}"
    try:
        data = _http_get_json(url)
    except Exception as exc:
        raise RuntimeError(f"Crossref search failed: {exc}") from exc

    items = ((data or {}).get("message") or {}).get("items") or []
    entries: List[LiteratureEntry] = []
    n = max(len(items), 1)
    for i, msg in enumerate(items):
        doi = str(msg.get("DOI") or "").strip()
        title_list = msg.get("title") or [""]
        title = title_list[0] if title_list else ""
        if not doi or not title:
            continue
        venue = (msg.get("container-title") or [""])[0]
        if not venue or "ssrn" in venue.lower() or doi.lower().startswith("10.2139/"):
            continue
        abstract = str(msg.get("abstract") or venue or "")
        # Strip trivial JATS tags if Crossref returned markup.
        abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "").strip()
        score = max(0.3, 1.0 - i / n * 0.7)
        entries.append(
            {
                "title": title,
                "authors": _authors_list(msg.get("author")),
                "year": _year_from_message(msg),
                "abstract": abstract,
                "doi": doi,
                "source": "crossref",
                "relevance_score": score,
            }
        )
    return entries
