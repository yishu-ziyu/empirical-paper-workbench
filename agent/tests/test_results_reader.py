"""Characterization: the single result reader reproduces every legacy reader.

The legacy readers are copied here verbatim as the reference, so switching
callers to ``agent.engine.results.read_effect`` is provably value-preserving on
the result objects the product actually produces.
"""
from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agent.engine.results import Effect, read_effect

REPO = Path(__file__).resolve().parents[2]
CK = REPO / "fixtures/classic-5/ck1994_long.csv"


@pytest.fixture
def statspai():
    # Optional estimator dependency must not skip the dependency-free reader test.
    if importlib.util.find_spec("statspai") is None:
        pytest.skip("Optional StatsPAI estimator dependency is not installed")
    # A present but broken install must fail, including missing transitive imports.
    return importlib.import_module("statspai")


# ---- legacy readers (verbatim reference, do not "fix") ---------------------

def legacy_effect_from_fit(fit, var=None):
    def _coef_se_p(result, v):
        try:
            d = result.to_dict()
            coefs = d.get("coefficients", {})
            entry = coefs.get(v) or coefs.get("treat") or {}
            if entry:
                return entry.get("estimate"), entry.get("std_error"), entry.get("p_value")
        except Exception:
            pass
        try:
            se_src = getattr(result, "bse", None)
            if se_src is None:
                se_src = result.std_errors
            return float(result.params[v]), float(se_src[v]), float(result.pvalues[v])
        except Exception:
            return None, None, None

    if hasattr(fit, "estimate") and (var is None or not hasattr(fit, "params")):
        coef = float(fit.estimate)
        se = None if getattr(fit, "se", None) is None else float(fit.se)
        pval = getattr(fit, "pvalue", None)
        p = None if pval is None else float(pval)
        n_raw = getattr(fit, "n_obs", None)
        return coef, se, p, None if n_raw is None else int(n_raw)
    coef, se, p = _coef_se_p(fit, var or "treat")
    n_raw = getattr(fit, "nobs", None)
    if n_raw is None:
        n_raw = getattr(fit, "n_obs", None)
    if n_raw is None:
        info = getattr(fit, "data_info", None) or {}
        if isinstance(info, dict):
            n_raw = info.get("nobs") or info.get("n_obs")
    return coef, se, p, None if n_raw is None else int(n_raw)


def legacy_robustness(result, var):
    def pick(key, attr):
        try:
            d = result.to_dict()
            coefs = d.get("coefficients", {})
            entry = coefs.get(var) or coefs.get("treat") or {}
            return entry.get(key)
        except Exception:
            pass
        try:
            return float(getattr(result, attr)[var])
        except Exception:
            return None

    return pick("estimate", "params"), pick("std_error", "bse"), pick("p_value", "pvalues")


def legacy_getattr(result):
    return getattr(result, "estimate", None), getattr(result, "se", None), getattr(result, "pvalue", None)


# ---- real objects -------------------------------------------------------------

def _rd_df():
    rng = np.random.default_rng(7)
    x = rng.uniform(-1, 1, 1500)
    return pd.DataFrame({"x": x, "y": 0.4 * (x >= 0) + 0.8 * x + rng.normal(0, 0.3, x.size)})


def _panel():
    rng = np.random.default_rng(11)
    rows = []
    for u in range(12):
        base = rng.normal(10, 1)
        for t in range(20):
            treated = u < 6
            rows.append({
                "unit": u, "year": 2000 + t, "first_treat": 2012 if treated else 0,
                "y": base + 0.3 * t + rng.normal(0, 0.2) + (2.0 if treated and t >= 12 else 0.0),
                "name": f"u{u}",
            })
    return pd.DataFrame(rows)


def _card(statspai):
    # same location rule as backend/services/card_demo.py
    path = Path(statspai.__file__).resolve().parents[2] / "papers" / "data_card1995.csv"
    if not path.is_file():
        pytest.skip("IV reader case requires external papers/data_card1995.csv (not bundled with PyPI StatsPAI)")
    return pd.read_csv(path)


@pytest.fixture
def regression_fit(request, statspai):
    name = request.param
    if name == "ivreg":
        return name, statspai.ivreg("lwage ~ (educ ~ nearc4) + exper + expersq", data=_card(statspai)), "educ"

    ck = pd.read_csv(CK)
    import statsmodels.formula.api as smf

    if name == "feols":
        return name, statspai.feols("fte ~ treated + period", data=ck), "treated"
    if name == "feols_interaction":
        return name, statspai.feols("fte ~ treated * period", data=ck), "treated:period"
    if name == "statsmodels_ols":
        return name, smf.ols("fte ~ treated + period", data=ck).fit(), "treated"
    if name == "statsmodels_cluster":
        return name, smf.ols("fte ~ treated", data=ck).fit(cov_type="cluster", cov_kwds={"groups": ck["store_id"]}), "treated"
    raise ValueError(f"Unknown regression reader case: {name}")


@pytest.fixture
def causal_fit(request, statspai):
    name = request.param
    if name == "rdrobust":
        return name, statspai.rdrobust(_rd_df(), y="y", x="x", c=0.0)
    if name == "mccrary":
        return name, statspai.mccrary_test(_rd_df(), x="x", c=0.0)
    panel = _panel()
    if name == "synth":
        return name, statspai.synth(panel.assign(unit=panel["name"]), outcome="y", unit="unit", time="year", treated_unit="u0", treatment_time=2012)
    if name == "callaway_santanna":
        return name, statspai.callaway_santanna(panel, y="y", g="first_treat", t="year", i="unit")
    raise ValueError(f"Unknown causal reader case: {name}")


@pytest.mark.parametrize("regression_fit", ["feols", "feols_interaction", "statsmodels_ols", "statsmodels_cluster", "ivreg"], indirect=True)
def test_regression_results_match_every_legacy_reader(regression_fit):
    name, fit, var = regression_fit
    new = read_effect(fit, var)
    assert isinstance(new, Effect)
    old = legacy_effect_from_fit(fit, var)
    for got, ref in zip(new, old):
        if ref is not None:
            assert got is not None and abs(float(got) - float(ref)) < 1e-12, (name, got, ref)
    rob = legacy_robustness(fit, var)
    for got, ref in zip((new.coef, new.se, new.p), rob):
        if ref is not None:
            assert got is not None and abs(float(got) - float(ref)) < 1e-12, (name, got, ref)
    assert new.coef is not None and new.se is not None, name


@pytest.mark.parametrize("causal_fit", ["rdrobust", "mccrary", "synth", "callaway_santanna"], indirect=True)
def test_causal_results_match_every_legacy_reader(causal_fit):
    name, fit = causal_fit
    new = read_effect(fit)
    old = legacy_effect_from_fit(fit)
    for got, ref in zip(new, old):
        if ref is not None:
            assert got is not None and abs(float(got) - float(ref)) < 1e-12, (name, got, ref)
    for got, ref in zip((new.coef, new.se, new.p), legacy_getattr(fit)):
        if ref is not None:
            assert got is not None and abs(float(got) - float(ref)) < 1e-12, (name, got, ref)
    assert new.coef is not None, name


def test_none_estimate_does_not_raise():
    class Stub:
        estimate = None
        estimand = "ATT"

    assert read_effect(Stub()) == Effect(None, None, None, None)
    assert read_effect(None) == Effect(None, None, None, None)
