"""Estimate-prep confirm flags and heterogeneity hard-block."""
from __future__ import annotations

from agent.engine.prewrite_gates import (
    BLOCK_CODE_HETERO_NO_INTERACTION,
    evaluate_blocking_decision,
    public_prewrite_gates,
    spec_has_interaction,
)


def test_interaction_detected_from_formula_and_spec_mode():
    assert spec_has_interaction(
        {"main_specification": {"formula": "ln_wage ~ educ + educ:region"}}
    )
    assert spec_has_interaction(
        {"main_specification": {"formula": "ln_wage ~ educ * region"}}
    )
    assert spec_has_interaction(
        {"specification_equation": "ln_wage = β₀ + β₁ educ + β₂ (educ×region) + ε"}
    )
    assert spec_has_interaction({}, {"specMode": "interaction"})
    assert not spec_has_interaction(
        {"main_specification": {"formula": "ln_wage ~ educ + region"}},
        {"specMode": "level"},
    )


def test_heterogeneity_without_interaction_is_block():
    decision = evaluate_blocking_decision(
        {
            "qType": "heterogeneity",
            "specMode": "level",
            "main_specification": {"formula": "ln_wage ~ educ + region"},
        }
    )
    assert decision["blocked"] is True
    assert decision["isBlock"] is True
    assert decision["code"] == BLOCK_CODE_HETERO_NO_INTERACTION
    assert "educ×region" in decision["reason"]


def test_heterogeneity_with_interaction_is_not_block():
    decision = evaluate_blocking_decision(
        {
            "research_direction": {"qType": "heterogeneity"},
            "main_specification": {"formula": "ln_wage ~ educ + educ×region"},
        }
    )
    assert decision["blocked"] is False
    assert decision["isBlock"] is False
    assert decision["hasInteraction"] is True


def test_average_qtype_never_hard_blocks():
    decision = evaluate_blocking_decision(
        {"qType": "average", "specMode": "level"}
    )
    assert decision["blocked"] is False


def test_public_gates_emit_camel_case_flags():
    payload = public_prewrite_gates(
        {"table1_confirmed": True, "q_type": "average"},
        {"specConfirmed": False},
    )
    assert payload["table1Confirmed"] is True
    assert payload["specConfirmed"] is False
    assert payload["qType"] == "average"
    assert payload["blockingDecision"]["isBlock"] is False
