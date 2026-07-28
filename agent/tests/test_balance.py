"""T-05 sub-step 7: panel balance check (Step class).

Seam: ``BalanceStep.run(datasets, config)`` detects attrition and
unbalanced panels, reporting:
- ``balanced``: number of entities present in ALL time periods
- ``n_periods``: number of distinct time periods observed
- ``attrition_rate``: fraction of entities that dropped out (present in
  period 1 but not the last period)

StatsPAI ``balance_panel()`` is attempted first; if unavailable or it
rejects the frame, a pandas fallback computes the same metrics.
"""
import pytest

from cleaning.balance import BalanceStep


@pytest.fixture
def csv_balanced_panel(tmp_path):
    """Balanced panel: 3 entities x 2 periods = 6 rows, no attrition."""
    p = tmp_path / "balanced.csv"
    p.write_text(
        "id,year,income\n"
        "1,2018,100\n"
        "1,2020,150\n"
        "2,2018,200\n"
        "2,2020,250\n"
        "3,2018,300\n"
        "3,2020,350\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def csv_unbalanced_panel(tmp_path):
    """Unbalanced panel: entity 3 drops out in period 2 (attrition)."""
    p = tmp_path / "unbalanced.csv"
    p.write_text(
        "id,year,income\n"
        "1,2018,100\n"
        "1,2020,150\n"
        "2,2018,200\n"
        "2,2020,250\n"
        "3,2018,300\n",
        encoding="utf-8",
    )
    return p


def _config(panel_id="id", time_col="year"):
    return {"panel_id": panel_id, "time_col": time_col}


# --------------------------------------------------------------------------- #
# Balanced panel
# --------------------------------------------------------------------------- #

def test_balanced_panel_all_entities_present(csv_balanced_panel):
    """A balanced panel reports balanced == 3, attrition_rate == 0.0."""
    ds = [{"path": str(csv_balanced_panel)}]
    result_datasets, result_report = BalanceStep().run(ds, _config())

    assert result_report["balanced"] == 3
    assert result_report["n_periods"] == 2
    assert result_report["attrition_rate"] == 0.0


# --------------------------------------------------------------------------- #
# Unbalanced panel / attrition
# --------------------------------------------------------------------------- #

def test_unbalanced_panel_detects_attrition(csv_unbalanced_panel):
    """Entity 3 dropped out -> balanced=2, attrition=1/3."""
    ds = [{"path": str(csv_unbalanced_panel)}]
    result_datasets, result_report = BalanceStep().run(ds, _config())

    assert result_report["balanced"] == 2
    assert result_report["n_periods"] == 2
    assert result_report["attrition_rate"] == pytest.approx(1 / 3)


# --------------------------------------------------------------------------- #
# Report shape
# --------------------------------------------------------------------------- #

def test_balance_report_has_required_keys(csv_balanced_panel):
    """The report dict carries balanced / n_periods / attrition_rate."""
    ds = [{"path": str(csv_balanced_panel)}]
    result_datasets, result_report = BalanceStep().run(ds, _config())

    for key in ("balanced", "n_periods", "attrition_rate"):
        assert key in result_report, f"missing key {key!r}"


# --------------------------------------------------------------------------- #
# Empty / no-path datasets
# --------------------------------------------------------------------------- #

def test_balance_empty_datasets():
    """Empty datasets list returns a zero-report."""
    result_datasets, result_report = BalanceStep().run([], _config())
    assert result_report["balanced"] == 0
    assert result_report["n_periods"] == 0
    assert result_report["attrition_rate"] == 0.0


def test_balance_missing_panel_id_returns_zero_report(csv_balanced_panel):
    """Missing panel_id in config returns a zero-report."""
    ds = [{"path": str(csv_balanced_panel)}]
    result_datasets, result_report = BalanceStep().run(
        ds, {"time_col": "year"}
    )
    assert result_report["balanced"] == 0
    assert result_report["n_periods"] == 0


# --------------------------------------------------------------------------- #
# Returns tuple (datasets, report)
# --------------------------------------------------------------------------- #

def test_balance_returns_tuple(csv_balanced_panel):
    """BalanceStep.run returns a (datasets, report) tuple."""
    ds = [{"path": str(csv_balanced_panel)}]
    result = BalanceStep().run(ds, _config())
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], dict)
