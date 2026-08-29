"""Missing `statspai` must not 500 set_direction / identification / prewrite."""
from __future__ import annotations

import sys

import pandas as pd
from agent.engine.prewrite import run_prewrite
from agent.nodes.estimate import estimate
from agent.nodes.robustness_check import robustness_check
from agent.nodes.set_direction import set_direction


def _block_statspai_import(monkeypatch):
    real_import = __import__

    def blocked(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "statspai" or (isinstance(name, str) and name.startswith("statspai.")):
            raise ModuleNotFoundError("No module named 'statspai'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked)
    monkeypatch.delitem(sys.modules, "statspai", raising=False)
    for key in [k for k in list(sys.modules) if k.startswith("statspai.")]:
        monkeypatch.delitem(sys.modules, key, raising=False)


def _panel_csv(tmp_path):
    path = tmp_path / "panel.csv"
    pd.DataFrame(
        {
            "y": [1.0, 1.2, 2.0, 2.4, 1.1, 1.3, 2.1, 2.5],
            "treat": [0, 0, 1, 1, 0, 0, 1, 1],
            "year": [2000, 2001, 2000, 2001, 2000, 2001, 2000, 2001],
            "id": [1, 1, 2, 2, 3, 3, 4, 4],
            "group": [0, 0, 1, 1, 0, 0, 1, 1],
        }
    ).to_csv(path, index=False)
    return path


def test_set_direction_and_prewrite_survive_missing_statspai(tmp_path, monkeypatch):
    """POST /direction write path: missing statspai returns outline, not 500."""
    csv_path = _panel_csv(tmp_path)
    _block_statspai_import(monkeypatch)

    direction = {
        "question": "treat on y",
        "dv": "y",
        "iv": "treat",
        "controls": [],
        "method": "did",
        "time_col": "year",
        "id_col": "id",
    }
    directed = set_direction(
        {"csv_path": str(csv_path), "research_direction": direction}
    )
    assert directed.get("main_specification", {}).get("method") == "did"

    state = run_prewrite(
        {"csv_path": str(csv_path), "research_direction": direction}
    )
    assert state.get("identification_failed") is not True
    assert state.get("star_rating") != 0
    assert state.get("identification_diag")
    assert any(
        item.get("reason") == "statspai_unavailable"
        for item in (state.get("degradations") or [])
    )
    estimate = state.get("estimate") or {}
    assert estimate.get("produced_by") == "estimate"
    assert estimate.get("status") == "degraded"
    assert estimate.get("estimator") == "statsmodels.ols"
    assert estimate.get("method") == "did"
    assert not (
        estimate.get("method") == "did" and estimate.get("status") == "ok"
    )
    assert estimate.get("treatment_row")
    formula = estimate.get("formula") or ""
    assert "|" not in formula
    assert "y ~ treat" in formula
    assert "FE dropped; pooled OLS" in (state.get("results") or "")
    assert any(
        item.get("reason") == "fe_dropped_pooled_ols"
        for item in (state.get("degradations") or [])
    )
    outline = state.get("outline") or []
    assert len(outline) == 6
    assert {ch.get("type") for ch in outline} >= {
        "intro",
        "lit_review",
        "data_desc",
        "methods",
        "results",
        "conclusion",
    }


def test_robustness_clustering_falls_back_when_statspai_missing(tmp_path, monkeypatch):
    csv_path = _panel_csv(tmp_path)
    _block_statspai_import(monkeypatch)

    out = robustness_check(
        {
            "csv_path": str(csv_path),
            "research_direction": {"method": "ols"},
            "main_specification": {
                "method": "ols",
                "formula": "y ~ treat",
                "treatment": "treat",
                "cluster_levels": ["id"],
                "heterogeneity_groups": ["group"],
            },
        }
    )
    rr = out["robustness_results"]
    assert rr.get("produced_by") == "robustness_check"
    assert rr.get("robustness")
    assert rr["robustness"][0]["coef"] is not None
    assert any(d.get("status") == "fallback" for d in (rr.get("diagnostics") or []))


def test_missing_statspai_persists_sm_formula_not_fe_syntax(tmp_path, monkeypatch):
    csv_path = _panel_csv(tmp_path)
    _block_statspai_import(monkeypatch)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "did",
                "formula": "y ~ treat | id + year",
                "feols_formula": "y ~ treat | id + year",
                "treatment": "treat",
                "id_col": "id",
                "time_col": "year",
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "degraded"
    assert est["status"] != "ok"
    assert est["estimator"] == "statsmodels.ols"
    assert est["method"] == "did"
    assert est["formula"] == "y ~ treat"
    assert "|" not in est["formula"]
    assert "y ~ treat | id + year" not in out["results"]
    assert "FE dropped; pooled OLS" in out["results"]
    assert any(
        item.get("reason") == "fe_dropped_pooled_ols"
        for item in (out.get("degradations") or [])
    )


def test_missing_statspai_did_is_degraded_not_successful_twfe(tmp_path, monkeypatch):
    """Captain rule: missing feols + pooled OLS is not a successful DiD table."""
    csv_path = _panel_csv(tmp_path)
    _block_statspai_import(monkeypatch)
    prior = [
        {
            "node": "identification_verify",
            "reason": "statspai_unavailable",
            "fallback": "skip_diagnostics",
            "visible": True,
        }
    ]
    out = estimate(
        {
            "csv_path": str(csv_path),
            "degradations": prior,
            "research_direction": {"method": "did", "dv": "y", "iv": "treat"},
            "main_specification": {
                "method": "did",
                "formula": "y ~ treat | id + year",
                "feols_formula": "y ~ treat | id + year",
                "treatment": "treat",
                "id_col": "id",
                "time_col": "year",
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "degraded"
    assert est["status"] != "ok"
    assert est["estimator"] == "statsmodels.ols"
    assert est["formula"] == "y ~ treat"
    assert "FE dropped; pooled OLS" in out["results"]
    reasons = [item.get("reason") for item in (out.get("degradations") or [])]
    assert "statspai_unavailable" in reasons
    assert "fe_dropped_pooled_ols" in reasons


def test_feols_runtime_error_stays_error_not_pooled_ols(tmp_path, monkeypatch):
    import types

    csv_path = _panel_csv(tmp_path)
    fake = types.ModuleType("statspai")

    def boom(*_a, **_k):
        raise ValueError("singular FE")

    fake.feols = boom
    monkeypatch.setitem(sys.modules, "statspai", fake)
    out = estimate(
        {
            "csv_path": str(csv_path),
            "main_specification": {
                "method": "ols",
                "formula": "y ~ treat | id + year",
                "treatment": "treat",
            },
        }
    )
    est = out["estimate"]
    assert est["status"] == "error"
    assert est.get("estimator") != "statsmodels.ols"
    assert est.get("treatment_row") in ("", None)
    assert "coef" not in est
