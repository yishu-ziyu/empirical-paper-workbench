"""clean_winsor: pywinsor2, cuts=(1, 99), continuous only, auditable.

Not Stata winsor2's default call (implicit cuts, replace=False, _w suffix).
"""
import logging
import sys
from unittest.mock import MagicMock, patch

import pandas as pd

from agent.cleaning.outliers import OutliersStep
from agent.cleaning.winsor import WINSOR_CUTS, clean_winsor


def _continuous_frame(n_bulk: int = 200) -> pd.DataFrame:
    bulk = (list(range(10, 110)) * ((n_bulk // 100) + 1))[:n_bulk]
    return pd.DataFrame(
        {
            "income": bulk + [10_000],
            "treat": [0] * (n_bulk // 2) + [1] * (n_bulk - n_bulk // 2) + [1],
            "city": ["A"] * n_bulk + ["B"],
            "id": list(range(1, n_bulk + 2)),
        }
    )


def test_default_cuts_are_one_ninety_nine():
    assert WINSOR_CUTS == (1, 99)


def test_clean_winsor_clips_continuous_at_1_99():
    df = _continuous_frame()
    out, audit = clean_winsor(df)

    assert audit["cuts"] == [1, 99]
    assert audit["stata_default"] is False
    assert audit["replace"] is True
    assert audit["engine"] == "pywinsor2"
    assert "income" in audit["columns"]
    assert out["income"].max() < df["income"].max()
    assert out["income"].max() <= 110
    assert audit["n_changed"]["income"] >= 1
    assert not any(str(col).endswith("_w") for col in out.columns)


def test_clean_winsor_skips_binary_and_non_numeric():
    df = _continuous_frame()
    out, audit = clean_winsor(df)

    assert audit["skipped"]["treat"] == "not_continuous"
    assert audit["skipped"]["city"] == "non_numeric"
    assert out["treat"].tolist() == df["treat"].tolist()
    assert out["city"].tolist() == df["city"].tolist()


def test_clean_winsor_skips_protected_columns():
    df = _continuous_frame()
    original_id = df["id"].tolist()
    out, audit = clean_winsor(df, protected_columns=["id"])

    assert audit["skipped"]["id"] == "protected"
    assert "id" not in audit["columns"]
    assert out["id"].tolist() == original_id
    assert "income" in audit["columns"]


def test_clean_winsor_passes_explicit_cuts_and_replace_not_stata_default():
    df = _continuous_frame()
    calls: list[dict] = []

    import pywinsor2

    real = pywinsor2.winsor2

    def wrapped(data, varlist, *args, **kwargs):
        calls.append({"varlist": varlist, "args": args, "kwargs": dict(kwargs)})
        return real(data, varlist, *args, **kwargs)

    with patch("pywinsor2.winsor2", wrapped):
        out, audit = clean_winsor(df)

    assert calls, "pywinsor2.winsor2 must be called"
    kwargs = calls[0]["kwargs"]
    assert kwargs["cuts"] == (1, 99)
    assert kwargs["replace"] is True
    assert kwargs.get("trim") is False
    assert audit["stata_default"] is False
    assert "cuts" in kwargs  # never the implicit Stata/library default
    assert not any(str(col).endswith("_w") for col in out.columns)


def test_clean_winsor_falls_back_when_pywinsor2_missing(caplog):
    df = _continuous_frame()
    with (
        patch.dict(sys.modules, {"pywinsor2": None}),
        caplog.at_level(logging.WARNING, logger="agent.cleaning.winsor"),
    ):
        out, audit = clean_winsor(df)

    assert audit["engine"] == "pandas"
    assert audit["cuts"] == [1, 99]
    assert out["income"].max() < df["income"].max()
    assert any("pywinsor2 not available" in r.message for r in caplog.records)


def test_clean_winsor_falls_back_when_pywinsor2_raises(caplog):
    df = _continuous_frame()
    mock_mod = MagicMock()
    mock_mod.winsor2.side_effect = Exception("simulated pywinsor2 failure")
    with (
        patch.dict(sys.modules, {"pywinsor2": mock_mod}),
        caplog.at_level(logging.WARNING, logger="agent.cleaning.winsor"),
    ):
        out, audit = clean_winsor(df)

    assert audit["engine"] == "pandas"
    assert out["income"].max() < df["income"].max()
    assert any("pywinsor2.winsor2 failed" in r.message for r in caplog.records)


def test_outliers_step_audit_is_explicit_1_99(tmp_path):
    df = _continuous_frame()
    path = tmp_path / "panel.csv"
    df.to_csv(path, index=False)
    datasets, report = OutliersStep().run(
        [{"path": str(path)}],
        {"workspace": str(tmp_path), "order": 3, "protected_columns": ["id"]},
    )

    assert report["stata_default"] is False
    assert report["cuts"] == [1, 99]
    assert report["stats_pai_used"] is False
    assert report["replace"] is True
    assert report["engine"][0] == "pywinsor2"
    assert "income" in report["columns"][0]
    assert "treat" not in report["columns"][0]
    assert "id" not in report["columns"][0]

    row = datasets[0]["outliers"]
    assert row["cuts"] == [1, 99]
    assert row["stata_default"] is False
    assert row["engine"] == "pywinsor2"
    assert row["before"]["income"]["max"] == 10_000
    assert row["after"]["income"]["max"] < 10_000

    cleaned = pd.read_csv(datasets[0]["path"])
    assert cleaned["id"].tolist() == df["id"].tolist()
    assert cleaned["treat"].tolist() == df["treat"].tolist()
    assert not any(str(col).endswith("_w") for col in cleaned.columns)
