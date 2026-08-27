"""Missing `statspai` must not 500 set_direction / identification / prewrite."""
from __future__ import annotations

import sys

import pandas as pd
from engine.prewrite import run_prewrite
from nodes.robustness_check import robustness_check
from nodes.set_direction import set_direction


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
    assert estimate.get("status") in {"ok", "error", "degraded"}
    assert estimate.get("estimator") != "statspai.feols"
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
