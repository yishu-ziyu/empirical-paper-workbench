"""T-05 sub-step 8: audit trail script generation (Step class).

Seam: ``AuditStep.run(datasets, config)`` reads ``config["steps"]``
(a list of StepReport dicts produced by prior steps) and generates a
Python script (``clean.py``) plus a Stata ``.do`` script (``clean.do``)
recording each successful cleaning step. Both scripts are written into
the workspace root.

workspace fixture 由根 conftest.py 提供（ADR-0003 Stage C）。
"""
from pathlib import Path

import pytest

from cleaning.audit import AuditStep


@pytest.fixture
def csv_dataset(tmp_path):
    """A simple dataset for the audit to reference."""
    p = tmp_path / "data.csv"
    p.write_text("id,year,income\n1,2018,100\n2,2020,200\n", encoding="utf-8")
    return p


def _config(workspace, step_names):
    """Build an AuditStep config with the given successful step names."""
    step_reports = [
        {"name": name, "status": "success", "report": {}}
        for name in step_names
    ]
    # Include a failed step to ensure it is filtered out.
    step_reports.append(
        {"name": "skipped_step", "status": "failed", "report": {"error": "x"}}
    )
    return {"workspace": workspace, "steps": step_reports}


# --------------------------------------------------------------------------- #
# File generation
# --------------------------------------------------------------------------- #

def test_generates_python_script(workspace, csv_dataset):
    """AuditStep writes clean.py into the workspace root."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["profiling", "merge", "missing", "outliers"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(workspace, step_names)
    )

    clean_py = Path(result_report["clean_py"])
    assert clean_py.exists(), f"missing {clean_py}"
    assert clean_py.name == "clean.py"
    assert clean_py.parent == Path(workspace)


def test_generates_stata_script(workspace, csv_dataset):
    """AuditStep writes clean.do into the workspace root."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["transform", "filter", "balance"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(workspace, step_names)
    )

    clean_do = Path(result_report["clean_do"])
    assert clean_do.exists(), f"missing {clean_do}"
    assert clean_do.name == "clean.do"


# --------------------------------------------------------------------------- #
# Script content
# --------------------------------------------------------------------------- #

def test_python_script_contains_successful_steps_only(workspace, csv_dataset):
    """The Python script records each successful step name (no failed ones)."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["profiling", "transform", "filter"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(workspace, step_names)
    )

    content = Path(result_report["clean_py"]).read_text(encoding="utf-8")
    for step in step_names:
        assert step in content, f"step {step!r} not found in Python script"
    # The failed 'skipped_step' should NOT appear.
    assert "skipped_step" not in content


def test_stata_script_contains_successful_steps_only(workspace, csv_dataset):
    """The Stata .do script records each successful step name."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["merge", "missing", "outliers"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(workspace, step_names)
    )

    content = Path(result_report["clean_do"]).read_text(encoding="utf-8")
    for step in step_names:
        assert step in content, f"step {step!r} not found in Stata script"
    assert "skipped_step" not in content


# --------------------------------------------------------------------------- #
# Return shape
# --------------------------------------------------------------------------- #

def test_returns_clean_py_and_clean_do_keys(workspace, csv_dataset):
    """The report dict carries clean_py and clean_do paths."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["profiling"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(workspace, step_names)
    )

    for key in ("clean_py", "clean_do"):
        assert key in result_report, f"missing key {key!r} in {sorted(result_report)}"


def test_returns_tuple(workspace, csv_dataset):
    """AuditStep.run returns a (datasets, report) tuple."""
    ds = [{"path": str(csv_dataset)}]
    step_names = ["profiling"]
    result = AuditStep().run(ds, _config(workspace, step_names))
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], dict)


# --------------------------------------------------------------------------- #
# Workspace directory creation
# --------------------------------------------------------------------------- #

def test_creates_workspace_if_missing(tmp_path, csv_dataset):
    """AuditStep creates the workspace root if it does not exist."""
    fresh = tmp_path / "fresh_workspace"
    ds = [{"path": str(csv_dataset)}]
    step_names = ["profiling"]
    result_datasets, result_report = AuditStep().run(
        ds, _config(str(fresh), step_names)
    )

    assert Path(result_report["clean_py"]).exists()
    assert Path(result_report["clean_do"]).exists()
