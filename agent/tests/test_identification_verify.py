"""Test identification_verify node with built-in StatsPAI datasets.

Coverage: DiD on california_prop99, IV on simulated dgp, RD on simulated dgp,
SCM on simulated dgp. Tests that node returns the expected structure
and passes/fails correctly.
"""
import pytest
import pandas as pd
from nodes.identification_verify import identification_verify
from state import EconPaperState


def test_identification_verify_missing_input():
    """Test with missing inputs returns a benign field, not a failure flag.

    未选研究方向时，节点返回良性非空字段（LangGraph 要求非空 dict），而
    不标记 identification_failed（避免全自动链路误报识别失败）。
    """
    state: EconPaperState = {}
    result = identification_verify(state)
    assert result != {}
    assert "identification_failed" not in result

    state: EconPaperState = {"research_direction": {}}
    result = identification_verify(state)
    assert result != {}
    assert "identification_failed" not in result

    state: EconPaperState = {"research_direction": {"method": "did"}, "csv_path": None}
    result = identification_verify(state)
    assert result.get("identification_failed") is True


def test_identification_verify_did_california_prop99(tmp_path):
    """Test DiD identification with built-in california_prop99 dataset."""
    statspai = pytest.importorskip("statspai")
    df = statspai.california_prop99()
    csv_path = tmp_path / "california_prop99.csv"
    df.to_csv(csv_path, index=False)

    state: EconPaperState = {
        "session_id": "test",
        "csv_path": str(csv_path),
        "research_direction": {
            "method": "did",
            "outcome_col": "packspercapita",
            "treatment_col": "treated",
            "time_col": "year",
            "id_col": "state",
        },
    }

    result = identification_verify(state)
    assert "identification_diag" in result
    assert "identification_failed" in result
    diag = result["identification_diag"]
    assert diag["strategy"] == "did"
    assert "diagnostics" in diag
    assert "passed" in diag
    assert "report" in diag
    # california_prop99 is 1 cohort + never-treated, so forbidden weight should be 0
    bacon_diag = next((d for d in diag["diagnostics"] if d["test"] == "bacon_decomposition"), None)
    assert bacon_diag is not None
    assert bacon_diag["status"] == "pass"
    assert (bacon_diag.get("forbidden_weight_share") or 0) < 0.1
    assert diag["passed"] is True
    assert result["identification_failed"] is False


def test_identification_verify_iv_dgp():
    """Test IV identification with generated dgp."""
    statspai = pytest.importorskip("statspai")
    import pandas as pd
    from pathlib import Path
    import tempfile

    df = statspai.dgp_iv(n=500, effect=0.5, first_stage=0.4, n_instruments=1, seed=1)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    try:
        state: EconPaperState = {
            "session_id": "test",
            "csv_path": csv_path,
            "research_direction": {
                "method": "iv",
                "outcome": "y",
                "endogenous": "treatment",
                "instrument": "instrument",
            },
        }
        result = identification_verify(state)
        assert "identification_diag" in result
        assert "identification_failed" in result
        diag = result["identification_diag"]
        assert any(d["test"] == "iv_diag" for d in diag["diagnostics"])
        assert any(d["test"] == "effective_f_test" for d in diag["diagnostics"])
        assert diag["passed"] is True  # F should be strong in this dgp
    finally:
        import os
        os.unlink(csv_path)


def test_identification_verify_rd_dgp():
    """Test RD identification with generated dgp."""
    statspai = pytest.importorskip("statspai")
    import tempfile

    df = statspai.dgp_rd(n=1000, effect=0.3, cutoff=0.0, seed=1)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    try:
        state: EconPaperState = {
            "session_id": "test",
            "csv_path": csv_path,
            "research_direction": {
                "method": "rd",
                "outcome": "y",
                "running_var": "x",
                "cutoff": 0.0,
            },
        }
        result = identification_verify(state)
        assert "identification_diag" in result
        diag = result["identification_diag"]
        assert any(d["test"] == "mccrary_test" for d in diag["diagnostics"])
        assert any(d["test"] == "rdrobust" for d in diag["diagnostics"])
        assert "passed" in diag
    finally:
        import os
        os.unlink(csv_path)


def test_identification_verify_scm_dgp():
    """Test SCM identification with generated dgp."""
    statspai = pytest.importorskip("statspai")
    import tempfile

    df = statspai.dgp_synth(n_units=20, n_periods=30, treated_unit=0, treatment_time=20, effect=0.5, seed=1)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name

    try:
        state: EconPaperState = {
            "session_id": "test",
            "csv_path": csv_path,
            "research_direction": {
                "method": "scm",
                "outcome": "y",
                "unit_col": "unit",
                "time_col": "time",
                "treated_unit": 0,
                "treatment_time": 20,
            },
        }
        result = identification_verify(state)
        assert "identification_diag" in result
        assert "identification_failed" in result
        diag = result["identification_diag"]
        assert any(d["test"] == "synth_time_placebo" for d in diag["diagnostics"])
    finally:
        import os
        os.unlink(csv_path)


def test_identification_verify_unknown_method():
    """OLS / 未知方法没有识别套餐：不截断，不标 0 星。"""
    import tempfile
    import pandas as pd
    df = pd.DataFrame({'x': [1, 2, 3]})
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name
    try:
        state: EconPaperState = {
            "session_id": "test",
            "csv_path": csv_path,
            "research_direction": {
                "method": "ols",
            },
        }
        result = identification_verify(state)
        assert result.get("identification_failed") is False
        assert result.get("star_rating") is None
        assert "识别诊断套餐" in result["identification_diag"]["report"]
    finally:
        import os
        os.unlink(csv_path)


def test_identification_verify_did_missing_cols_unscored():
    """DiD 缺时间/个体列：跳过诊断，不算 0 星，不截断。"""
    import tempfile
    import pandas as pd

    df = pd.DataFrame({"y": [1, 2], "treat": [0, 1]})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name
    try:
        result = identification_verify(
            {
                "csv_path": csv_path,
                "research_direction": {"method": "did", "outcome": "y", "treatment": "treat"},
            }
        )
        assert result.get("identification_failed") is False
        assert result.get("star_rating") is None
        assert result.get("star_rating") != 3
        bacon = next(
            d
            for d in result["identification_diag"]["diagnostics"]
            if d["test"] == "bacon_decomposition"
        )
        assert bacon["status"] == "skipped"
        assert bacon["status"] != "pass"
    finally:
        import os
        os.unlink(csv_path)


def _block_statspai_import(monkeypatch):
    """Force every `import statspai` to raise ModuleNotFoundError."""
    import sys

    real_import = __import__

    def blocked(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "statspai" or (isinstance(name, str) and name.startswith("statspai.")):
            raise ModuleNotFoundError("No module named 'statspai'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked)
    monkeypatch.delitem(sys.modules, "statspai", raising=False)
    for key in [k for k in list(sys.modules) if k.startswith("statspai.")]:
        monkeypatch.delitem(sys.modules, key, raising=False)


def test_identification_verify_missing_statspai_does_not_raise(tmp_path, monkeypatch):
    """`import statspai` raising ModuleNotFoundError must not 500 identification."""
    csv_path = tmp_path / "panel.csv"
    pd.DataFrame(
        {
            "y": [1.0, 1.2, 2.0, 2.4],
            "treat": [0, 0, 1, 1],
            "year": [2000, 2001, 2000, 2001],
            "id": [1, 1, 2, 2],
        }
    ).to_csv(csv_path, index=False)
    _block_statspai_import(monkeypatch)

    result = identification_verify(
        {
            "csv_path": str(csv_path),
            "research_direction": {
                "method": "did",
                "outcome": "y",
                "treatment": "treat",
                "time_col": "year",
                "id_col": "id",
            },
        }
    )
    assert result.get("identification_failed") is False
    assert result.get("star_rating") is None
    diag = result["identification_diag"]
    bacon = next(d for d in diag["diagnostics"] if d["test"] == "bacon_decomposition")
    assert bacon["status"] == "error"
    assert bacon["reason"] == "statspai_unavailable"
    assert "No module named 'statspai'" in bacon["error"]
    assert any(
        item.get("reason") == "statspai_unavailable"
        and item.get("node") == "identification_verify"
        for item in (result.get("degradations") or [])
    )
    assert "不编造" in diag["report"]
