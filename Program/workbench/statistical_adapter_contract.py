from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.statistical_adapter_contract.v1"
DEFAULT_METHOD_EXECUTION_PATH = Path("Results/json/method_execution_result.json")
DEFAULT_CGSS_RESULTS_EVIDENCE_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/results_evidence_package.json")
DEFAULT_REPORT_PATH = Path("Results/json/statistical_adapter_contract.json")
DEFAULT_REVIEW_PATH = Path("Reviews/statistical_adapter_contract.md")
SUPPORTED_METHODS = ["ols", "ordered_logit", "iv", "did", "rdd", "psm", "dml"]
PROTECTED_PATHS = [
    "Results/json/method_execution_result.json",
    "Results/json/statspai_execution_result.json",
    "Results/json/iv_diag_result.json",
    "Manuscripts/sections/empirical-strategy.md",
    "Manuscripts/sections/robustness-mechanisms-heterogeneity.md",
    "Data/literature/processed/verified_bibliography.csv",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
    "state/product/statistical_adapter_contract.json",
]


def build_statistical_adapter_contract(
    *,
    method_execution: dict[str, Any],
    cgss_results_evidence: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    has_method_execution = bool(method_execution)
    has_cgss_results = bool(cgss_results_evidence)
    base = base_contract(method_execution, cgss_results_evidence, source_paths)
    if not has_method_execution and not has_cgss_results:
        return base | {
            "status": "blocked_missing_statistical_sources",
            "missing_sources": ["method_execution", "cgss_results_evidence"],
            "normalized_results": [],
            "capability_matrix": empty_capability_matrix(),
            "source_consistency": {},
        }

    normalized_results = []
    if has_method_execution:
        normalized_results.extend(normalize_method_execution(method_execution))
    if has_cgss_results:
        normalized_results.extend(normalize_cgss_results_evidence(cgss_results_evidence))

    return base | {
        "status": "needs_human_statistical_adapter_review",
        "missing_sources": [],
        "normalized_results": normalized_results,
        "capability_matrix": build_capability_matrix(normalized_results),
        "source_consistency": cgss_results_evidence.get("evidence_consistency", {}) if has_cgss_results else {},
    }


def base_contract(
    method_execution: dict[str, Any],
    cgss_results_evidence: dict[str, Any],
    source_paths: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "adapter_contract": {
            "id": "auto_mode_statistical_result_adapter_contract",
            "version": 1,
            "purpose": "Normalize statistical execution artifacts for Auto Mode paper-package consumers.",
            "supported_methods": SUPPORTED_METHODS,
            "required_result_fields": [
                "method_id",
                "evidence_level",
                "dataset_path",
                "nobs",
                "focal_estimate",
            ],
            "contract_status_values": ["contract_ready", "needs_mapping_review"],
        },
        "source_artifacts": {
            "method_execution": {
                "path": source_paths.get("method_execution", str(DEFAULT_METHOD_EXECUTION_PATH)),
                "present": bool(method_execution),
                "engine": method_execution.get("engine", ""),
                "evidence_level": method_execution.get("evidence_level", ""),
            },
            "cgss_results_evidence": {
                "path": source_paths.get("cgss_results_evidence", str(DEFAULT_CGSS_RESULTS_EVIDENCE_PATH)),
                "present": bool(cgss_results_evidence),
                "schema_version": cgss_results_evidence.get("schema_version", ""),
                "status": cgss_results_evidence.get("status", ""),
            },
        },
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "boundary_flags": {
            "reran_models": False,
            "modified_method_execution_artifacts": False,
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
        },
        "write_policy": {
            "mode": "statistical_adapter_contract_report_only",
            "does_not_modify": PROTECTED_PATHS,
            "requires_human_review_before_formal_state_writeback": True,
        },
    }


def normalize_method_execution(method_execution: dict[str, Any]) -> list[dict[str, Any]]:
    engine = method_execution.get("engine") or method_execution.get("execution_contract", {}).get("active_backend") or ""
    source_evidence_level = method_execution.get("evidence_level", "")
    normalized = []
    for index, method in enumerate(method_execution.get("methods", []), start=1):
        task_id = method.get("task_id") or f"method_{index}"
        method_id = str(method.get("method_id") or method.get("estimator") or "unknown")
        focal_variable = infer_focal_variable(method)
        focal_estimate = build_focal_estimate(method, focal_variable)
        result = {
            "result_id": f"method_execution:{task_id}",
            "source_kind": "method_execution_result",
            "task_id": task_id,
            "method_id": method_id,
            "estimator": method.get("estimator") or method_id,
            "engine": engine,
            "evidence_level": method.get("evidence_level") or source_evidence_level,
            "dataset_path": method.get("dataset_path", ""),
            "formula": method.get("formula", ""),
            "nobs": method.get("nobs"),
            "outcome": infer_outcome(method),
            "focal_variable": focal_variable,
            "focal_estimate": focal_estimate,
            "coefficient_terms": coefficient_terms(method),
            "diagnostics": method.get("diagnostics", {}),
            "reproducibility": method.get("reproducibility", {}),
            "backend_validations": method.get("backend_validations", []),
        }
        missing = missing_required_fields(result)
        result["missing_required_fields"] = missing
        result["contract_status"] = "contract_ready" if not missing else "needs_mapping_review"
        normalized.append(result)
    return normalized


def normalize_cgss_results_evidence(package: dict[str, Any]) -> list[dict[str, Any]]:
    primary = package.get("primary_result", {})
    variables = package.get("variables", {})
    dataset = package.get("dataset", {})
    normalized = []
    for method_id in ["ols", "ordered_logit"]:
        result = primary.get(method_id)
        if not isinstance(result, dict):
            continue
        focal_variable = result.get("variable") or variables.get("social_capital", {}).get("index", "")
        formula = build_cgss_formula(variables, focal_variable)
        normalized_result = {
            "result_id": f"cgss_results_evidence:{method_id}",
            "source_kind": "cgss_results_evidence_package",
            "task_id": method_id,
            "method_id": method_id,
            "estimator": method_id,
            "engine": "cgss_results_evidence_package",
            "evidence_level": "local_execution",
            "dataset_path": dataset.get("path", ""),
            "formula": formula,
            "nobs": result.get("nobs"),
            "outcome": variables.get("outcome", ""),
            "focal_variable": focal_variable,
            "focal_estimate": {
                "term": focal_variable,
                "coefficient": result.get("coef"),
                "standard_error": result.get("std_error"),
                "p_value": result.get("p_value"),
                "confidence_interval": {},
            },
            "coefficient_terms": [
                {
                    "term": focal_variable,
                    "coefficient": result.get("coef"),
                    "standard_error": result.get("std_error"),
                    "p_value": result.get("p_value"),
                    "confidence_interval": {},
                }
            ],
            "diagnostics": {"model": result.get("model", ""), "package_status": package.get("status", "")},
            "reproducibility": {"adapter": "cgss_results_evidence_package", "source_schema": package.get("schema_version", "")},
            "backend_validations": [],
            "ordered_outcome_levels": result.get("outcome_levels") or variables.get("ordered_outcome_levels", []),
        }
        missing = missing_required_fields(normalized_result)
        normalized_result["missing_required_fields"] = missing
        normalized_result["contract_status"] = "contract_ready" if not missing else "needs_mapping_review"
        normalized.append(normalized_result)
    return normalized


def infer_focal_variable(method: dict[str, Any]) -> str:
    for key in ["treatment", "focal_variable", "endogenous_treatment"]:
        if method.get(key):
            return str(method[key])
    coefficients = method.get("coefficients", {})
    for term in coefficients:
        if term.lower() not in {"intercept", "const", "_cons"}:
            return term
    return ""


def infer_outcome(method: dict[str, Any]) -> str:
    formula = str(method.get("formula") or "")
    if "~" in formula:
        return formula.split("~", 1)[0].strip()
    return str(method.get("dependent_var") or "")


def build_focal_estimate(method: dict[str, Any], focal_variable: str) -> dict[str, Any]:
    if not focal_variable:
        return {}
    coefficients = method.get("coefficients", {})
    if focal_variable not in coefficients:
        return {}
    return {
        "term": focal_variable,
        "coefficient": coefficients.get(focal_variable),
        "standard_error": (method.get("standard_errors") or {}).get(focal_variable),
        "p_value": (method.get("p_values") or {}).get(focal_variable),
        "confidence_interval": (method.get("confidence_intervals") or {}).get(focal_variable, {}),
    }


def coefficient_terms(method: dict[str, Any]) -> list[dict[str, Any]]:
    terms = []
    coefficients = method.get("coefficients", {})
    for term, coefficient in coefficients.items():
        terms.append(
            {
                "term": term,
                "coefficient": coefficient,
                "standard_error": (method.get("standard_errors") or {}).get(term),
                "p_value": (method.get("p_values") or {}).get(term),
                "confidence_interval": (method.get("confidence_intervals") or {}).get(term, {}),
            }
        )
    return terms


def build_cgss_formula(variables: dict[str, Any], focal_variable: str) -> str:
    outcome = variables.get("outcome", "")
    controls = variables.get("controls", [])
    rhs = [focal_variable, *controls]
    return f"{outcome} ~ {' + '.join(item for item in rhs if item)}"


def missing_required_fields(result: dict[str, Any]) -> list[str]:
    missing = []
    for field in ["method_id", "evidence_level", "dataset_path", "nobs"]:
        if result.get(field) in {None, ""}:
            missing.append(field)
    if not result.get("formula"):
        missing.append("formula")
    if not result.get("focal_estimate"):
        missing.append("focal_estimate")
    return missing


def build_capability_matrix(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    matrix = empty_capability_matrix()
    for result in results:
        method_id = result.get("method_id") or "unknown"
        if method_id not in matrix:
            matrix[method_id] = empty_capability_entry(method_id)
        entry = matrix[method_id]
        entry["result_count"] += 1
        if result.get("contract_status") == "contract_ready":
            entry["contract_ready_count"] += 1
        else:
            entry["incomplete_count"] += 1
            entry["missing_required_fields"] = sorted(
                set(entry["missing_required_fields"]) | set(result.get("missing_required_fields", []))
            )
        entry["status"] = "contract_ready" if entry["contract_ready_count"] and not entry["incomplete_count"] else "needs_mapping_review"
    return matrix


def empty_capability_matrix() -> dict[str, dict[str, Any]]:
    return {method_id: empty_capability_entry(method_id) for method_id in SUPPORTED_METHODS}


def empty_capability_entry(method_id: str) -> dict[str, Any]:
    return {
        "method_id": method_id,
        "supported_by_contract": method_id in SUPPORTED_METHODS,
        "result_count": 0,
        "contract_ready_count": 0,
        "incomplete_count": 0,
        "missing_required_fields": [],
        "status": "not_observed",
    }


def write_outputs(
    project_root: Path,
    contract: dict[str, Any],
    report_path: Path,
    review_path: Path,
) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(contract), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(contract: dict[str, Any]) -> str:
    lines = [
        "# Statistical Adapter Contract",
        "",
        f"- 状态：{contract['status']}",
        f"- normalized results：{len(contract.get('normalized_results', []))}",
        "- 模型重跑：否",
        "- 正式层写回：否",
        "- 方法执行产物覆盖：否",
        "- product state 写回：否",
        "",
        "## Capability Matrix",
    ]
    for method_id, entry in contract.get("capability_matrix", {}).items():
        if entry["result_count"]:
            lines.append(
                f"- `{method_id}`：ready={entry['contract_ready_count']} incomplete={entry['incomplete_count']} status={entry['status']}"
            )
    if not any(entry["result_count"] for entry in contract.get("capability_matrix", {}).values()):
        lines.append("- 无可消费统计结果。")
    if contract.get("missing_sources"):
        lines.extend(["", "## 缺失来源"])
        lines.extend(f"- `{source}`" for source in contract["missing_sources"])
    lines.extend(["", "## 人工审阅"])
    lines.extend(
        [
            "- 核对 normalized result 是否足够支撑论文表格和方法门。",
            "- 对 `needs_mapping_review` 的方法补齐缺失字段或保留为不可消费。",
            "- 后续 Auto Mode 只能消费 `contract_ready` 的统计结果。",
        ]
    )
    return "\n".join(lines) + "\n"


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
