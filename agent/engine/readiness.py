"""Per-chapter write gate and claim mode.

A chapter exists only when its existence conditions are already on state.
Client-supplied TRUTH_KEYS must not satisfy this gate.
"""
from __future__ import annotations

from typing import Any

SLOT_REQUIREMENTS = {
    "intro": ("identification",),
    "data_desc": ("identification",),
    "methods": ("identification",),
    "conclusion": ("identification",),
    "results": ("identification", "estimate", "robustness"),
    "lit_review": ("identification", "literature"),
}

TRUTH_KEYS = frozenset(
    {
        "results",
        "estimate",
        "robustness_results",
        "identification_diag",
        "star_rating",
        "literature_entries",
        "literature_source",
        "citation_indices",
        "literature_produced_by",
        "literature_query",
        "citation_graph",
        "main_specification",
        "write_blocked",
        "produced_by",
        "treatment_row",
        "claim",
    }
)


def paper_ready_to_write(state: dict, chapter_type: str) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if state.get("star_rating") == 0:
        return False, ["star_0"]
    need = SLOT_REQUIREMENTS.get(chapter_type, ("identification",))
    if "identification" in need and not state.get("identification_diag"):
        missing.append("no_identification")
    if "estimate" in need and not estimate_ran(state):
        missing.append("no_results")
    if "robustness" in need and not robustness_ran(state):
        missing.append("no_robustness")
    if "literature" in need and not literature_ran(state):
        missing.append("no_literature")
    return (not missing, missing)


def estimate_ran(state: dict) -> bool:
    est = state.get("estimate") or {}
    return (
        isinstance(est, dict)
        and est.get("produced_by") == "estimate"
        and est.get("status") in ("ok", "error", "degraded")
        and bool((state.get("results") or "").strip())
        and bool(est.get("treatment_row"))
    )


def robustness_ran(state: dict) -> bool:
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, dict):
        return False
    if rob.get("produced_by") == "robustness_check":
        return True
    return "diagnostics" in rob


def literature_ran(state: dict) -> bool:
    if state.get("literature_produced_by") == "search_literature":
        return True
    src = state.get("literature_source")
    if src in {"mock_degraded", "disabled"}:
        return True
    return src in {"mock", "crossref", "semantic_scholar"} and isinstance(
        state.get("literature_query"), str
    )


def machine_claim(state: dict) -> str:
    rd = state.get("research_direction") or {}
    method = str(rd.get("method") or "").strip().lower()
    star = state.get("star_rating")
    if star == 0:
        return "blocked"
    if method in {"did", "iv", "rd", "rdd", "scm"} and isinstance(star, int) and star >= 1:
        return "causal_with_caveat"
    return "association"


def claim_mode(state: dict) -> str:
    machine = machine_claim(state)
    user = str((state.get("research_direction") or {}).get("claim") or "").strip().lower()
    if machine == "blocked":
        return "blocked"
    if user in {"association", "assoc", "correlation"}:
        return "association"
    return machine


def resolve_slot(state: dict) -> tuple[int, dict]:
    outline = state.get("outline") or []
    requested = state.get("current_chapter") or {}
    want = requested.get("type") if isinstance(requested, dict) else None
    if want:
        for i, spec in enumerate(outline):
            if isinstance(spec, dict) and spec.get("type") == want:
                return i, spec
        raise ValueError(f"chapter.type {want!r} not in outline")
    idx = state.get("current_chapter_index")
    if idx is None or not outline or not isinstance(idx, int) or idx >= len(outline):
        return -1, {}
    spec = outline[idx]
    return idx, dict(spec) if isinstance(spec, dict) else {}
