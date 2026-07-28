"""T-05 sub-step 6: sample filtering (Step class).

Seam: ``FilterStep.run(datasets, config)`` filters rows by a list of
conditions, records before/after sample counts, and writes the filtered
frame to a sidecar ``<order>_filter_<i>.csv``.

Condition shape: ``{"col": str, "op": str, "val": Any}`` where op is one of
``>=``, ``<=``, ``>``, ``<``, ``==``, ``!=``. Multiple conditions are ANDed.
"""
from pathlib import Path

import pandas as pd
import pytest

from cleaning.filter import FilterStep


@pytest.fixture
def csv_demographics(tmp_path):
    """5-row CSV with age/year/treated columns for filtering tests."""
    p = tmp_path / "demo.csv"
    p.write_text(
        "id,age,year,income,treated\n"
        "1,30,2018,100,1\n"
        "2,45,2019,200,0\n"
        "3,60,2020,300,1\n"
        "4,25,2021,150,0\n"
        "5,55,2022,250,1\n",
        encoding="utf-8",
    )
    return p


def _config(tmp_path, conditions):
    return {
        "workspace": str(tmp_path),
        "order": 5,
        "conditions": conditions,
    }


# --------------------------------------------------------------------------- #
# Single condition
# --------------------------------------------------------------------------- #

def test_filter_age_ge(csv_demographics, tmp_path):
    """age >= 50 keeps rows 3 and 5 (2 of 5)."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "age", "op": ">=", "val": 50}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 2
    assert (df["age"] >= 50).all()


def test_filter_year_eq(csv_demographics, tmp_path):
    """year == 2020 keeps exactly 1 row."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "year", "op": "==", "val": 2020}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 1
    assert df["year"].iloc[0] == 2020


def test_filter_treated_eq(csv_demographics, tmp_path):
    """treated == 1 keeps 3 rows."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "treated", "op": "==", "val": 1}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 3
    assert (df["treated"] == 1).all()


# --------------------------------------------------------------------------- #
# Multiple conditions (AND)
# --------------------------------------------------------------------------- #

def test_filter_multiple_conditions_anded(csv_demographics, tmp_path):
    """age >= 30 AND treated == 1 keeps rows 1, 3, 5."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [
        {"col": "age", "op": ">=", "val": 30},
        {"col": "treated", "op": "==", "val": 1},
    ]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 3
    assert (df["age"] >= 30).all()
    assert (df["treated"] == 1).all()


# --------------------------------------------------------------------------- #
# Before/after sample counts recorded in report
# --------------------------------------------------------------------------- #

def test_filter_report_records_before_after(csv_demographics, tmp_path):
    """FilterStep report has n_before / n_after / conditions."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "age", "op": ">=", "val": 50}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    assert result_report["n_before"] == [5]
    assert result_report["n_after"] == [2]
    assert result_report["conditions"] == conditions

    filter_report = result_datasets[0].get("filter")
    assert filter_report is not None
    assert filter_report["n_before"] == 5
    assert filter_report["n_after"] == 2
    assert filter_report["conditions"] == conditions


# --------------------------------------------------------------------------- #
# Operators
# --------------------------------------------------------------------------- #

def test_filter_less_than(csv_demographics, tmp_path):
    """age < 30 keeps row 4 (age=25)."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "age", "op": "<", "val": 30}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 1
    assert df["age"].iloc[0] == 25


def test_filter_not_equal(csv_demographics, tmp_path):
    """treated != 1 keeps 2 rows (treated=0)."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "treated", "op": "!=", "val": 1}]
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, conditions)
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == 2
    assert (df["treated"] == 0).all()


# --------------------------------------------------------------------------- #
# Empty conditions = sidecar still written with all rows
# --------------------------------------------------------------------------- #

def test_filter_empty_conditions_writes_sidecar(csv_demographics, tmp_path):
    """empty conditions list writes a sidecar with all rows preserved."""
    ds = [{"path": str(csv_demographics)}]
    before = pd.read_csv(csv_demographics)
    result_datasets, result_report = FilterStep().run(
        ds, _config(tmp_path, [])
    )

    df = pd.read_csv(result_datasets[0]["path"])
    assert len(df) == len(before)
    assert Path(result_datasets[0]["step_paths"][-1]).exists()


# --------------------------------------------------------------------------- #
# Sidecar path + step_paths append
# --------------------------------------------------------------------------- #

def test_filter_sidecar_path_appended(csv_demographics, tmp_path):
    """ds['step_paths'] receives the sidecar path."""
    ds = [{"path": str(csv_demographics)}]
    conditions = [{"col": "age", "op": ">=", "val": 50}]
    result_datasets, _ = FilterStep().run(ds, _config(tmp_path, conditions))

    sidecar = result_datasets[0]["step_paths"][-1]
    assert sidecar.endswith("05_filter_0.csv")
    assert Path(sidecar).exists()
    assert result_datasets[0]["path"] == sidecar
