"""T-05 / ADR-0002: clean_data node runs all 8 sub-steps via Step orchestration.

Seam: ``clean_data(state)`` iterates a list of ``CleaningStep`` implementations
(profiling / merge / missing / outliers / transform / filter / balance / audit).
Each step is wrapped in a unified try/except; failures are recorded as
``status="failed"`` + ``report.error`` in ``cleaning_report.steps`` without
blocking the rest of the pipeline. The function signature is unchanged
(``state -> dict``).

workspace fixture 由根 conftest.py 提供（ADR-0003 Stage C）。
"""
import pandas as pd
import pytest

from agent.nodes.clean_data import clean_data

from conftest import make_state


@pytest.fixture
def csv_full(tmp_path):
    """A panel CSV suitable for all 8 sub-steps."""
    p = tmp_path / "full.csv"
    p.write_text(
        "id,year,income,age,city,treated,post\n"
        "1,2018,100,30,Beijing,1,0\n"
        "1,2020,150,32,Beijing,1,1\n"
        "2,2018,200,45,Shanghai,0,0\n"
        "2,2020,250,47,Shanghai,0,1\n"
        "3,2018,300,60,Guangzhou,1,0\n"
        "3,2020,350,62,Guangzhou,1,1\n",
        encoding="utf-8",
    )
    return p


# --------------------------------------------------------------------------- #
# Report structure (ADR-0002): cleaning_report.steps is a list of 8 StepReports
# --------------------------------------------------------------------------- #

def test_clean_data_report_has_eight_steps(csv_full, workspace):
    """cleaning_report.steps is a list of 8, each with the required keys."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        workspace=workspace,
    )
    result = clean_data(state)

    steps = result["cleaning_report"]["steps"]
    assert isinstance(steps, list)
    assert len(steps) == 8
    expected_names = [
        "profiling", "merge", "missing", "outliers",
        "transform", "filter", "balance", "audit",
    ]
    assert [s["name"] for s in steps] == expected_names
    for s in steps:
        assert set(s.keys()) >= {"name", "status", "started_at", "duration", "report"}
        assert s["status"] in ("success", "failed")


# --------------------------------------------------------------------------- #
# Sub-step 5: transform (via state.transform_config)
# --------------------------------------------------------------------------- #

def test_clean_data_runs_transform(csv_full, workspace):
    """Sub-step 5: clean_data applies transform_config from state."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        transform_config={
            "log_transform": ["income"],
            "policy_dummies": {"treat_post": {"treat": "treated", "post": "post"}},
        },
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    df = pd.read_csv(ds["path"])
    assert "income_log" in df.columns
    assert "treat_post" in df.columns
    assert "constructed_vars" in ds

    # transform is step index 4
    transform_report = result["cleaning_report"]["steps"][4]
    assert transform_report["name"] == "transform"
    assert transform_report["status"] == "success"
    assert "income_log" in transform_report["report"]["constructed_vars"]


# --------------------------------------------------------------------------- #
# Sub-step 6: filter (via state.filter_conditions)
# --------------------------------------------------------------------------- #

def test_clean_data_runs_filter(csv_full, workspace):
    """Sub-step 6: clean_data applies filter_conditions from state."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        filter_conditions=[{"col": "age", "op": ">=", "val": 40}],
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    df = pd.read_csv(ds["path"])
    # age >= 40 keeps rows 2,3,4,5 (ages 45,47,60,62) -> 4 rows
    assert len(df) == 4
    assert (df["age"] >= 40).all()
    assert ds["filter"]["n_before"] == 6
    assert ds["filter"]["n_after"] == 4

    # filter is step index 5
    filter_report = result["cleaning_report"]["steps"][5]
    assert filter_report["name"] == "filter"
    assert filter_report["status"] == "success"


# --------------------------------------------------------------------------- #
# Sub-step 7: balance (via state.panel_id + state.time_col)
# --------------------------------------------------------------------------- #

def test_clean_data_runs_balance(csv_full, workspace):
    """Sub-step 7: clean_data writes a balance report when panel_id is set."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        panel_id="id",
        time_col="year",
        workspace=workspace,
    )
    result = clean_data(state)

    # balance is step index 6
    balance_report = result["cleaning_report"]["steps"][6]
    assert balance_report["name"] == "balance"
    assert balance_report["status"] == "success"
    balance = balance_report["report"]
    assert balance["balanced"] == 3
    assert balance["attrition_rate"] == 0.0


# --------------------------------------------------------------------------- #
# Sub-step 8: audit (via state.workspace)
# --------------------------------------------------------------------------- #

def test_clean_data_runs_audit(csv_full, workspace):
    """Sub-step 8: clean_data writes clean.py + clean.do when workspace is set."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        workspace=workspace,
    )
    result = clean_data(state)

    # audit is step index 7
    audit_report = result["cleaning_report"]["steps"][7]
    assert audit_report["name"] == "audit"
    assert audit_report["status"] == "success"
    audit = audit_report["report"]
    assert "clean_py" in audit
    assert "clean_do" in audit
    from pathlib import Path
    assert Path(audit["clean_py"]).exists()
    assert Path(audit["clean_do"]).exists()


# --------------------------------------------------------------------------- #
# All 8 sub-steps run together
# --------------------------------------------------------------------------- #

def test_clean_data_runs_all_eight_substeps(csv_full, workspace):
    """All 8 sub-steps execute in one clean_data call without error."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        transform_config={"log_transform": ["income"]},
        filter_conditions=[{"col": "age", "op": ">=", "val": 30}],
        panel_id="id",
        time_col="year",
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    df = pd.read_csv(ds["path"])

    # Sub-step 5: transform applied
    assert "income_log" in df.columns
    # Sub-step 6: filter applied (all rows now have age >= 30, original 6 rows all pass)
    assert (df["age"] >= 30).all()
    assert ds["filter"]["n_before"] == 6
    # Sub-step 7: balance report present
    steps = result["cleaning_report"]["steps"]
    assert steps[6]["name"] == "balance"
    assert steps[6]["status"] == "success"
    # Sub-step 8: audit scripts written
    assert steps[7]["name"] == "audit"
    assert steps[7]["status"] == "success"


def test_clean_data_promotes_cleaned_path_for_downstream_nodes(csv_full, workspace):
    """Downstream analysis reads the final cleaned sidecar, not the raw upload."""
    result = clean_data(
        make_state(
            csv_path=str(csv_full),
            uploaded_datasets=[{"path": str(csv_full)}],
            filter_conditions=[{"col": "age", "op": ">=", "val": 40}],
            workspace=workspace,
        )
    )

    cleaned_path = result["cleaned_datasets"][0]["path"]
    assert cleaned_path != str(csv_full)
    assert result["csv_path"] == cleaned_path
    assert len(pd.read_csv(result["csv_path"])) == 4


def test_clean_data_does_not_winsorize_design_columns(tmp_path, workspace):
    """Identifiers and binary treatment columns must survive outlier cleaning."""
    raw_path = tmp_path / "agent.design.csv"
    original = pd.DataFrame(
        {
            "id": [*range(1, 21), 999],
            "year": [2020] * 21,
            "treat": [0] * 20 + [1],
            "income": [*range(10, 210, 10), 1000],
        }
    )
    original.to_csv(raw_path, index=False)

    result = clean_data(
        make_state(
            csv_path=str(raw_path),
            uploaded_datasets=[{"path": str(raw_path)}],
            research_direction={
                "method": "did",
                "id_col": "id",
                "time_col": "year",
                "iv": "treat",
            },
            workspace=workspace,
        )
    )
    cleaned = pd.read_csv(result["csv_path"])

    assert cleaned["id"].tolist() == original["id"].tolist()
    assert cleaned["treat"].tolist() == original["treat"].tolist()
    assert cleaned["income"].max() < original["income"].max()


# --------------------------------------------------------------------------- #
# Sub-step failure isolation (ADR-0002 unified try/except)
# --------------------------------------------------------------------------- #

def test_clean_data_substep_failure_does_not_block(csv_full, workspace):
    """A failing sub-step (bad transform config) does not block the rest."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        transform_config="not-a-dict",  # will raise inside _step_config
        workspace=workspace,
    )
    # Should not raise; audit should still run.
    result = clean_data(state)

    steps = result["cleaning_report"]["steps"]
    # transform (index 4) failed
    assert steps[4]["name"] == "transform"
    assert steps[4]["status"] == "failed"
    assert "error" in steps[4]["report"]
    # audit (index 7) still succeeded
    assert steps[7]["name"] == "audit"
    assert steps[7]["status"] == "success"


# --------------------------------------------------------------------------- #
# Backward compatibility: no new state keys = all 8 steps still run
# (ADR-0002: orchestrator always runs all steps; absent config => step is
#  a no-op or uses defaults, not skipped)
# --------------------------------------------------------------------------- #

def test_clean_data_backward_compatible_no_new_keys(csv_full, workspace):
    """Without the optional state keys, clean_data still produces 8 step reports."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_full)}],
        workspace=workspace,
    )
    result = clean_data(state)

    assert "cleaning_report" in result
    steps = result["cleaning_report"]["steps"]
    assert len(steps) == 8
    # balance / audit are not top-level keys anymore (they're in steps[6] / steps[7])
    assert "balance" not in result["cleaning_report"]
    assert "audit" not in result["cleaning_report"]
