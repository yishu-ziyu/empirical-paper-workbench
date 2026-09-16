"""Table 1 + specification equation for the prewrite direction pause."""
from __future__ import annotations

from agent.engine.prewrite_preview import (
    PREWRITE_GATE_AWAITING_ESTIMATE,
    build_prewrite_preview,
    compute_table1,
    specification_equation_text,
)


def test_ols_formula_becomes_display_equation():
    text = specification_equation_text(
        {
            "method": "ols",
            "formula": "income ~ age + gender",
            "outcome": "income",
            "treatment": "age",
        }
    )
    assert text == "income = β₀ + β₁ age + β₂ gender + ε"


def test_iv_formula_kept_as_two_stage_display():
    text = specification_equation_text(
        {
            "method": "iv",
            "formula": "wage ~ (edu ~ nearc4) + exper",
            "iv_formula": "wage ~ (edu ~ nearc4) + exper",
        }
    )
    assert text == "wage ~ (edu ~ nearc4) + exper"


def test_rd_and_scm_equations_without_ols_formula():
    rd = specification_equation_text(
        {"method": "rd", "outcome": "y", "running_var": "score", "cutoff": 0.5}
    )
    scm = specification_equation_text(
        {"method": "scm", "outcome": "gdp", "treated_unit": "CA"}
    )
    assert rd == "y = f(score) + τ·1[score ≥ 0.5] + ε"
    assert scm == "gdp_{CA} vs synthetic control"


def test_table1_describes_spec_columns(tmp_path):
    csv = tmp_path / "t1.csv"
    csv.write_text(
        "income,age,gender,noise\n"
        "10,20,1,9\n"
        "12,22,0,8\n"
        "14,,1,7\n",
        encoding="utf-8",
    )
    table = compute_table1(
        str(csv),
        {
            "outcome": "income",
            "treatment": "age",
            "controls": ["gender"],
        },
    )
    assert table["produced_by"] == "prewrite_preview"
    assert table["n"] == 3
    names = [row["variable"] for row in table["rows"]]
    assert names == ["income", "age", "gender"]
    assert "noise" not in names
    by_name = {row["variable"]: row for row in table["rows"]}
    assert by_name["age"]["missing"] == 1
    assert by_name["age"]["role"] == "treatment"
    assert by_name["income"]["role"] == "outcome"
    assert by_name["gender"]["role"] == "control"
    assert by_name["income"]["mean"] == 12.0


def test_build_preview_sets_awaiting_gate(tmp_path):
    csv = tmp_path / "t1.csv"
    csv.write_text("y,x\n1,2\n3,4\n", encoding="utf-8")
    out = build_prewrite_preview(
        {
            "csv_path": str(csv),
            "main_specification": {
                "method": "ols",
                "formula": "y ~ x",
                "outcome": "y",
                "treatment": "x",
            },
        }
    )
    assert out["prewrite_gate"] == PREWRITE_GATE_AWAITING_ESTIMATE
    assert out["specification_equation"] == "y = β₀ + β₁ x + ε"
    assert out["table1"]["rows"]
