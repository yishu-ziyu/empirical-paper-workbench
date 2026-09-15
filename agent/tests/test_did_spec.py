"""DID-BE-spec: allow_did forces treated×period; missing hard-blocks."""
from __future__ import annotations

import pandas as pd

from agent.engine.did_spec import (
    DID_MISSING_INTERACTION,
    can_form_did_main_term,
    did_spec_block_reason,
    force_did_main_term,
    has_did_main_term,
)
from agent.engine.readiness import estimate_ran, paper_ready_to_write
from agent.nodes.estimate import estimate
from agent.nodes.generate_chapter import generate_chapter
from agent.nodes.set_direction import set_direction


def test_has_did_main_term_accepts_interaction_and_dummy():
    assert has_did_main_term({"formula": "emp ~ treated:period"})
    assert has_did_main_term({"formula": "emp ~ treated * period"})
    assert has_did_main_term({"formula": "emp ~ treat × post"})
    assert has_did_main_term({"formula": "emp ~ treat#post"})
    assert has_did_main_term({"treatment": "treat_post"})
    assert has_did_main_term({"formula": "emp ~ did + wage"})
    assert has_did_main_term({"formula": "emp ~ nj_after"})
    assert has_did_main_term(columns=["treat_post"])


def test_has_did_main_term_rejects_substitutes():
    assert not has_did_main_term({"formula": "emp ~ treat", "method": "did"})
    assert not has_did_main_term({"formula": "emp ~ treat | id + year"})
    assert not has_did_main_term(
        {"formula": "emp ~ treat", "id_col": "id", "time_col": "year"}
    )
    assert not has_did_main_term({"formula": "emp ~ post"})
    assert not has_did_main_term({"first_treat_col": "g"})
    assert not has_did_main_term({"method": "did", "treatment": "treat"})


def test_force_builds_treat_times_post_and_drops_twfe():
    forced = force_did_main_term(
        {
            "outcome": "emp",
            "treatment": "treat",
            "formula": "emp ~ treat",
            "feols_formula": "emp ~ treat | id + year",
            "controls": ["wage"],
        },
        columns=["emp", "treat", "post", "id", "year"],
    )
    assert forced is not None
    assert forced["formula"] == "emp ~ treat * post + wage"
    assert forced["treatment"] == "treat:post"
    assert "feols_formula" not in forced


def test_force_uses_treat_post_dummy():
    forced = force_did_main_term(
        {"outcome": "emp", "treatment": "treat", "formula": "emp ~ treat"},
        columns=["treat_post", "emp"],
    )
    assert forced is not None
    assert forced["formula"] == "emp ~ treat_post"
    assert forced["treatment"] == "treat_post"


def test_force_none_without_period_or_dummy():
    assert (
        force_did_main_term(
            {"outcome": "emp", "treatment": "treat", "formula": "emp ~ treat"},
            columns=["emp", "treat", "id", "year"],
        )
        is None
    )


def test_set_direction_forces_interaction_when_allow_did(tmp_path):
    csv_path = tmp_path / "ck.csv"
    pd.DataFrame(
        {
            "emp": [1.0, 1.2, 2.0, 2.4],
            "treat": [0, 0, 1, 1],
            "post": [0, 1, 0, 1],
        }
    ).to_csv(csv_path, index=False)
    out = set_direction(
        {
            "allow_did": True,
            "csv_path": str(csv_path),
            "research_direction": {
                "question": "Minimum wage and employment",
                "dv": "emp",
                "iv": "treat",
                "method": "did",
            },
        }
    )
    spec = out["main_specification"]
    assert "treat * post" in spec["formula"]
    assert "|" not in spec["formula"]
    assert "feols_formula" not in spec


def test_set_direction_without_allow_did_keeps_twfe_formula():
    out = set_direction(
        {
            "research_direction": {
                "question": "q",
                "dv": "y",
                "iv": "treat",
                "method": "did",
                "time_col": "year",
                "id_col": "pid",
            }
        }
    )
    assert out["main_specification"]["feols_formula"] == "y ~ treat | pid + year"


def test_estimate_allow_did_missing_term_hard_blocks(tmp_path):
    csv_path = tmp_path / "treat_only.csv"
    pd.DataFrame(
        {"emp": [1.0, 2.0, 3.0, 4.0], "treat": [0, 1, 0, 1]}
    ).to_csv(csv_path, index=False)
    out = estimate(
        {
            "allow_did": True,
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "emp ~ treat",
                "treatment": "treat",
                "outcome": "emp",
                "method": "did",
            },
        }
    )
    payload = out["estimate"]
    assert payload["status"] == "error"
    assert payload["error"] == DID_MISSING_INTERACTION
    assert payload["produced_by"] == "estimate"
    assert not payload.get("treatment_row")
    assert payload.get("coef") is None


def test_estimate_allow_did_with_interaction_runs_2x2(tmp_path):
    csv_path = tmp_path / "ck.csv"
    pd.DataFrame(
        {
            "emp": [1.0, 1.1, 2.0, 2.6, 1.2, 1.0, 2.1, 2.8],
            "treat": [0, 0, 1, 1, 0, 0, 1, 1],
            "post": [0, 1, 0, 1, 0, 1, 0, 1],
        }
    ).to_csv(csv_path, index=False)
    out = estimate(
        {
            "allow_did": True,
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "emp ~ treat * post",
                "treatment": "treat:post",
                "outcome": "emp",
                "method": "did",
            },
        }
    )
    payload = out["estimate"]
    assert payload["status"] == "ok"
    assert payload["produced_by"] == "estimate"
    assert payload["treatment_row"]
    assert "treat * post" in (payload.get("formula") or "")
    assert "|" not in (payload.get("formula") or "")
    assert payload["estimator"] == "OLS"
    assert payload["coef"] is not None


def test_estimate_allow_did_false_does_not_block_plain_ols(tmp_path):
    csv_path = tmp_path / "ols.csv"
    pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "x": [0, 1, 0, 1]}).to_csv(
        csv_path, index=False
    )
    out = estimate(
        {
            "allow_did": False,
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "y ~ x",
                "treatment": "x",
                "outcome": "y",
                "method": "ols",
            },
        }
    )
    assert out["estimate"]["status"] == "ok"
    assert out["estimate"]["treatment_row"]


def test_planted_estimate_does_not_count_as_ran_when_term_missing():
    state = {
        "allow_did": True,
        "main_specification": {"formula": "emp ~ treat", "treatment": "treat"},
        "estimate": {
            "produced_by": "estimate",
            "status": "ok",
            "treatment_row": "| treat | 0.1 | 0.1 | 0.1 |",
            "formula": "emp ~ treat",
        },
        "results": "# 主结果\n| treat | 0.1 | 0.1 | 0.1 |",
    }
    assert estimate_ran(state) is False
    assert did_spec_block_reason(state) == DID_MISSING_INTERACTION
    ready, blockers = paper_ready_to_write(state, "results")
    assert ready is False
    assert DID_MISSING_INTERACTION in blockers


def test_results_chapter_blocked_when_allow_did_missing_term():
    state = {
        "allow_did": True,
        "current_chapter_index": 0,
        "outline": [{"type": "results", "title": "结果"}],
        "identification_diag": {"report": "ok"},
        "main_specification": {"formula": "emp ~ treat", "treatment": "treat"},
        "estimate": {
            "produced_by": "estimate",
            "status": "ok",
            "treatment_row": "| treat | 0.1 | 0.1 | 0.1 |",
        },
        "results": "FAKE",
        "robustness_results": {"produced_by": "robustness_check"},
    }
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert DID_MISSING_INTERACTION in result.get("write_blockers", [])
    assert "body_chapters" not in result


def test_can_form_from_controls_without_csv():
    assert can_form_did_main_term(
        {"allow_did": True},
        {"dv": "emp", "iv": "treat", "controls": ["post"]},
    )
    assert not can_form_did_main_term(
        {"allow_did": True},
        {"dv": "emp", "iv": "treat", "method": "did"},
    )
