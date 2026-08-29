"""T-04 / ADR-0002 clean_data node contract tests.

Seams: the 8 cleaning steps orchestrated by the clean_data node --
1. profiling  -- variable type inference, missing rate, unique count, distribution
2. merge      -- multi-period / multi-source datasets appended by ID+year
3. missing    -- 3 strategies (drop / impute / mice), strategy read from state
4. outliers   -- IQR detection + winsorize, before/after distribution recorded
5. transform  -- variable recoding & construction
6. filter     -- sample filtering by conditions
7. balance    -- panel balance / attrition check
8. audit      -- clean.py + clean.do written to workspace

ADR-0002: clean_data now iterates a list of ``CleaningStep`` implementations
and aggregates per-step reports into ``cleaning_report.steps`` (a list of 8
StepReport dicts with name/status/started_at/duration/report). The old flat
procedural orchestration and ``_ensure_report`` / ``_all_steps`` helpers are
gone. HITL simplification (T-04): clean_data reads ``state.missing_strategy``
instead of calling LangGraph ``interrupt()``. When no strategy is provided the
missing step is *detect-only* (writes ``missing_count`` but does not modify the
data), which preserves the T-02 contract pinned by
``test_graph_clean_data_detects_missing``.
"""
import pandas as pd
import pytest

from agent.nodes.clean_data import clean_data

from conftest import make_state


# --------------------------------------------------------------------------- #
# Fixtures (local, tmp_path-isolated)
# --------------------------------------------------------------------------- #
# workspace fixture 由根 conftest.py 提供（ADR-0003 Stage C）。

@pytest.fixture
def csv_with_missing(tmp_path):
    """5-row CSV with exactly 1 missing income value (no outlier)."""
    p = tmp_path / "missing.csv"
    p.write_text(
        "income,age,city\n"
        "100,30,Beijing\n"
        "200,25,Shanghai\n"
        ",40,Guangzhou\n"  # missing income -> 1 missing cell
        "300,35,Beijing\n"
        "150,28,Shenzhen\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def csv_with_outliers(tmp_path):
    """21-row CSV with a single extreme outlier (income=1000), no missing.

    The 20 non-outlier incomes are all <= 90. After winsorize at (5, 95) the
    95th percentile is 90, so the 1000 outlier is clipped to 90 and the
    post-winsor max of income is 90 (<= 100).
    """
    incomes = [10, 20, 30, 40, 50, 60, 70, 80, 90,
               10, 20, 30, 40, 50, 60, 70, 80, 90,
               10, 20, 1000]
    ages = list(range(21))
    rows = ["income,age,city"] + [
        f"{inc},{age},city{age}" for inc, age in zip(incomes, ages)
    ]
    p = tmp_path / "outliers.csv"
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return p


@pytest.fixture
def csv_with_missing_and_outliers(tmp_path):
    """5-row CSV with both a missing value and an outlier (profiling fixture)."""
    p = tmp_path / "mixed.csv"
    p.write_text(
        "income,age,city\n"
        "100,30,Beijing\n"
        "200,25,Shanghai\n"
        ",40,Guangzhou\n"      # missing income
        "300,35,Beijing\n"
        "1000,28,Shenzhen\n",  # outlier income
        encoding="utf-8",
    )
    return p


@pytest.fixture
def two_csv_files(tmp_path):
    """Two same-schema CSVs representing 2 waves (for the merge sub-step)."""
    p1 = tmp_path / "wave1.csv"
    p1.write_text("id,year,income\n1,2018,100\n2,2018,200\n3,2018,300\n",
                  encoding="utf-8")
    p2 = tmp_path / "wave2.csv"
    p2.write_text("id,year,income\n1,2020,150\n2,2020,250\n3,2020,350\n",
                  encoding="utf-8")
    return [p1, p2]


# --------------------------------------------------------------------------- #
# ADR-0002: cleaning_report.steps structure
# --------------------------------------------------------------------------- #

def test_clean_data_report_has_eight_steps(csv_with_missing, workspace):
    """cleaning_report.steps is a list of 8 StepReport dicts."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_with_missing)}],
        workspace=workspace,
    )
    result = clean_data(state)

    assert "cleaning_report" in result
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
# Sub-step 1: profiling
# --------------------------------------------------------------------------- #

def test_clean_data_runs_profiling(csv_with_missing_and_outliers, workspace):
    """Sub-step 1: profiling returns row/col counts and per-variable info."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_with_missing_and_outliers)}],
        workspace=workspace,
    )
    result = clean_data(state)

    assert "cleaning_report" in result, f"no cleaning_report in {sorted(result)}"
    steps = result["cleaning_report"]["steps"]
    # profiling is step index 0
    assert steps[0]["name"] == "profiling"
    assert steps[0]["status"] == "success"

    profile = steps[0]["report"]["profiles"][0]
    assert profile["n_rows"] == 5, f"expected 5 rows, got {profile.get('n_rows')}"
    assert profile["n_cols"] == 3, f"expected 3 cols, got {profile.get('n_cols')}"
    assert "variables" in profile

    vars_ = profile["variables"]
    assert "income" in vars_
    income_var = vars_["income"]
    assert "dtype" in income_var
    assert "missing_rate" in income_var
    assert "n_unique" in income_var
    assert "is_numeric" in income_var
    assert income_var["is_numeric"] is True
    # 1 of 5 income cells is missing -> 0.2
    assert income_var["missing_rate"] == pytest.approx(0.2)
    assert income_var["n_unique"] == 4  # [100,200,300,1000] (NaN excluded)


# --------------------------------------------------------------------------- #
# Sub-step 2: merge
# --------------------------------------------------------------------------- #

def test_clean_data_merge_multiple_datasets(two_csv_files, workspace):
    """Sub-step 2: multiple datasets are appended into a single dataset."""
    state = make_state(
        uploaded_datasets=[
            {"path": str(two_csv_files[0])},
            {"path": str(two_csv_files[1])},
        ],
        workspace=workspace,
    )
    result = clean_data(state)

    datasets = result["uploaded_datasets"]
    assert len(datasets) == 1, (
        f"merge should collapse to 1 dataset, got {len(datasets)}"
    )
    merged = pd.read_csv(datasets[0]["path"])
    assert len(merged) == 6, (
        f"expected 6 rows after appending 2 waves of 3, got {len(merged)}"
    )


# --------------------------------------------------------------------------- #
# Sub-step 3: missing value handling
# --------------------------------------------------------------------------- #

def test_clean_data_drop_strategy_reduces_missing(csv_with_missing, workspace):
    """Sub-step 3: 'drop' removes rows with missing values."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_with_missing)}],
        missing_strategy="drop",
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    assert ds["missing_count"] == 0, (
        f"drop should leave 0 missing cells, got {ds.get('missing_count')}"
    )
    assert ds["rows"] == 4, f"1 of 5 rows dropped, expected 4 rows, got {ds.get('rows')}"


def test_clean_data_impute_strategy_fills_missing(csv_with_missing, workspace):
    """Sub-step 3: 'impute' fills missing numeric cells with the median."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_with_missing)}],
        missing_strategy="impute",
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    assert ds["missing_count"] == 0, (
        f"impute should leave 0 missing cells, got {ds.get('missing_count')}"
    )
    assert ds["rows"] == 5, f"impute keeps all rows, expected 5, got {ds.get('rows')}"
    # the missing income cell is now filled (median of [100,200,300,150] = 175)
    df = pd.read_csv(ds["path"])
    assert df["income"].isna().sum() == 0


# --------------------------------------------------------------------------- #
# Sub-step 4: outliers
# --------------------------------------------------------------------------- #

def test_clean_data_winsorize_handles_outliers(csv_with_outliers, workspace):
    """Sub-step 4: winsorize clips the extreme outlier and records before/after."""
    state = make_state(
        uploaded_datasets=[{"path": str(csv_with_outliers)}],
        workspace=workspace,
    )
    result = clean_data(state)

    ds = result["uploaded_datasets"][0]
    assert "outliers" in ds, "clean_data did not write an outliers report"

    df = pd.read_csv(ds["path"])
    new_max = float(df["income"].max())
    # behavioral truth: the 1000 outlier must be clipped into the normal range
    assert new_max < 1000, f"winsorize did not clip the 1000 outlier, max={new_max}"
    assert new_max <= 100, (
        f"winsorize should reduce outlier into normal range (<=100), got {new_max}"
    )

    # before/after distribution recorded for the UI comparison
    report = ds["outliers"]
    assert "before" in report and "after" in report
    assert report["before"]["income"]["max"] == 1000
    assert report["after"]["income"]["max"] <= 100
