"""heterogeneity_groups / educ×region must emit an interaction, not an additive dummy.

OLS lock must keep public labels as OLS / regress / lm, never feols.
"""
from __future__ import annotations

from agent.design.spec import (
    DirectionSpec,
    apply_heterogeneity_to_formula,
    build_heterogeneity_ols_formula,
    infer_heterogeneity_groups,
)
from agent.engine.bind import format_estimate_facts
from agent.nodes.estimate import estimate, table_var_names
from agent.nodes.robustness_check import robustness_check
from agent.nodes.set_direction import set_direction


def _is_interaction_formula(formula: str, treatment: str = "educ", group: str = "region") -> bool:
    compact = formula.replace(" ", "").lower()
    treat = treatment.lower()
    grp = group.lower()
    return (
        f"{treat}:{grp}" in compact
        or f"{grp}:{treat}" in compact
        or f"{treat}*{grp}" in compact
        or f"{grp}*{treat}" in compact
    )


def test_infer_educ_times_region_from_question():
    groups = infer_heterogeneity_groups(
        "Does the return to educ × region vary?",
        treatment="educ",
        controls=["exper", "region"],
    )
    assert groups == ["region"]
    groups = infer_heterogeneity_groups(
        "Does the return to education vary by region?",
        treatment="educ",
        controls=["exper", "south"],
    )
    assert groups == ["south"]
    groups = infer_heterogeneity_groups(
        "教育回报是否因地区而异？",
        treatment="educ",
        controls=["exper"],
    )
    assert groups == ["region"]


def test_plain_earnings_question_does_not_invent_region_group():
    assert infer_heterogeneity_groups(
        "Does education increase earnings?",
        treatment="educ",
        controls=["exper", "region"],
    ) == []


def test_explicit_heterogeneity_groups_win():
    assert infer_heterogeneity_groups(
        "Does education increase earnings?",
        treatment="educ",
        controls=["exper"],
        explicit=["region"],
    ) == ["region"]


def test_ols_formula_is_educ_times_group_not_additive_dummy():
    formula = build_heterogeneity_ols_formula(
        "lwage", "educ", ["exper", "region"], ["region"]
    )
    assert _is_interaction_formula(formula)
    assert "lwage ~ educ" in formula.replace("  ", " ")
    assert "exper" in formula
    # Additive-only region dummy is the failure mode: educ + region with no product.
    additive_only = "lwage ~ educ + exper + region"
    assert formula.replace(" ", "") != additive_only.replace(" ", "")
    assert formula.count("region") >= 1


def test_apply_rewrites_additive_region_dummy():
    rewritten = apply_heterogeneity_to_formula(
        "lwage ~ educ + exper + region",
        {"treatment": "educ", "heterogeneity_groups": ["region"]},
    )
    assert _is_interaction_formula(rewritten)
    assert "exper" in rewritten
    assert "region" in rewritten


def test_direction_spec_heterogeneity_groups_emits_interaction():
    spec = DirectionSpec.from_direction(
        {
            "question": "educ × region returns",
            "dv": "lwage",
            "iv": "educ",
            "controls": ["exper", "region"],
            "method": "ols",
            "heterogeneity_groups": ["region"],
        }
    )
    assert spec is not None
    assert spec.heterogeneity_groups == ["region"]
    main = spec.to_main_specification()
    assert main["method"] == "ols"
    assert main["heterogeneity_groups"] == ["region"]
    assert _is_interaction_formula(main["formula"])
    assert "feols" not in str(main.get("formula")).lower()
    assert "feols_formula" not in main


def test_direction_question_educ_region_infers_interaction():
    spec = DirectionSpec.from_direction(
        {
            "question": "Does the return to education vary by region?",
            "dv": "lwage",
            "iv": "educ",
            "controls": ["exper", "region"],
            "method": "ols",
        }
    )
    assert spec is not None
    assert spec.heterogeneity_groups == ["region"]
    main = spec.to_main_specification()
    assert _is_interaction_formula(main["formula"])
    compact = main["formula"].replace(" ", "")
    assert "educ:region" in compact or "educ*region" in compact


def test_set_direction_writes_educ_region_interaction():
    out = set_direction(
        {
            "research_direction": {
                "question": "educ × region heterogeneity",
                "dv": "lwage",
                "iv": "educ",
                "controls": ["exper", "region"],
                "method": "ols",
                "heterogeneity_groups": ["region"],
            }
        }
    )
    main = out["main_specification"]
    assert main["heterogeneity_groups"] == ["region"]
    assert _is_interaction_formula(main["formula"])
    assert out["research_direction"]["heterogeneity_groups"] == ["region"]


def test_estimate_ols_heterogeneity_fits_interaction_and_labels_ols(tmp_path):
    import pandas as pd

    df = pd.DataFrame(
        {
            "lwage": [1.0, 1.2, 1.5, 1.8, 2.0, 2.4, 1.1, 1.3],
            "educ": [8, 10, 12, 14, 8, 10, 12, 16],
            "region": [0, 0, 0, 0, 1, 1, 1, 1],
            "exper": [2, 4, 6, 8, 3, 5, 7, 9],
        }
    )
    csv_path = tmp_path / "wage.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "ols", "dv": "lwage", "iv": "educ"},
            "main_specification": {
                "method": "ols",
                "formula": "lwage ~ educ + exper + region",
                "outcome": "lwage",
                "treatment": "educ",
                "controls": ["exper", "region"],
                "heterogeneity_groups": ["region"],
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "ok"
    assert _is_interaction_formula(str(est["formula"]))
    # 9/15 recut keeps engine truth in state; the OLS label is user-facing only
    # (``agent/design/spec.py`` ``display_estimate_engine_label``).
    assert est["estimator"] in {"statspai.feols", "statsmodels.ols"}
    table = out["results"]
    assert "feols" not in table.lower()
    assert "估计器：`OLS`" in table
    assert "| educ:region |" in table or "educ:region" in str(est.get("table_rows"))


def test_table_var_names_include_interaction():
    names = table_var_names(
        {
            "treatment": "educ",
            "controls": ["exper"],
            "heterogeneity_groups": ["region"],
            "formula": "lwage ~ educ + exper + region + educ:region",
        }
    )
    assert names[0] == "educ"
    assert "region" in names
    assert "educ:region" in names
    assert "exper" in names


def test_ols_robustness_heterogeneity_is_interaction_not_feols(tmp_path):
    import pandas as pd

    df = pd.DataFrame(
        {
            "lwage": [1.0, 1.2, 1.5, 1.8, 2.0, 2.4, 1.1, 1.3],
            "educ": [8, 10, 12, 14, 8, 10, 12, 16],
            "region": [0, 0, 0, 0, 1, 1, 1, 1],
        }
    )
    csv_path = tmp_path / "wage.csv"
    df.to_csv(csv_path, index=False)
    out = robustness_check(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "ols"},
            "main_specification": {
                "method": "ols",
                "formula": "lwage ~ educ + region",
                "outcome": "lwage",
                "treatment": "educ",
                "heterogeneity_groups": ["region"],
            },
        }
    )
    rr = out["robustness_results"]
    assert rr["heterogeneity"]
    row = rr["heterogeneity"][0]
    assert row["group"] == "region"
    assert row["interaction_coef"] is not None
    assert _is_interaction_formula(str(row.get("formula") or ""))
    blob = str(rr).lower()
    assert "feols" not in blob
    assert "feols" not in str(rr.get("summary_table") or "").lower()


def test_bind_ols_facts_hide_feols_estimator():
    facts = format_estimate_facts(
        {
            "research_direction": {"method": "ols"},
            "main_specification": {"method": "ols", "formula": "lwage ~ educ:region"},
            "estimate": {
                "status": "ok",
                "estimator": "statspai.feols",
                "method": "ols",
                "formula": "lwage ~ educ + region + educ:region",
                "n": 8,
                "treatment_row": "| educ | 0.1 | 0.02 | 0.01 |",
            },
        },
        method="ols",
    )
    assert "估计器：OLS" in facts
    assert "feols" not in facts.lower()
    assert "educ:region" in facts
