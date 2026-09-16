"""NORMS-BE: design_gates.yaml + chapter_gates.yaml hooked on propose/write."""
from __future__ import annotations

from pathlib import Path

import pytest

from agent.design.propose import propose_design
from agent.nodes.generate_chapter import generate_chapter
from agent.norms.loader import (
    CHAPTER_GATE_IDS,
    CHAPTER_GATES_FILE,
    DESIGN_GATE_IDS,
    DESIGN_GATES_FILE,
    GATES_MISSING,
    SKILL_RUNNER,
    assert_propose_gates,
    chapter_write_blockers,
    design_gate_blockers,
    load_gates,
)
from conftest import make_state, make_write_ready_state


@pytest.fixture
def chapter_llm(mock_llm_for):
    return mock_llm_for("generate_chapter", return_value="MOCK CHAPTER CONTENT")


def _did_term(design: dict) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("kind") == "did"
        and (
            item.get("term") == "treated:period"
            or {item.get("left"), item.get("right")} == {"treated", "period"}
        )
        for item in (design.get("interactions") or [])
    )


def _confirmed(**overrides) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "method": "ols",
        "qType": "average",
        "outcome": "y",
        "treatment": "x",
        "interactions": [],
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    design.update(overrides)
    return design


def _formal_state(**overrides) -> dict:
    state = make_write_ready_state(
        design=_confirmed(),
        dataAttached=True,
        table1Confirmed=True,
        specConfirmed=True,
        cleaning_report={"steps": [{"name": "clean_winsor", "status": "ok"}]},
    )
    state.update(overrides)
    return state


def test_yaml_files_exist_with_distilled_ids():
    design = load_gates(DESIGN_GATES_FILE)
    chapter = load_gates(CHAPTER_GATES_FILE)
    assert design["hook"] == "propose"
    assert chapter["hook"] == "write"
    assert {g["id"] for g in design["gates"]} == set(DESIGN_GATE_IDS)
    assert {g["id"] for g in chapter["gates"]} == set(CHAPTER_GATE_IDS)
    assert "ppt" in chapter["forbidden_export_formats"]
    assert "xhs" in chapter["forbidden_export_formats"]
    assert "tex" in chapter["allowed_export_formats"]


def test_missing_yaml_fails_closed_on_propose(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError, match=GATES_MISSING):
        assert_propose_gates(
            {"status": "draft", "confirmed": False, "method": "ols"},
            gates_dir=empty,
        )


def test_missing_yaml_fails_closed_on_write(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert chapter_write_blockers(make_state(), "intro", gates_dir=empty) == [
        GATES_MISSING
    ]


def test_propose_hook_runs_yaml_and_keeps_draft():
    design = propose_design("最低工资对就业的影响")
    assert design["status"] == "draft"
    assert design["confirmed"] is False
    assert design["method"] == "did"
    assert _did_term(design)
    assert design_gate_blockers(design) == []


def test_propose_skips_yaml_is_fail_closed(monkeypatch):
    called = {"n": 0}

    def boom(design):
        called["n"] += 1
        raise ValueError(GATES_MISSING)

    monkeypatch.setattr("agent.design.propose.assert_propose_gates", boom)
    with pytest.raises(ValueError, match=GATES_MISSING):
        propose_design("教育对工资的影响")
    assert called["n"] == 1


def test_did_without_interaction_hard_blocks_propose():
    draft = propose_design("最低工资对就业的影响")
    draft["interactions"] = []
    with pytest.raises(ValueError, match="did_missing_interaction"):
        assert_propose_gates(draft)


def test_het_without_interaction_hard_blocks():
    draft = propose_design("教育对工资的影响")
    draft["qType"] = "heterogeneity"
    with pytest.raises(ValueError, match="het_missing_interaction"):
        assert_propose_gates(draft)
    draft["interactions"] = [
        {"kind": "het", "left": "educ", "right": "region", "term": "educ:region"}
    ]
    assert_propose_gates(draft)


def test_catalog_id_on_draft_is_not_locked_spec():
    draft = propose_design("ck1994_long")
    assert draft["method"] == "ols"
    draft["catalog_entry_id"] = "ck1994_long"
    with pytest.raises(ValueError, match="catalog_as_locked_spec"):
        assert_propose_gates(draft)


def test_confirmed_object_cannot_come_from_propose_hook():
    draft = propose_design("教育对工资的影响")
    draft["status"] = "confirmed"
    draft["confirmed"] = True
    with pytest.raises(ValueError, match="design_treated_as_locked"):
        assert_propose_gates(draft)


def test_skill_runner_is_not_the_gate_engine():
    assert SKILL_RUNNER is False
    import agent.norms as norms
    import agent.norms.loader as loader

    assert not hasattr(norms, "run_skill")
    assert not hasattr(loader, "run_skill")
    assert not hasattr(loader, "run_claude_skill")
    skills_dump = Path(__file__).resolve().parents[2] / ".agents" / "skills"
    assert not skills_dump.exists()
    draft = propose_design("教育对工资的影响")
    with pytest.raises(ValueError, match="skill_runner_not_allowed"):
        assert_propose_gates(draft, extra={"skill_runner": True})


def test_unconfirmed_write_does_not_treat_aer_as_passed_or_locked(chapter_llm):
    state = make_state(
        identification_diag={"report": "ok"},
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
    )
    assert chapter_write_blockers(state, "intro") == []
    result = generate_chapter(state)
    assert result.get("write_blocked") is not True
    assert "body_chapters" in result


def test_confirmed_write_without_prewrite_flags_is_blocked(chapter_llm):
    state = make_write_ready_state(
        design=_confirmed(),
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
    )
    blockers = chapter_write_blockers(state, "intro")
    assert "data_not_attached" in blockers
    assert "table1_not_confirmed" in blockers
    assert "spec_not_confirmed" in blockers
    assert "clean_winsor_not_recorded" in blockers
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert "table1_not_confirmed" in result["write_blockers"]
    assert "body_chapters" not in result


def test_confirmed_write_with_flags_passes_chapter_gates(chapter_llm):
    state = _formal_state()
    assert chapter_write_blockers(state, "intro") == []
    result = generate_chapter(
        {
            **state,
            "current_chapter_index": 0,
            "outline": [{"type": "intro", "title": "引言"}],
        }
    )
    assert result.get("write_blocked") is not True
    assert result["body_chapters"][0]["type"] == "intro"


def test_confirmed_did_without_interaction_blocks_write():
    state = _formal_state(
        design=_confirmed(method="did", qType="causal", interactions=[]),
        current_chapter_index=0,
        outline=[{"type": "results", "title": "结果"}],
    )
    blockers = chapter_write_blockers(state, "results")
    assert "did_missing_interaction" in blockers


def test_r_lit_bar_still_blocks_lit_review_write(chapter_llm):
    state = _formal_state(
        current_chapter_index=1,
        outline=[
            {"type": "intro", "title": "引言"},
            {"type": "lit_review", "title": "文献"},
        ],
    )
    blockers = chapter_write_blockers(state, "lit_review")
    assert "r_lit_bar_need_5_cards" in blockers
    result = generate_chapter(state)
    assert result.get("write_blocked") is True
    assert "r_lit_bar_need_5_cards" in result["write_blockers"]


def test_export_pptx_and_xhs_are_forbidden():
    state = _formal_state()
    assert chapter_write_blockers(
        state, "intro", extra={"export_format": "docx"}
    ) == []
    assert "export_format_not_allowed" in chapter_write_blockers(
        state, "intro", extra={"export_format": "pptx"}
    )
    assert "export_format_not_allowed" in chapter_write_blockers(
        state, "intro", extra={"export_format": "xhs"}
    )


def test_phack_is_not_an_aer_gate_pass():
    state = _formal_state()
    assert chapter_write_blockers(state, "intro") == []
    assert "phack_not_allowed" in chapter_write_blockers(
        state, "intro", extra={"phack": True}
    )


def test_generate_chapter_invokes_chapter_gates(monkeypatch, chapter_llm):
    seen = {"n": 0}

    def hook(state, chapter_type):
        seen["n"] += 1
        assert chapter_type == "intro"
        return ["table1_not_confirmed"]

    monkeypatch.setattr("agent.norms.loader.chapter_write_blockers", hook)
    state = make_write_ready_state(
        current_chapter_index=0,
        outline=[{"type": "intro", "title": "引言"}],
        identification_diag={"report": "ok"},
    )
    result = generate_chapter(state)
    assert seen["n"] == 1
    assert result.get("write_blocked") is True
    assert "table1_not_confirmed" in result["write_blockers"]


def test_unknown_gate_id_fails_closed(tmp_path):
    path = tmp_path / DESIGN_GATES_FILE
    path.write_text(
        "version: 1\nhook: propose\ngates:\n  - id: invented_skill\n    blocker: x\n",
        encoding="utf-8",
    )
    blockers = design_gate_blockers(
        {"status": "draft", "confirmed": False, "method": "ols"},
        gates_dir=tmp_path,
    )
    assert "unknown_gate:invented_skill" in blockers
