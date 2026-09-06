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
    if chapter_type == "results" and research_claims_exist(state):
        claim = current_research_claim(state)
        if not claim or not claim.get("approved_by_user"):
            missing.append("claim_unapproved")
    return (not missing, missing)


def research_claims_exist(state: dict) -> bool:
    lab = state.get("research_lab")
    if not isinstance(lab, dict):
        return False
    claims = lab.get("claims") or []
    return any(isinstance(item, dict) and item.get("id") for item in claims)


def current_research_claim(state: dict) -> dict | None:
    lab = state.get("research_lab")
    if not isinstance(lab, dict):
        return None
    claims = [item for item in (lab.get("claims") or []) if isinstance(item, dict)]
    cid = lab.get("current_claim_id")
    if cid:
        for item in claims:
            if item.get("id") == cid:
                return item
    existing = lab.get("claim")
    if isinstance(existing, dict) and existing.get("id"):
        return existing
    return claims[-1] if claims else None


def results_is_grounded(state: dict, chapter: dict | None = None) -> bool:
    chapter = chapter if isinstance(chapter, dict) else {}
    if chapter.get("stale") or chapter.get("needs_regeneration"):
        return False
    content = str(chapter.get("content") or "")
    claim = current_research_claim(state)
    if research_claims_exist(state):
        if not claim or not claim.get("approved_by_user"):
            return False
        forbidden = str(claim.get("unsupported_wording") or "").strip()
        if forbidden and forbidden in content:
            return False
        return True
    est = state.get("estimate") or {}
    return isinstance(est, dict) and est.get("status") in ("ok", "degraded")


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
