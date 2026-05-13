from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import load_saved_variable_role_set


def design_spec_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "design_spec.json"


def run_plan_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "run_plan.json"


def load_saved_design_spec(project_root: Path) -> dict[str, Any] | None:
    path = design_spec_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_saved_run_plan(project_root: Path) -> dict[str, Any] | None:
    path = run_plan_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def has_approved_design_spec(project_root: Path) -> bool:
    saved = load_saved_design_spec(project_root)
    return bool(saved and saved.get("status") == "approved")


def has_approved_run_plan(project_root: Path) -> bool:
    saved = load_saved_run_plan(project_root)
    return bool(saved and saved.get("status") == "approved")


def get_project_design_spec(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    design_spec = load_saved_design_spec(project_root) or build_draft_design_spec(project, project_root)
    return {
        "_meta": {
            "evidence_level": design_spec.get("evidence_level", "local_file"),
            "service": "design_spec_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "design_spec": design_spec,
    }


def save_project_design_spec(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    research_question: str,
    identification_strategy: dict[str, Any],
    model: dict[str, Any],
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    variable_role_set = require_approved_variable_role_set(project_root)
    existing = load_saved_design_spec(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if existing else []
    event = {
        "actor": "user",
        "action": "confirm_design_spec",
        "timestamp": utc_now(),
        "note": note,
    }
    design_spec = {
        "id": "design_spec",
        "version": version,
        "status": "approved",
        "evidence_level": "local_file",
        "variable_role_set_version": variable_role_set.get("version", 0),
        "dataset_path": variable_role_set.get("dataset_path"),
        "research_question": research_question,
        "variables": variable_role_set.get("roles", {}),
        "identification_strategy": normalize_identification_strategy(identification_strategy),
        "model": normalize_model(model),
        "updated_at": event["timestamp"],
        "decision_events": [*previous_events, event],
    }
    path = design_spec_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(design_spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "design_spec_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "design_spec": design_spec,
    }


def get_project_run_plan(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    run_plan = load_saved_run_plan(project_root) or build_draft_run_plan(project_root)
    run_plan = enrich_run_plan_with_method_catalog(project_root, run_plan)
    return {
        "_meta": {
            "evidence_level": run_plan.get("evidence_level", "local_file"),
            "service": "run_plan_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "run_plan": run_plan,
    }


def save_project_run_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    tasks: list[dict[str, Any]],
    outputs: list[str],
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    design_spec = require_approved_design_spec(project_root)
    existing = load_saved_run_plan(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if existing else []
    event = {
        "actor": "user",
        "action": "confirm_run_plan",
        "timestamp": utc_now(),
        "note": note,
    }
    run_plan = {
        "id": "run_plan",
        "version": version,
        "status": "approved",
        "evidence_level": "local_file",
        "design_spec_version": design_spec.get("version", 0),
        "dataset_path": design_spec.get("dataset_path"),
        "tasks": normalize_tasks(tasks),
        "outputs": normalize_outputs(outputs),
        "updated_at": event["timestamp"],
        "decision_events": [*previous_events, event],
    }
    path = run_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "run_plan_service",
            "generated_at": utc_now(),
        },
        "project": project_identity(project),
        "run_plan": run_plan,
    }


def build_draft_design_spec(project: dict[str, Any], project_root: Path) -> dict[str, Any]:
    variable_role_set = require_approved_variable_role_set(project_root)
    variables = variable_role_set.get("roles", {})
    formula = build_formula(variables)
    return {
        "id": "design_spec",
        "version": 0,
        "status": "draft",
        "evidence_level": "local_file",
        "variable_role_set_version": variable_role_set.get("version", 0),
        "dataset_path": variable_role_set.get("dataset_path"),
        "research_question": project.get("question") or read_research_question(project_root),
        "variables": variables,
        "identification_strategy": {
            "name": "baseline_ols",
            "summary": "基于已确认变量角色生成第一版 OLS 研究设计。",
            "assumptions": [],
            "threats": [],
        },
        "model": {
            "estimator": "ols",
            "formula": formula,
            "fixed_effects": variables.get("fixed_effects", []),
            "cluster_by": variables.get("cluster_by", []),
            "sample_filter": "all",
        },
        "updated_at": utc_now(),
        "decision_events": [],
    }


def build_draft_run_plan(project_root: Path) -> dict[str, Any]:
    design_spec = require_approved_design_spec(project_root)
    method_catalog = build_method_catalog(design_spec)
    task = {
        "id": "baseline_regression",
        "label": "Baseline regression",
        "method_id": "ols",
        "status": "planned",
        "design_spec_id": design_spec.get("id", "design_spec"),
        "formula": design_spec.get("model", {}).get("formula", ""),
        "estimator": design_spec.get("model", {}).get("estimator", "ols"),
        "evidence_level": "local_file",
    }
    ready_method_ids = {method["id"] for method in method_catalog["methods"] if method["readiness_status"] == "ready"}
    tasks = [task] if task["method_id"] in ready_method_ids else []
    return {
        "id": "run_plan",
        "version": 0,
        "status": "draft",
        "evidence_level": "local_file",
        "design_spec_version": design_spec.get("version", 0),
        "dataset_path": design_spec.get("dataset_path"),
        "method_catalog": method_catalog,
        "tasks": tasks,
        "outputs": ["regression_table", "run_manifest", "run_events", "paper_draft_section"],
        "updated_at": utc_now(),
        "decision_events": [],
    }


def require_approved_variable_role_set(project_root: Path) -> dict[str, Any]:
    role_set = load_saved_variable_role_set(project_root)
    if not role_set or role_set.get("status") != "approved":
        raise FileNotFoundError("approved VariableRoleSet is required")
    return role_set


def require_approved_design_spec(project_root: Path) -> dict[str, Any]:
    design_spec = load_saved_design_spec(project_root)
    if not design_spec or design_spec.get("status") != "approved":
        raise FileNotFoundError("approved DesignSpec is required")
    return design_spec


def build_formula(variables: dict[str, Any]) -> str:
    outcome = first_value(variables.get("outcome"))
    treatment = first_value(variables.get("treatment"))
    controls = normalize_string_list(variables.get("controls"))
    rhs = [value for value in [treatment, *controls] if value]
    if not outcome or not rhs:
        return ""
    return f"{outcome} ~ {' + '.join(rhs)}"


def read_research_question(project_root: Path) -> str:
    paper_path = project_root / "paper.yaml"
    if not paper_path.exists():
        return ""
    text = paper_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("question:"):
            return stripped.split(":", 1)[1].strip()
    return ""


def normalize_identification_strategy(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(value.get("name", "baseline_ols")).strip() or "baseline_ols",
        "summary": str(value.get("summary", "")).strip(),
        "assumptions": normalize_string_list(value.get("assumptions")),
        "threats": normalize_string_list(value.get("threats")),
    }


def normalize_model(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "estimator": str(value.get("estimator", "ols")).strip() or "ols",
        "formula": str(value.get("formula", "")).strip(),
        "fixed_effects": normalize_string_list(value.get("fixed_effects")),
        "cluster_by": normalize_string_list(value.get("cluster_by")),
        "sample_filter": str(value.get("sample_filter", "all")).strip() or "all",
    }


def normalize_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for task in tasks:
        normalized.append(
            {
                "id": str(task.get("id", "task")).strip() or "task",
                "label": str(task.get("label", task.get("id", "Task"))).strip(),
                "method_id": str(task.get("method_id", task.get("estimator", "ols"))).strip() or "ols",
                "status": str(task.get("status", "planned")).strip() or "planned",
                "design_spec_id": str(task.get("design_spec_id", "design_spec")).strip() or "design_spec",
                "formula": str(task.get("formula", "")).strip(),
                "estimator": str(task.get("estimator", "ols")).strip() or "ols",
                "evidence_level": "local_file",
            }
        )
    return normalized


def enrich_run_plan_with_method_catalog(project_root: Path, run_plan: dict[str, Any]) -> dict[str, Any]:
    design_spec = load_saved_design_spec(project_root)
    if not design_spec:
        return run_plan
    enriched = dict(run_plan)
    enriched["method_catalog"] = build_method_catalog(design_spec)
    enriched["tasks"] = normalize_tasks(enriched.get("tasks", []))
    return enriched


def build_method_catalog(design_spec: dict[str, Any]) -> dict[str, Any]:
    variables = design_spec.get("variables", {})
    model = design_spec.get("model", {})
    context = {
        "outcome": normalize_string_list(variables.get("outcome")),
        "treatment": normalize_string_list(variables.get("treatment")),
        "controls": normalize_string_list(variables.get("controls")),
        "instruments": normalize_string_list(variables.get("instruments")),
        "fixed_effects": normalize_string_list(model.get("fixed_effects") or variables.get("fixed_effects")),
        "cluster_by": normalize_string_list(model.get("cluster_by") or variables.get("cluster_by")),
        "running_variable": normalize_string_list(variables.get("running_variable")),
        "score": normalize_string_list(variables.get("score")),
        "covariates": normalize_string_list(variables.get("covariates") or variables.get("controls")),
    }
    definitions = [
        {
            "id": "ols",
            "label": "OLS 基准回归",
            "summary": "第一版基准估计，用于建立可复现 baseline。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "处理变量"),
            ],
            "optional": [
                ("controls", "控制变量"),
                ("fixed_effects", "固定效应"),
                ("cluster_by", "聚类方式"),
            ],
            "agent_role": "ExecutionAgent",
            "statspai_method": "sp.ols",
        },
        {
            "id": "did",
            "label": "DID 双重差分",
            "summary": "需要处理组、时间维度和政策前后变化。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "处理变量"),
                ("panel_time", "面板或时间变量"),
            ],
            "optional": [("controls", "控制变量")],
            "agent_role": "DesignAgent",
            "statspai_method": "sp.did",
        },
        {
            "id": "iv",
            "label": "IV 工具变量",
            "summary": "需要明确工具变量，并人工审查相关性与排除限制。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "内生处理变量"),
                ("instruments", "工具变量"),
            ],
            "optional": [("controls", "控制变量")],
            "agent_role": "DesignAgent",
            "statspai_method": "sp.iv",
        },
        {
            "id": "rdd",
            "label": "RDD 断点回归",
            "summary": "需要 running variable、阈值和带宽诊断。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "处理变量"),
                ("running_variable", "断点运行变量"),
            ],
            "optional": [("controls", "控制变量")],
            "agent_role": "DesignAgent",
            "statspai_method": "sp.rdd",
        },
        {
            "id": "psm",
            "label": "PSM 倾向得分匹配",
            "summary": "需要处理变量和用于匹配的协变量集合。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "处理变量"),
                ("covariates", "匹配协变量"),
            ],
            "optional": [],
            "agent_role": "ExecutionAgent",
            "statspai_method": "sp.psm",
        },
        {
            "id": "dml",
            "label": "DML 双重机器学习",
            "summary": "需要处理变量、结果变量和足够控制变量作为机器学习特征。",
            "required": [
                ("outcome", "结果变量"),
                ("treatment", "处理变量"),
                ("covariates", "机器学习特征"),
            ],
            "optional": [],
            "agent_role": "ExecutionAgent",
            "statspai_method": "sp.dml",
        },
    ]
    return {
        "id": "method_catalog",
        "version": 1,
        "source": "StatsPAI/CoPaper methodology index",
        "evidence_level": "local_file",
        "methods": [build_method_entry(definition, context) for definition in definitions],
    }


def build_method_entry(definition: dict[str, Any], context: dict[str, list[str]]) -> dict[str, Any]:
    requirements = [
        build_requirement(requirement_id, label, context)
        for requirement_id, label in definition["required"]
    ]
    blockers = [requirement["blocker"] for requirement in requirements if requirement["status"] == "missing"]
    optional = [
        build_requirement(requirement_id, label, context)
        for requirement_id, label in definition.get("optional", [])
    ]
    return {
        "id": definition["id"],
        "label": definition["label"],
        "summary": definition["summary"],
        "readiness_status": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "requirements": requirements,
        "optional_requirements": optional,
        "agent_role": definition["agent_role"],
        "statspai_method": definition["statspai_method"],
        "evidence_level": "local_file",
    }


def build_requirement(requirement_id: str, label: str, context: dict[str, list[str]]) -> dict[str, Any]:
    values = requirement_values(requirement_id, context)
    status = "present" if values else "missing"
    return {
        "id": requirement_id,
        "label": label,
        "status": status,
        "values": values,
        "blocker": blocker_for_requirement(requirement_id) if status == "missing" else "",
    }


def requirement_values(requirement_id: str, context: dict[str, list[str]]) -> list[str]:
    if requirement_id == "panel_time":
        return [*context.get("fixed_effects", []), *context.get("cluster_by", [])]
    if requirement_id == "running_variable":
        return [*context.get("running_variable", []), *context.get("score", [])]
    return context.get(requirement_id, [])


def blocker_for_requirement(requirement_id: str) -> str:
    return {
        "outcome": "missing_outcome",
        "treatment": "missing_treatment",
        "controls": "missing_controls",
        "covariates": "missing_covariates",
        "instruments": "missing_instrument",
        "panel_time": "missing_panel_time",
        "running_variable": "missing_running_variable",
    }.get(requirement_id, f"missing_{requirement_id}")


def normalize_outputs(outputs: list[str]) -> list[str]:
    return normalize_string_list(outputs)


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def first_value(value: Any) -> str:
    values = normalize_string_list(value)
    return values[0] if values else ""


def project_identity(project: dict[str, Any]) -> dict[str, str]:
    return {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
    }
