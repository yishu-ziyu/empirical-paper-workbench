"""One reader for estimator results, used by every stage.

Before this module the same question — "what are the coefficient, standard
error, p-value and sample size of this fit?" — was answered in five places
(main estimate, robustness, identification, spec runs, replication). They
drifted apart: RD / SCM / CS main estimates once reported ``status=ok`` with
no coefficient because one copy misread a newer StatsPAI result object.

Two shapes are recognised:

* causal results (``CausalResult``: RD, SCM, Callaway–Sant'Anna, density
  tests…) expose one effect as ``estimate`` / ``se`` / ``pvalue`` / ``n_obs``;
* regression results (StatsPAI ``EconometricResults``, statsmodels) expose a
  coefficient table, read for one named variable.

A fit is read as causal when it has ``estimate`` and the caller did not name a
variable (or the object has no coefficient table). This is the rule the main
estimate already used; keeping it means switching callers changes no values.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Optional


@dataclass(frozen=True)
class Effect:
    coef: Optional[float]
    se: Optional[float]
    p: Optional[float]
    n: Optional[int]

    def __iter__(self) -> Iterator[Any]:  # allows ``coef, se, p, n = read_effect(...)``
        return iter((self.coef, self.se, self.p, self.n))


def _float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _n_of(fit: Any) -> Optional[int]:
    for attr in ("nobs", "n_obs"):
        value = getattr(fit, attr, None)
        if value is not None:
            return _int(value)
    info = getattr(fit, "data_info", None) or {}
    if isinstance(info, dict):
        return _int(info.get("nobs") or info.get("n_obs"))
    return None


def _table_entry(fit: Any, var: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
    try:
        coefs = fit.to_dict().get("coefficients", {})
        entry = coefs.get(var) or coefs.get("treat") or {}
        if entry:
            return _float(entry.get("estimate")), _float(entry.get("std_error")), _float(entry.get("p_value"))
    except Exception:
        pass
    try:
        se_src = getattr(fit, "bse", None)
        if se_src is None:
            se_src = fit.std_errors
        return _float(fit.params[var]), _float(se_src[var]), _float(fit.pvalues[var])
    except Exception:
        return None, None, None


def is_causal(fit: Any, var: Optional[str] = None) -> bool:
    return hasattr(fit, "estimate") and (var is None or not hasattr(fit, "params"))


def read_effect(fit: Any, var: Optional[str] = None) -> Effect:
    """Coefficient, SE, p and n of ``fit``; ``None`` for whatever is missing."""
    if fit is None:
        return Effect(None, None, None, None)
    if is_causal(fit, var):
        return Effect(
            _float(getattr(fit, "estimate", None)),
            _float(getattr(fit, "se", None)),
            _float(getattr(fit, "pvalue", None)),
            _int(getattr(fit, "n_obs", None)),
        )
    coef, se, p = _table_entry(fit, var or "treat")
    return Effect(coef, se, p, _n_of(fit))
