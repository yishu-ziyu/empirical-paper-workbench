"""Test robustness_check node with a main specification.

Uses a simulated panel dataset (from statspai.dgp_did) written to a real
CSV file in tmp_path, then runs the node and asserts robustness_results /
summary_table are produced.
"""
import pytest
import pandas as pd
from agent.nodes.robustness_check import robustness_check
from agent.state import EconPaperState

import statspai


def test_robustness_check_no_main_spec():
    """Test that missing main_specification returns placeholder, no exception."""
    state: EconPaperState = {}
    result = robustness_check(state)
    assert "robustness_results" in result
    assert result["robustness_results"]["summary_table"] == "No main specification available"


def test_robustness_check_basic(tmp_path):
    """Test robustness_check runs clustering + heterogeneity + placebo."""
    df = statspai.dgp_did(n_units=100, n_periods=10, effect=0.5, seed=1)
    df["treat"] = df["treated"]
    # 构造与处理变量不共线的真实分组变量（unit 奇偶），否则交互项与 treat
    # 完全共线，feols 会丢弃交互项导致 interaction_coef 恒为 None。
    df["group_even"] = (df["unit"] % 2 == 0).astype(int)
    csv_path = tmp_path / "panel.csv"
    df.to_csv(csv_path, index=False)

    state: EconPaperState = {
        "session_id": "test",
        "csv_path": str(csv_path),
        "research_direction": {"method": "did"},
        "main_specification": {
            "formula": "y ~ treat",
            "outcome": "y",
            "treatment": "treat",
            "cluster": "unit",
            "cluster_levels": ["unit"],
            "heterogeneity_groups": ["group_even"],
        },
    }

    result = robustness_check(state)
    assert "robustness_results" in result
    rr = result["robustness_results"]
    assert "robustness" in rr
    assert "heterogeneity" in rr
    assert "placebos" in rr
    assert "summary_table" in rr
    assert isinstance(rr["summary_table"], str)
    assert "稳健性检验汇总" in rr["summary_table"]
    # clustering ran for the single level
    assert len(rr["robustness"]) >= 1
    assert rr["robustness"][0]["type"] == "clustering"
    assert rr["robustness"][0]["level"] == "unit"
    # heteroogeneity interaction coefficient actually estimated
    assert len(rr["heterogeneity"]) >= 1
    assert rr["heterogeneity"][0]["group"] == "group_even"
    assert rr["heterogeneity"][0]["interaction_coef"] is not None
    # placebo ran (wild_cluster_bootstrap for did)
    assert len(rr["placebos"]) >= 1
    assert rr["placebos"][0]["type"] == "wild_cluster_bootstrap"
    # explore-arm spec curve is attached but does not rewrite the main spec
    assert "spec_curve" in result
    assert result["spec_curve"]["n_specs"] >= 1
    assert "设定表" in result["spec_curve"]["markdown"]


def test_robustness_check_scm_placebo(tmp_path):
    """Test SCM placebo path when method is synthetic-control."""
    df = statspai.dgp_synth(n_units=20, n_periods=30, treated_unit=0, treatment_time=20, effect=0.5, seed=1)
    csv_path = tmp_path / "synth.csv"
    df.to_csv(csv_path, index=False)

    state: EconPaperState = {
        "session_id": "test",
        "csv_path": str(csv_path),
        "research_direction": {"method": "scm"},
        "main_specification": {
            "formula": "y ~ treated",
            "outcome": "y",
            "treatment": "treated",
            "unit": "unit",
            "time": "time",
            "treated_unit": 0,
            "treatment_time": 20,
            "cluster_levels": [],
            "heterogeneity_groups": [],
        },
    }

    result = robustness_check(state)
    assert "robustness_results" in result
    rr = result["robustness_results"]
    assert len(rr["placebos"]) >= 1
    assert rr["placebos"][0]["type"] == "placebo_time"


def test_robustness_check_missing_csv(tmp_path):
    """Test that a missing csv_path returns placeholder, no exception."""
    state: EconPaperState = {
        "session_id": "test",
        "main_specification": {"formula": "y ~ x", "cluster_levels": []},
    }
    result = robustness_check(state)
    assert "robustness_results" in result
    assert result["robustness_results"]["summary_table"] == "No main specification available"


def test_iv_robustness_does_not_run_ols_feols(tmp_path, monkeypatch):
    df = statspai.dgp_iv(n=200, effect=0.5, first_stage=0.5, seed=2)
    csv_path = tmp_path / "iv.csv"
    df.to_csv(csv_path, index=False)

    def boom(*_a, **_k):
        raise AssertionError("feols(y ~ treat) must not run on IV")

    monkeypatch.setattr(statspai, "feols", boom)

    refused = robustness_check(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "iv"},
            "main_specification": {
                "method": "iv",
                "formula": "y ~ treatment",
                "outcome": "y",
                "treatment": "treatment",
            },
        }
    )
    assert refused["robustness_results"]["reason"] == "ols_battery_on_non_ols"
    assert refused["robustness_results"]["produced_by"] == "robustness_check"

    ran = robustness_check(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "iv"},
            "main_specification": {
                "method": "iv",
                "outcome": "y",
                "treatment": "treatment",
                "endogenous": "treatment",
                "instruments": ["instrument"],
                "iv_formula": "y ~ (treatment ~ instrument)",
                "cluster_levels": [],
            },
        }
    )
    rr = ran["robustness_results"]
    assert rr.get("reason") != "ols_battery_on_non_ols" or rr.get("degraded")
    assert all(row.get("test") != "feols_clustering" for row in rr.get("diagnostics") or [])


def test_ols_empty_cluster_levels_skips_statspai_import(tmp_path, monkeypatch):
    csv_path = tmp_path / "ols.csv"
    pd.DataFrame({"y": [1, 2], "x": [0, 1]}).to_csv(csv_path, index=False)

    real_import = __import__

    def guarded(name, *args, **kwargs):
        if name == "statspai" or name.startswith("statspai."):
            raise AssertionError("empty cluster_levels must not import statspai")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded)
    out = robustness_check(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "ols"},
            "main_specification": {
                "method": "ols",
                "formula": "y ~ x",
                "treatment": "x",
                "cluster_levels": [],
                "heterogeneity_groups": [],
            },
        }
    )
    assert out["robustness_results"]["reason"] == "no_cluster_or_groups"
    assert out["robustness_results"]["produced_by"] == "robustness_check"


def _cs_state(csv_path: str, **spec_extra) -> dict:
    spec = {
        "method": "did",
        "outcome": "y",
        "first_treat_col": "first_treat",
        "time_col": "time",
        "id_col": "unit",
    }
    spec.update(spec_extra)
    return {
        "session_id": "test",
        "csv_path": str(csv_path),
        "research_direction": {"method": "did"},
        "main_specification": spec,
        "estimate": {
            "estimator": "statspai.callaway_santanna",
            "status": "ok",
            "produced_by": "estimate",
        },
    }


def test_cs_did_robustness_uses_cs_knobs_not_feols(tmp_path, monkeypatch):
    """CS 主估计只拧 control_group / notyet_cutoff，不跑 y ~ treat 的 feols。"""
    df = statspai.dgp_did(
        n_units=40, n_periods=8, effect=0.5, staggered=True, n_groups=3, seed=3
    )
    df["first_treat"] = df["first_treat"].fillna(0)
    csv_path = tmp_path / "cs_panel.csv"
    df.to_csv(csv_path, index=False)

    def boom(*_a, **_k):
        raise AssertionError("CS 主估计不得再跑 feols(y ~ treat)")

    monkeypatch.setattr(statspai, "feols", boom)

    result = robustness_check(_cs_state(csv_path))
    rr = result["robustness_results"]
    assert rr["produced_by"] == "robustness_check"
    assert rr.get("reason") != "ols_battery_on_non_ols"
    assert rr.get("reason") != "cs_battery_failed"
    assert all(row.get("type") != "clustering" for row in rr.get("robustness") or [])
    assert "spec_curve" not in result
    rows = rr["robustness"]
    assert len(rows) >= 2
    assert all(row.get("type") == "cs_variant" for row in rows)
    groups = {row.get("control_group") for row in rows}
    cutoffs = {row.get("notyet_cutoff") for row in rows}
    assert len(groups) >= 2 or len(cutoffs) >= 2
    assert "y ~ treat" in rr["summary_table"] or "OLS" in rr["summary_table"]


def test_cs_did_battery_failed_when_cols_missing(tmp_path, monkeypatch):
    """缺队列列：cs_battery_failed，不回落到 OLS 套餐。"""
    df = statspai.dgp_did(n_units=20, n_periods=6, effect=0.4, seed=4)
    csv_path = tmp_path / "cs_missing.csv"
    df.to_csv(csv_path, index=False)

    def boom(*_a, **_k):
        raise AssertionError("CS 失败路径不得跑 feols")

    monkeypatch.setattr(statspai, "feols", boom)

    result = robustness_check(
        _cs_state(csv_path, first_treat_col=None, g=None, time_col="time", id_col="unit")
    )
    rr = result["robustness_results"]
    assert rr["produced_by"] == "robustness_check"
    assert rr["reason"] == "cs_battery_failed"
    assert rr.get("diagnostics")
    assert "OLS" in rr["summary_table"] or "y ~ treat" in rr["summary_table"]
    assert all(row.get("type") != "clustering" for row in rr.get("robustness") or [])