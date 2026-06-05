"""/api/capabilities router — Task 43 BDD.

Backs the DesignPanel "查看全部方法" drawer. Read-only; no project context
required.
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from Product.backend.capabilities_query_service import get_methods_overview, search_methods

router = APIRouter()


@router.get("/api/capabilities/methods")
def get_capabilities_methods(
    category: str | None = Query(default=None, description="Filter by category name (e.g. 'causal')"),
    q: str | None = Query(default=None, description="Substring search over name + description"),
    limit: int = Query(default=200, ge=1, le=2000),
) -> dict:
    """Drawer payload: categories (always full) + methods (filtered).

    Front-end Strategy: call once with no params to get everything (1018
    methods) plus all 49 categories, then filter in memory. The ``q`` /
    ``category`` params are still exposed so the e2e tests can hit a
    single endpoint to verify the server-side filter as well.
    """
    if q:
        return {
            "total_filtered": -1,  # filled below
            "methods": search_methods(q, category=category, limit=limit),
            "categories": get_methods_overview()["categories"],
        }
    overview = get_methods_overview(category=category)
    if category:
        overview["total_filtered"] = len(overview["methods"])
    return overview
