"""T-11 + refactor: ProfilingStep integration with CHARLS detection.

Verifies that ``ProfilingStep().run(datasets, config)`` returns a report
with ``profiles`` (list, one entry per dataset) where each profile carries
``dataset_type`` and, when CHARLS is detected, a ``charls_config`` field —
WITHOUT breaking the existing per-profile contract (n_rows / n_cols /
variables).

charls_csv / generic_csv fixture 由根 conftest.py 提供（ADR-0003 Stage C）。
"""
from __future__ import annotations

import pytest


# ---------- backward-compat: existing profiling contract on each profile --

def test_profiling_step_returns_existing_fields_on_generic_csv(generic_csv):
    """T-04 contract: n_rows / n_cols / variables still present per profile."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(generic_csv)}]
    result_datasets, result_report = ProfilingStep().run(ds, {})
    profile = result_report["profiles"][0]

    assert "n_rows" in profile
    assert "n_cols" in profile
    assert "variables" in profile
    assert profile["n_rows"] == 3
    assert profile["n_cols"] == 3


def test_profiling_step_returns_empty_profile_when_no_path():
    """T-04 contract: missing path -> empty profile dict in the list."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{}]
    result_datasets, result_report = ProfilingStep().run(ds, {})
    assert result_report["profiles"] == [{}]
    assert result_report["merged_profile"] is None


# ---------- new: dataset_type + charls_config fields -----------------------

def test_profiling_step_detects_charls_dataset_type(charls_csv):
    """CHARLS CSV -> profile['dataset_type'] == 'CHARLS'."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(charls_csv)}]
    _, result_report = ProfilingStep().run(ds, {})
    profile = result_report["profiles"][0]
    assert profile.get("dataset_type") == "CHARLS"


def test_profiling_step_includes_charls_config_when_charls(charls_csv):
    """CHARLS CSV -> profile['charls_config'] contains variable_mapping dict."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(charls_csv)}]
    _, result_report = ProfilingStep().run(ds, {})
    cfg = result_report["profiles"][0].get("charls_config")
    assert isinstance(cfg, dict)
    assert isinstance(cfg.get("variable_mapping"), dict)
    assert cfg["variable_mapping"]["qe303_hi"] == "oopc_exp"


def test_profiling_step_no_charls_config_for_generic_csv(generic_csv):
    """Generic CSV -> dataset_type == 'generic', no charls_config key."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(generic_csv)}]
    _, result_report = ProfilingStep().run(ds, {})
    profile = result_report["profiles"][0]
    assert profile.get("dataset_type") == "generic"
    assert "charls_config" not in profile


def test_profiling_step_does_not_mutate_existing_return_keys(charls_csv):
    """T-04 backward-compat: existing keys unchanged in shape."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(charls_csv)}]
    _, result_report = ProfilingStep().run(ds, {})
    profile = result_report["profiles"][0]
    assert isinstance(profile["n_rows"], int)
    assert isinstance(profile["n_cols"], int)
    assert isinstance(profile["variables"], dict)
    for col, info in profile["variables"].items():
        assert "dtype" in info
        assert "missing_rate" in info
        assert "n_unique" in info
        assert "is_numeric" in info


# ---------- multi-dataset profiling ----------------------------------------

def test_profiling_step_profiles_all_datasets(generic_csv, charls_csv):
    """ProfilingStep profiles ALL datasets (not just datasets[0])."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [
        {"path": str(generic_csv)},
        {"path": str(charls_csv)},
    ]
    _, result_report = ProfilingStep().run(ds, {})
    profiles = result_report["profiles"]
    assert len(profiles) == 2
    assert profiles[0]["dataset_type"] == "generic"
    assert profiles[1]["dataset_type"] == "CHARLS"


# ---------- return shape ---------------------------------------------------

def test_profiling_step_returns_tuple(generic_csv):
    """ProfilingStep.run returns (datasets, report) tuple."""
    from agent.cleaning.profiling import ProfilingStep

    ds = [{"path": str(generic_csv)}]
    result = ProfilingStep().run(ds, {})
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], dict)
    assert "profiles" in result[1]
    assert "merged_profile" in result[1]
