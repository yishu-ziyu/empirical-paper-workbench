from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.codex_provider import local_codex_status, run_local_codex_prompt
from Product.backend.design_spec_service import load_saved_design_spec, load_saved_run_plan
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import load_saved_variable_role_set


SUPERVISOR_PLAN_PATH = Path("state/product/supervisor_plan.json")
SUPERVISOR_PLAN_RAW_PATH = Path("state/product/supervisor_plan.raw.md")


class SupervisorPlanBlockedError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class SupervisorPlanExecutionError(RuntimeError):
    pass


def supervisor_plan_state_path(project_root: Path) -> Path:
    return project_root / SUPERVISOR_PLAN_PATH


def supervisor_plan_raw_path(project_root: Path) -> Path:
    return project_root / SUPERVISOR_PLAN_RAW_PATH


def get_project_supervisor_plan(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    plan = load_saved_supervisor_plan(project_root) or build_empty_supervisor_plan(project_root)
    return {
        "_meta": {
            "evidence_level": plan.get("evidence_level", "local_file"),
            "service": "supervisor_plan_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "supervisor_plan": plan,
    }


def generate_project_supervisor_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    objective: str,
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    provider = local_codex_status()
    if not provider.get("available"):
        raise SupervisorPlanBlockedError("local_codex_not_found", "Local Codex CLI is not available.")
    if not provider.get("execution_enabled"):
        raise SupervisorPlanBlockedError(
            "local_codex_execution_not_enabled",
            f"Set {provider.get('execution_env')}=1 to allow local Codex supervisor execution.",
        )

    variable_roles = require_approved_state(load_saved_variable_role_set(project_root), "VariableRoleSet")
    design_spec = require_approved_state(load_saved_design_spec(project_root), "DesignSpec")
    run_plan = require_approved_state(load_saved_run_plan(project_root), "RunPlan")
    existing = load_saved_supervisor_plan(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    raw_path = supervisor_plan_raw_path(project_root)
    result = run_local_codex_prompt(
        project_root,
        build_supervisor_plan_prompt(project, objective, variable_roles, design_spec, run_plan),
        raw_path,
        timeout_seconds=300,
    )
    if result.get("returncode") != 0:
        raise SupervisorPlanExecutionError(result.get("stderr") or "Local Codex supervisor execution failed.")

    raw_text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else result.get("stdout", "")
    generated = parse_supervisor_plan_output(raw_text)
    timestamp = utc_now()
    plan = normalize_supervisor_plan(
        generated,
        project,
        objective,
        note,
        provider,
        variable_roles,
        design_spec,
        run_plan,
        version,
        timestamp,
    )
    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_execution",
            "service": "supervisor_plan_service",
            "generated_at": timestamp,
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "supervisor_plan": plan,
    }


def load_saved_supervisor_plan(project_root: Path) -> dict[str, Any] | None:
    path = supervisor_plan_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_supervisor_plan(project_root: Path) -> dict[str, Any]:
    return {
        "id": "supervisor_plan",
        "version": 0,
        "status": "empty",
        "evidence_level": "local_file",
        "provider": local_codex_status(),
        "objective": "",
        "stage_plan": [],
        "subagent_dispatch": [],
        "evidence_requirements": [],
        "risks": [],
        "human_gates": [],
        "next_action": {
            "id": "generate_supervisor_plan",
            "label": "生成 SupervisorPlan",
        },
        "write_boundary": "SupervisorPlan 只能提出计划；不可直接改写 VariableRoleSet、DesignSpec 或 RunPlan。",
        "path": SUPERVISOR_PLAN_PATH.as_posix(),
        "exists": supervisor_plan_state_path(project_root).exists(),
    }


def require_approved_state(state: dict[str, Any] | None, label: str) -> dict[str, Any]:
    if not state or state.get("status") != "approved":
        raise SupervisorPlanBlockedError(
            f"{label.lower()}_required",
            f"Approved {label} is required before generating SupervisorPlan.",
        )
    return state


def build_supervisor_plan_prompt(
    project: dict[str, Any],
    objective: str,
    variable_roles: dict[str, Any],
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
) -> str:
    context = {
        "project": {
            "id": project["id"],
            "title": project["title"],
            "question": project.get("question", ""),
        },
        "objective": objective,
        "approved_variable_roles": compact_state(variable_roles),
        "approved_design_spec": compact_state(design_spec),
        "approved_run_plan": compact_state(run_plan),
        "write_boundary": "You must not modify VariableRoleSet, DesignSpec, or RunPlan. Propose a reviewable plan only.",
    }
    return (
        "你是本地 Codex Supervisor，负责为实证论文工作台生成下一轮可审阅研究执行计划。\n"
        "只输出 JSON，不要输出 Markdown。JSON 必须包含：stage_plan、subagent_dispatch、"
        "evidence_requirements、risks、human_gates、next_action。\n"
        "所有建议必须基于输入状态，不得声称已执行分析，不得改写任何已批准状态。\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def compact_state(state: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "version",
        "status",
        "evidence_level",
        "dataset_path",
        "roles",
        "research_question",
        "identification_strategy",
        "model",
        "tasks",
        "outputs",
    )
    return {key: state.get(key) for key in keys if key in state}


def parse_supervisor_plan_output(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if not text:
        raise SupervisorPlanExecutionError("Local Codex did not produce a supervisor plan.")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise SupervisorPlanExecutionError("Local Codex output was not valid JSON.")


def normalize_supervisor_plan(
    generated: dict[str, Any],
    project: dict[str, Any],
    objective: str,
    note: str,
    provider: dict[str, Any],
    variable_roles: dict[str, Any],
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    version: int,
    timestamp: str,
) -> dict[str, Any]:
    return {
        "id": "supervisor_plan",
        "version": version,
        "status": "needs_review",
        "evidence_level": "local_execution",
        "project_id": project["id"],
        "provider": provider,
        "objective": objective,
        "stage_plan": normalize_list(generated.get("stage_plan")),
        "subagent_dispatch": normalize_list(generated.get("subagent_dispatch")),
        "evidence_requirements": normalize_list(generated.get("evidence_requirements")),
        "risks": normalize_list(generated.get("risks")),
        "human_gates": normalize_list(generated.get("human_gates")),
        "next_action": generated.get("next_action") or {
            "id": "review_supervisor_plan",
            "label": "审阅 SupervisorPlan",
        },
        "input_state_versions": {
            "variable_role_set_version": int(variable_roles.get("version", 0)),
            "design_spec_version": int(design_spec.get("version", 0)),
            "run_plan_version": int(run_plan.get("version", 0)),
        },
        "input_evidence": {
            "variable_roles_path": "state/product/variable_roles.json",
            "design_spec_path": "state/product/design_spec.json",
            "run_plan_path": "state/product/run_plan.json",
        },
        "write_boundary": "本地 Codex Supervisor 只能提出计划和审阅意见；不可直接改写 VariableRoleSet、DesignSpec 或 RunPlan。",
        "raw_output_path": SUPERVISOR_PLAN_RAW_PATH.as_posix(),
        "updated_at": timestamp,
        "decision_events": [
            {
                "actor": "local_codex_supervisor",
                "action": "generate_supervisor_plan",
                "timestamp": timestamp,
                "note": note,
            }
        ],
    }


def normalize_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]
