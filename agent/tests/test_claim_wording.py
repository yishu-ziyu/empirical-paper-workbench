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


def test_chinese_period_splits_without_whitespace():
    text = (
        "在工具变量假设成立时，IV 估计表明存在局部因果回报。"
        "多读一年书导致所有人工资提高13%。"
    )
    assert wording_exceeds_evidence(CLAIM, text)
    split_only = (
        "在工具变量假设成立时，IV 估计表明存在局部因果回报。"
        "多读一年书导致工资提高13%。"
    )
    assert wording_exceeds_evidence(CLAIM, split_only)


def test_english_period_splits_without_whitespace():
    text = (
        "Under the college-proximity IV assumptions, IV estimates suggest "
        "a local return.Education causes wages to rise."
    )
    assert wording_exceeds_evidence(CLAIM, text)


def test_caveat_does_not_greenlight_population_wide_ate():
    text = (
        "Under the college-proximity IV assumptions, IV estimates suggest "
        "a local return, but education raises everyone's wage by 13%."
    )
    assert wording_exceeds_evidence(CLAIM, text)


def test_population_wide_wording_exceeds_even_with_iv_caveat():
    cases = [
        "Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises wages for everyone.",
        "Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises everyone's wage by 13%.",
        "Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises wages for all workers.",
        "Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises wages for all people.",
        "在工具变量假设成立时，IV 估计表明存在局部因果回报，多读一年书导致所有人工资提高13%。",
        "在工具变量假设成立时，IV 估计表明存在局部因果回报，多读一年书导致每个人工资提高13%。",
        "在工具变量假设成立时，IV 估计表明存在局部因果回报，教育使工资普遍提高。",
    ]
    for text in cases:
        assert wording_exceeds_evidence(CLAIM, text), text


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
