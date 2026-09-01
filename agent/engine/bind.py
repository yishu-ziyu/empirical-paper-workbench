"""Project node products into chapter-prompt kwargs.

Truth for overlapping keys comes from state written by graph nodes,
not from HTTP or client-supplied placeholders.
"""
from __future__ import annotations

import json
import math
from numbers import Real
from typing import Any, Iterable, Mapping

from .data_eda import compute_csv_eda
from .readiness import claim_mode


_MISSING = "未提供"
_CAUSAL_METHOD_ALIASES = {
    "did": "did",
    "iv": "iv",
    "rd": "rd",
    "rdd": "rd",
    "scm": "scm",
}
_CAUSAL_ESTIMATORS = {
    "did": frozenset({"statspai.feols", "statspai.callaway_santanna"}),
    "iv": frozenset({"statspai.ivreg"}),
    "rd": frozenset({"statspai.rdrobust"}),
    "scm": frozenset({"statspai.synth"}),
}
_FAILED_IDENTIFICATION_STATUSES = {
    "degraded",
    "error",
    "failed",
    "failure",
    "blocked",
}
_PASSED_STATUSES = {"ok", "pass", "passed", "success"}
_FAILURE_TEXT_MARKERS = (
    "not actually verified",
    "not verified",
    "unverified",
    "not run",
    "not-run",
    "skipped",
    "fallback",
    "degraded",
    "failed",
    "failure",
    "error",
    "blocked",
    "mock",
    "placeholder",
    "未验证",
    "未通过",
    "未运行",
    "失败",
    "跳过",
    "降级",
    "回退",
    "错误",
    "阻塞",
    "模拟",
    "占位",
)
_FAILURE_FLAG_NAMES = {
    "degraded",
    "error",
    "fail",
    "failed",
    "failure",
    "fallback",
    "mock",
    "placeholder",
    "skipped",
}
_BAD_PROVENANCE_MARKERS = {"fallback", "mock", "placeholder"}
_ROBUSTNESS_STAT_FIELDS = {
    "clustering": frozenset({"coef", "se", "p"}),
    "cs_variant": frozenset({"coef", "se", "p"}),
    "iv_cluster": frozenset({"coef", "se", "p"}),
    "rd_variant": frozenset({"coef", "se", "p"}),
    "placebo_time": frozenset(
        {
            "n_placebos",
            "n_significant",
            "share_significant",
            "min_p",
            "median_p",
        }
    ),
    "wild_cluster_bootstrap": frozenset(
        {
            "beta_hat",
            "se_cluster",
            "p_boot",
            "p_cluster",
            "ci_boot",
            "n_clusters",
        }
    ),
}


def _has_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Mapping, list, tuple, set, frozenset)):
        return bool(value)
    return bool(value)


def _signals_failure(value: Any) -> bool:
    if not isinstance(value, str):
        return _has_value(value)
    normalized = value.strip().lower()
    return bool(normalized) and any(
        marker in normalized for marker in _FAILURE_TEXT_MARKERS
    )


def _is_failure_flag(key: str, value: Any) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    if normalized in _FAILURE_FLAG_NAMES:
        return _has_value(value)
    tokens = set(normalized.split("_"))
    marks_failure = bool(tokens & _FAILURE_FLAG_NAMES)
    is_flag_shape = (
        normalized.startswith(("has_", "is_", "used_", "was_"))
        or normalized.endswith(("_flag", "_used", "_failed", "_failure"))
    )
    return marks_failure and is_flag_shape and _has_value(value)


def _is_bad_provenance(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower().replace("-", "_").replace(".", "_")
    tokens = set(normalized.split("_"))
    return bool(tokens & _BAD_PROVENANCE_MARKERS)


def _evidence_tree_is_successful(value: Any) -> bool:
    """Reject explicit failure or synthetic markers anywhere in evidence."""
    if isinstance(value, Mapping):
        if "status" in value:
            status = str(value.get("status") or "").strip().lower()
            if status not in _PASSED_STATUSES:
                return False
        if "passed" in value and value.get("passed") is not True:
            return False
        if "success" in value and value.get("success") is not True:
            return False
        for raw_key, child in value.items():
            key = str(raw_key).strip().lower()
            if key == "error" and _has_value(child):
                return False
            if key in {"reason", "message"} and _signals_failure(child):
                return False
            if _is_failure_flag(key, child):
                return False
            if key in {"source", "type", "mode"} and _is_bad_provenance(child):
                return False
            if isinstance(
                child, (Mapping, list, tuple)
            ) and not _evidence_tree_is_successful(child):
                return False
        return True
    if isinstance(value, (list, tuple)):
        return all(_evidence_tree_is_successful(item) for item in value)
    return True


def _is_finite_real(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, Real) and math.isfinite(float(value))


def _is_ordered_interval(lower: Any, upper: Any) -> bool:
    return (
        _is_finite_real(lower)
        and _is_finite_real(upper)
        and float(lower) <= float(upper)
    )


def _is_finite_statistic(value: Any) -> bool:
    if _is_finite_real(value):
        return True
    if isinstance(value, (list, tuple)):
        return len(value) == 2 and _is_ordered_interval(value[0], value[1])
    if isinstance(value, Mapping):
        for low, high in (
            ("lower", "upper"),
            ("low", "high"),
            ("left", "right"),
            ("ci_low", "ci_high"),
        ):
            if low in value and high in value:
                return _is_ordered_interval(value[low], value[high])
    return False


def _is_real_robustness_row(row: Any) -> bool:
    if not isinstance(row, Mapping) or not row:
        return False
    row_type = str(row.get("type") or "").strip().lower()
    stat_fields = _ROBUSTNESS_STAT_FIELDS.get(row_type)
    if stat_fields is None or not _evidence_tree_is_successful(row):
        return False
    statistics = [row.get(key) for key in stat_fields if key in row]
    return bool(statistics) and all(
        _is_finite_statistic(value) for value in statistics
    )


def _first_text(source: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = source.get(key)
        if value in (None, "", [], {}):
            continue
        if isinstance(value, (list, tuple)):
            return "、".join(str(item) for item in value)
        return str(value)
    return _MISSING


def format_data_provenance(state: Mapping[str, Any]) -> str:
    """Expose uploaded dataset metadata without inferring survey provenance."""
    datasets = state.get("uploaded_datasets") or []
    entries = [entry for entry in datasets if isinstance(entry, Mapping)]
    if not entries:
        entries = [{}]

    blocks: list[str] = []
    for index, entry in enumerate(entries, start=1):
        prefix = f"数据集 {index}\n" if len(entries) > 1 else ""
        rows = _first_text(entry, "rows")
        columns = _first_text(entry, "columns")
        blocks.append(
            prefix
            + "\n".join(
                [
                    f"数据集名称：{_first_text(entry, 'name')}",
                    f"调查机构：{_first_text(entry, 'institution', 'organization', 'provider')}",
                    f"调查年份/覆盖时段：{_first_text(entry, 'survey_years', 'years', 'period', 'coverage_period')}",
                    f"抽样框/抽样设计：{_first_text(entry, 'sampling_frame', 'sampling_design')}",
                    f"样本行数：{rows}",
                    f"字段：{columns}",
                ]
            )
        )
    return "\n\n".join(blocks)


def format_variable_roles(state: Mapping[str, Any]) -> str:
    """Expose only variable roles explicitly assigned in research_direction."""
    rd = state.get("research_direction") or {}
    if not isinstance(rd, Mapping):
        rd = {}

    def role_text(key: str) -> str:
        if key not in rd or rd.get(key) in (None, "", {}):
            return _MISSING
        value = rd.get(key)
        if isinstance(value, (list, tuple)):
            if not value:
                return "无（state 明确为空）" if key == "controls" else _MISSING
            return "、".join(str(item) for item in value)
        return str(value)

    return "\n".join(
        [
            f"因变量：{role_text('dv')}",
            f"自变量：{role_text('iv')}",
            f"控制变量：{role_text('controls')}",
        ]
    )


def _controls_text(state: Mapping[str, Any]) -> str:
    spec = state.get("main_specification") or {}
    rd = state.get("research_direction") or {}
    for source in (spec, rd):
        if not isinstance(source, Mapping) or "controls" not in source:
            continue
        controls = source.get("controls")
        if controls in (None, ""):
            return _MISSING
        if isinstance(controls, str):
            return controls.strip() or "无（state 明确为空）"
        if isinstance(controls, (list, tuple)):
            return "、".join(str(item) for item in controls) or "无（state 明确为空）"
        return str(controls)
    return _MISSING


def _covariance_text(estimate: Mapping[str, Any]) -> str:
    explicit = _first_text(estimate, "covariance", "cov_type", "vcov")
    if explicit != _MISSING:
        return explicit
    cluster = estimate.get("cluster")
    if cluster not in (None, ""):
        return f"按 {cluster} 聚类的标准误"
    return "未提供（不得据此写成 HC1、聚类稳健或其他设定）"


def format_estimate_facts(
    state: Mapping[str, Any], *, effective_claim: str | None = None
) -> str:
    """Project the executed estimate and its design inputs into one fact block."""
    estimate = state.get("estimate") or {}
    if not isinstance(estimate, Mapping):
        estimate = {}
    return "\n".join(
        [
            f"主张类型：{effective_claim or claim_mode(dict(state))}",
            f"估计状态：{_first_text(estimate, 'status')}",
            f"真实公式：{_first_text(estimate, 'formula')}",
            f"控制变量：{_controls_text(state)}",
            f"估计器：{_first_text(estimate, 'estimator')}",
            f"协方差/标准误设定：{_covariance_text(estimate)}",
            f"N：{_first_text(estimate, 'n')}",
            f"主处理变量行：{_first_text(estimate, 'treatment_row')}",
        ]
    )


def _canonical_causal_method(value: Any) -> str | None:
    method = str(value or "").strip().lower()
    return _CAUSAL_METHOD_ALIASES.get(method)


def _is_supported_causal_estimator(method: str, estimator: Any) -> bool:
    normalized = str(estimator or "").strip().lower()
    return normalized in _CAUSAL_ESTIMATORS.get(method, frozenset())


def _identification_failed(state: Mapping[str, Any]) -> bool:
    if state.get("identification_failed") is True or state.get("star_rating") == 0:
        return True
    diag = state.get("identification_diag") or {}
    if not isinstance(diag, Mapping):
        return False
    if diag.get("passed") is False or diag.get("degraded") is True:
        return True
    status = str(diag.get("status") or "").strip().lower()
    return status in _FAILED_IDENTIFICATION_STATUSES


def _identification_passed(state: Mapping[str, Any], method: str) -> bool:
    """Accept only a production-shaped, explicitly successful diagnosis."""
    if _identification_failed(state):
        return False
    diag = state.get("identification_diag") or {}
    if (
        not isinstance(diag, Mapping)
        or not _evidence_tree_is_successful(diag)
        or diag.get("passed") is not True
    ):
        return False
    if _canonical_causal_method(diag.get("strategy")) != method:
        return False
    rating = diag.get("star_rating")
    if isinstance(rating, bool) or not isinstance(rating, int) or rating != 3:
        return False
    state_rating = state.get("star_rating")
    if (
        isinstance(state_rating, bool)
        or not isinstance(state_rating, int)
        or state_rating != rating
    ):
        return False
    diagnostics = diag.get("diagnostics")
    if not isinstance(diagnostics, list) or not diagnostics:
        return False
    return all(
        isinstance(item, Mapping)
        and str(item.get("status") or "").strip().lower() in _PASSED_STATUSES
        and _evidence_tree_is_successful(item)
        for item in diagnostics
    )


def _robustness_passed(state: Mapping[str, Any]) -> bool:
    """Normalize the current robustness node output into a conservative pass."""
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, Mapping) or rob.get("produced_by") != "robustness_check":
        return False
    if not _evidence_tree_is_successful(rob):
        return False
    diagnostics = rob.get("diagnostics")
    if not isinstance(diagnostics, list):
        return False
    for item in diagnostics:
        if not isinstance(item, Mapping):
            return False
        status = str(item.get("status") or "").strip().lower()
        if status not in _PASSED_STATUSES or not _evidence_tree_is_successful(item):
            return False

    result_rows: list[Any] = []
    for key in ("robustness", "placebos"):
        rows = rob.get(key)
        if not isinstance(rows, list):
            return False
        result_rows.extend(rows)
    if not result_rows:
        return False
    return all(_is_real_robustness_row(row) for row in result_rows)


def identification_status(state: Mapping[str, Any]) -> str:
    diag = state.get("identification_diag") or {}
    if not isinstance(diag, Mapping) or not diag:
        return _MISSING
    if _identification_failed(state):
        return "failed/degraded（识别失败，不能支持因果主张）"
    method = _canonical_causal_method(diag.get("strategy"))
    if method is not None and _identification_passed(state, method):
        return "已通过（只可转述 state 中明确提供的验真证据）"
    return "未验证/未提供（不能据此判断假设已满足）"


def method_execution_binding(
    state: Mapping[str, Any], requested_method: Any, requested_claim: str
) -> tuple[str, str]:
    """Resolve the methods claim from the executed estimator, not the request."""
    if requested_claim != "causal_with_caveat":
        return "association", "执行边界：当前有效主张为 association。"

    requested = _canonical_causal_method(requested_method)
    estimate = state.get("estimate") or {}
    if not isinstance(estimate, Mapping):
        estimate = {}
    actual_method = _canonical_causal_method(estimate.get("method"))
    status = str(estimate.get("status") or "").strip().lower()
    estimator = str(estimate.get("estimator") or "").strip()
    executed = (
        requested is not None
        and status == "ok"
        and actual_method == requested
        and _is_supported_causal_estimator(requested, estimator)
    )
    identification_passed = requested is not None and _identification_passed(
        state, requested
    )
    robustness_passed = _robustness_passed(state)
    if executed and identification_passed and robustness_passed:
        return (
            requested_claim,
            f"执行边界：请求方法 {requested} 已由实际估计器 {estimator} "
            "以 status=ok 执行，且识别与稳健性证据已明确通过；"
            "因果表述仍受已绑定证据边界约束。",
        )
    if executed:
        missing_evidence = []
        if not identification_passed:
            missing_evidence.append("识别证据未明确通过")
        if not robustness_passed:
            missing_evidence.append("稳健性证据未明确通过")
        return (
            "association",
            f"执行边界：请求方法 {requested} 虽已执行，但"
            + "、".join(missing_evidence)
            + "；"
            "实际结果不能支持因果主张，有效主张降级为 association。",
        )
    shown_method = requested or str(requested_method or "未提供").strip().lower()
    actual = str(estimate.get("method") or "未提供").strip().lower()
    shown_status = status or "未提供"
    shown_estimator = estimator or "未提供"
    return (
        "association",
        f"执行边界：请求方法 {shown_method} 未成功执行；"
        f"实际方法 {actual}，估计状态 {shown_status}，估计器 {shown_estimator}。"
        "实际结果不能支持因果主张，只支持 association；"
        "不能撰写因果识别策略或声称识别假设已满足。",
    )


def robustness_status(state: Mapping[str, Any]) -> str:
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, Mapping) or not rob:
        return "未运行"
    ran = rob.get("produced_by") == "robustness_check" or "diagnostics" in rob
    if not ran:
        return "未运行"
    if rob.get("degraded"):
        reason = rob.get("reason") or "未提供原因"
        return f"已运行但降级，证据不足（原因：{reason}）"
    if _robustness_passed(state):
        return "已运行且明确通过；只能依据下方已绑定结果判断"
    diagnostics = rob.get("diagnostics") or []
    if diagnostics or str(rob.get("status") or "").strip():
        return "已运行，但存在未通过、跳过或错误的检查，证据不足"
    rows = rob.get("robustness") or []
    placebos = rob.get("placebos") or []
    if not rows and not placebos:
        return "已运行，但未提供可支持“结果稳健”的稳健性结果"
    return "已运行，但现有结构不能明确证明通过"


def format_heterogeneity_evidence(state: Mapping[str, Any]) -> str:
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, Mapping):
        return "未运行/未提供"
    rows = rob.get("heterogeneity") or []
    if not isinstance(rows, list) or not rows:
        return "未运行/未提供"
    return json.dumps(rows, ensure_ascii=False, sort_keys=True)


def format_policy_evidence(state: Mapping[str, Any]) -> str:
    evidence = state.get("policy_evidence")
    if evidence in (None, "", [], {}):
        return _MISSING
    if isinstance(evidence, (Mapping, list, tuple)):
        return json.dumps(evidence, ensure_ascii=False, sort_keys=True)
    return str(evidence)


def format_entries(entries: Iterable[Any]) -> str:
    """Turn literature_entries into a prompt-facing reference list."""
    lines: list[str] = []
    for entry in entries or []:
        if not isinstance(entry, Mapping):
            continue
        authors = entry.get("authors") or []
        if isinstance(authors, (list, tuple)):
            author_str = ", ".join(str(a) for a in authors if a)
        else:
            author_str = str(authors)
        year = entry.get("year")
        year_str = str(year) if year not in (None, "") else "n.d."
        title = str(entry.get("title") or "").strip()
        if author_str and title:
            lines.append(f"{author_str} ({year_str}). {title}.")
        elif title:
            lines.append(f"({year_str}). {title}.")
        elif author_str:
            lines.append(f"{author_str} ({year_str}).")
    return "\n".join(lines)


def bind_chapter_kwargs(state: Mapping[str, Any], chapter_spec: Mapping[str, Any]) -> dict:
    rd = state.get("research_direction") or {}
    if not isinstance(rd, Mapping):
        rd = {}
    spec = chapter_spec if isinstance(chapter_spec, Mapping) else {}
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, Mapping):
        rob = {}
    diag = state.get("identification_diag") or {}
    if not isinstance(diag, Mapping):
        diag = {}
    data_summary, eda_results = "", ""
    chapter_type = str(spec.get("type") or "")
    if chapter_type == "data_desc":
        data_summary, eda_results = compute_csv_eda(state)
    requested_method = spec.get("method") or rd.get("method") or ""
    requested_claim = claim_mode(dict(state))
    claim_method = rd.get("method") or requested_method
    effective_claim, execution_notice = method_execution_binding(
        state, claim_method, requested_claim
    )
    return {
        "research_question": rd.get("question") or state.get("research_question") or "",
        "method": requested_method,
        "results": state.get("results") or "",
        "robustness_table": rob.get("summary_table") or "",
        "key_references": format_entries(state.get("literature_entries") or []),
        "citation_indices": state.get("citation_indices") or {},
        "star_rating": state.get("star_rating"),
        "claim": effective_claim,
        "identification_report": diag.get("report") or "",
        "identification_status": identification_status(state),
        "data_summary": data_summary,
        "eda_results": eda_results,
        "data_provenance": format_data_provenance(state),
        "variable_roles": format_variable_roles(state),
        "estimate_facts": format_estimate_facts(
            state, effective_claim=effective_claim
        ),
        "method_execution_notice": execution_notice,
        "robustness_status": robustness_status(state),
        "heterogeneity_evidence": format_heterogeneity_evidence(state),
        "policy_evidence": format_policy_evidence(state),
    }
