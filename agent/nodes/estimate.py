"""estimate node -- 主结果估计。

按 ``main_specification.method`` 分派到 StatsPAI：
OLS ``feols`` / DiD ``feols`` 或 ``callaway_santanna`` / IV ``ivreg`` /
RD ``rdrobust`` / SCM ``synth``。

IV 主表必须是 ``statspai.ivreg``，禁止用 ``iv_diag`` 当主表。
缺工具变量或方法列：``status=error``，不准编假系数。
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from design.spec import norm_method
from protocols import EstimateOutput
from state import EconPaperState


def _coef_se_p(result: Any, var: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
    try:
        d = result.to_dict()
        coefs = d.get("coefficients", {})
        entry = coefs.get(var) or coefs.get("treat") or {}
        if entry:
            return entry.get("estimate"), entry.get("std_error"), entry.get("p_value")
    except Exception:
        pass
    try:
        se_src = getattr(result, "bse", None)
        if se_src is None:
            se_src = result.std_errors
        return float(result.params[var]), float(se_src[var]), float(result.pvalues[var])
    except Exception:
        return None, None, None


def effect_from_fit(
    fit: Any, var: str | None = None
) -> tuple[Optional[float], Optional[float], Optional[float], Optional[int]]:
    """抽出 (coef, se, p, n)。CausalResult 用 ``estimate``，不要 ``float(result)``。"""
    if hasattr(fit, "estimate") and not hasattr(fit, "params"):
        coef = float(fit.estimate)
        se = None if getattr(fit, "se", None) is None else float(fit.se)
        pval = getattr(fit, "pvalue", None)
        p = None if pval is None else float(pval)
        n_raw = getattr(fit, "n_obs", None)
        n = None if n_raw is None else int(n_raw)
        return coef, se, p, n
    label = var or "treat"
    coef, se, p = _coef_se_p(fit, label)
    n_raw = getattr(fit, "nobs", None)
    if n_raw is None:
        n_raw = getattr(fit, "n_obs", None)
    if n_raw is None:
        info = getattr(fit, "data_info", None) or {}
        if isinstance(info, dict):
            n_raw = info.get("nobs") or info.get("n_obs")
    n = None if n_raw is None else int(n_raw)
    return coef, se, p, n


def _fit(formula: str, df: Any, cluster: Optional[str]) -> Any:
    try:
        import statspai

        kwargs: Dict[str, Any] = {"data": df}
        if cluster:
            kwargs["vcov"] = {"CRV1": cluster}
        return statspai.feols(formula, **kwargs)
    except Exception:
        import statsmodels.formula.api as smf

        fit_kwargs: Dict[str, Any] = {}
        if cluster is not None:
            fit_kwargs = {"cov_type": "cluster", "cov_kwds": {"groups": df[cluster]}}
        return smf.ols(formula, data=df).fit(**fit_kwargs)


def _fmt(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.4f}"


OMITTED_CELL = "未估计"

_RHS_SKIP = {"", "1", "0"}


def table_var_names(spec: Dict[str, Any], formula: Optional[str] = None) -> List[str]:
    """Treatment first, then controls / formula RHS. Never invent names."""
    names: List[str] = []
    treatment = spec.get("treatment") or spec.get("treatment_col")
    if treatment:
        names.append(str(treatment))
    for raw in spec.get("controls") or []:
        name = str(raw).strip()
        if name and name not in names:
            names.append(name)
    src = formula or spec.get("formula") or spec.get("feols_formula") or ""
    if "~" in str(src):
        rhs = str(src).split("~", 1)[1]
        rhs = rhs.split("|", 1)[0]
        rhs = re.sub(r"\([^)]*\)", " ", rhs)
        for tok in rhs.split("+"):
            name = tok.strip()
            if name and name not in names and name not in _RHS_SKIP:
                names.append(name)
    return names


def _all_coefs(fit: Any) -> Dict[str, tuple]:
    """name → (coef, se, p) from a StatsPAI / statsmodels fit. Missing keys stay out."""
    out: Dict[str, tuple] = {}
    try:
        payload = fit.to_dict()
        for name, entry in (payload.get("coefficients") or {}).items():
            if not isinstance(entry, dict):
                continue
            out[str(name)] = (
                entry.get("estimate"),
                entry.get("std_error"),
                entry.get("p_value"),
            )
    except Exception:
        pass
    try:
        params = fit.params
        se_src = getattr(fit, "bse", None)
        if se_src is None:
            se_src = getattr(fit, "std_errors", None)
        pvalues = getattr(fit, "pvalues", None)
        index = getattr(params, "index", params)
        for name in index:
            key = str(name)
            if key in out:
                continue
            se = None if se_src is None else float(se_src[name])
            pval = None if pvalues is None else float(pvalues[name])
            out[key] = (float(params[name]), se, pval)
    except Exception:
        pass
    return out


def row_for_name(name: str, coefs: Optional[Dict[str, tuple]] = None) -> str:
    """Real coef row, or an explicit 未估计 cell. Never invent a number."""
    entry = (coefs or {}).get(name)
    if not entry:
        return f"| {name} | {OMITTED_CELL} | — | — |"
    coef, se, p = entry
    if coef is None and se is None and p is None:
        return f"| {name} | {OMITTED_CELL} | — | — |"
    return f"| {name} | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |"


def _table_rows_from_fit(
    fit: Any, spec: Dict[str, Any], formula: Optional[str], treatment: str
) -> List[str]:
    coefs = _all_coefs(fit)
    names = table_var_names(spec, formula)
    if treatment and treatment not in names:
        names.insert(0, str(treatment))
    return [row_for_name(name, coefs) for name in names]


def splice_missing_table_rows(
    content: str, spec: Dict[str, Any], estimate: Dict[str, Any]
) -> str:
    """Insert omitted/real rows for formula vars the markdown table dropped."""
    if not content:
        return content
    formula = estimate.get("formula") or spec.get("formula") or spec.get("feols_formula")
    names = table_var_names(spec, formula)
    stored = estimate.get("table_rows") or []
    by_name: Dict[str, str] = {}
    for row in stored:
        if not isinstance(row, str):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if cells:
            by_name[cells[0]] = row if row.startswith("|") else f"| {row}"
    extras: List[str] = []
    for name in names:
        if re.search(rf"\|\s*{re.escape(name)}\s*\|", content):
            continue
        extras.append(by_name.get(name) or row_for_name(name))
    if not extras:
        return content
    lines = content.splitlines()
    last_table = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            last_table = i
    if last_table >= 0:
        lines[last_table + 1 : last_table + 1] = extras
        return "\n".join(lines)
    header = [
        "| 变量 | 系数 | SE | p |",
        "|------|------|----|---|",
        *extras,
    ]
    return content.rstrip() + "\n\n" + "\n".join(header)


def _error(
    message: str,
    *,
    error: str,
    method: Optional[str] = None,
    formula: Optional[str] = None,
) -> EstimateOutput:
    payload: Dict[str, Any] = {
        "status": "error",
        "produced_by": "estimate",
        "treatment_row": "",
        "error": error,
    }
    if method:
        payload["method"] = method
    if formula:
        payload["formula"] = formula
    return {"results": message, "estimate": payload}


def _ok_table(payload: Dict[str, Any]) -> str:
    formula = payload.get("formula") or ""
    lines = [
        "# 主结果",
        "",
        f"估计器：`{payload['estimator']}`",
    ]
    if formula:
        lines.append(f"公式：`{formula}`")
    if payload.get("n") is not None:
        lines.append(f"N = {payload['n']}")
    rows = payload.get("table_rows") or [payload["treatment_row"]]
    lines.extend(
        [
            "",
            "| 变量 | 系数 | SE | p |",
            "|------|------|----|---|",
            *[row for row in rows if row],
        ]
    )
    return "\n".join(lines)


def _method_of(state: EconPaperState, spec: Dict[str, Any]) -> Optional[str]:
    raw = spec.get("method")
    if not raw:
        rd = state.get("research_direction")
        if isinstance(rd, dict):
            raw = rd.get("method")
    return norm_method(raw)


def _iv_formula(spec: Dict[str, Any]) -> Optional[str]:
    explicit = spec.get("iv_formula")
    if explicit:
        return str(explicit)
    formula = spec.get("formula") or ""
    if "(" in str(formula) and "~" in str(formula).split("(", 1)[-1]:
        return str(formula)
    outcome = spec.get("outcome")
    endog = spec.get("endogenous") or spec.get("treatment")
    instruments = spec.get("instruments") or []
    if isinstance(instruments, str):
        instruments = [instruments]
    one = spec.get("instrument") or spec.get("instrument_col")
    if one and not instruments:
        instruments = [one]
    if not (outcome and endog and instruments):
        return None
    z = " + ".join(str(z) for z in instruments)
    controls = [
        c
        for c in (spec.get("controls") or [])
        if c and c != endog and c not in instruments
    ]
    extra = f" + {' + '.join(controls)}" if controls else ""
    return f"{outcome} ~ ({endog} ~ {z}){extra}"


def _has_instruments(spec: Dict[str, Any]) -> bool:
    instruments = spec.get("instruments") or []
    if isinstance(instruments, str):
        instruments = [instruments]
    if instruments:
        return True
    return bool(spec.get("instrument") or spec.get("instrument_col"))


def _bacon_forbidden_over(state: EconPaperState) -> bool:
    diag = state.get("identification_diag") or {}
    rows = diag.get("diagnostics") if isinstance(diag, dict) else None
    if not rows:
        return False
    for row in rows:
        if not isinstance(row, dict) or row.get("test") != "bacon_decomposition":
            continue
        share = row.get("forbidden_weight_share")
        if share is None:
            continue
        try:
            return float(share) >= 0.1
        except (TypeError, ValueError):
            return False
    return False


def _estimate_ols(df: Any, spec: Dict[str, Any], formula: str) -> EstimateOutput:
    treatment = spec.get("treatment") or spec.get("treatment_col") or "treat"
    cluster = spec.get("cluster") or spec.get("cluster_col") or None
    if cluster == "":
        cluster = None
    fitted = _fit(str(formula), df, cluster)
    coef, se, p, n = effect_from_fit(fitted, str(treatment))
    n = int(n or len(df))
    table_rows = _table_rows_from_fit(fitted, spec, formula, str(treatment))
    treatment_row = next(
        (row for row in table_rows if row.startswith(f"| {treatment} |")),
        f"| {treatment} | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |",
    )
    payload = {
        "status": "ok",
        "produced_by": "estimate",
        "estimator": "statspai.feols",
        "method": str(spec.get("method") or "ols"),
        "formula": formula,
        "treatment": treatment,
        "treatment_row": treatment_row,
        "table_rows": table_rows,
        "n": n,
        "coef": coef,
        "se": se,
        "p": p,
        "cluster": cluster,
    }
    return {"results": _ok_table(payload), "estimate": payload}


def _estimate_iv(df: Any, spec: Dict[str, Any], formula: str) -> EstimateOutput:
    import statspai

    treatment = spec.get("endogenous") or spec.get("treatment") or "treat"
    cluster = spec.get("cluster") or spec.get("cluster_col") or None
    if cluster == "":
        cluster = None
    kwargs: Dict[str, Any] = {"data": df}
    if cluster:
        kwargs["cluster"] = cluster
    fitted = statspai.ivreg(formula, **kwargs)
    coef, se, p, n = effect_from_fit(fitted, str(treatment))
    n = int(n or len(df))
    table_rows = _table_rows_from_fit(fitted, spec, formula, str(treatment))
    treatment_row = next(
        (row for row in table_rows if row.startswith(f"| {treatment} |")),
        f"| {treatment} | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |",
    )
    payload = {
        "status": "ok",
        "produced_by": "estimate",
        "estimator": "statspai.ivreg",
        "method": "iv",
        "formula": formula,
        "treatment": treatment,
        "treatment_row": treatment_row,
        "table_rows": table_rows,
        "n": n,
        "coef": coef,
        "se": se,
        "p": p,
        "cluster": cluster,
    }
    return {"results": _ok_table(payload), "estimate": payload}


def _estimate_rd(df: Any, spec: Dict[str, Any]) -> EstimateOutput:
    import statspai

    outcome = spec.get("outcome")
    running = spec.get("running_var")
    cutoff = spec.get("cutoff", 0)
    try:
        c = float(cutoff)
    except (TypeError, ValueError):
        c = 0.0
    fitted = statspai.rdrobust(df, y=outcome, x=running, c=c)
    coef, se, p, n = effect_from_fit(fitted)
    n = int(n or len(df))
    treatment_row = f"| RD | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |"
    formula = f"rdrobust({outcome}, {running}, c={c})"
    payload = {
        "status": "ok",
        "produced_by": "estimate",
        "estimator": "statspai.rdrobust",
        "method": "rd",
        "formula": formula,
        "treatment": "RD",
        "treatment_row": treatment_row,
        "table_rows": [treatment_row],
        "n": n,
        "coef": coef,
        "se": se,
        "p": p,
    }
    return {"results": _ok_table(payload), "estimate": payload}


def _estimate_scm(df: Any, spec: Dict[str, Any]) -> EstimateOutput:
    import statspai

    outcome = spec.get("outcome")
    unit = spec.get("unit") or spec.get("unit_col")
    time_col = spec.get("time") or spec.get("time_col")
    treated_unit = spec.get("treated_unit")
    treatment_time = spec.get("treatment_time")
    fitted = statspai.synth(
        df,
        outcome=outcome,
        unit=unit,
        time=time_col,
        treated_unit=treated_unit,
        treatment_time=treatment_time,
    )
    coef, se, p, n = effect_from_fit(fitted)
    n = int(n or len(df))
    treatment_row = f"| SCM_gap | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |"
    formula = (
        f"synth({outcome}, unit={unit}, time={time_col}, "
        f"treated={treated_unit}, t0={treatment_time})"
    )
    payload = {
        "status": "ok",
        "produced_by": "estimate",
        "estimator": "statspai.synth",
        "method": "scm",
        "formula": formula,
        "treatment": "SCM_gap",
        "treatment_row": treatment_row,
        "table_rows": [treatment_row],
        "n": n,
        "coef": coef,
        "se": se,
        "p": p,
    }
    return {"results": _ok_table(payload), "estimate": payload}


def _estimate_did(df: Any, spec: Dict[str, Any], state: EconPaperState) -> EstimateOutput:
    first_treat = spec.get("first_treat_col")
    if first_treat and _bacon_forbidden_over(state):
        import statspai

        outcome = spec.get("outcome")
        time_col = spec.get("time_col") or spec.get("time")
        id_col = spec.get("id_col") or spec.get("id")
        fitted = statspai.callaway_santanna(
            df, y=outcome, g=first_treat, t=time_col, i=id_col
        )
        coef, se, p, n = effect_from_fit(fitted)
        n = int(n or len(df))
        treatment_row = f"| ATT | {_fmt(coef)} | {_fmt(se)} | {_fmt(p)} |"
        formula = f"callaway_santanna({outcome}, g={first_treat}, t={time_col}, i={id_col})"
        payload = {
            "status": "ok",
            "produced_by": "estimate",
            "estimator": "statspai.callaway_santanna",
            "method": "did",
            "formula": formula,
            "treatment": "ATT",
            "treatment_row": treatment_row,
            "table_rows": [treatment_row],
            "n": n,
            "coef": coef,
            "se": se,
            "p": p,
        }
        return {"results": _ok_table(payload), "estimate": payload}

    if _bacon_forbidden_over(state) and not first_treat:
        return _error(
            "主估计未跑：Goodman-Bacon 禁止 TWFE，且缺少队列列 first_treat_col，未编造系数",
            error="twfe_without_cohort",
            method="did",
            formula=spec.get("feols_formula") or spec.get("formula") or None,
        )

    formula = spec.get("feols_formula") or spec.get("formula")
    if not formula:
        return _error(
            "主估计未跑：缺少公式或数据路径",
            error="missing_formula_or_csv",
            method="did",
        )
    cluster = (
        spec.get("cluster")
        or spec.get("cluster_col")
        or spec.get("id_col")
        or spec.get("id")
    )
    if cluster == "":
        cluster = None
    try:
        out = _estimate_ols(df, spec, str(formula))
    except Exception as exc:
        return _error(f"主估计失败：{exc}", error=str(exc), method="did", formula=str(formula))
    out["estimate"]["method"] = "did"
    return out


def estimate(state: EconPaperState) -> EstimateOutput:
    """跑主设定，写出结果章能引用的表。"""
    spec = state.get("main_specification") or {}
    if not isinstance(spec, dict):
        spec = {}
    csv_path = state.get("csv_path")
    method = _method_of(state, spec)

    if method == "iv":
        if not csv_path:
            return _error(
                "主估计未跑：缺少公式或数据路径",
                error="missing_formula_or_csv",
                method="iv",
            )
        if not _has_instruments(spec) and not _iv_formula(spec):
            return _error(
                "主估计未跑：IV 缺少工具变量，未编造系数",
                error="missing_instrument",
                method="iv",
            )
        formula = _iv_formula(spec)
        if not formula:
            return _error(
                "主估计未跑：IV 缺少工具变量，未编造系数",
                error="missing_instrument",
                method="iv",
            )
    elif method == "rd":
        if not csv_path or not spec.get("outcome") or not spec.get("running_var"):
            return _error(
                "主估计未跑：RD 缺少 running_var 或数据路径",
                error="missing_rd_fields",
                method="rd",
            )
        formula = None
    elif method == "scm":
        unit = spec.get("unit") or spec.get("unit_col")
        time_col = spec.get("time") or spec.get("time_col")
        if not csv_path or not spec.get("outcome") or not unit or not time_col:
            return _error(
                "主估计未跑：SCM 缺少 unit/time 或数据路径",
                error="missing_scm_fields",
                method="scm",
            )
        if spec.get("treatment_time") is None:
            return _error(
                "主估计未跑：SCM 缺少 treatment_time",
                error="missing_scm_fields",
                method="scm",
            )
        formula = None
    else:
        formula = spec.get("formula") if method != "did" else (
            spec.get("feols_formula") or spec.get("formula")
        )
        if not formula or not csv_path:
            return _error(
                "主估计未跑：缺少公式或数据路径",
                error="missing_formula_or_csv",
                method=method,
            )

    import pandas as pd

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        return _error(
            f"无法读取数据，主估计未跑：{exc}",
            error=str(exc),
            method=method,
        )

    try:
        if method == "iv":
            return _estimate_iv(df, spec, str(formula))
        if method == "rd":
            return _estimate_rd(df, spec)
        if method == "scm":
            return _estimate_scm(df, spec)
        if method == "did":
            return _estimate_did(df, spec, state)
        return _estimate_ols(df, spec, str(formula))
    except Exception as exc:
        return _error(
            f"主估计失败：{exc}",
            error=str(exc),
            method=method,
            formula=str(formula) if formula else None,
        )


__all__ = ["estimate", "effect_from_fit"]
