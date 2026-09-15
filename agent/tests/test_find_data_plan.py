"""FD-BE-plan: confirmed design facets → find-data plan (DECIDE-7 / R-sources)."""
from __future__ import annotations

import pytest

from agent.find_data.plan import (
    DesignUnconfirmed,
    PRIMARY_VENUE,
    build_find_data_plan,
    classify_route_family,
    is_confirmed_design,
    read_find_data,
)


def _confirmed(**overrides):
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:01:00Z",
        "source": {"title": "最低工资对就业的影响", "question": ""},
        "method": "did",
        "outcome": "employment",
        "treatment": "min_wage",
        "controls": [],
        "group": "treated",
        "treated": "treated",
        "period": "post",
        "time_col": "",
        "id_col": "",
        "first_treat_col": "",
        "interactions": [
            {
                "kind": "did",
                "left": "treated",
                "right": "period",
                "term": "treated:period",
            }
        ],
        "qType": "causal",
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    design.update(overrides)
    return design


def test_unconfirmed_design_raises():
    with pytest.raises(DesignUnconfirmed):
        build_find_data_plan(None)
    with pytest.raises(DesignUnconfirmed):
        build_find_data_plan({})
    with pytest.raises(DesignUnconfirmed):
        build_find_data_plan(_confirmed(status="draft", confirmed=False, confirmed_at=None))
    assert is_confirmed_design(_confirmed(status="draft", confirmed=True)) is False
    assert is_confirmed_design({"status": "confirmed"}) is False


def test_minwage_plan_names_where_and_how():
    record = build_find_data_plan(_confirmed(), now="2026-09-15T12:02:00Z")
    assert record["status"] == "planned"
    assert record["route_family"] == "minwage"
    assert record["primary_venue"] == PRIMARY_VENUE["minwage"]
    plan = record["plan"]
    assert "ck fixture" in plan["where"]
    assert "Card zip" in plan["where"]
    assert "ck fixture" in plan["how"]
    assert "Card zip" in plan["how"]
    assert "Dataverse" in plan["how"]
    assert "employment" in plan["how"]
    assert "min_wage" in plan["how"]
    facets = plan["search_facets"]
    assert facets["method"] == "did"
    assert facets["outcome"] == "employment"
    assert facets["treatment"] == "min_wage"
    assert "treated:period" in facets["interactions"]
    assert record["candidates"] == []
    assert "allow_did" not in record
    assert "dataAttached" not in record
    assert record["planned_at"] == "2026-09-15T12:02:00Z"


def test_educ_wage_from_schooling_wages_slots():
    design = _confirmed(
        source={"title": "教育对工资的影响", "question": ""},
        method="ols",
        outcome="wages",
        treatment="schooling",
        interactions=[],
        qType="average",
        treated="",
        period="",
        group="",
    )
    assert classify_route_family(design) == "educ_wage"
    record = build_find_data_plan(design)
    assert record["primary_venue"] == "IPUMS"
    assert "IPUMS" in record["plan"]["where"]
    assert "wage1" not in record["plan"]["where"]
    assert "IPUMS" in record["plan"]["how"]
    assert "teaching" in record["plan"]["how"]
    assert record["candidates"] == []


def test_growth_from_barro_title():
    design = _confirmed(
        source={"title": "Barro growth: determinants of economic growth", "question": ""},
        method="ols",
        outcome="growth",
        treatment="",
        interactions=[],
        qType="average",
        treated="",
        period="",
        group="",
    )
    assert classify_route_family(design) == "growth"
    record = build_find_data_plan(design)
    assert record["primary_venue"] == "WDI"
    assert "WDI" in record["plan"]["where"]
    assert "barro" not in record["plan"]["where"]
    assert "WDI" in record["plan"]["how"]
    assert record["candidates"] == []


def test_macro_from_fred_style_title():
    design = _confirmed(
        source={"title": "FRED unemployment rate and federal funds aggregates", "question": ""},
        method="ols",
        outcome="unemployment_rate",
        treatment="",
        interactions=[],
        qType="average",
        treated="",
        period="",
        group="",
    )
    assert classify_route_family(design) == "macro"
    record = build_find_data_plan(design)
    assert record["primary_venue"] == "FRED"
    assert record["plan"]["where"] == "FRED"
    assert "FRED" in record["plan"]["how"]
    assert "Dataverse" in record["plan"]["how"]


def test_else_is_dataverse():
    design = _confirmed(
        source={"title": "医保整合对住院支出的影响", "question": ""},
        method="did",
        outcome="out_of_pocket",
        treatment="insurance_merge",
        interactions=[
            {"kind": "did", "left": "treated", "right": "period", "term": "treated:period"}
        ],
        qType="causal",
    )
    assert classify_route_family(design) == "else"
    record = build_find_data_plan(design)
    assert record["primary_venue"] == "Dataverse"
    assert record["plan"]["where"] == "Dataverse"
    assert "Dataverse" in record["plan"]["how"]
    assert "out_of_pocket" in record["plan"]["search_facets"]["query_terms"]
    assert "insurance_merge" in record["plan"]["search_facets"]["query_terms"]


def test_bare_wage_without_schooling_is_else_not_educ_wage():
    design = _confirmed(
        source={"title": "城市工资分布", "question": ""},
        method="ols",
        outcome="wage",
        treatment="",
        interactions=[],
        qType="average",
        treated="",
        period="",
        group="",
    )
    assert classify_route_family(design) == "else"


def test_catalog_id_does_not_choose_the_route():
    design = _confirmed(
        source={"title": "教育对工资的影响", "question": ""},
        method="ols",
        outcome="wages",
        treatment="schooling",
        interactions=[],
        qType="average",
        treated="",
        period="",
        group="",
        catalog_entry_id="ck1994_long",
    )
    assert classify_route_family(design) == "educ_wage"
    record = build_find_data_plan(design)
    assert record["route_family"] == "educ_wage"
    assert "ck1994" not in (record["plan"]["how"] or "")


def test_plan_stub_has_zero_candidates():
    record = build_find_data_plan(_confirmed())
    assert record["candidates"] == []
    assert record["status"] == "planned"


def test_read_find_data_empty_without_confirm_or_plan():
    empty = read_find_data({})
    assert empty["status"] == "missing"
    assert empty["plan"] is None
    assert empty["candidates"] == []

    draft_state = {"design": _confirmed(status="draft", confirmed=False)}
    assert read_find_data(draft_state)["status"] == "missing"

    planned = build_find_data_plan(_confirmed())
    stale = {"design": _confirmed(status="draft", confirmed=False), "find_data": planned}
    assert read_find_data(stale)["status"] == "missing"

    live = {"design": _confirmed(), "find_data": planned}
    assert read_find_data(live)["status"] == "planned"
    assert read_find_data(live)["route_family"] == "minwage"
