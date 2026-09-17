"""Per-chapter write gate and claim mode.

A chapter exists only when its existence conditions are already on state.
Client-supplied TRUTH_KEYS must not satisfy this gate.
"""
from __future__ import annotations

from typing import Any

from .identification_state import (
    PERMISSION_FORBID,
    identification_decision,
    identification_hard_block,
    permission_is,
)

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
    # 阻断口径来自 identification_state：与图的条件边、串行预写路径、HTTP Facade 同一函数。
    # 阻挡码沿用 "star_0"，它已经流到 write_blockers 与前端 InstrumentReadout。
    if identification_hard_block(state):
        return False, ["star_0"]
    from .did_spec import DID_MISSING_INTERACTION, did_spec_block_reason

    if did_spec_block_reason(state) and chapter_type == "results":
        missing.append(DID_MISSING_INTERACTION)
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
        elif _claim_is_stale(state, claim):
            missing.append("claim_stale")
        elif _canonical_mismatches_claim(state, claim):
            missing.append("canonical_mismatch")
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


def _lab(state: dict) -> dict | None:
    lab = state.get("research_lab")
    return lab if isinstance(lab, dict) else None


def claim_revision_is_stale(lab: dict | None, claim: dict | None) -> bool:
    """Fail closed when the lab has an evidence_revision (including 0)."""
    if not isinstance(claim, dict):
        return False
    if claim.get("stale"):
        return True
    if not isinstance(lab, dict):
        return False
    current = lab.get("evidence_revision")
    if current is None:
        return False
    based = claim.get("based_on_evidence_revision")
    if based is None:
        return True
    try:
        return int(based) != int(current)
    except (TypeError, ValueError):
        return True


def _claim_is_stale(state: dict, claim: dict | None) -> bool:
    return claim_revision_is_stale(_lab(state), claim)


def _canonical_mismatches_claim(state: dict, claim: dict | None) -> bool:
    if not isinstance(claim, dict):
        return False
    lab = _lab(state)
    if lab is None:
        return False
    required = (claim.get("provenance") or {}).get("iv_spec_id")
    if not required:
        return False
    return lab.get("canonical_spec_id") != required


def results_is_grounded(state: dict, chapter: dict | None = None) -> bool:
    from .claim_wording import wording_exceeds_evidence

    chapter = chapter if isinstance(chapter, dict) else {}
    if chapter.get("stale") or chapter.get("needs_regeneration"):
        return False
    content = str(chapter.get("content") or "")
    claim = current_research_claim(state)
    if research_claims_exist(state):
        if not claim or not claim.get("approved_by_user"):
            return False
        if _claim_is_stale(state, claim):
            return False
        if _canonical_mismatches_claim(state, claim):
            return False
        if wording_exceeds_evidence(claim, content):
            return False
        return True
    est = state.get("estimate") or {}
    return isinstance(est, dict) and est.get("status") in ("ok", "degraded")


def estimate_ran(state: dict) -> bool:
    from .did_spec import did_spec_block_reason

    if did_spec_block_reason(state):
        return False
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
    """机器给出的主张档位：blocked / causal_with_caveat / association。

    因果档不再直接读星级，而读 ``identification_state`` 的 ``causal_language``
    许可：``confirm``（1–2 星，可写因果但必须披露留痕）与 ``allow`` 都给
    ``causal_with_caveat``；``forbid``（0 星与未知）落到 association。
    """
    rd = state.get("research_direction") or {}
    method = str(rd.get("method") or "").strip().lower()
    decision = identification_decision(state)
    if decision["hard_block"]:
        return "blocked"
    if method in {"did", "iv", "rd", "rdd", "scm"} and not permission_is(
        decision["permissions"]["causal_language"], PERMISSION_FORBID
    ):
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
