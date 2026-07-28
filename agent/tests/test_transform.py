"""T-05 sub-step 5: variable recoding & construction (Step class).

Seams: the ``TransformStep`` class applies, in order:
- one-hot / label encoding for categorical columns
- equal-frequency / equal-width binning for continuous columns
- log transform on positive numeric columns
- interaction terms (product of two columns)
- policy dummy (DiD treat x post)

Each operation writes new column(s) to a sidecar CSV
``<order>_transform_<i>.csv`` and records the constructed variable names in
``ds["constructed_vars"]`` (and appends to ``ds["step_paths"]``).
"""
import math
from pathlib import Path

import pandas as pd
import pytest

from cleaning.transform import TransformStep


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def csv_categorical(tmp_path):
    """CSV with a categorical city column (3 unique values)."""
    p = tmp_path / "categorical.csv"
    p.write_text(
        "income,age,city\n"
        "100,30,Beijing\n"
        "200,25,Shanghai\n"
        "300,40,Guangzhou\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def csv_positive(tmp_path):
    """CSV with a positive income column suitable for log transform."""
    p = tmp_path / "positive.csv"
    p.write_text(
        "income,age\n100,30\n200,25\n300,40\n400,35\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def csv_panel(tmp_path):
    """CSV with treat/post columns for DiD dummy construction."""
    p = tmp_path / "panel.csv"
    p.write_text(
        "id,year,income,treated,post\n"
        "1,2018,100,1,0\n"
        "1,2020,150,1,1\n"
        "2,2018,200,0,0\n"
        "2,2020,250,0,1\n",
        encoding="utf-8",
    )
    return p


def _config(tmp_path, **kwargs):
    base = {"workspace": str(tmp_path), "order": 4}
    base.update(kwargs)
    return base


# --------------------------------------------------------------------------- #
# One-hot encoding
# --------------------------------------------------------------------------- #

def test_onehot_encoding_creates_dummy_columns(csv_categorical, tmp_path):
    """one-hot on city creates one column per category."""
    ds = [{"path": str(csv_categorical)}]
    config = _config(tmp_path, encodings={"city": "onehot"})
    result_datasets, result_report = TransformStep().run(ds, config)

    assert isinstance(result_report, dict)
    df = pd.read_csv(result_datasets[0]["path"])
    assert "city_Beijing" in df.columns
    assert "city_Shanghai" in df.columns
    assert "city_Guangzhou" in df.columns
    dummies = df[["city_Beijing", "city_Shanghai", "city_Guangzhou"]]
    assert (dummies.sum(axis=1) == 1).all()

    sidecar = result_datasets[0]["step_paths"][-1]
    assert Path(sidecar).exists()
    assert "04_transform_0" in sidecar


# --------------------------------------------------------------------------- #
# Label encoding
# --------------------------------------------------------------------------- #

def test_label_encoding_creates_integer_column(csv_categorical, tmp_path):
    """label encoding replaces city with integer codes (city_label)."""
    ds = [{"path": str(csv_categorical)}]
    config = _config(tmp_path, encodings={"city": "label"})
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "city_label" in df.columns
    assert df["city_label"].nunique() == 3
    assert df["city_label"].dtype.kind in "iu"


# --------------------------------------------------------------------------- #
# Equal-frequency binning
# --------------------------------------------------------------------------- #

def test_equal_freq_binning(csv_positive, tmp_path):
    """equal_freq binning produces n bins with roughly equal counts."""
    ds = [{"path": str(csv_positive)}]
    config = _config(tmp_path, bins={"income": {"method": "equal_freq", "n": 2}})
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "income_bin" in df.columns
    counts = df["income_bin"].value_counts().sort_index()
    assert len(counts) == 2
    assert counts.min() == 2


# --------------------------------------------------------------------------- #
# Equal-width binning
# --------------------------------------------------------------------------- #

def test_equal_width_binning(csv_positive, tmp_path):
    """equal_width binning produces n bins spanning the value range."""
    ds = [{"path": str(csv_positive)}]
    config = _config(tmp_path, bins={"income": {"method": "equal_width", "n": 4}})
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "income_bin" in df.columns
    assert df["income_bin"].nunique() <= 4


# --------------------------------------------------------------------------- #
# Log transform
# --------------------------------------------------------------------------- #

def test_log_transform_creates_log_column(csv_positive, tmp_path):
    """log_transform produces a log1p column of the original."""
    ds = [{"path": str(csv_positive)}]
    config = _config(tmp_path, log_transform=["income"])
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "income_log" in df.columns
    assert df["income_log"].iloc[0] == pytest.approx(math.log(101))


# --------------------------------------------------------------------------- #
# Interaction term
# --------------------------------------------------------------------------- #

def test_interaction_term_creates_product_column(csv_positive, tmp_path):
    """interaction [income, age] creates income_x_age = income * age."""
    ds = [{"path": str(csv_positive)}]
    config = _config(tmp_path, interactions=[["income", "age"]])
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "income_x_age" in df.columns
    assert df["income_x_age"].iloc[0] == 3000


# --------------------------------------------------------------------------- #
# Policy dummy (DiD treat x post)
# --------------------------------------------------------------------------- #

def test_policy_dummy_creates_treat_post(csv_panel, tmp_path):
    """policy_dummies produces a treat_post = treated * post column."""
    ds = [{"path": str(csv_panel)}]
    config = _config(
        tmp_path,
        policy_dummies={"treat_post": {"treat": "treated", "post": "post"}},
    )
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert "treat_post" in df.columns
    treated_post = df[df["treat_post"] == 1]
    assert len(treated_post) == 1
    assert treated_post.iloc[0]["id"] == 1


# --------------------------------------------------------------------------- #
# Constructed vars recorded
# --------------------------------------------------------------------------- #

def test_constructed_vars_recorded(csv_positive, tmp_path):
    """transform records constructed var names in report + ds meta."""
    ds = [{"path": str(csv_positive)}]
    config = _config(
        tmp_path,
        log_transform=["income"],
        interactions=[["income", "age"]],
    )
    result_datasets, result_report = TransformStep().run(ds, config)

    assert "constructed_vars" in result_report
    assert "income_log" in result_report["constructed_vars"]
    assert "income_x_age" in result_report["constructed_vars"]

    constructed = result_datasets[0].get("constructed_vars", [])
    assert "income_log" in constructed
    assert "income_x_age" in constructed


# --------------------------------------------------------------------------- #
# Empty config is a no-op (but still writes a sidecar)
# --------------------------------------------------------------------------- #

def test_empty_config_writes_sidecar(csv_positive, tmp_path):
    """empty config still produces a sidecar with the unchanged frame."""
    ds = [{"path": str(csv_positive)}]
    before = pd.read_csv(csv_positive)
    config = _config(tmp_path)
    result_datasets, result_report = TransformStep().run(ds, config)

    df = pd.read_csv(result_datasets[0]["path"])
    assert list(df.columns) == list(before.columns)
    assert len(result_datasets[0]["step_paths"]) == 1
    assert Path(result_datasets[0]["step_paths"][0]).exists()


# --------------------------------------------------------------------------- #
# Sidecar path + step_paths append
# --------------------------------------------------------------------------- #

def test_sidecar_path_appended_to_step_paths(csv_positive, tmp_path):
    """ds['step_paths'] receives the sidecar path."""
    ds = [{"path": str(csv_positive)}]
    config = _config(tmp_path, log_transform=["income"])
    result_datasets, _ = TransformStep().run(ds, config)

    sidecar = result_datasets[0]["step_paths"][-1]
    assert sidecar.endswith("04_transform_0.csv")
    assert Path(sidecar).exists()
    assert result_datasets[0]["path"] == sidecar
