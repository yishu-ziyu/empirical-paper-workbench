"""Characterization: the single result reader reproduces every legacy reader.

The legacy readers are copied here verbatim as the reference, so switching
callers to ``agent.engine.results.read_effect`` is provably value-preserving on
the result objects the product actually produces.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from agent.engine.results import Effect, read_effect

statspai = pytest.importorskip("statspai")

REPO = Path(__file__).resolve().parents[2]
CK = REPO / "fixtures/classic-5/ck1994_long.csv"


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


def _card():
    # same location rule as backend/services/card_demo.py
    path = Path(statspai.__file__).resolve().parents[2] / "papers" / "data_card1995.csv"
    if not path.is_file():
        pytest.skip("Card data not available")
    return pd.read_csv(path)


def regression_fits():
    ck = pd.read_csv(CK)
    import statsmodels.formula.api as smf

    yield "feols", statspai.feols("fte ~ treated + period", data=ck), "treated"
    yield "feols_interaction", statspai.feols("fte ~ treated * period", data=ck), "treated:period"
    yield "statsmodels_ols", smf.ols("fte ~ treated + period", data=ck).fit(), "treated"
    yield "statsmodels_cluster", smf.ols("fte ~ treated", data=ck).fit(cov_type="cluster", cov_kwds={"groups": ck["store_id"]}), "treated"
    card = _card()
    yield "ivreg", statspai.ivreg("lwage ~ (educ ~ nearc4) + exper + expersq", data=card), "educ"


def causal_fits():
    rd = _rd_df()
    panel = _panel()
    yield "rdrobust", statspai.rdrobust(rd, y="y", x="x", c=0.0)
    yield "mccrary", statspai.mccrary_test(rd, x="x", c=0.0)
    yield "synth", statspai.synth(panel.assign(unit=panel["name"]), outcome="y", unit="unit", time="year", treated_unit="u0", treatment_time=2012)
    yield "callaway_santanna", statspai.callaway_santanna(panel, y="y", g="first_treat", t="year", i="unit")


@pytest.mark.parametrize("name,fit,var", list(regression_fits()), ids=lambda x: x if isinstance(x, str) else "")
def test_regression_results_match_every_legacy_reader(name, fit, var):
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


@pytest.mark.parametrize("name,fit", list(causal_fits()), ids=lambda x: x if isinstance(x, str) else "")
def test_causal_results_match_every_legacy_reader(name, fit):
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
