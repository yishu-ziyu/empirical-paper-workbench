"""T-11 RED tests: CHARLS dataset detection + charls.yaml config.

These tests assert behavior that does not exist yet (RED stage):
- cleaning.profiling._detect_dataset_type returns "CHARLS" for a mock
  CHARLS CSV (community_id + ≥5 qe*_hi columns) and "generic" otherwise.
- dataset_profiles.load_profile("charls") returns the parsed YAML config
  with the required structural fields.

charls_csv / generic_csv fixture 由根 conftest.py 提供（ADR-0003 Stage C）。
"""
from __future__ import annotations

import pandas as pd
import pytest


# ---------- _detect_dataset_type tests --------------------------------------

def test_detect_charls_returns_charls_for_mock_charls_csv(charls_csv):
    """CSV with community_id + ≥5 qe*_hi columns → 'CHARLS'."""
    from cleaning.profiling import _detect_dataset_type

    df = pd.read_csv(charls_csv)
    assert _detect_dataset_type(df) == "CHARLS"


def test_detect_charls_returns_generic_for_plain_csv(generic_csv):
    """Plain CSV without CHARLS patterns → 'generic'."""
    from cleaning.profiling import _detect_dataset_type

    df = pd.read_csv(generic_csv)
    assert _detect_dataset_type(df) == "generic"


def test_detect_charls_returns_generic_when_only_community_id_present(tmp_path):
    """community_id present but < 5 qe*_hi columns → not CHARLS."""
    from cleaning.profiling import _detect_dataset_type

    df = pd.DataFrame(
        {
            "community_id": [1, 2, 3],
            "qe303_hi": [100, 200, 300],  # only 1 qe*_hi → below threshold
            "income": [1, 2, 3],
        }
    )
    assert _detect_dataset_type(df) == "generic"


# ---------- charls.yaml structure tests -------------------------------------

def test_charls_yaml_loads_and_has_required_fields():
    """charls.yaml parses and contains identifier / variable_mapping / waves / presets."""
    import yaml

    from dataset_profiles import load_profile

    cfg = load_profile("charls")
    assert isinstance(cfg, dict)
    assert cfg.get("name") == "CHARLS"

    # identifier block
    identifier = cfg.get("identifier")
    assert isinstance(identifier, dict)
    assert "community_id" in identifier.get("required_columns", [])
    assert identifier.get("min_pattern_matches", 0) >= 5

    # variable_mapping: at least the 7 spec-named variables
    vm = cfg.get("variable_mapping")
    assert isinstance(vm, dict)
    for key in ("qe303_hi", "qe304_hi", "qe305_hi", "rage", "ragender", "rmarital", "redu"):
        assert key in vm, f"variable_mapping missing {key}"

    # waves: 6 entries including 2018 and 2020
    waves = cfg.get("waves")
    assert isinstance(waves, list) and len(waves) == 6
    assert 2018 in waves and 2020 in waves
    assert set(cfg.get("default_waves", [])) == {2018, 2020}

    # filter_presets: 3 presets
    presets = cfg.get("filter_presets")
    assert isinstance(presets, list) and len(presets) == 3
    preset_names = {p.get("name") for p in presets}
    assert preset_names == {"60岁以上", "城乡居民医保", "无缺失值样本"}


def test_charls_yaml_min_pattern_matches_is_5():
    """Spec: identifier.min_pattern_matches must equal 5."""
    from dataset_profiles import load_profile

    cfg = load_profile("charls")
    assert cfg["identifier"]["min_pattern_matches"] == 5


def test_load_profile_returns_none_for_unknown_profile():
    """load_profile on unknown name → None or KeyError (graceful)."""
    from dataset_profiles import load_profile

    result = load_profile("does_not_exist")
    assert result is None
