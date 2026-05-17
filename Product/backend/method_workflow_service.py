from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


class MethodWorkflowBlockedError(Exception):
    """Raised when a RunPlan tries to approve a method with missing prerequisites."""

    def __init__(self, blocked_methods: list[dict[str, Any]]) -> None:
        self.code = "method_workflow_blocked"
        self.blocked_methods = blocked_methods
        method_labels = ", ".join(method.get("label", method.get("id", "")) for method in blocked_methods)
        super().__init__(f"Blocked empirical methods cannot be approved for RunPlan: {method_labels}")


def get_project_method_workflows(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    design_spec = load_design_spec(project_root)
    methods = build_method_workflows(design_spec)
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "method_workflow_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "source": "StatsPAI/CoPaper method workflow checklist",
        "evidence_level": "local_file",
        "methods": methods,
    }


def assert_run_plan_methods_ready(design_spec: dict[str, Any], tasks: list[dict[str, Any]]) -> None:
    methods = {method["id"]: method for method in build_method_workflows(design_spec)}
    blocked: list[dict[str, Any]] = []
    for task in tasks:
        method_id = str(task.get("method_id") or task.get("estimator") or "ols").strip().lower()
        workflow = methods.get(method_id)
        if workflow and workflow.get("readiness_status") == "blocked":
            blocked.append(
                {
                    "id": method_id,
                    "label": workflow.get("label", method_id),
                    "task_id": task.get("id", "task"),
                    "blockers": workflow.get("blockers", []),
                }
            )
    if blocked:
        raise MethodWorkflowBlockedError(blocked)


def build_method_workflows(design_spec: dict[str, Any] | None) -> list[dict[str, Any]]:
    context = build_context(design_spec or {})
    definitions = [
        {
            "id": "ols",
            "method": "OLS",
            "ready_label": "OLS：可执行",
            "blocked_label": "OLS：缺少结果变量或处理变量",
            "required_inputs": ["outcome", "treatment"],
            "required_diagnostics": ["sample_size", "missingness", "coefficient_table", "residual_diagnostics"],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
            },
            "summary": "基准相关关系估计，用于建立第一版可复现 baseline。",
        },
        {
            "id": "did",
            "method": "DID",
            "ready_label": "DID：可执行",
            "blocked_label": "DID：缺少时间变量、处理时点",
            "required_inputs": ["outcome", "treatment", "unit_id", "time_variable", "treatment_timing"],
            "required_diagnostics": [
                "parallel_trends",
                "event_study",
                "sensitivity_analysis",
                "heterogeneous_treatment_effects",
            ],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
                "time_variable": "time_variable_required",
                "treatment_timing": "treatment_timing_required",
            },
            "summary": "双重差分需要面板或时间维度、处理时点和事件研究类诊断。",
        },
        {
            "id": "iv",
            "method": "IV",
            "ready_label": "IV：可执行",
            "blocked_label": "IV：缺少工具变量",
            "required_inputs": ["outcome", "treatment", "instruments"],
            "required_diagnostics": [
                "first_stage",
                "weak_instrument_test",
                "overidentification_test",
                "exclusion_restriction_review",
            ],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
                "instruments": "instrument_required",
            },
            "summary": "工具变量方法需要先确认工具变量与识别假设，再进入执行。",
        },
        {
            "id": "rdd",
            "method": "RDD",
            "ready_label": "RDD：可执行",
            "blocked_label": "RDD：缺少断点运行变量",
            "required_inputs": ["outcome", "treatment", "running_variable", "cutoff"],
            "required_diagnostics": ["bandwidth_sensitivity", "density_test", "covariate_balance", "cutoff_review"],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
                "running_variable": "running_variable_required",
            },
            "summary": "断点回归需要 running variable、cutoff 和带宽/密度诊断。",
        },
        {
            "id": "psm",
            "method": "PSM",
            "ready_label": "PSM：可预检",
            "blocked_label": "PSM：缺少协变量",
            "required_inputs": ["outcome", "treatment", "covariates"],
            "required_diagnostics": ["propensity_score_overlap", "covariate_balance", "matching_quality", "common_support"],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
                "covariates": "covariates_required",
            },
            "summary": "倾向得分匹配可先做重叠区间和匹配质量预检。",
        },
        {
            "id": "dml",
            "method": "DML",
            "ready_label": "DML：可预检",
            "blocked_label": "DML：缺少机器学习特征",
            "required_inputs": ["outcome", "treatment", "covariates"],
            "required_diagnostics": ["cross_fitting", "nuisance_model_quality", "orthogonality_check", "feature_audit"],
            "blocker_requirements": {
                "outcome": "outcome_required",
                "treatment": "treatment_required",
                "covariates": "covariates_required",
            },
            "summary": "双重机器学习需要足够控制变量，并先声明交叉拟合与正交化诊断。",
        },
    ]
    return [build_method_workflow(definition, context) for definition in definitions]


def build_method_workflow(definition: dict[str, Any], context: dict[str, list[str]]) -> dict[str, Any]:
    blockers = [
        blocker
        for requirement_id, blocker in definition["blocker_requirements"].items()
        if not context.get(requirement_id)
    ]
    readiness_status = "ready" if not blockers else "blocked"
    return {
        "id": definition["id"],
        "method": definition["method"],
        "label": definition["ready_label"] if readiness_status == "ready" else definition["blocked_label"],
        "summary": definition["summary"],
        "readiness_status": readiness_status,
        "required_inputs": definition["required_inputs"],
        "required_diagnostics": definition["required_diagnostics"],
        "blockers": blockers,
        "evidence_level": "local_file",
    }


def build_context(design_spec: dict[str, Any]) -> dict[str, list[str]]:
    variables = design_spec.get("variables", {})
    model = design_spec.get("model", {})
    controls = normalize_string_list(variables.get("controls"))
    return {
        "outcome": normalize_string_list(variables.get("outcome")),
        "treatment": normalize_string_list(variables.get("treatment")),
        "controls": controls,
        "covariates": normalize_string_list(variables.get("covariates")) or controls,
        "instruments": normalize_string_list(variables.get("instruments")),
        "unit_id": normalize_string_list(variables.get("unit_id")) or normalize_string_list(variables.get("entity_id")),
        "time_variable": (
            normalize_string_list(variables.get("time_variable"))
            or normalize_string_list(variables.get("panel_time"))
            or normalize_string_list(model.get("time_variable"))
        ),
        "treatment_timing": normalize_string_list(variables.get("treatment_timing"))
        or normalize_string_list(model.get("treatment_timing")),
        "running_variable": normalize_string_list(variables.get("running_variable")) or normalize_string_list(variables.get("score")),
    }


def load_design_spec(project_root: Path) -> dict[str, Any] | None:
    path = project_root / "state" / "product" / "design_spec.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
