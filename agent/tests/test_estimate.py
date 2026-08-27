"""Main estimate writes a table the results chapter can cite."""
from nodes.estimate import estimate, splice_missing_table_rows, table_var_names


def test_estimate_empty_without_spec():
    out = estimate({})
    assert out["estimate"]["status"] == "error"
    assert out["estimate"]["produced_by"] == "estimate"
    assert not out["estimate"]["treatment_row"]
    out2 = estimate({"csv_path": "/tmp/x.csv"})
    assert out2["estimate"]["status"] == "error"


def test_estimate_writes_treatment_row(tmp_path):
    import pandas as pd

    df = pd.DataFrame(
        {
            "y": [1.0, 2.0, 2.0, 3.0, 3.0, 4.0],
            "x": [0, 0, 1, 0, 1, 1],
        }
    )
    csv_path = tmp_path / "main.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "y ~ x",
                "treatment": "x",
                "outcome": "y",
            },
        }
    )
    assert "y ~ x" in out["results"]
    assert "| x |" in out["results"]
    assert out["estimate"]["status"] == "ok"
    assert out["estimate"]["n"] == 6
    assert out["estimate"]["coef"] is not None
    assert out["estimate"]["table_rows"]
    assert any(row.startswith("| x |") for row in out["estimate"]["table_rows"])


def test_estimate_ols_table_includes_treat_coef_or_omitted(tmp_path):
    """income ~ age + treat: treat gets a real row, never invented DiD."""
    import pandas as pd

    df = pd.read_csv("frontend/public/samples/course-panel.csv")
    csv_path = tmp_path / "course.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "income ~ age + treat",
                "treatment": "age",
                "controls": ["treat"],
                "method": "ols",
            },
        }
    )
    table = out["results"]
    assert "| age |" in table
    assert "| treat |" in table
    treat_line = next(line for line in table.splitlines() if line.startswith("| treat |"))
    cells = [c.strip() for c in treat_line.strip("|").split("|")]
    assert cells[0] == "treat"
    assert cells[1] != ""
    assert cells[1] not in {"", "DiD", "ATT"}
    if cells[1] == "未估计":
        assert cells[2] == "—"
    else:
        float(cells[1])


def test_estimate_omitted_control_not_in_data(tmp_path):
    """Control named in spec but absent from the fit is 未估计, not a fake number."""
    import pandas as pd

    df = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "x": [0, 1, 0, 1]})
    csv_path = tmp_path / "no_treat.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "formula": "y ~ x",
                "treatment": "x",
                "controls": ["treat"],
            },
        }
    )
    assert "| x |" in out["results"]
    assert "| treat | 未估计 | — | — |" in out["results"]
    assert "0.9999" not in out["results"]


def test_splice_missing_table_rows_adds_treat_omitted():
    content = (
        "# 主结果\n\n"
        "| 变量 | 系数 | SE | p |\n"
        "|------|------|----|---|\n"
        "| age | -0.0687 | 0.0100 | 0.0010 |"
    )
    out = splice_missing_table_rows(
        content,
        {"formula": "income ~ age + treat", "treatment": "age", "controls": ["treat"]},
        {"formula": "income ~ age + treat"},
    )
    assert "| treat | 未估计 | — | — |" in out
    assert "| age | -0.0687 | 0.0100 | 0.0010 |" in out
    assert table_var_names(
        {"treatment": "age", "controls": ["treat"], "formula": "income ~ age + treat"}
    ) == ["age", "treat"]


def test_results_chapter_user_prompt_contains_estimate(tmp_path, mock_llm_for):
    """结果章拿到的是主估计表，不是空占位。"""
    import pandas as pd
    from nodes.generate_chapter import generate_chapter

    df = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "x": [0, 1, 0, 1]})
    csv_path = tmp_path / "main.csv"
    df.to_csv(csv_path, index=False)
    estimated = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {"formula": "y ~ x", "treatment": "x"},
        }
    )
    from conftest import make_write_ready_state

    recorder = mock_llm_for("generate_chapter", return_value="MOCK")
    generate_chapter(
        make_write_ready_state(
            current_chapter_index=0,
            outline=[{"type": "results", "title": "结果"}],
            method="OLS",
            **estimated,
        )
    )
    _, user = recorder.calls[0]["args"]
    assert "y ~ x" in user
    assert "| x |" in user


def test_estimate_iv_uses_ivreg(tmp_path):
    import statspai

    df = statspai.dgp_iv(n=250, effect=0.5, first_stage=0.6, seed=1)
    csv_path = tmp_path / "iv.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "iv",
                "outcome": "y",
                "treatment": "treatment",
                "endogenous": "treatment",
                "instruments": ["instrument"],
                "iv_formula": "y ~ (treatment ~ instrument) + x1 + x2",
                "controls": ["x1", "x2"],
            },
        }
    )
    assert out["estimate"]["estimator"] == "statspai.ivreg"
    assert out["estimate"]["status"] == "ok"
    assert out["estimate"]["treatment_row"]
    assert "| treatment |" in out["estimate"]["treatment_row"]
    assert out["estimate"]["coef"] is not None
    assert "iv_diag" not in str(out["estimate"].get("estimator"))


def test_estimate_iv_missing_instrument_is_error_without_fake_coef(tmp_path):
    import pandas as pd

    csv_path = tmp_path / "iv_missing.csv"
    pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "treatment": [0, 1, 0, 1]}).to_csv(
        csv_path, index=False
    )
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "iv",
                "outcome": "y",
                "treatment": "treatment",
                "formula": "y ~ treatment",
            },
        }
    )
    assert out["estimate"]["status"] == "error"
    assert out["estimate"]["produced_by"] == "estimate"
    assert out["estimate"]["treatment_row"] == ""
    assert "coef" not in out["estimate"]
    assert "| treatment |" not in out["results"]
    assert "0." not in out["results"]


def test_estimate_rd_is_not_ols(tmp_path):
    import statspai

    df = statspai.dgp_rd(n=400, effect=0.3, cutoff=0.0, seed=1)
    csv_path = tmp_path / "rd.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "rd",
                "outcome": "y",
                "treatment": "treatment",
                "running_var": "x",
                "cutoff": 0.0,
            },
        }
    )
    assert out["estimate"]["estimator"] == "statspai.rdrobust"
    assert out["estimate"]["status"] == "ok"
    assert out["estimate"]["treatment_row"]
    assert "y ~ treat" not in str(out["estimate"].get("formula") or "")
    assert out["estimate"]["estimator"] != "statspai.feols"


def test_bacon_forbids_twfe_without_cohort_is_error(tmp_path):
    """Bacon 禁 TWFE 且没有 first_treat_col：error，不交主表，不编系数。"""
    import pandas as pd

    csv_path = tmp_path / "did_no_cohort.csv"
    pd.DataFrame(
        {
            "y": [1.0, 2.0, 2.0, 3.0],
            "treat": [0, 1, 0, 1],
        }
    ).to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "did",
                "formula": "y ~ treat",
                "treatment": "treat",
            },
            "identification_diag": {
                "diagnostics": [
                    {
                        "test": "bacon_decomposition",
                        "forbidden_weight_share": 0.4,
                    }
                ]
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "error"
    assert est["treatment_row"] == ""
    assert est["produced_by"] == "estimate"
    assert "| 变量 | 系数 | SE | p |" not in out["results"]
    assert est.get("coef") is None
    assert est.get("estimator") != "statspai.feols"


def test_bacon_with_cohort_does_not_fall_back_to_twfe(tmp_path):
    """Bacon 超阈但有队列列：走 CS，失败也不得落到 feols TWFE 主表。"""
    import statspai

    df = statspai.dgp_did(n_units=40, n_periods=6, effect=0.5, seed=1)
    csv_path = tmp_path / "did_cs.csv"
    df.to_csv(csv_path, index=False)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "did",
                "formula": "y ~ treated",
                "outcome": "y",
                "treatment": "treated",
                "first_treat_col": "first_treat",
                "time_col": "time",
                "id_col": "unit",
            },
            "identification_diag": {
                "diagnostics": [
                    {
                        "test": "bacon_decomposition",
                        "forbidden_weight_share": 0.4,
                    }
                ]
            },
        }
    )
    est = out["estimate"]
    assert est.get("estimator") != "statspai.feols"
    if est.get("status") == "ok":
        assert est["estimator"] == "statspai.callaway_santanna"
        assert est["treatment_row"]
    else:
        assert est["status"] == "error"
        assert est.get("treatment_row") in ("", None)
        assert "| 变量 | 系数 | SE | p |" not in out["results"]


def test_estimate_scm_is_not_ols(tmp_path, monkeypatch):
    import pandas as pd
    import statspai

    df = pd.DataFrame(
        {
            "unit": [0, 0, 1, 1],
            "time": [1, 2, 1, 2],
            "y": [1.0, 2.0, 1.1, 1.2],
            "treated": [0, 1, 0, 0],
        }
    )
    csv_path = tmp_path / "scm.csv"
    df.to_csv(csv_path, index=False)

    called: dict[str, bool] = {}

    class _Fake:
        estimate = 0.42
        se = 0.11
        pvalue = 0.03
        n_obs = 4

    def fake_synth(*_a, **_k):
        called["synth"] = True
        return _Fake()

    def fake_feols(*_a, **_k):
        called["feols"] = True
        raise AssertionError("SCM 主表不得走 feols(y ~ treat)")

    monkeypatch.setattr(statspai, "synth", fake_synth)
    monkeypatch.setattr(statspai, "feols", fake_feols)

    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "scm",
                "outcome": "y",
                "treatment": "treated",
                "unit_col": "unit",
                "time_col": "time",
                "treated_unit": 0,
                "treatment_time": 2,
            },
        }
    )
    assert called.get("synth") is True
    assert "feols" not in called
    assert out["estimate"]["estimator"] == "statspai.synth"
    assert out["estimate"]["treatment_row"]
    assert "y ~ treat" not in str(out["estimate"].get("formula") or "")
