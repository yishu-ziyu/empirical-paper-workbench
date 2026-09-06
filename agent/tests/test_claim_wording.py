from agent.engine.claim_wording import wording_exceeds_evidence
from agent.engine.readiness import results_is_grounded
from agent.nodes.review_sources.grounding import check_grounding
from conftest import make_write_ready_state


CLAIM = {
    "id": "claim.card.education-earnings",
    "approved_by_user": True,
    "stale": False,
    "based_on_evidence_revision": 1,
    "unsupported_wording": "One more year of education raises everyone's wage by 13%.",
}


def _state(content_claim=None, **lab_extra):
    lab = {
        "evidence_revision": 1,
        "canonical_spec_id": "iv_region_dummies",
        "claims": [CLAIM],
        "current_claim_id": CLAIM["id"],
        "claim": CLAIM,
        **lab_extra,
    }
    return make_write_ready_state(research_lab=lab)


def test_paraphrased_unconditional_causal_exceeds_policy():
    assert wording_exceeds_evidence(CLAIM, "Education causes wages to rise by about 13%.")
    assert wording_exceeds_evidence(
        CLAIM, "An additional year of schooling raises wages by 13%."
    )
    assert wording_exceeds_evidence(CLAIM, "多读一年书导致工资提高13%。")


def test_caveated_iv_wording_is_allowed():
    text = (
        "Under the college-proximity IV assumptions, IV estimates suggest "
        "a positive local causal return to schooling."
    )
    assert wording_exceeds_evidence(CLAIM, text) is False


def test_grounding_and_results_gate_share_policy():
    state = _state()
    row = state["estimate"]["treatment_row"]
    table = "# 主结果\n\n| 变量 | 系数 | SE | p |\n|------|------|----|---|\n" + row + "\n"
    bad = table + "Education causes wages to rise by about 13%."
    assert "wording_exceeds_evidence" in check_grounding(state, bad)
    assert results_is_grounded(state, {"content": bad, "type": "results"}) is False
    good = (
        table
        + "Under the college-proximity IV assumptions, IV estimates suggest "
        "a positive local causal return to schooling."
    )
    assert "wording_exceeds_evidence" not in check_grounding(state, good)
    assert results_is_grounded(state, {"content": good, "type": "results"}) is True
