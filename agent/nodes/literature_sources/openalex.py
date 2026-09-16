"""OpenAlex works search. Stdlib only. Failures raise RuntimeError."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, List

from .polite_pool import user_agent
from ...protocols import LiteratureEntry

OPENALEX = "https://api.openalex.org/works"
HTTP_TIMEOUT_SECONDS = 10
MAX_RESULTS = 20


def _http_get_json(url: str, timeout: float = HTTP_TIMEOUT_SECONDS) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent(),
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _authors_list(authorships: list[dict[str, Any]] | None) -> List[str]:
    names: List[str] = []
    for item in authorships or []:
        author = item.get("author") if isinstance(item, dict) else None
        name = ""
        if isinstance(author, dict):
            name = str(author.get("display_name") or "").strip()
        if name:
            names.append(name)
        if len(names) >= 8:
            break
    return names


def _year(work: dict[str, Any]) -> int:
    try:
        return int(work.get("publication_year") or 0)
    except (TypeError, ValueError):
        return 0


def openalex_search(query: str, *, max_results: int = MAX_RESULTS) -> List[LiteratureEntry]:
    if not query or not query.strip():
        return []
    params = urllib.parse.urlencode(
        {
            "search": query.strip(),
            "per-page": str(min(max_results, MAX_RESULTS)),
        }
    )
    url = f"{OPENALEX}?{params}"
    try:
        data = _http_get_json(url)
    except Exception as exc:
        raise RuntimeError(f"OpenAlex search failed: {exc}") from exc

    results = (data or {}).get("results") or []
    entries: List[LiteratureEntry] = []
    n = max(len(results), 1)
    for i, work in enumerate(results):
        if not isinstance(work, dict):
            continue
        title = str(work.get("display_name") or work.get("title") or "").strip()
        if not title:
            continue
        doi = str(work.get("doi") or "").strip() or None
        landing = ""
        loc = work.get("primary_location") if isinstance(work.get("primary_location"), dict) else {}
        landing = str(loc.get("landing_page_url") or "").strip()
        oa_id = str(work.get("id") or "").strip()
        url_out = landing or oa_id
        score = max(0.3, 1.0 - i / n * 0.7)
        entries.append(
            {
                "title": title,
                "authors": _authors_list(work.get("authorships")),
                "year": _year(work),
                "abstract": str(work.get("abstract") or ""),
                "doi": doi,
                "url": url_out,
                "source": "openalex",
                "relevance_score": score,
            }
        )
    return entries
