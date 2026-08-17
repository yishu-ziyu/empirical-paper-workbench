"""robustness_check node -- 稳健性检验（AERS 体系）。

在主体章节生成完毕后、翻译代码之前运行。读取 ``state.main_specification``
（可选 dict，含 formula / outcome / treatment / cluster / cluster_levels /
heterogeneity_groups）与 ``state.csv_path``，跑预设稳健性套餐：

1. 替代聚类：对 ``cluster_levels`` 里每个 level 用 ``feols`` 重跑，收集
   coef / se / p。
2. 异质性：对 ``heterogeneity_groups`` 里每个 group 跑交互项，收集
   interaction_coef / p。
3. 安慰剂：对 method 用 ``wild_cluster_bootstrap``（或 ``synth_time_placebo``）
   跑安慰剂分布。

每个 StatsPAI 调用独立 try/except 降级：单次失败不中断整体，失败记录进
``diagnostics``。最终写 ``robustness_results``（含 robustness /
heterogeneity / placebos / summary_table）。节点不 import fastapi，纯函数。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from design.spec import norm_method
from state import EconPaperState


def _coef_of(result: Any, var: str) -> Optional[float]:
    """取回归结果中指定变量的系数（缺失返回 None）。

    兼容 statspai.feols 的 ``to_dict()`` 结构与 statsmodels 的
    ``params``（当 pyfixest 不可用、feols 降级到 statsmodels 时）。
    """
    try:
        d = result.to_dict()
        coefs = d.get("coefficients", {})
        entry = coefs.get(var) or coefs.get("treat") or {}
        return entry.get("estimate")
    except Exception:
        pass
    try:
        return float(result.params[var])
    except Exception:
        return None


def _se_of(result: Any, var: str) -> Optional[float]:
    """取回归结果中指定变量的标准误（缺失返回 None）。"""
    try:
        d = result.to_dict()
        coefs = d.get("coefficients", {})
        entry = coefs.get(var) or coefs.get("treat") or {}
        return entry.get("std_error")
    except Exception:
        pass
    try:
        return float(result.bse[var])
    except Exception:
        return None


def _p_of(result: Any, var: str) -> Optional[float]:
    """取回归结果中指定变量的 p 值（缺失返回 None）。"""
    try:
        d = result.to_dict()
        coefs = d.get("coefficients", {})
        entry = coefs.get(var) or coefs.get("treat") or {}
        return entry.get("p_value")
    except Exception:
        pass
    try:
        return float(result.pvalues[var])
    except Exception:
        return None


def _sm_ols(formula: str, data: Any, cluster: Optional[str] = None) -> Any:
    """statsmodels OLS 降级实现（当 pyfixest 不可用时替代 feols）。

    返回 statsmodels 拟合结果，其 ``params``/``bse``/``pvalues`` 可被
    ``_coef_of``/``_se_of``/``_p_of`` 读取。``cluster`` 提供时使用聚类稳健
    标准误（对应 feols 的 ``vcov={"CRV1": level}``）。
    """
    import statsmodels.formula.api as smf

    kwargs: Dict[str, Any] = {}
    if cluster is not None:
        kwargs = {"cov_type": "cluster", "cov_kwds": {"groups": data[cluster]}}
    return smf.ols(formula, data=data).fit(**kwargs)


def _fmt(x: Optional[float]) -> str:
    """把数值格式化为 3 位小数，None 显示为 '—'。"""
    return "—" if x is None else f"{x:.3f}"


def _run_clustering(
    df: Any,
    main_spec: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """替代聚类：对每个 cluster_level 用 feols 重跑主回归。"""
    formula = main_spec.get("formula")
    if not formula:
        return []
    treatment = main_spec.get("treatment") or "treat"
    levels = main_spec.get("cluster_levels") or []
    if not levels:
        return []

    import statspai

    results: List[Dict[str, Any]] = []
    for level in levels:
        try:
            res = statspai.feols(formula, data=df, vcov={"CRV1": level})
        except Exception as exc:
            # pyfixest 未安装时 feols 抛 ImportError，降级到 statsmodels 聚类
            # OLS，保证替代聚类仍产出结果（降级被如实记入 diagnostics）。
            diagnostics.append({
                "test": "feols_clustering",
                "level": level,
                "status": "fallback",
                "error": str(exc),
            })
            try:
                res = _sm_ols(formula, data=df, cluster=level)
            except Exception as exc2:
                diagnostics.append({
                    "test": "statsmodels_clustering",
                    "level": level,
                    "status": "error",
                    "error": str(exc2),
                })
                continue
        results.append({
            "type": "clustering",
            "level": level,
            "coef": _coef_of(res, treatment),
            "se": _se_of(res, treatment),
            "p": _p_of(res, treatment),
        })
    return results


def _run_heterogeneity(
    df: Any,
    main_spec: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """异质性：对每个 heterogeneity_group 跑交互项。"""
    groups = main_spec.get("heterogeneity_groups") or []
    if not groups:
        return []
    formula = main_spec.get("formula")
    if not formula:
        return []

    # 从公式中提取 outcome 与处理变量（用于拼交互项）
    if "~" not in formula:
        return []
    import statspai

    outcome, rhs = formula.split("~", 1)
    outcome = outcome.strip()
    treatment = main_spec.get("treatment") or "treat"

    results: List[Dict[str, Any]] = []
    for group in groups:
        # y ~ treat + group + treat:group
        interaction_formula = f"{outcome} ~ {treatment} + {group} + {treatment}:{group}"
        interaction_var = f"{treatment}:{group}"
        try:
            res = statspai.feols(interaction_formula, data=df)
        except Exception as exc:
            # pyfixest 未安装时 feols 抛 ImportError，降级到 statsmodels 交互
            # OLS，保证异质性交互项仍被估计（降级被如实记入 diagnostics）。
            diagnostics.append({
                "test": "feols_heterogeneity",
                "group": group,
                "status": "fallback",
                "error": str(exc),
            })
            try:
                res = _sm_ols(interaction_formula, data=df)
            except Exception as exc2:
                diagnostics.append({
                    "test": "statsmodels_heterogeneity",
                    "group": group,
                    "status": "error",
                    "error": str(exc2),
                })
                continue
        results.append({
            "group": group,
            "interaction_coef": _coef_of(res, interaction_var),
            "p": _p_of(res, interaction_var),
        })
    return results


def _run_placebo(
    df: Any,
    main_spec: Dict[str, Any],
    method: Optional[str],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """安慰剂：按 method 分派（wild_cluster_bootstrap 或 synth_time_placebo）。"""
    method_norm = str(method or "").strip().lower()

    # SCM：时点安慰剂
    if method_norm in ("scm", "synthetic-control", "synthetic control"):
        outcome = main_spec.get("outcome")
        unit = main_spec.get("unit") or main_spec.get("unit_col")
        time_col = main_spec.get("time") or main_spec.get("time_col")
        treated_unit = main_spec.get("treated_unit")
        treatment_time = main_spec.get("treatment_time")
        if all([outcome, unit, time_col, treated_unit is not None, treatment_time is not None]):
            try:
                import statspai

                placebo = statspai.synth_time_placebo(
                    df,
                    outcome=outcome,
                    unit=unit,
                    time=time_col,
                    treated_unit=treated_unit,
                    treatment_time=treatment_time,
                )
                if placebo is not None and len(placebo) > 0:
                    pvals = placebo["pvalue"].dropna().astype(float)
                    n = int(len(pvals))
                    n_sig = int((pvals < 0.05).sum())
                    share = n_sig / n if n else 0.0
                    return [{
                        "type": "placebo_time",
                        "n_placebos": n,
                        "n_significant": n_sig,
                        "share_significant": share,
                        "min_p": float(pvals.min()) if n else None,
                        "median_p": float(pvals.median()) if n else None,
                    }]
            except Exception as exc:
                diagnostics.append({
                    "test": "synth_time_placebo",
                    "status": "error",
                    "error": str(exc),
                })
                return []
        return []

    # 默认：聚类稳健 bootstrap 安慰剂
    treatment = main_spec.get("treatment") or "treat"
    cluster = main_spec.get("cluster") or main_spec.get("cluster_col")
    outcome = main_spec.get("outcome") or main_spec.get("y")
    if not all([outcome, treatment, cluster]):
        return []
    try:
        import statspai

        res = statspai.wild_cluster_bootstrap(
            df,
            y=outcome,
            x=[treatment],
            cluster=cluster,
            test_var=treatment,
            n_boot=999,
        )
        return [{
            "type": "wild_cluster_bootstrap",
            "beta_hat": res.get("beta_hat"),
            "se_cluster": res.get("se_cluster"),
            "p_boot": res.get("p_boot"),
            "p_cluster": res.get("p_cluster"),
            "ci_boot": res.get("ci_boot"),
            "n_clusters": res.get("n_clusters"),
        }]
    except Exception as exc:
        diagnostics.append({
            "test": "wild_cluster_bootstrap",
            "status": "error",
            "error": str(exc),
        })
        return []


def _is_cs_estimate(state: EconPaperState) -> bool:
    """CS 主估计只看 estimate.estimator，不要把所有 DiD 都当成 CS。"""
    estimate = state.get("estimate") or {}
    if not isinstance(estimate, dict):
        return False
    return estimate.get("estimator") == "statspai.callaway_santanna"


def _cs_fields(main_spec: Dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    outcome = main_spec.get("outcome") or main_spec.get("y")
    group = (
        main_spec.get("first_treat_col")
        or main_spec.get("g")
        or main_spec.get("treatment_group_col")
    )
    time_col = main_spec.get("time_col") or main_spec.get("time")
    id_col = main_spec.get("id_col") or main_spec.get("id") or main_spec.get("unit_col")
    return outcome, group, time_col, id_col


def _run_cs_battery(
    df: Any,
    main_spec: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """交替 control_group / notyet_cutoff。不做 y ~ treat 的 OLS 重拟合。"""
    outcome, group, time_col, id_col = _cs_fields(main_spec)
    if not all([outcome, group, time_col, id_col]):
        diagnostics.append({
            "test": "callaway_santanna",
            "status": "error",
            "error": "缺少 outcome / first_treat_col(g) / time_col / id_col",
        })
        return []
    missing = [name for name in (outcome, group, time_col, id_col) if name not in df.columns]
    if missing:
        diagnostics.append({
            "test": "callaway_santanna",
            "status": "error",
            "error": f"列不在数据中: {missing}",
        })
        return []
    try:
        import statspai
    except Exception as exc:
        diagnostics.append({
            "test": "callaway_santanna",
            "status": "error",
            "error": str(exc),
        })
        return []

    work = df.copy()
    if work[group].isna().any():
        work[group] = work[group].fillna(0)

    variants = [
        {"control_group": "nevertreated", "notyet_cutoff": "period"},
        {"control_group": "notyettreated", "notyet_cutoff": "period"},
        {"control_group": "notyettreated", "notyet_cutoff": "cohort"},
    ]
    results: List[Dict[str, Any]] = []
    for variant in variants:
        try:
            res = statspai.callaway_santanna(
                work,
                y=outcome,
                g=group,
                t=time_col,
                i=id_col,
                **variant,
            )
        except Exception as exc:
            diagnostics.append({
                "test": "callaway_santanna",
                "status": "error",
                "error": str(exc),
                **variant,
            })
            continue
        results.append({
            "type": "cs_variant",
            "control_group": variant["control_group"],
            "notyet_cutoff": variant["notyet_cutoff"],
            "level": f"{variant['control_group']}/{variant['notyet_cutoff']}",
            "coef": getattr(res, "estimate", None),
            "se": getattr(res, "se", None),
            "p": getattr(res, "pvalue", None),
        })
    return results


def _method_of(state: EconPaperState, main_spec: Dict[str, Any]) -> Optional[str]:
    raw = main_spec.get("method") if isinstance(main_spec, dict) else None
    if not raw:
        rd = state.get("research_direction")
        if isinstance(rd, dict):
            raw = rd.get("method")
    return norm_method(raw)


def _is_iv_formula(main_spec: Dict[str, Any]) -> bool:
    formula = str(main_spec.get("iv_formula") or main_spec.get("formula") or "")
    if "(" in formula and "~" in formula.split("(", 1)[-1]:
        return True
    instruments = main_spec.get("instruments") or []
    if isinstance(instruments, str):
        instruments = [instruments]
    if instruments:
        return True
    return bool(main_spec.get("instrument") or main_spec.get("instrument_col"))


def _refused_ols_battery() -> Dict[str, Any]:
    return {
        "robustness_results": {
            "produced_by": "robustness_check",
            "degraded": True,
            "reason": "ols_battery_on_non_ols",
            "diagnostics": [
                {
                    "test": "robustness_dispatch",
                    "status": "skipped",
                    "reason": "ols_battery_on_non_ols",
                }
            ],
            "robustness": [],
            "heterogeneity": [],
            "placebos": [],
            "summary_table": "未对非 OLS 方法套用 y ~ treat 的 OLS 稳健性套餐。",
        }
    }


def _run_iv_battery(
    df: Any,
    main_spec: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    formula = main_spec.get("iv_formula") or main_spec.get("formula")
    if not formula:
        return []
    treatment = main_spec.get("endogenous") or main_spec.get("treatment") or "treat"
    levels = list(main_spec.get("cluster_levels") or [])
    cluster = main_spec.get("cluster") or main_spec.get("cluster_col")
    if cluster and cluster not in levels:
        levels.append(cluster)
    try:
        import statspai
    except Exception as exc:
        diagnostics.append({"test": "ivreg", "status": "error", "error": str(exc)})
        return []

    results: List[Dict[str, Any]] = []
    targets = levels or [None]
    for level in targets:
        try:
            kwargs: Dict[str, Any] = {"data": df}
            if level:
                kwargs["cluster"] = level
            res = statspai.ivreg(str(formula), **kwargs)
        except Exception as exc:
            diagnostics.append({
                "test": "ivreg",
                "level": level,
                "status": "error",
                "error": str(exc),
            })
            continue
        results.append({
            "type": "iv_cluster",
            "level": level or "none",
            "coef": _coef_of(res, treatment),
            "se": _se_of(res, treatment),
            "p": _p_of(res, treatment),
        })
    return results


def _run_rd_battery(
    df: Any,
    main_spec: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    outcome = main_spec.get("outcome")
    running = main_spec.get("running_var")
    if not outcome or not running:
        return []
    try:
        cutoff = float(main_spec.get("cutoff") or 0)
    except (TypeError, ValueError):
        cutoff = 0.0
    try:
        import statspai
    except Exception as exc:
        diagnostics.append({"test": "rdrobust", "status": "error", "error": str(exc)})
        return []

    variants = [
        {"kernel": "triangular", "bwselect": "mserd", "donut": 0},
        {"kernel": "epanechnikov", "bwselect": "mserd", "donut": 0},
        {"kernel": "triangular", "bwselect": "mserd", "donut": 0.05},
    ]
    results: List[Dict[str, Any]] = []
    for variant in variants:
        try:
            res = statspai.rdrobust(
                df, y=outcome, x=running, c=cutoff, **variant
            )
        except Exception as exc:
            diagnostics.append({
                "test": "rdrobust",
                "status": "error",
                "error": str(exc),
                **variant,
            })
            continue
        results.append({
            "type": "rd_variant",
            "level": f"{variant['kernel']}/donut={variant['donut']}",
            "coef": getattr(res, "estimate", None),
            "se": getattr(res, "se", None),
            "p": getattr(res, "pvalue", None),
        })
    return results


def robustness_check(state: EconPaperState) -> Dict[str, Any]:
    """稳健性检验节点。

    读 ``state.main_specification``（可选）与 ``state.csv_path``，按下述
    套餐跑稳健性并汇总 Markdown 表格写 ``robustness_results``。若
    main_specification 缺失，返回占位 summary_table，不抛异常。
    """
    main_spec = state.get("main_specification")
    if not main_spec:
        return {
            "robustness_results": {
                "produced_by": "robustness_check",
                "diagnostics": [],
                "degraded": True,
                "reason": "no_main_specification",
                "summary_table": "No main specification available",
            }
        }

    if not isinstance(main_spec, dict):
        main_spec = {}
    method = _method_of(state, main_spec)
    cs_main = _is_cs_estimate(state)

    csv_path = state.get("csv_path")
    if not csv_path:
        return {
            "robustness_results": {
                "produced_by": "robustness_check",
                "diagnostics": [],
                "degraded": True,
                "reason": "no_csv_path",
                "summary_table": "No main specification available",
            }
        }

    if method in {"iv", "rd"} and (
        (method == "iv" and not _is_iv_formula(main_spec))
        or (method == "rd" and not (main_spec.get("running_var") and main_spec.get("outcome")))
    ):
        return _refused_ols_battery()

    levels = main_spec.get("cluster_levels") or []
    groups = main_spec.get("heterogeneity_groups") or []
    if not cs_main and method not in {"iv", "rd", "scm"} and not levels and not groups:
        return {
            "robustness_results": {
                "produced_by": "robustness_check",
                "diagnostics": [],
                "degraded": True,
                "reason": "no_cluster_or_groups",
                "robustness": [],
                "heterogeneity": [],
                "placebos": [],
                "summary_table": "No cluster_levels or heterogeneity_groups; OLS battery skipped.",
            }
        }

    import pandas as pd

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        return {
            "robustness_results": {
                "produced_by": "robustness_check",
                "diagnostics": [{"test": "read_csv", "status": "error", "error": str(exc)}],
                "degraded": True,
                "reason": "csv_unreadable",
                "robustness": [],
                "heterogeneity": [],
                "placebos": [],
                "summary_table": f"无法读取数据: {exc}",
            }
        }

    diagnostics: List[Dict[str, Any]] = []
    robustness: List[Dict[str, Any]] = []
    heterogeneity: List[Dict[str, Any]] = []
    placebos: List[Dict[str, Any]] = []
    reason: Optional[str] = None
    degraded = False

    if cs_main:
        robustness = _run_cs_battery(df, main_spec, diagnostics)
        if not robustness:
            degraded = True
            reason = "cs_battery_failed"
    elif method == "iv":
        robustness = _run_iv_battery(df, main_spec, diagnostics)
        if not robustness:
            degraded = True
            reason = "iv_battery_failed"
    elif method == "rd":
        robustness = _run_rd_battery(df, main_spec, diagnostics)
        if not robustness:
            degraded = True
            reason = "rd_battery_failed"
    elif method == "scm":
        placebos = _run_placebo(df, main_spec, "scm", diagnostics)
    else:
        robustness = _run_clustering(df, main_spec, diagnostics)
        heterogeneity = _run_heterogeneity(df, main_spec, diagnostics)
        placebos = _run_placebo(
            df,
            main_spec,
            method
            or (
                state.get("research_direction", {}).get("method")
                if isinstance(state.get("research_direction"), dict)
                else None
            ),
            diagnostics,
        )

    # 汇总 Markdown 表格：稳健性 + 异质性 + 安慰剂三块
    lines: List[str] = ["# 稳健性检验汇总", ""]
    lines.append("## 替代聚类")
    lines.append("| 检验 | 水平 | 系数 | SE | p |")
    lines.append("|------|------|------|----|---|")
    for rc in robustness:
        lines.append(
            f"| {rc.get('type', 'clustering')} | {rc.get('level', '—')} | "
            f"{_fmt(rc.get('coef'))} | {_fmt(rc.get('se'))} | {_fmt(rc.get('p'))} |"
        )
    if not robustness:
        lines.append("| — | — | — | — | — |")

    lines.append("")
    lines.append("## 异质性")
    lines.append("| 分组 | 交互系数 | p |")
    lines.append("|------|----------|---|")
    for hg in heterogeneity:
        lines.append(
            f"| {hg.get('group', '—')} | {_fmt(hg.get('interaction_coef'))} | "
            f"{_fmt(hg.get('p'))} |"
        )
    if not heterogeneity:
        lines.append("| — | — | — |")

    lines.append("")
    lines.append("## 安慰剂")
    lines.append("| 检验 | 要点 | 结果 |")
    lines.append("|------|------|------|")
    for pb in placebos:
        if pb.get("type") == "placebo_time":
            lines.append(
                f"| placebo_time | {pb.get('n_placebos', '—')} 个时点 | "
                f"显著占比 {pb.get('share_significant', '—')} |"
            )
        else:
            lines.append(
                f"| wild_cluster_bootstrap | β={_fmt(pb.get('beta_hat'))} | "
                f"bootstrap p={_fmt(pb.get('p_boot'))} |"
            )
    if not placebos:
        lines.append("| — | — | — |")

    spec_curve = None
    if not cs_main and method not in {"iv", "rd", "scm"}:
        try:
            from design.spec_curve import run_spec_curve_from_state

            spec_curve = run_spec_curve_from_state(
                {
                    "csv_path": csv_path,
                    "main_specification": main_spec,
                    "research_direction": state.get("research_direction"),
                }
            )
        except Exception as exc:  # pragma: no cover - 探索臂失败不挡主路径
            diagnostics.append({
                "test": "spec_curve",
                "status": "error",
                "error": str(exc),
            })

    if spec_curve and spec_curve.get("markdown"):
        lines.extend(["", spec_curve["markdown"]])

    if cs_main:
        lines.extend(["", "CS 主估计：未套用 y ~ treat 的 OLS 套餐。"])

    rr: Dict[str, Any] = {
        "produced_by": "robustness_check",
        "robustness": robustness,
        "heterogeneity": heterogeneity,
        "placebos": placebos,
        "diagnostics": diagnostics,
        "summary_table": "\n".join(lines),
    }
    if degraded:
        rr["degraded"] = True
        if reason:
            rr["reason"] = reason
    payload: Dict[str, Any] = {"robustness_results": rr}
    if spec_curve:
        payload["spec_curve"] = spec_curve
    return payload


__all__ = ["robustness_check"]