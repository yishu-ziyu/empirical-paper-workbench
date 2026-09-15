"""INF-BE-propose: title/question → session.design draft (DECIDE-6 §8 bullets 1–3)."""
from __future__ import annotations

from agent.design.propose import propose_design
from agent.design import propose as propose_mod


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


def test_ck_title_proposes_did_with_treated_period():
    design = propose_design("最低工资对就业的影响")
    assert design["method"] == "did"
    assert design["status"] == "draft"
    assert design["confirmed"] is False
    assert design["confirmed_at"] is None
    assert design["catalog_entry_id"] is None
    assert design["source"]["title"] == "最低工资对就业的影响"
    assert design["source"]["question"] == ""
    assert design["outcome"] == "employment"
    assert design["treatment"] == "min_wage"
    assert design["treated"] == "treated"
    assert design["period"] == "post"
    assert _did_term(design)
    assert "allow_did" not in design
    assert "dataAttached" not in design


def test_ck_english_title_proposes_did_before_any_fixture():
    design = propose_design("The Effect of Minimum Wages on Employment")
    assert design["method"] == "did"
    assert _did_term(design)
    assert design["catalog_entry_id"] is None


def test_catalog_id_alone_cannot_open_did():
    for token in (
        "ck1994",
        "ck1994_long",
        "minimum-wage-employment",
        "barro1991_growth",
    ):
        design = propose_design(token)
        assert design["method"] == "ols", token
        assert not _did_term(design)
        assert design["catalog_entry_id"] is None
        assert design["status"] == "draft"
        assert design["confirmed"] is False


def test_level_ols_schooling_wages():
    design = propose_design("教育对工资的影响")
    assert design["method"] == "ols"
    assert not _did_term(design)
    assert design["outcome"] == "wages"
    assert design["treatment"] == "schooling"
    assert design["qType"] == "average"


def test_level_ols_barro_growth():
    design = propose_design("Barro growth: determinants of economic growth")
    assert design["method"] == "ols"
    assert not _did_term(design)
    assert design["outcome"] == "growth"
    assert design["catalog_entry_id"] is None


def test_explicit_did_language_still_fills_interaction():
    design = propose_design("用双重差分估计医保整合对住院支出的影响")
    assert design["method"] == "did"
    assert _did_term(design)


def test_optional_question_is_stamped():
    design = propose_design(
        "最低工资对就业的影响",
        question="新泽西提高最低工资后，快餐业就业是否下降？",
    )
    assert design["source"]["question"].startswith("新泽西")
    assert design["method"] == "did"
    assert _did_term(design)


def test_empty_title_raises():
    try:
        propose_design("  ")
    except ValueError as exc:
        assert "title" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")


def test_propose_output_excludes_deprecated_win_paths():
    design = propose_design("最低工资对就业的影响")
    assert "allow_did" not in design
    assert "dataAttached" not in design
    assert design["catalog_entry_id"] is None
    imported = {name for name in dir(propose_mod) if not name.startswith("_")}
    assert "propose_design" in imported
