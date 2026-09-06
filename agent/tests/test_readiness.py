"""Per-chapter write gate and claim mode."""
from agent.engine.readiness import (
    TRUTH_KEYS,
    claim_mode,
    estimate_ran,
    literature_ran,
    paper_ready_to_write,
    resolve_slot,
    results_is_grounded,
    robustness_ran,
)

from conftest import make_state, make_write_ready_state


def test_intro_needs_identification():
    ok, blockers = paper_ready_to_write(make_state(), "intro")
    assert ok is False
    assert "no_identification" in blockers


def test_intro_ready_with_identification_only():
    ok, blockers = paper_ready_to_write(
        make_state(identification_diag={"report": "ok"}),
        "intro",
    )
    assert ok is True
    assert blockers == []


def test_results_need_estimate_stamp():
    state = make_state(
        identification_diag={"report": "ok"},
        results="FAKE",
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is False
    assert "no_results" in blockers
    assert estimate_ran(state) is False


def test_results_ready_when_write_ready():
    ok, blockers = paper_ready_to_write(make_write_ready_state(), "results")
    assert ok is True
    assert blockers == []


def test_results_blocked_when_claims_exist_unapproved():
    state = make_write_ready_state(
        research_lab={
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": False,
                    "supported_wording": "Education is positively associated with earnings.",
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is False
    assert "claim_unapproved" in blockers
    intro_ok, intro_blockers = paper_ready_to_write(state, "intro")
    assert intro_ok is True
    assert intro_blockers == []


def test_results_blocked_when_claim_stale():
    state = make_write_ready_state(
        research_lab={
            "evidence_revision": 2,
            "canonical_spec_id": "iv_region_dummies",
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": True,
                    "stale": True,
                    "based_on_evidence_revision": 1,
                    "provenance": {"iv_spec_id": "iv_region_dummies"},
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is False
    assert "claim_stale" in blockers
    assert results_is_grounded(state, {"type": "results", "content": "ok"}) is False


def test_missing_based_on_is_stale_when_evidence_revision_is_zero():
    state = make_write_ready_state(
        research_lab={
            "evidence_revision": 0,
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": True,
                    "stale": False,
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is False
    assert "claim_stale" in blockers
    assert results_is_grounded(state, {"type": "results", "content": "ok"}) is False


def test_missing_based_on_revision_blocks_results_when_lab_has_revision():
    state = make_write_ready_state(
        research_lab={
            "evidence_revision": 3,
            "canonical_spec_id": "iv_region_dummies",
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": True,
                    "stale": False,
                    "provenance": {"iv_spec_id": "iv_region_dummies"},
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is False
    assert "claim_stale" in blockers
    assert results_is_grounded(state, {"type": "results", "content": "ok"}) is False


def test_results_ready_when_claim_approved():
    state = make_write_ready_state(
        research_lab={
            "claims": [
                {
                    "id": "claim.card.education-earnings",
                    "approved_by_user": True,
                    "unsupported_wording": (
                        "One more year of education raises everyone's wage by 13%."
                    ),
                }
            ],
            "current_claim_id": "claim.card.education-earnings",
        }
    )
    ok, blockers = paper_ready_to_write(state, "results")
    assert ok is True
    assert blockers == []


def test_lit_review_needs_literature_node():
    state = make_state(identification_diag={"report": "ok"})
    ok, blockers = paper_ready_to_write(state, "lit_review")
    assert ok is False
    assert "no_literature" in blockers
    assert literature_ran(state) is False


def test_star_zero_blocks_all_slots():
    state = make_write_ready_state(star_rating=0)
    ok, blockers = paper_ready_to_write(state, "intro")
    assert ok is False
    assert blockers == ["star_0"]


def test_claim_mode_only_downgrades():
    did = make_state(
        research_direction={"method": "did", "claim": "association"},
        star_rating=2,
    )
    assert claim_mode(did) == "association"
    ols = make_state(research_direction={"method": "ols"}, star_rating=None)
    assert claim_mode(ols) == "association"
    causal = make_state(research_direction={"method": "iv"}, star_rating=2)
    assert claim_mode(causal) == "causal_with_caveat"


def test_truth_keys_include_stamps():
    assert "results" in TRUTH_KEYS
    assert "estimate" in TRUTH_KEYS
    assert "literature_produced_by" in TRUTH_KEYS
    assert "treatment_row" in TRUTH_KEYS


def test_resolve_slot_prefers_current_chapter_type():
    state = make_write_ready_state(current_chapter={"type": "results"})
    idx, spec = resolve_slot(state)
    assert idx == 4
    assert spec["type"] == "results"


def test_robustness_placeholder_without_stamp_does_not_count():
    state = make_state(
        robustness_results={"summary_table": "No main specification available"}
    )
    assert robustness_ran(state) is False
    stamped = make_state(
        robustness_results={
            "produced_by": "robustness_check",
            "diagnostics": [],
        }
    )
    assert robustness_ran(stamped) is True
