from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.codex_provider import local_codex_status, run_local_codex_prompt
from Product.backend.design_spec_service import load_saved_design_spec, load_saved_run_plan
from Product.backend.internal_agent_skill_registry import (
    build_internal_agent_skill_recommendation_bundle,
    compact_internal_agent_skills_for_prompt,
)
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.research_question_service import load_saved_research_question
from Product.backend.variable_role_service import load_saved_variable_role_set


SUPERVISOR_PLAN_PATH = Path("state/product/supervisor_plan.json")
SUPERVISOR_PLAN_RAW_PATH = Path("state/product/supervisor_plan.raw.md")

REFERENCE_CHAIN_SOURCE_PRIORITY = ["cnki", "scholar", "zotero", "local_notes", "arxiv"]
REFERENCE_CHAIN_SOURCES: list[dict[str, Any]] = [
    {
        "id": "cnki",
        "label": "CNKI",
        "trigger": "中文制度背景、国内实证研究、硕博论文和政策语境。",
        "mode": "manual_assisted_or_browser_assisted_search",
    },
    {
        "id": "scholar",
        "label": "Google Scholar",
        "trigger": "英文引用网络、高被引经济学和社会科学文献。",
        "mode": "browser_or_manual_assisted_search",
    },
    {
        "id": "zotero",
        "label": "Zotero",
        "trigger": "用户已有文献库、PDF、笔记和引用条目。",
        "mode": "local_library_or_connector",
    },
    {
        "id": "local_notes",
        "label": "Local Notes",
        "trigger": "本机 Obsidian、项目笔记、人工摘录和已有资料。",
        "mode": "local_file_search",
    },
    {
        "id": "arxiv",
        "label": "arXiv",
        "trigger": "开放论文、方法论文和英文技术背景。",
        "mode": "api_or_web_search",
    },
]


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
        "reference_chain_policy": build_default_reference_chain_policy(),
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
        "reference_chain_policy_template": build_default_reference_chain_policy(),
        "write_boundary": "You must not modify VariableRoleSet, DesignSpec, or RunPlan. Propose a reviewable plan only.",
    }
    return (
        "你是本地 Codex Supervisor，负责为实证论文工作台生成下一轮可审阅研究执行计划。\n"
        "只输出 JSON，不要输出 Markdown。JSON 必须包含：stage_plan、subagent_dispatch、"
        "evidence_requirements、risks、human_gates、internal_skill_judgments、"
        "reference_chain_policy、next_action。\n"
        "internal_skill_judgments 用来解释你为什么选择某个内部 Agent Skill；"
        "每项必须只使用 internal_skill_registry.skills 中存在的 skill_id，并包含 reason、"
        "evidence_fit、agent_fit、risk_note、human_review_note、confidence。"
        "如果没有合适 skill，输出空数组，不要编造 registry 外 skill。\n"
        "reference_chain_policy 用来规划文献和引用证据链；必须包含 source_priority、sources、"
        "max_depth、max_iterations、draft_citation_policy、formal_writeback_gate、writes_formal_layer。"
        "可用来源包括 CNKI、Google Scholar、Zotero、Local Notes、arXiv；"
        "writes_formal_layer 必须为 false，候选引用只能进入草案层和人工审阅队列。\n"
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


def build_default_reference_chain_policy() -> dict[str, Any]:
    return {
        "contract_version": "reference_chain.v1",
        "status": "needs_review",
        "source_priority": list(REFERENCE_CHAIN_SOURCE_PRIORITY),
        "sources": [dict(source) for source in REFERENCE_CHAIN_SOURCES],
        "max_depth": 2,
        "max_iterations": 5,
        "required_artifacts": [
            "LiteratureSeedPackage",
            "search_query_graph",
            "citation_verification_queue",
            "source_relevance_review",
        ],
        "draft_citation_policy": "候选文献可以进入草案，但必须显示 candidate / verified / rejected 审阅状态。",
        "formal_writeback_gate": "review_literature_seed_package",
        "writes_formal_layer": False,
    }


def normalize_reference_chain_policy(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    default = build_default_reference_chain_policy()
    source_priority = [
        str(item)
        for item in normalize_list(raw.get("source_priority"))
        if str(item).strip()
    ] or default["source_priority"]
    sources = normalize_reference_chain_sources(raw.get("sources")) or default["sources"]
    return {
        "contract_version": str(raw.get("contract_version") or default["contract_version"]),
        "status": str(raw.get("status") or default["status"]),
        "source_priority": source_priority,
        "sources": sources,
        "max_depth": normalize_positive_int(raw.get("max_depth"), default["max_depth"]),
        "max_iterations": normalize_positive_int(raw.get("max_iterations"), default["max_iterations"]),
        "required_artifacts": [
            str(item)
            for item in normalize_list(raw.get("required_artifacts"))
            if str(item).strip()
        ] or default["required_artifacts"],
        "draft_citation_policy": str(
            raw.get("draft_citation_policy") or default["draft_citation_policy"]
        ),
        "formal_writeback_gate": str(
            raw.get("formal_writeback_gate") or default["formal_writeback_gate"]
        ),
        "writes_formal_layer": False,
    }


def normalize_reference_chain_sources(value: Any) -> list[dict[str, str]]:
    sources = []
    for source in normalize_list(value):
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("id") or source.get("name") or "").strip()
        if not source_id:
            continue
        sources.append(
            {
                "id": source_id,
                "label": str(source.get("label") or source_id),
                "trigger": str(source.get("trigger") or ""),
                "mode": str(source.get("mode") or ""),
            }
        )
    return sources


def normalize_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


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
    reference_chain_policy = normalize_reference_chain_policy(generated.get("reference_chain_policy"))
    llm_internal_skill_judgments = normalize_list(
        generated.get("internal_skill_judgments")
        or generated.get("skill_judgments")
        or generated.get("recommended_internal_skills")
    )
    internal_skill_recommendations = build_internal_agent_skill_recommendation_bundle(
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
            "internal_skill_judgments": llm_internal_skill_judgments,
        }
    )
    recommended_internal_skills = internal_skill_recommendations["recommended_internal_skills"]
    unmatched_internal_skill_judgments = internal_skill_recommendations[
        "unmatched_internal_skill_judgments"
    ]
    skill_review_contract = build_skill_review_contract(
        recommended_internal_skills,
        unmatched_internal_skill_judgments,
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
        "reference_chain_policy": reference_chain_policy,
        "llm_internal_skill_judgments": llm_internal_skill_judgments,
        "recommended_internal_skills": recommended_internal_skills,
        "unmatched_internal_skill_judgments": unmatched_internal_skill_judgments,
        "skill_review_contract": skill_review_contract,
        "skill_review_status": skill_review_contract["status"],
        "selected_skill_ids": skill_review_contract["selected_skill_ids"],
        "skill_sources": skill_review_contract["skill_sources"],
        "applicability_reason": skill_review_contract["applicability_reason"],
        "missing_evidence": skill_review_contract["missing_evidence"],
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


def build_skill_review_contract(
    recommended_internal_skills: list[Any],
    unmatched_internal_skill_judgments: list[Any],
) -> dict[str, Any]:
    selected_skills = [skill for skill in recommended_internal_skills if isinstance(skill, dict)]
    unmatched = [item for item in unmatched_internal_skill_judgments if isinstance(item, dict)]
    selected_skill_ids = [str(skill.get("skill_id") or skill.get("id") or "") for skill in selected_skills]
    selected_skill_ids = [skill_id for skill_id in selected_skill_ids if skill_id]
    status = "no_internal_skill_selected"
    if selected_skills:
        status = "ready_for_human_skill_review"
    if unmatched:
        status = "needs_human_skill_review"

    return {
        "status": status,
        "human_review_required": bool(selected_skills or unmatched),
        "selected_skill_ids": selected_skill_ids,
        "skill_sources": [compact_skill_source_for_review(skill) for skill in selected_skills],
        "applicability_reason": {
            str(skill.get("skill_id") or skill.get("id")): (
                skill.get("semantic_selection_reason")
                or skill.get("matched_reason")
                or ""
            )
            for skill in selected_skills
            if skill.get("skill_id") or skill.get("id")
        },
        "missing_evidence": [
            *[compact_skill_missing_evidence(skill) for skill in selected_skills],
            *[compact_unmatched_skill_judgment(item) for item in unmatched],
        ],
        "execution_boundary": {
            "queue_dispatch_requires_human_review": True,
            "canonical_method_write_allowed": False,
            "formal_state_write_allowed": False,
        },
    }


def compact_skill_source_for_review(skill: dict[str, Any]) -> dict[str, Any]:
    skill_sources = [source for source in normalize_list(skill.get("skill_sources")) if isinstance(source, dict)]
    return {
        "skill_id": skill.get("skill_id") or skill.get("id"),
        "name": skill.get("name", ""),
        "owner_agent": skill.get("owner_agent", ""),
        "risk_level": skill.get("risk_level", "medium"),
        "selection_source": skill.get("selection_source", "registry_rule_match"),
        "source_policy": skill.get("source_policy", ""),
        "external_source_names": [
            str(source.get("name"))
            for source in skill_sources
            if source.get("name")
        ],
        "skill_sources": skill_sources,
    }


def compact_skill_missing_evidence(skill: dict[str, Any]) -> dict[str, Any]:
    human_confirmation = skill.get("human_confirmation") if isinstance(skill.get("human_confirmation"), dict) else {}
    return {
        "skill_id": skill.get("skill_id") or skill.get("id"),
        "required_state": normalize_list(skill.get("required_state")),
        "blockers": normalize_list(skill.get("blockers")),
        "required_before": normalize_list(human_confirmation.get("required_before")),
        "quality_gates": skill.get("quality_gates") if isinstance(skill.get("quality_gates"), dict) else {},
    }


def compact_unmatched_skill_judgment(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "skill_id": item.get("skill_id") or item.get("id"),
        "status": item.get("status", "ignored_unknown_skill"),
        "reason_code": item.get("reason_code", "skill_not_in_internal_registry"),
        "reason": item.get("reason", ""),
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
