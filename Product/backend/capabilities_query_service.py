"""Capabilities query service — Task 43 BDD (DesignPanel 抽屉).

Backs `GET /api/capabilities/methods?category=&q=` and the in-browser
``MethodsDrawer`` component. The drawer is fed once on first open, then
filtering happens client-side, so this service is intentionally a thin
read-side adapter over ``index_statspai_capabilities()`` (which itself
delegates to the live StatsPAI install).

Why a separate service (not just `capability_registry`)?
  - ``capability_registry`` is project-scoped and writes JSON to
    ``state/product/capabilities.json``. The drawer is a global
    library browser, not a per-project artifact.
  - We want zero coupling to project state — opening the drawer must
    work even when no project is selected.

The Drawer is "B2 (right-side) / not-blocking" (BDD 行为 4): the service
is sync + cached, so the API returns fast and the user can keep
interacting with DesignPanel while it's open.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Any

from Product.backend.statspai_adapter import index_statspai_capabilities


@lru_cache(maxsize=1)
def _all_caps() -> tuple[dict[str, Any], ...]:
    """Cache the full StatsPAI capabilities list (1018 functions).

    Computing the index calls into the live StatsPAI install on first hit.
    Subsequent calls (the drawer re-opens, filters reset, etc.) are O(1).
    """
    return tuple(index_statspai_capabilities())


def _category_counts(caps: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    """Return [{name, count}] sorted by count desc, then name asc for stability."""
    counts = Counter(c.get("category", "unknown") for c in caps)
    return [
        {"name": name, "count": count}
        for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


def get_methods_overview(category: str | None = None) -> dict[str, Any]:
    """Return the full drawer payload (categories + methods).

    Pass ``category`` to pre-filter the returned methods list. The
    client still gets every category so the chip bar stays complete.
    """
    caps = _all_caps()
    categories = _category_counts(caps)
    methods: list[dict[str, Any]] = []
    for cap in caps:
        if category and cap.get("category") != category:
            continue
        methods.append({
            "id": cap.get("id", ""),
            "name": cap.get("name", ""),
            "category": cap.get("category", "unknown"),
            "description": cap.get("description", ""),
            "risk_level": cap.get("risk_level", "low"),
        })
    return {
        "total": len(caps),
        "categories": categories,
        "methods": methods,
    }


def search_methods(query: str, category: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    """Substring match (case-insensitive) over name + description.

    Used by the drawer's search input. ``limit`` exists to keep the wire
    payload sane — the front-end chips can re-filter the 1018-item set
    in memory after the first fetch.
    """
    q = (query or "").strip().lower()
    caps = _all_caps()
    out: list[dict[str, Any]] = []
    for cap in caps:
        if category and cap.get("category") != category:
            continue
        if q:
            haystack = f"{cap.get('name', '')} {cap.get('description', '')}".lower()
            if q not in haystack:
                continue
        out.append({
            "id": cap.get("id", ""),
            "name": cap.get("name", ""),
            "category": cap.get("category", "unknown"),
            "description": cap.get("description", ""),
            "risk_level": cap.get("risk_level", "low"),
        })
        if len(out) >= limit:
            break
    return out
