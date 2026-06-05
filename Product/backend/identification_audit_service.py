"""Identification audit service — 6th tab (identification-audit) real statspai diagnostics.

Task 44 (ui-gap-fill): 把占位 tab 接到 statspai 真实诊断, 同时保留失败兜底.

Inputs:
    results_path: path to results.json (执行实验产物)
    design_path: path to design.json (方法设计产物)

Output (structured):
    {
      "method": "IV" | "DID" | ...,
      "pretrend": {
        "joint_pvalue": float | None,
        "joint_statistic": float | None,
        "n_pre_periods": int | None,
        "coefficients": [{"period": int, "estimate": float, "se": float, "pvalue": float, "ci_lower": float, "ci_upper": float}],
        "source": "statspai" | "results_json" | "unavailable"
      },
      "weak_iv": {
        "partial_r2": float | None,
        "f_statistic": float | None,
        "n_obs": int | None,
        "ar_pvalue": float | None,
        "ar_ci_lower": float | None,
        "ar_ci_upper": float | None,
        "source": "statspai" | "results_json" | "unavailable"
      },
      "dag": {
        "spec": str,            # raw DAG edge spec
        "mermaid": str,         # rendered mermaid text
        "adjustment_sets": list[list[str]],
        "source": "statspai" | "design_json" | "unavailable"
      }
    }

失败兜底 (BDD 行为 3): 任何 IO 错误 / statspai 不可用 / 字段缺失
— 不抛 500, 返回 dict with `error`/`reason` keys, 字段值一律 None / unavailable.
前端据此展示 N/A, 不崩.

业务背景: 用户的 1 大痛点是把 reduced-form 当 IV-2SLS 报告.
所以 weak_iv 必须含 AR (size-correct under weak IV), 优先 AR p-value 而非裸 F.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class IdentificationAuditError(Exception):
    """Base error for identification audit failures. 端点会转成 4xx/5xx, 但 service 层总是返回结构化 dict."""


# ── 路径解析 ──────────────────────────────────────────────────────────────
def _resolve(path_str: str) -> Path:
    """把传入 path 解析成绝对路径. 支持相对路径 (相对 REPO_ROOT) 和 ~. 失败抛 IdentificationAuditError."""
    if not path_str or not isinstance(path_str, str):
        raise IdentificationAuditError("path is required")
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        # 相对路径: 相对 REPO_ROOT (Product/backend/identification_audit_service.py → 4 up = REPO_ROOT)
        repo_root = Path(__file__).resolve().parents[2]
        p = repo_root / p
    return p


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    """安全读 JSON — 缺文件 / 解析失败 / 顶层不是 dict 都返回 None, 不抛."""
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except (OSError, json.JSONDecodeError):
        return None


# ── statspai 调用 (optional dependency) ───────────────────────────────────
def _try_import_statspai() -> Any:
    """尝试 import statspai — 失败返回 None. 不抛."""
    try:
        import sys
        repo_root = Path(__file__).resolve().parents[2]
        sp_path = repo_root.parent / "StatsPAI"
        # repo root 可能在不同位置, 多试几处
        candidates = [
            sp_path,
            repo_root / "StatsPAI",
            Path("/Users/mahaoxuan/Desktop/经济学论文/StatsPAI"),
        ]
        for c in candidates:
            if c.exists() and str(c) not in sys.path:
                sys.path.insert(0, str(c))
        import statspai as sp  # type: ignore[import-untyped]
        return sp
    except Exception:
        return None


def _extract_pretrend_from_results(results: dict[str, Any]) -> dict[str, Any] | None:
    """从 results.json 提取 event-study 系数 (如果执行端有写).

    支持的 schema:
      results["event_study"] / results["pretrends"] / results["diagnostics"]["event_study"]
    每个 coef 至少含: period, estimate, se
    """
    candidate = (
        results.get("event_study")
        or results.get("pretrends")
        or (results.get("diagnostics") or {}).get("event_study")
    )
    if not isinstance(candidate, dict):
        return None
    coefs_raw = (
        candidate.get("coefficients")
        or candidate.get("coefs")
        or candidate.get("estimates")
    )
    if not isinstance(coefs_raw, list) or not coefs_raw:
        return None
    out: list[dict[str, Any]] = []
    for c in coefs_raw:
        if not isinstance(c, dict):
            continue
        try:
            out.append({
                "period": int(c.get("period") or c.get("relative_time") or c.get("t") or 0),
                "estimate": float(c.get("estimate") or c.get("coef") or 0.0),
                "se": float(c.get("se") or c.get("std_error") or 0.0),
                "pvalue": c.get("pvalue"),
                "ci_lower": c.get("ci_lower"),
                "ci_upper": c.get("ci_upper"),
            })
        except (TypeError, ValueError):
            continue
    if not out:
        return None
    pre_coefs = [c for c in out if c["period"] < 0]
    return {
        "joint_pvalue": candidate.get("joint_pvalue") or candidate.get("pvalue"),
        "joint_statistic": candidate.get("joint_statistic") or candidate.get("statistic"),
        "n_pre_periods": len(pre_coefs),
        "coefficients": out,
    }


def _extract_weak_iv_from_results(results: dict[str, Any]) -> dict[str, Any] | None:
    """从 results.json 提取 weak-IV 诊断数字.

    支持 schema:
      results["first_stage"] / results["weak_iv"] / results["diagnostics"]["first_stage"]
    """
    candidate = (
        results.get("first_stage")
        or results.get("weak_iv")
        or (results.get("diagnostics") or {}).get("first_stage")
        or (results.get("diagnostics") or {}).get("weak_iv")
    )
    if not isinstance(candidate, dict):
        return None
    out: dict[str, Any] = {}
    for src_key, dst_key in (
        ("partial_r2", "partial_r2"),
        ("partial_r_squared", "partial_r2"),
        ("f_statistic", "f_statistic"),
        ("f_stat", "f_statistic"),
        ("f_eff", "f_statistic"),
        ("n_obs", "n_obs"),
        ("ar_pvalue", "ar_pvalue"),
        ("ar_p_value", "ar_pvalue"),
        ("ar_ci_lower", "ar_ci_lower"),
        ("ar_ci_upper", "ar_ci_upper"),
    ):
        v = candidate.get(src_key)
        if v is None:
            continue
        try:
            out[dst_key] = float(v)
        except (TypeError, ValueError):
            continue
    if not out:
        return None
    # n_obs 允许 int
    n_obs = candidate.get("n_obs")
    if isinstance(n_obs, int) and "n_obs" not in out:
        out["n_obs"] = n_obs
    return out


def _extract_dag_from_design(design: dict[str, Any]) -> dict[str, Any] | None:
    """从 design.json 提取 DAG 信息 (如果 design spec 有)."""
    # 设计 spec 里可能写: identification_strategy.causal_graph
    ident = design.get("identification_strategy") or design.get("identification") or {}
    candidate = (
        ident.get("causal_graph")
        or ident.get("dag")
        or design.get("dag")
        or design.get("causal_graph")
    )
    if isinstance(candidate, str) and candidate.strip():
        return {"spec": candidate.strip()}
    if isinstance(candidate, dict):
        spec = candidate.get("spec") or candidate.get("edges")
        if isinstance(spec, str) and spec.strip():
            return {"spec": spec.strip()}
    return None


# ── statspai 真实诊断 (用 _try_import_statspai 拿到的 sp) ────────────────
def _run_pretrends_statspai(sp: Any, result_obj: Any) -> dict[str, Any] | None:
    """如果有可用的 CausalResult 对象, 调 sp.pretrends_test 拿联合 p."""
    try:
        out = sp.pretrends_test(result_obj)
    except Exception:
        return None
    if not isinstance(out, dict):
        return None
    return {
        "joint_pvalue": out.get("pvalue"),
        "joint_statistic": out.get("statistic"),
        "n_pre_periods": None,
        "coefficients": [],  # statspai pretrends_test 不直接给 coef 表
    }


def _render_dag_mermaid(sp: Any, spec: str) -> dict[str, Any]:
    """用 sp.dag() 解析 spec, 渲染成 mermaid 文本 + adjustment sets."""
    if not spec:
        return {"spec": "", "mermaid": "", "adjustment_sets": [], "source": "unavailable"}
    try:
        g = sp.dag(spec)
    except Exception:
        return {
            "spec": spec,
            "mermaid": _naive_spec_to_mermaid(spec),
            "adjustment_sets": [],
            "source": "design_json",
        }
    mermaid = _graph_to_mermaid(g, spec)
    adj_sets: list[list[str]] = []
    try:
        nodes = _safe_nodes(g)
        if nodes and len(nodes) >= 2:
            # 找一个 outcome 节点: 在 spec 右侧出现得最多的变量
            from collections import Counter
            right_counter: Counter[str] = Counter()
            for edge in _safe_edges(g):
                if len(edge) >= 2:
                    right_counter[edge[1]] += 1
            if right_counter:
                outcome = right_counter.most_common(1)[0][0]
                treat_candidates = [n for n in nodes if n != outcome]
                for t in treat_candidates:
                    try:
                        sets = g.adjustment_sets(t, outcome)
                    except Exception:
                        sets = []
                    for s in (sets or []):
                        adj_sets.append(sorted(list(s)))
    except Exception:
        adj_sets = []
    return {
        "spec": spec,
        "mermaid": mermaid,
        "adjustment_sets": adj_sets,
        "source": "statspai",
    }


def _safe_nodes(g: Any) -> list[str]:
    for attr in ("nodes", "variables", "V"):
        try:
            v = getattr(g, attr)()
            if isinstance(v, (list, tuple, set)):
                return [str(x) for x in v]
        except Exception:
            continue
    return []


def _safe_edges(g: Any) -> list[tuple[str, str]]:
    for attr in ("edges", "E"):
        try:
            v = getattr(g, attr)()
            if isinstance(v, (list, tuple, set)):
                out: list[tuple[str, str]] = []
                for e in v:
                    if isinstance(e, (list, tuple)) and len(e) >= 2:
                        out.append((str(e[0]), str(e[1])))
                return out
        except Exception:
            continue
    return []


def _graph_to_mermaid(g: Any, spec: str) -> str:
    nodes = _safe_nodes(g)
    edges = _safe_edges(g)
    if not nodes:
        return _naive_spec_to_mermaid(spec)
    lines = ["graph LR"]
    for n in nodes:
        nid = _mermaid_id(n)
        lines.append(f"  {nid}[{n}]")
    for (u, v) in edges:
        lines.append(f"  {_mermaid_id(u)} --> {_mermaid_id(v)}")
    return "\n".join(lines)


def _mermaid_id(s: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in s) or "n"


def _naive_spec_to_mermaid(spec: str) -> str:
    """spec 解析失败的 fallback: 把 "X -> Y; Z -> X" 翻成 mermaid."""
    lines = ["graph LR"]
    for piece in spec.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        if "->" in piece:
            u, _, v = piece.partition("->")
            u, v = u.strip(), v.strip()
            if u and v:
                lines.append(f"  {_mermaid_id(u)}[{u}] --> {_mermaid_id(v)}[{v}]")
    return "\n".join(lines) if len(lines) > 1 else "graph LR\n  X[未配置]"


# ── 主入口 ──────────────────────────────────────────────────────────────
def run_identification_audit(
    results_path: str,
    design_path: str,
) -> dict[str, Any]:
    """对外暴露的 6th tab audit 主函数. 永远不抛 — 失败也返回结构化 dict.

    业务规则:
      B1: results.json / design.json 至少一个能读到 → 进入正常流程
      B2: 三块 (pretrend / weak_iv / dag) 各自独立, 一块缺数据不影响其他
      B3: statspai 可用时优先 statspai 诊断, 否则从 results.json 提取, 都没有就 N/A
    """
    payload: dict[str, Any] = {
        "method": None,
        "pretrend": {"source": "unavailable"},
        "weak_iv": {"source": "unavailable"},
        "dag": {"source": "unavailable"},
    }
    warnings: list[str] = []

    # 路径解析
    try:
        r_path = _resolve(results_path)
    except IdentificationAuditError as exc:
        return {"error": "invalid_results_path", "reason": str(exc), **payload}
    try:
        d_path = _resolve(design_path)
    except IdentificationAuditError as exc:
        return {"error": "invalid_design_path", "reason": str(exc), **payload}

    results = _safe_read_json(r_path)
    design = _safe_read_json(d_path)
    if results is None and design is None:
        return {
            "error": "no_artifacts",
            "reason": (
                f"both results.json ({r_path}) and design.json ({d_path}) are missing "
                "or unreadable. Run execution first."
            ),
            **payload,
        }

    method = (
        (results or {}).get("method")
        or (design or {}).get("method")
        or (design or {}).get("identification_strategy", {}).get("method")
        or "unknown"
    )
    payload["method"] = method

    # 1) Pre-trend
    pt_data = None
    pt_source = "unavailable"
    sp = _try_import_statspai()
    cached_result = (results or {}).get("statspai_result") or (results or {}).get("causal_result")
    if sp is not None and cached_result is not None:
        pt_data = _run_pretrends_statspai(sp, cached_result)
        if pt_data is not None:
            pt_source = "statspai"
    if pt_data is None and results is not None:
        pt_data = _extract_pretrend_from_results(results)
        if pt_data is not None:
            pt_source = "results_json"
    if pt_data is None:
        warnings.append(
            "pretrend: no statspai CausalResult cached in results.json and no event_study field. "
            "Showing N/A."
        )
        payload["pretrend"] = {
            "joint_pvalue": None,
            "joint_statistic": None,
            "n_pre_periods": None,
            "coefficients": [],
            "source": "unavailable",
        }
    else:
        payload["pretrend"] = {**pt_data, "source": pt_source}

    # 2) Weak-IV
    wiv_data = None
    wiv_source = "unavailable"
    if results is not None:
        wiv_data = _extract_weak_iv_from_results(results)
        if wiv_data is not None:
            wiv_source = "results_json"
    if wiv_data is None:
        warnings.append(
            "weak_iv: no first_stage / weak_iv field in results.json. "
            "Showing N/A. Run statspai iv_diag during execution to populate."
        )
        payload["weak_iv"] = {
            "partial_r2": None,
            "f_statistic": None,
            "n_obs": None,
            "ar_pvalue": None,
            "ar_ci_lower": None,
            "ar_ci_upper": None,
            "source": "unavailable",
        }
    else:
        # 强制 keys 存在 (None 表示 N/A)
        for k in ("partial_r2", "f_statistic", "n_obs", "ar_pvalue", "ar_ci_lower", "ar_ci_upper"):
            wiv_data.setdefault(k, None)
        payload["weak_iv"] = {**wiv_data, "source": wiv_source}

    # 3) DAG
    dag_spec_data = _extract_dag_from_design(design or {})
    if dag_spec_data is None:
        warnings.append(
            "dag: no causal_graph / dag field in design.json. "
            "Showing default DAG text."
        )
        default_spec = "Z -> X -> Y; U -> X; U -> Y"
        payload["dag"] = {
            "spec": default_spec,
            "mermaid": _naive_spec_to_mermaid(default_spec),
            "adjustment_sets": [],
            "source": "default",
        }
    else:
        spec = dag_spec_data["spec"]
        if sp is not None:
            payload["dag"] = _render_dag_mermaid(sp, spec)
        else:
            payload["dag"] = {
                "spec": spec,
                "mermaid": _naive_spec_to_mermaid(spec),
                "adjustment_sets": [],
                "source": "design_json",
            }

    if warnings:
        payload["warnings"] = warnings
    return payload
