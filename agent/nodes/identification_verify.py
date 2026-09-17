"""identification_verify node -- 识别策略验真（AERS 体系）。

根据用户指定的因果识别方法（DiD / IV / RD / SCM），调用 StatsPAI 顶层
API 跑对应诊断：

- DiD：Goodman-Bacon 分解（``bacon_decomposition``）+ 交错 DiD 稳健估计
  （``callaway_santanna``，数据支持时）。
- IV：``iv_diag`` + ``effective_f_test``（first-stage F，F<10 为弱识别警告）。
- RD：``mccrary_test``（密度连续性，p>0.05 通过）+ ``rdrobust``。
- SCM：``synth_time_placebo``（时点安慰剂分布）。

每个诊断独立 try/except 降级：单次失败不阻塞整体，失败记录进
``diagnostics``，最终 ``passed`` 由所有诊断共同决定。节点不 import
fastapi，纯函数，输入 state 返回待合并的 dict，与现有节点风格一致。

判定口径集中在 ``agent/engine/identification_state.py``（issue #40 参谋意见
§2.2、§4）：这里只负责跑诊断、把每条检查的 ``status`` 记准，然后交给它算出
``execution`` / ``assessment`` / ``passed`` / ``star_rating`` / ``permissions``。
本节点不再自己算星级 —— 两份判定会漂移，而漂移正是「同一输入从不同入口得到不同
许可决定」的来源。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..engine.identification_state import (
    ASSESSMENT_INSUFFICIENT_EVIDENCE,
    ASSESSMENT_NOT_APPLICABLE,
    ASSESSMENT_RISK_FOUND,
    ASSESSMENT_RISK_NOT_FOUND,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    EXECUTION_NOT_RUN,
    EXECUTION_PARTIAL,
    ROLE_EFFECT_ESTIMATE,
    assess_diagnostics,
    permissions_for,
)
from ..state import EconPaperState

# 弱工具变量 first-stage F 阈值（Stock & Yogo 经验值）
WEAK_IV_F_THRESHOLD = 10.0
# McCrary 密度检验显著性阈值（p > alpha 视为不能拒绝密度连续 → 通过）
MANIPULATION_ALPHA = 0.05
# Goodman-Bacon 中已处理对照组权重占比上限（超过则建议改用稳健估计）
FORBIDDEN_WEIGHT_THRESHOLD = 0.1

# 各方法别名 → 规范化方法名
_METHOD_ALIASES = {
    "did": "did",
    "difference-in-differences": "did",
    "diff-in-diff": "did",
    "iv": "iv",
    "instrumental-variables": "iv",
    "instrumental-variable": "iv",
    "rd": "rd",
    "regression-discontinuity": "rd",
    "regression-discontinuity-design": "rd",
    "rdd": "rd",
    "scm": "scm",
    "synthetic-control": "scm",
    "synthetic control": "scm",
}


def _norm_method(method: Optional[str]) -> Optional[str]:
    """把方法别名归一化为 did / iv / rd / scm，未知方法返回 None。"""
    if not method:
        return None
    key = str(method).strip().lower()
    return _METHOD_ALIASES.get(key)


def _load_statspai(
    diagnostics: List[Dict[str, Any]],
    report_lines: List[str],
    test: str,
) -> Any:
    """Load StatsPAI. A missing package is a recorded skip, not an exception.

    Identification diagnostics have no pandas stand-in. Do not invent
    Bacon / IV / McCrary / SCM results when the library is absent.
    """
    try:
        import statspai
        return statspai
    except ImportError as exc:
        diagnostics.append({
            "test": test,
            "status": "error",
            "reason": "statspai_unavailable",
            "error": str(exc),
        })
        report_lines.append(
            "StatsPAI 未安装，跳过识别诊断，不编造因果检验结果。"
        )
        return None


def _diag_did(
    df: Any,
    d: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
    report_lines: List[str],
) -> bool:
    """交错 DiD 诊断：Goodman-Bacon 分解（+ 可选 Callaway-Sant'Anna）。"""
    outcome = d.get("outcome_col") or d.get("outcome")
    treatment = d.get("treatment_col") or d.get("treatment")
    time_col = d.get("time_col") or d.get("time")
    id_col = d.get("id_col") or d.get("id")
    if not all([outcome, treatment, time_col, id_col]):
        diagnostics.append({
            "test": "bacon_decomposition",
            "status": "skipped",
            "reason": "缺少 outcome/treatment/time/id 列配置",
        })
        report_lines.append("DiD: 缺少 outcome/treatment/time/id 列配置，跳过 Goodman-Bacon 分解。")
        return False

    statspai = _load_statspai(diagnostics, report_lines, "bacon_decomposition")
    if statspai is None:
        return False

    required_columns = [outcome, treatment, time_col, id_col]
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]
    if missing_columns:
        diagnostics.append({
            "test": "bacon_decomposition",
            "status": "skipped",
            "reason": "数据缺少必需列",
            "missing_columns": missing_columns,
        })
        report_lines.append(
            "DiD: 数据缺少必需列 " + ", ".join(missing_columns) + "，跳过分解。"
        )
        return False
    analysis_df = df.dropna(subset=required_columns)
    rows_dropped_missing = int(len(df) - len(analysis_df))
    sample_meta = {
        "n_obs": int(len(analysis_df)),
        "rows_dropped_missing": rows_dropped_missing,
    }
    if rows_dropped_missing:
        report_lines.append(
            "Goodman-Bacon 完整样本过滤: "
            f"删除必需列缺失的 {rows_dropped_missing} 行。"
        )

    passed = True
    try:
        bacon = statspai.bacon_decomposition(
            analysis_df, y=outcome, treat=treatment, time=time_col, id=id_col
        )
        negative_share = float(bacon.get("negative_weight_share", 0.0) or 0.0)
        already_share = float(
            bacon.get("already_treated_control_weight_share", 0.0) or 0.0
        )
        forbidden_share = negative_share + already_share
        ok = forbidden_share < FORBIDDEN_WEIGHT_THRESHOLD
        diagnostics.append({
            "test": "bacon_decomposition",
            "status": "pass" if ok else "fail",
            "beta_twfe": bacon.get("beta_twfe"),
            "negative_weight_share": negative_share,
            "already_treated_control_weight_share": already_share,
            "forbidden_weight_share": forbidden_share,
            "n_comparisons": bacon.get("n_comparisons"),
            **sample_meta,
        })
        report_lines.append(
            f"Goodman-Bacon 分解: TWFE β={bacon.get('beta_twfe'):.3f}, "
            f"forbidden 权重占比={forbidden_share:.1%}。"
        )
        if not ok:
            passed = False
            report_lines.append(
                "⚠️ 相当比例权重来自已处理比较（forbidden > "
                f"{FORBIDDEN_WEIGHT_THRESHOLD:.0%}），TWFE 可能被污染，"
                "建议改用 Callaway-Sant'Anna 稳健估计。"
            )
    except Exception as exc:  # pragma: no cover - 降级路径
        diagnostics.append({
            "test": "bacon_decomposition",
            "status": "error",
            "error": str(exc),
            **sample_meta,
        })
        report_lines.append(f"Goodman-Bacon 分解失败: {exc}")

    # 交错 DiD 稳健估计（可选，数据支持时）。
    # 记成 role="effect_estimate"：这是「估计出来是多少」，不是「设计站不站得住」。
    # 旧写法拿效应的 p<0.05 生成 pass、否则 warn，等于把显著性当成设计有效性，还会把
    # 缺失的 p 值经 `or 0.0` 折成 0 —— 于是没跑出 p 值反而判成显著通过。两条都去掉。
    if d.get("treatment_group_col") or d.get("first_treat_col"):
        g_col = d.get("treatment_group_col") or d.get("first_treat_col")
        try:
            cs_df = analysis_df.dropna(subset=[g_col])
            cs = statspai.callaway_santanna(
                cs_df, y=outcome, g=g_col, t=time_col, i=id_col
            )
            raw_p = getattr(cs, "pvalue", None)
            try:
                pvalue = float(raw_p) if raw_p is not None else None
            except (TypeError, ValueError):
                pvalue = None
            diagnostics.append({
                "test": "callaway_santanna",
                "role": ROLE_EFFECT_ESTIMATE,
                "status": "reported",
                "estimate": getattr(cs, "estimate", None),
                "pvalue": pvalue,
                # 缺失 p 值保留为未知，不当作 0，也不推断显著与否。
                "significant_at_0_05": (
                    None if pvalue is None else bool(pvalue < MANIPULATION_ALPHA)
                ),
            })
            report_lines.append(
                f"Callaway-Sant'Anna 估计: β={getattr(cs, 'estimate', None)}, "
                f"p={pvalue if pvalue is not None else '缺失'}（效应估计记录，"
                "不参与设计有效性判定）。"
            )
        except Exception as exc:  # pragma: no cover - 降级路径
            # 同样是效应估计这一支：它失败说明这个稳健估计没算出来，不等于
            # Goodman-Bacon 那条设计有效性检查没通过。记录保留、报告里说出来，
            # 但不冒充「设计有效性未核查」。
            diagnostics.append({
                "test": "callaway_santanna",
                "role": ROLE_EFFECT_ESTIMATE,
                "status": "error",
                "error": str(exc),
            })
            report_lines.append(f"Callaway-Sant'Anna 估计失败: {exc}")

    return passed


def _diag_iv(
    df: Any,
    d: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
    report_lines: List[str],
) -> bool:
    """IV 诊断：iv_diag（含 first-stage F / AR 置信集）+ effective_f_test。"""
    outcome = d.get("outcome_col") or d.get("outcome")
    endog = d.get("endogenous_col") or d.get("endogenous") or d.get("treatment_col")
    instrument = d.get("instrument_col") or d.get("instrument")
    if not all([outcome, endog, instrument]):
        diagnostics.append({
            "test": "iv_diag",
            "status": "skipped",
            "reason": "缺少 outcome/endogenous/instrument 列配置",
        })
        report_lines.append("IV: 缺少 outcome/endogenous/instrument 列配置，跳过诊断。")
        return False

    statspai = _load_statspai(diagnostics, report_lines, "iv_diag")
    if statspai is None:
        return False

    passed = True
    f_stat: Optional[float] = None
    try:
        res = statspai.iv_diag(df, y=outcome, endog=endog, instruments=instrument)
        f_stat = getattr(res, "first_stage_F", None)
        ar_pvalue = getattr(res, "ar_pvalue", None)
        if f_stat is not None:
            try:
                f_stat = float(f_stat)
            except (TypeError, ValueError):
                f_stat = None
        weak = f_stat is not None and f_stat < WEAK_IV_F_THRESHOLD
        diagnostics.append({
            "test": "iv_diag",
            "status": "warn" if weak else "pass",
            "first_stage_F": f_stat,
            "kp_rk_f": getattr(res, "kp_rk_f", None),
            "ar_pvalue": ar_pvalue,
            "ar_stat": getattr(res, "ar_stat", None),
            "beta_2sls": getattr(res, "beta_2sls", None),
        })
        report_lines.append(
            f"IV 诊断: first-stage F={f_stat if f_stat is not None else 'N/A'}, "
            f"Anderson-Rubin p={ar_pvalue}。"
        )
        if weak:
            passed = False
            report_lines.append(
                f"⚠️ first-stage F={f_stat:.1f} < {WEAK_IV_F_THRESHOLD}，"
                "存在弱工具变量风险，建议改用 Anderson-Rubin 置信集。"
            )
    except Exception as exc:  # pragma: no cover - 降级路径
        diagnostics.append({
            "test": "iv_diag",
            "status": "error",
            "error": str(exc),
        })
        report_lines.append(f"IV 诊断失败: {exc}")

    try:
        eff = statspai.effective_f_test(
            df,
            endog=endog,
            instruments=[instrument] if isinstance(instrument, str) else list(instrument),
        )
        eff_f = eff.get("F_eff")
        eff_weak = eff_f is not None and float(eff_f) < WEAK_IV_F_THRESHOLD
        diagnostics.append({
            "test": "effective_f_test",
            "status": "warn" if eff_weak else "pass",
            "F_eff": eff_f,
            "first_stage_F": eff.get("first_stage_F"),
            "strength": eff.get("strength"),
        })
        report_lines.append(
            f"有效 F 检验: F_eff={eff_f if eff_f is not None else 'N/A'}"
            f"（{eff.get('strength', '')}）。"
        )
        if eff_weak:
            passed = False
            report_lines.append(
                f"⚠️ effective F={eff_f:.1f} < {WEAK_IV_F_THRESHOLD}，弱识别告警。"
            )
    except Exception as exc:  # pragma: no cover - 降级路径
        diagnostics.append({
            "test": "effective_f_test",
            "status": "error",
            "error": str(exc),
        })
        report_lines.append(f"有效 F 检验失败: {exc}")

    return passed


def _diag_rd(
    df: Any,
    d: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
    report_lines: List[str],
) -> bool:
    """RD 诊断：McCrary 密度检验（连续性）+ rdrobust 对照估计。"""
    running = d.get("running_var") or d.get("running_variable")
    cutoff = d.get("cutoff", 0) or 0
    outcome = d.get("outcome_col") or d.get("outcome")
    if not running:
        diagnostics.append({
            "test": "mccrary_test",
            "status": "skipped",
            "reason": "缺少 running_var 配置",
        })
        report_lines.append("RD: 缺少 running_var 配置，跳过密度检验。")
        return False

    statspai = _load_statspai(diagnostics, report_lines, "mccrary_test")
    if statspai is None:
        return False

    passed = True
    try:
        c = float(cutoff)
    except (TypeError, ValueError):
        c = 0.0

    try:
        mcc = statspai.mccrary_test(df, x=running, c=c)
        pvalue = getattr(mcc, "pvalue", None)
        try:
            pvalue = float(pvalue)
        except (TypeError, ValueError):
            pvalue = None
        density_ok = pvalue is not None and pvalue > MANIPULATION_ALPHA
        diagnostics.append({
            "test": "mccrary_test",
            "status": "pass" if density_ok else "fail",
            "pvalue": pvalue,
            "se": getattr(mcc, "se", None),
            "estimate": getattr(mcc, "estimate", None),
        })
        report_lines.append(
            f"McCrary 密度检验: p={pvalue if pvalue is not None else 'N/A'}。"
        )
        if not density_ok:
            passed = False
            report_lines.append(
                "⚠️ 密度在 cutoff 处不连续（p≤0.05），可能存在操纵，"
                "建议改用 donut-hole RD 或部分识别界。"
            )
    except Exception as exc:  # pragma: no cover - 降级路径
        diagnostics.append({
            "test": "mccrary_test",
            "status": "error",
            "error": str(exc),
        })
        report_lines.append(f"McCrary 密度检验失败: {exc}")

    if outcome:
        try:
            rd = statspai.rdrobust(df, y=outcome, x=running, c=c)
            rd_p = getattr(rd, "pvalue", None)
            try:
                rd_p = float(rd_p)
            except (TypeError, ValueError):
                rd_p = None
            diagnostics.append({
                "test": "rdrobust",
                "status": "pass",
                "estimate": getattr(rd, "estimate", None),
                "se": getattr(rd, "se", None),
                "pvalue": rd_p,
                "ci": getattr(rd, "ci", None),
            })
            report_lines.append(
                f"RD 稳健估计: β={getattr(rd, 'estimate', None)}, "
                f"p={rd_p}。"
            )
        except Exception as exc:  # pragma: no cover - 降级路径
            diagnostics.append({
                "test": "rdrobust",
                "status": "error",
                "error": str(exc),
            })
            report_lines.append(f"RD 稳健估计失败: {exc}")

    return passed


def _diag_scm(
    df: Any,
    d: Dict[str, Any],
    diagnostics: List[Dict[str, Any]],
    report_lines: List[str],
) -> bool:
    """SCM 诊断：时点安慰剂（synth_time_placebo）收集安慰剂分布。"""
    outcome = d.get("outcome_col") or d.get("outcome")
    unit = d.get("unit_col") or d.get("unit")
    time_col = d.get("time_col") or d.get("time")
    treated_unit = d.get("treated_unit")
    treatment_time = d.get("treatment_time")
    if not all([outcome, unit, time_col, treatment_time is not None]):
        diagnostics.append({
            "test": "synth_time_placebo",
            "status": "skipped",
            "reason": "缺少 outcome/unit/time/treatment_time 配置",
        })
        report_lines.append("SCM: 缺少 outcome/unit/time/treatment_time 配置，跳过安慰剂检验。")
        return False

    statspai = _load_statspai(diagnostics, report_lines, "synth_time_placebo")
    if statspai is None:
        return False

    passed = True
    try:
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
            # 真实处理时点之后（或全样本）的安慰剂 p 值分布
            n = int(len(pvals))
            n_significant = int((pvals < MANIPULATION_ALPHA).sum())
            share_significant = n_significant / n if n else 0.0
            # 安慰剂 p 值大量显著说明潜在混淆 → 告警
            suspicious = share_significant > 0.5
            diagnostics.append({
                "test": "synth_time_placebo",
                "status": "warn" if suspicious else "pass",
                "n_placebos": n,
                "n_significant": n_significant,
                "share_significant": share_significant,
                "min_p": float(pvals.min()) if n else None,
                "median_p": float(pvals.median()) if n else None,
            })
            report_lines.append(
                f"SCM 时点安慰剂: {n} 个安慰剂时点，其中 {n_significant} 个 "
                f"p<0.05（占比 {share_significant:.0%}）。"
            )
            if suspicious:
                passed = False
                report_lines.append(
                    "⚠️ 超过半数安慰剂时点显著，处理效应可能混入时间趋势，"
                    "建议补充 in-space 安慰剂或稳健性检验。"
                )
        else:
            diagnostics.append({
                "test": "synth_time_placebo",
                "status": "warn",
                "reason": "无语数安慰剂时点",
            })
            report_lines.append("SCM 时点安慰剂未返回结果。")
    except Exception as exc:  # pragma: no cover - 降级路径
        diagnostics.append({
            "test": "synth_time_placebo",
            "status": "error",
            "error": str(exc),
        })
        report_lines.append(f"SCM 时点安慰剂失败: {exc}")

    return passed


_DISPATCH = {
    "did": _diag_did,
    "iv": _diag_iv,
    "rd": _diag_rd,
    "scm": _diag_scm,
}


_EXECUTION_TEXT = {
    EXECUTION_COMPLETED: "已完成",
    EXECUTION_PARTIAL: "只完成了一部分",
    EXECUTION_FAILED: "没有跑成",
    EXECUTION_NOT_RUN: "尚未运行",
}

_ASSESSMENT_TEXT = {
    ASSESSMENT_RISK_FOUND: "发现了需要处理的风险",
    ASSESSMENT_RISK_NOT_FOUND: "没有发现这类风险",
    ASSESSMENT_INSUFFICIENT_EVIDENCE: "证据不足，尚未核查",
    ASSESSMENT_NOT_APPLICABLE: "本次没有适用的检查",
}


def _build_report(report_lines: List[str], assessed: Dict[str, Any]) -> str:
    """把「执行到哪一步」和「发现了什么」分开写清楚。

    未知不能被写成通过，执行失败也不能被写成「该方法不成立」：前一句会把没核过的
    风险说成没风险，后一句会把基础设施问题说成科学结论。
    """
    lines = list(report_lines) if report_lines else ["无诊断结果。"]
    counts = assessed["counts"]
    execution = assessed["execution"]
    assessment = assessed["assessment"]
    star = assessed["star_rating"]
    evaluable = counts["pass"] + counts["warn"] + counts["fail"]

    lines.append(
        f"识别检查执行情况：{_EXECUTION_TEXT[execution]}"
        f"（可评估 {evaluable} 项：通过 {counts['pass']}、告警 {counts['warn']}、"
        f"不通过 {counts['fail']}；未跑成 {counts['error']}、跳过 {counts['skipped']}）"
    )
    lines.append(f"发现：{_ASSESSMENT_TEXT[assessment]}")
    if execution == EXECUTION_FAILED:
        lines.append(
            "诊断工具没有运行成功，识别策略的风险尚未核查；写作可继续，"
            "但不要据此声称识别已验真。"
        )

    if star is None:
        lines.append(
            "识别策略尚未评分：没有可评估的诊断"
            "（检查时间 / 个体 / 工具变量等列是否已指定）。未知不等于通过。"
        )
    else:
        lines.append(f"识别策略星级：{'★' * star}{'☆' * (3 - star)}（{star}星）")
        if star == 0:
            lines.append("⚠️ 0星：识别策略完全不可信，流程已截断，请调整研究设计后重试。")
        elif star == 1:
            lines.append("⚠️ 有诊断不通过，已标注；因果表述与主结果晋升需要用户确认。")
        elif star == 2:
            lines.append("⚠️ 存在识别风险，已标注并在后续步骤中披露。")

    if assessment == ASSESSMENT_RISK_NOT_FOUND:
        lines.append("结论：跑到的检查都没有发现问题；这不等于风险不存在。")
    return "\n".join(lines)


def _diag_payload(
    *,
    strategy: Any,
    diagnostics: List[Dict[str, Any]],
    report: str,
    execution: str,
    assessment: str,
    passed: Optional[bool],
    star_rating: Optional[int],
) -> Dict[str, Any]:
    """三轴状态 + 展示字段 + 许可，一次组装，结构恒定。"""
    return {
        "strategy": strategy,
        "diagnostics": diagnostics,
        "execution": execution,
        "assessment": assessment,
        "passed": passed,
        "star_rating": star_rating,
        "permissions": permissions_for(
            assessment=assessment,
            star_rating=star_rating,
            has_failures=passed is False,
            hard_block=star_rating == 0,
        ),
        "report": report,
    }


def identification_verify(state: EconPaperState) -> Dict[str, Any]:
    """识别策略验证节点。

    读取 ``state.research_direction``（dict）与 ``state.csv_path``，按
    method 分派到 StatsPAI 诊断，收集 ``diagnostics`` 并生成自然语言
    ``report``。写入 ``identification_diag``（含 strategy / diagnostics /
    execution / assessment / passed / star_rating / permissions / report）
    与 ``identification_failed``。

    ``identification_failed`` 只表示**硬阻断**（0 星或没有数据）。跑不成、跑不全
    一律不是硬阻断：``passed`` 写 ``None``（未知），由 ``permissions`` 说明未知状态
    下允许做什么。评估档位与许可口径见
    ``agent/engine/identification_state.py``。

    边界：无 research_direction 或 csv_path 时返回空或
    ``identification_failed=True``；数据读取失败降级为 failed 报告，不抛异常。
    """
    research_direction = state.get("research_direction")
    if not research_direction:
        # 尚未选方向：全自动链路（run_upload_pipeline）在 set_direction 前
        # 也会跑到这里。此时不应标记"识别失败"（会污染语义），返回良性
        # 非空字段以满足 LangGraph 要求（空 dict 会抛 InvalidUpdateError）。
        return {"research_direction": research_direction}

    d = research_direction if isinstance(research_direction, dict) else {}
    method = _norm_method(d.get("method"))
    if not method:
        raw = str(d.get("method") or "").strip()
        report = (
            "当前方法没有对应的识别诊断套餐（支持 DiD / IV / RD / SCM）。"
            "写作可继续；主张按相关或关联表述，不要写成因果识别。"
            if raw
            else "尚未指定可诊断的识别方法（DiD / IV / RD / SCM）。写作可继续。"
        )
        # 没有可诊断的方法：不是「通过」，也不是「不通过」——本次没有适用的检查。
        return {
            "identification_diag": _diag_payload(
                strategy=raw.lower() or None,
                diagnostics=[],
                report=report,
                execution=EXECUTION_NOT_RUN,
                assessment=ASSESSMENT_NOT_APPLICABLE,
                passed=None,
                star_rating=None,
            ),
            "identification_failed": False,
            "star_rating": None,
        }

    csv_path = state.get("csv_path")
    if not csv_path:
        # 没有数据就无法评估，而且必须停下：这一档是产品已定的「未挂数据不许跑估计」，
        # 不是识别诊断给出的科学结论，所以用 execution=not_run 而不是假装跑了 0 星。
        return {
            "identification_diag": _diag_payload(
                strategy=method,
                diagnostics=[],
                report="还没有数据文件，无法验真识别。请先上传 CSV。",
                execution=EXECUTION_NOT_RUN,
                assessment=ASSESSMENT_INSUFFICIENT_EVIDENCE,
                passed=False,
                star_rating=0,
            ),
            "identification_failed": True,
            "star_rating": 0,
        }

    import pandas as pd

    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:
        return {
            "identification_diag": _diag_payload(
                strategy=method,
                diagnostics=[],
                report=f"无法读取数据: {exc}",
                execution=EXECUTION_FAILED,
                assessment=ASSESSMENT_INSUFFICIENT_EVIDENCE,
                passed=False,
                star_rating=0,
            ),
            "identification_failed": True,
            "star_rating": 0,
        }

    diagnostics: List[Dict[str, Any]] = []
    report_lines: List[str] = []
    # 分派函数的返回值不参与判定：设计有效性以每条诊断的 status 为准。留两条会漂移。
    _DISPATCH[method](df, d, diagnostics, report_lines)

    assessed = assess_diagnostics(diagnostics)
    star_rating = assessed["star_rating"]
    report = _build_report(report_lines, assessed)
    out: Dict[str, Any] = {
        "identification_diag": _diag_payload(
            strategy=method,
            diagnostics=diagnostics,
            report=report,
            execution=assessed["execution"],
            assessment=assessed["assessment"],
            passed=assessed["passed"],
            star_rating=star_rating,
        ),
        # 只有 0 星是硬阻断。全 warn、全 error、全 skipped 都不停流程。
        "identification_failed": star_rating == 0,
        "star_rating": star_rating,
    }
    if any(item.get("reason") == "statspai_unavailable" for item in diagnostics):
        out["degradations"] = list(state.get("degradations") or []) + [
            {
                "node": "identification_verify",
                "reason": "statspai_unavailable",
                "fallback": "skip_diagnostics",
                "visible": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]
    return out


__all__ = ["identification_verify"]
