from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.codex_provider import local_codex_status, run_local_codex_prompt
from Product.backend.design_spec_service import load_saved_design_spec, load_saved_run_plan
from Product.backend.internal_agent_skill_registry import (
    compact_internal_agent_skills_for_prompt,
    recommend_internal_agent_skills_for_plan_context,
)
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.research_question_service import load_saved_research_question
from Product.backend.variable_role_service import load_saved_variable_role_set


SUPERVISOR_PLAN_PATH = Path("state/product/supervisor_plan.json")
SUPERVISOR_PLAN_RAW_PATH = Path("state/product/supervisor_plan.raw.md")


class SupervisorPlanBlockedError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class SupervisorPlanExecutionError(RuntimeError):
    pass


class InvalidSupervisorPlanReviewActionError(ValueError):
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

    research_question = require_confirmed_research_question(load_saved_research_question(project_root))
    variable_roles = require_approved_state(load_saved_variable_role_set(project_root), "VariableRoleSet")
    design_spec = require_approved_state(load_saved_design_spec(project_root), "DesignSpec")
    run_plan = require_approved_state(load_saved_run_plan(project_root), "RunPlan")
    existing = load_saved_supervisor_plan(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    raw_path = supervisor_plan_raw_path(project_root)
    result = run_local_codex_prompt(
        project_root,
        build_supervisor_plan_prompt(project, objective, research_question, variable_roles, design_spec, run_plan),
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
        research_question,
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


def review_project_supervisor_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    action: str,
    note: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    plan = load_saved_supervisor_plan(project_root)
    if not plan:
        raise SupervisorPlanBlockedError(
            "supervisor_plan_required",
            "SupervisorPlan is required before review.",
        )

    next_state = supervisor_plan_review_state(action)
    timestamp = utc_now()
    reviewed = {
        **plan,
        "status": next_state["status"],
        "can_dispatch": next_state["can_dispatch"],
        "next_action": next_state["next_action"],
        "human_review": {
            "actor": "user",
            "action": action,
            "note": note,
            "timestamp": timestamp,
        },
        "updated_at": timestamp,
    }
    reviewed["decision_events"] = normalize_list(plan.get("decision_events")) + [
        {
            "actor": "user",
            "action": f"review_supervisor_plan:{action}",
            "timestamp": timestamp,
            "note": note,
        }
    ]

    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "supervisor_plan_service",
            "generated_at": timestamp,
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "supervisor_plan": reviewed,
    }


def supervisor_plan_review_state(action: str) -> dict[str, Any]:
    states = {
        "approve": {
            "status": "approved",
            "can_dispatch": True,
            "next_action": {
                "id": "create_agent_task_queue",
                "label": "创建 Agent Task Queue",
            },
        },
        "needs_revision": {
            "status": "needs_revision",
            "can_dispatch": False,
            "next_action": {
                "id": "revise_supervisor_plan",
                "label": "修改 SupervisorPlan",
            },
        },
        "reject": {
            "status": "rejected",
            "can_dispatch": False,
            "next_action": {
                "id": "regenerate_supervisor_plan",
                "label": "重新生成 SupervisorPlan",
            },
        },
    }
    try:
        return states[action]
    except KeyError as exc:
        raise InvalidSupervisorPlanReviewActionError(action) from exc


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


def require_confirmed_research_question(state: dict[str, Any] | None) -> dict[str, Any]:
    if not state or state.get("status") != "confirmed":
        raise SupervisorPlanBlockedError(
            "research_question_required",
            "Confirmed ResearchQuestion is required before generating SupervisorPlan.",
        )
    return state


def build_supervisor_plan_prompt(
    project: dict[str, Any],
    objective: str,
    research_question: dict[str, Any],
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
        "confirmed_research_question": compact_research_question(research_question),
        "approved_variable_roles": compact_state(variable_roles),
        "approved_design_spec": compact_state(design_spec),
        "approved_run_plan": compact_state(run_plan),
        "internal_skill_registry": compact_internal_agent_skills_for_prompt(),
        "write_boundary": "You must not modify VariableRoleSet, DesignSpec, or RunPlan. Propose a reviewable plan only.",
    }
    return (
        "你是本地 Codex Supervisor，负责为实证论文工作台生成下一轮可审阅研究执行计划。\n"
        "只输出 JSON，不要输出 Markdown。JSON 必须包含：stage_plan、subagent_dispatch、"
        "evidence_requirements、risks、human_gates、next_action。\n"
        "所有建议必须基于输入状态，不得声称已执行分析，不得改写任何已批准状态。\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def compact_research_question(state: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "topic_session_id",
        "version",
        "status",
        "question",
        "evidence_level",
        "source",
        "path",
    )
    return {key: state.get(key) for key in keys if key in state}


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
    research_question: dict[str, Any],
    variable_roles: dict[str, Any],
    design_spec: dict[str, Any],
    run_plan: dict[str, Any],
    version: int,
    timestamp: str,
) -> dict[str, Any]:
    stage_plan = normalize_list(generated.get("stage_plan"))
    subagent_dispatch = normalize_list(generated.get("subagent_dispatch"))
    evidence_requirements = normalize_list(generated.get("evidence_requirements"))
    risks = normalize_list(generated.get("risks"))
    human_gates = normalize_list(generated.get("human_gates"))
    recommended_internal_skills = recommend_internal_agent_skills_for_plan_context(
        {
            "project": project,
            "objective": objective,
            "research_question": research_question,
            "variable_roles": variable_roles,
            "design_spec": design_spec,
            "run_plan": run_plan,
            "stage_plan": stage_plan,
            "subagent_dispatch": subagent_dispatch,
            "evidence_requirements": evidence_requirements,
            "risks": risks,
            "human_gates": human_gates,
        }
    )
    return {
        "id": "supervisor_plan",
        "version": version,
        "status": "needs_review",
        "evidence_level": "local_execution",
        "project_id": project["id"],
        "provider": provider,
        "objective": objective,
        "input_research_question": compact_research_question(research_question),
        "stage_plan": stage_plan,
        "subagent_dispatch": subagent_dispatch,
        "evidence_requirements": evidence_requirements,
        "risks": risks,
        "human_gates": human_gates,
        "recommended_internal_skills": recommended_internal_skills,
        "next_action": generated.get("next_action") or {
            "id": "review_supervisor_plan",
            "label": "审阅 SupervisorPlan",
        },
        "input_state_versions": {
            "research_question_version": int(research_question.get("version", 0)),
            "variable_role_set_version": int(variable_roles.get("version", 0)),
            "design_spec_version": int(design_spec.get("version", 0)),
            "run_plan_version": int(run_plan.get("version", 0)),
        },
        "input_evidence": {
            "research_question_path": "state/product/research_question.json",
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


# ── Default plan draft (intake-time preview) ─────────────────────────────────
# Mirrors Product/web-react/src/components/SupervisorPlanReview.tsx::DEFAULT_STAGES.
# This is the static 8-stage plan shown in the brief tab when the user has
# selected codex-supervisor mode. Backend is the single source of truth for
# the structure; the frontend re-uses the same shape when receiving JSON.
# When the user approves, the per-project generate_project_supervisor_plan()
# produces a live Codex-driven plan (see /api/v1/projects/{id}/supervisor-plan).

DEFAULT_PLAN_DRAFT_STAGES: list[dict[str, Any]] = [
    {
        "id": "literature-search",
        "title": "1. 文献检索与理论构建",
        "owner": "LiteratureAgent",
        "status": "ready",
        "reason": "识别核心机制、经典文献中对该效应的理论建模，抽取关键机制假说。",
        "inputs": ["研究题目", "文献数据库 API"],
        "outputs": ["理论假说", "机制框架图"],
    },
    {
        "id": "data-variables",
        "title": "2. 数据检索与变量画像",
        "owner": "DataAgent",
        "status": "running",
        "reason": "【推荐首选分支】已附带本地数据文件，优先对数据文件开展字段解析、缺失值评估与类型画像。",
        "inputs": ["本地附件 (csv/dta)", "变量定义字典"],
        "outputs": ["VariableRoleSet", "字段缺失值报告"],
    },
    {
        "id": "method-design",
        "title": "3. 因果识别与方法设计",
        "owner": "MethodAgent",
        "status": "draft",
        "reason": "基于自变量与因变量的数据分布，设计双重差分 (DID) 或工具变量 (IV) 识别方程。",
        "inputs": ["VariableRoleSet", "时点分布"],
        "outputs": ["DesignSpec (方程设定)", "平行趋势前置条件"],
    },
    {
        "id": "preflight-check",
        "title": "4. 执行预检与沙盒模拟",
        "owner": "Supervisor",
        "status": "empty",
        "reason": "静态解析 Stata/Python 代码块，开展因果依赖冲突、循环共线性等预检。",
        "inputs": ["DesignSpec", "本地环境配置"],
        "outputs": ["PreflightReport", "环境依赖树"],
    },
    {
        "id": "experiment-run",
        "title": "5. 实证跑码与实验运行",
        "owner": "ExecutionAgent",
        "status": "empty",
        "reason": "启动本地 Stata/Python 进程，执行回归计算、稳健性检验并捕获完整输出。",
        "inputs": ["approved RunPlan", "本地计算沙盒"],
        "outputs": ["回归系数表", "异质性分析结果"],
    },
    {
        "id": "findings-review",
        "title": "6. 结果解释与证据审核",
        "owner": "ReviewerAgent",
        "status": "empty",
        "reason": "审核回归结果是否显性、控制变量是否稳定，以及机制分析是否符合逻辑路径。",
        "inputs": ["回归系数表", "机制分析结论"],
        "outputs": ["approved Finding", "可复现证据包"],
    },
    {
        "id": "manuscript-draft",
        "title": "7. 论文草稿与学术表述",
        "owner": "ManuscriptAgent",
        "status": "empty",
        "reason": "自动根据因果系数及机制审核包，起草实证部分的 LaTeX/Docx 段落及表格。",
        "inputs": ["approved Finding", "LaTeX 模板"],
        "outputs": ["Manuscript 草稿段落", "Word 数据附表"],
    },
    {
        "id": "export-reproducibility",
        "title": "8. 导出审计与可复现包",
        "owner": "Supervisor",
        "status": "empty",
        "reason": "对最终论文段落、Stata dofile、原始数据画像及人工审核链进行完整打包，生成可复现指纹。",
        "inputs": ["Manuscript", "完整执行 Trace"],
        "outputs": ["可复现压缩包 (zip)", "数据指纹签名"],
    },
]


def get_default_plan_draft() -> list[dict[str, Any]]:
    """Return the static 8-stage plan draft used by the brief tab's
    SupervisorPlanReview component when the user picks `codex-supervisor` mode.

    This is NOT the same as `generate_project_supervisor_plan()` — the latter
    requires a registered project, a confirmed ResearchQuestion, and an
    approved DesignSpec + RunPlan. The intake-time preview only needs the
    shape of what a plan would look like.
    """
    # Return a deep-ish copy so callers can't mutate the module constant.
    return [dict(stage) for stage in DEFAULT_PLAN_DRAFT_STAGES]
