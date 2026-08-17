"""ADR-0010: spec curve keeps every defensible spec on the table."""
import pandas as pd

from design.spec_curve import build_specs, run_spec_curve, spec_curve_markdown


def test_build_specs_includes_bivariate_and_splits():
    specs = build_specs(["age", "urban"], ["y", "d", "age", "urban"])
    names = [s["spec"] for s in specs]
    assert "bivariate" in names
    assert "baseline_controls" in names
    assert "urban_1" in names
    assert "urban_0" in names


def test_run_spec_curve_keeps_every_row():
    n = 80
    df = pd.DataFrame(
        {
            "y": [0.1 * i for i in range(n)],
            "d": [i % 2 for i in range(n)],
            "age": [20 + (i % 10) for i in range(n)],
            "urban": [i % 2 for i in range(n)],
        }
    )
    rows = run_spec_curve(df, outcome="y", treatment="d", controls=["age", "urban"])
    assert len(rows) >= 3
    names = {r["spec"] for r in rows}
    assert "bivariate" in names
    assert all("treatment_coef" in r for r in rows)
    md = spec_curve_markdown(rows, slug="demo")
    assert "设定表" in md
    assert "bivariate" in md


def test_run_spec_curve_missing_columns_returns_empty():
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert run_spec_curve(df, outcome="y", treatment="d") == []
