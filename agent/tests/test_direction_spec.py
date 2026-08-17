"""Research direction normalizes into the spec downstream nodes read."""
from design.spec import DirectionSpec, slug_for_topic


def test_from_direction_dict_builds_main_specification():
    spec = DirectionSpec.from_direction(
        {
            "question": "父母受教育水平对子女工资收入的影响",
            "dv": "ln_wage",
            "iv": "parent_education",
            "controls": ["age", "female"],
            "method": "ols",
        }
    )
    assert spec is not None
    assert spec.slug == "parent_education_wage"
    main = spec.to_main_specification()
    assert main["outcome"] == "ln_wage"
    assert main["treatment"] == "parent_education"
    assert main["formula"] == "ln_wage ~ parent_education + age + female"


def test_from_direction_string_still_works():
    spec = DirectionSpec.from_direction("劳动供给")
    assert spec is not None
    assert spec.topic == "劳动供给"
    assert spec.to_main_specification() == {}


def test_from_empty_returns_none():
    assert DirectionSpec.from_direction({}) is None
    assert DirectionSpec.from_direction("") is None
    assert DirectionSpec.from_direction(None) is None


def test_known_charls_topic_keeps_readable_slug():
    slug = slug_for_topic("城乡居民基本医疗保险整合是否降低农村中老年人的住院自付支出？")
    assert slug == "charls_did_urb_rur_insurance"


def test_enrich_direction_fills_aliases_without_dropping_user_fields():
    spec = DirectionSpec.from_direction(
        {"question": "q", "dv": "y", "iv": "d", "method": "did"}
    )
    assert spec is not None
    out = spec.enrich_direction({"question": "q", "method": "did", "extra": 1})
    assert out["outcome_col"] == "y"
    assert out["treatment_col"] == "d"
    assert out["extra"] == 1


def test_iv_main_specification_is_not_plain_ols_formula():
    spec = DirectionSpec.from_direction(
        {
            "question": "q",
            "dv": "y",
            "iv": "treatment",
            "method": "iv",
            "instrument": "z",
            "controls": ["x1"],
        }
    )
    assert spec is not None
    main = spec.to_main_specification()
    assert main["method"] == "iv"
    assert main["instruments"] == ["z"]
    assert main["endogenous"] == "treatment"
    assert main["iv_formula"] == "y ~ (treatment ~ z) + x1"
    assert "y ~ treatment" not in main.get("formula", "")
    assert "(" in main["formula"]


def test_rd_and_scm_main_specification_have_no_ols_formula():
    rd = DirectionSpec.from_direction(
        {
            "question": "q",
            "dv": "y",
            "iv": "d",
            "method": "rd",
            "running": "x",
            "cutoff": 0,
        }
    )
    assert rd is not None
    rd_main = rd.to_main_specification()
    assert rd_main["method"] == "rd"
    assert rd_main["running_var"] == "x"
    assert "formula" not in rd_main

    scm = DirectionSpec.from_direction(
        {
            "question": "q",
            "dv": "y",
            "iv": "d",
            "method": "scm",
            "unit_col": "unit",
            "time_col": "time",
            "treated_unit": 0,
            "treatment_time": 10,
        }
    )
    assert scm is not None
    scm_main = scm.to_main_specification()
    assert scm_main["method"] == "scm"
    assert scm_main["unit_col"] == "unit"
    assert scm_main["treatment_time"] == 10
    assert "formula" not in scm_main


def test_did_main_specification_carries_panel_columns():
    spec = DirectionSpec.from_direction(
        {
            "question": "q",
            "dv": "y",
            "iv": "treat",
            "method": "did",
            "time_col": "year",
            "id_col": "pid",
        }
    )
    assert spec is not None
    main = spec.to_main_specification()
    assert main["time_col"] == "year"
    assert main["id_col"] == "pid"
    assert main["feols_formula"] == "y ~ treat | pid + year"


def test_direction_request_allows_method_columns():
    """agent venv 没有 fastapi，核对门上的字段和 extra=allow。"""
    from pathlib import Path

    text = (
        Path(__file__).resolve().parents[2] / "backend" / "routers" / "outline.py"
    ).read_text(encoding="utf-8")
    assert 'model_config = {"extra": "allow"}' in text
    for name in (
        "time_col",
        "instrument",
        "instrument_col",
        "running",
        "running_var",
        "id_col",
        "cutoff",
        "cluster_levels",
    ):
        assert name in text

    spec = DirectionSpec.from_direction(
        {
            "question": "q",
            "dv": "y",
            "iv": "d",
            "method": "iv",
            "instrument": "z",
            "time_col": "year",
            "running": "x",
        }
    )
    assert spec is not None
    assert spec.instruments == ["z"]
    assert spec.time_col == "year"
    assert spec.running_var == "x"


def test_set_direction_projects_charls_then_panel_then_user_wins():
    from nodes.set_direction import set_direction

    from_charls = set_direction(
        {
            "research_direction": {
                "question": "q",
                "dv": "y",
                "iv": "d",
                "method": "did",
            },
            "charls_config": {
                "variable_mapping": {"pid": "pid", "wave": "wave"},
                "waves": [2018, 2020],
            },
            "panel_id": "unit",
            "time_col": "year",
        }
    )
    assert from_charls["research_direction"]["id_col"] == "pid"
    assert from_charls["research_direction"]["time_col"] == "wave"
    assert from_charls["main_specification"]["id_col"] == "pid"
    assert from_charls["main_specification"]["time_col"] == "wave"

    user_wins = set_direction(
        {
            "research_direction": {
                "question": "q",
                "dv": "y",
                "iv": "d",
                "method": "did",
                "time_col": "year",
                "id_col": "sid",
            },
            "charls_config": {"variable_mapping": {"pid": "pid", "wave": "wave"}},
            "panel_id": "unit",
            "time_col": "t",
        }
    )
    assert user_wins["research_direction"]["time_col"] == "year"
    assert user_wins["research_direction"]["id_col"] == "sid"

    from_panel = set_direction(
        {
            "research_direction": {
                "question": "q",
                "dv": "y",
                "iv": "d",
                "method": "did",
            },
            "panel_id": "unit",
            "time_col": "year",
        }
    )
    assert from_panel["research_direction"]["id_col"] == "unit"
    assert from_panel["research_direction"]["time_col"] == "year"


def test_set_direction_guesses_exact_year_id_columns(tmp_path):
    import pandas as pd
    from nodes.set_direction import set_direction

    csv_path = tmp_path / "panel.csv"
    pd.DataFrame({"year": [2010], "id": [1], "y": [1.0], "d": [0]}).to_csv(
        csv_path, index=False
    )
    out = set_direction(
        {
            "csv_path": str(csv_path),
            "research_direction": {
                "question": "q",
                "dv": "y",
                "iv": "d",
                "method": "did",
            },
        }
    )
    assert out["research_direction"]["time_col"] == "year"
    assert out["research_direction"]["id_col"] == "id"
    guessed = out.get("degradations") or []
    assert any(item.get("reason") == "column_guessed" for item in guessed)
