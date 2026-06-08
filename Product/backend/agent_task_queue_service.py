from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.internal_agent_skill_registry import normalize_agent_role_name
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.supervisor_plan_service import load_saved_supervisor_plan


AGENT_TASK_QUEUE_PATH = Path("state/product/agent_task_queue.json")
VALID_REFERENCE_SEED_REVIEW_ACTIONS = {
    "approve_for_draft",
    "needs_revision",
    "reject",
}
VALID_DRAFT_LITERATURE_REVIEW_REVIEW_ACTIONS = {
    "approve_for_citation_verification",
    "needs_revision",
    "reject",
}
VALID_VERIFIED_LITERATURE_PACKAGE_REVIEW_ACTIONS = {
    "approve_for_manuscript_citations",
    "needs_revision",
    "reject",
}
VALID_MANUSCRIPT_CITATION_PLAN_REVIEW_ACTIONS = {
    "approve_for_draft_sections",
    "needs_revision",
    "reject",
}
VALID_DRAFT_SECTION_PLAN_REVIEW_ACTIONS = {
    "approve_for_section_tasks",
    "needs_revision",
    "reject",
}
CITATION_VERIFICATION_REQUIRED_CHECKS = [
    "authors",
    "year",
    "title",
    "venue",
    "doi_or_stable_url",
    "relevance",
]
CITATION_VERIFICATION_EVIDENCE_REQUIRED_FIELDS = [
    "connector",
    "authors",
    "year",
    "title",
    "venue",
    "doi_or_stable_url",
    "relevance",
    "evidence_url",
]


class AgentTaskQueueBlockedError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def agent_task_queue_state_path(project_root: Path) -> Path:
    return project_root / AGENT_TASK_QUEUE_PATH


def get_project_agent_task_queue(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = load_saved_agent_task_queue(project_root)
    if not queue:
        queue = build_empty_agent_task_queue(project_root)
    return build_agent_task_queue_response(project, queue)


def create_project_agent_task_queue(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    plan = load_saved_supervisor_plan(project_root)
    require_approved_supervisor_plan(plan)
    dispatch_items = normalize_list(plan.get("subagent_dispatch"))
    if not dispatch_items:
        raise AgentTaskQueueBlockedError(
            "subagent_dispatch_required",
            "Approved SupervisorPlan must include subagent_dispatch before creating Agent Task Queue.",
        )

    timestamp = utc_now()
    queue = build_agent_task_queue(plan, dispatch_items, timestamp)
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return build_agent_task_queue_response(project, queue)


def load_saved_agent_task_queue(project_root: Path) -> dict[str, Any] | None:
    path = agent_task_queue_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_agent_task_queue(project_root: Path) -> dict[str, Any]:
    plan = load_saved_supervisor_plan(project_root)
    blockers = agent_task_queue_blockers(plan)
    can_create = not blockers and bool(normalize_list(plan.get("subagent_dispatch") if plan else []))
    llm_intervention_contract = build_llm_intervention_contract(plan)
    reference_chain_policy = build_reference_chain_policy(plan)
    return {
        "id": "agent_task_queue",
        "version": 0,
        "status": "ready_to_create" if can_create else "empty",
        "exists": agent_task_queue_state_path(project_root).exists(),
        "can_create": can_create,
        "evidence_level": "local_file",
        "source_supervisor_plan": compact_supervisor_plan_source(plan),
        "summary": {
            "total_tasks": 0,
            "queued_count": 0,
            "blocked_count": len(blockers),
            "owner_agents": [],
            "internal_skill_count": 0,
            "high_risk_internal_skill_count": 0,
        },
        "tasks": [],
        "blockers": blockers,
        "llm_intervention_contract": llm_intervention_contract,
        "reference_chain_policy": reference_chain_policy,
        "ui_contract": build_queue_ui_contract(),
        "primary_action": build_empty_queue_primary_action(can_create),
        "next_action": {
            "id": "create_agent_task_queue" if can_create else "approve_supervisor_plan",
            "label": "创建 Agent 任务队列" if can_create else "先批准 SupervisorPlan",
        },
        "path": AGENT_TASK_QUEUE_PATH.as_posix(),
    }


def require_approved_supervisor_plan(plan: dict[str, Any] | None) -> None:
    if not plan:
        raise AgentTaskQueueBlockedError(
            "supervisor_plan_required",
            "Approved SupervisorPlan is required before creating Agent Task Queue.",
        )
    if plan.get("status") != "approved" or plan.get("can_dispatch") is not True:
        raise AgentTaskQueueBlockedError(
            "supervisor_plan_not_approved",
            "SupervisorPlan must be approved and can_dispatch=true before creating Agent Task Queue.",
        )


def agent_task_queue_blockers(plan: dict[str, Any] | None) -> list[dict[str, str]]:
    if not plan:
        return [
            {
                "code": "supervisor_plan_required",
                "label": "缺少 SupervisorPlan",
                "description": "先由本地 Codex Supervisor 生成可审阅计划。",
            }
        ]
    if plan.get("status") != "approved" or plan.get("can_dispatch") is not True:
        return [
            {
                "code": "supervisor_plan_not_approved",
                "label": "SupervisorPlan 尚未批准",
                "description": "只有人工批准后的计划才能创建任务队列。",
            }
        ]
    if not normalize_list(plan.get("subagent_dispatch")):
        return [
            {
                "code": "subagent_dispatch_required",
                "label": "缺少子 Agent 分工",
                "description": "Approved SupervisorPlan 必须包含 subagent_dispatch。",
            }
        ]
    return []


def build_agent_task_queue(plan: dict[str, Any], dispatch_items: list[Any], timestamp: str) -> dict[str, Any]:
    llm_intervention_contract = build_llm_intervention_contract(plan)
    reference_chain_policy = build_reference_chain_policy(plan)
    tasks = [
        build_agent_task(index, dispatch, plan, timestamp, llm_intervention_contract, reference_chain_policy)
        for index, dispatch in enumerate(dispatch_items, start=1)
    ]
    return {
        "id": "agent_task_queue",
        "version": 1,
        "status": "ready_for_dispatch",
        "exists": True,
        "can_create": False,
        "evidence_level": "local_file",
        "source_supervisor_plan": compact_supervisor_plan_source(plan),
        "summary": build_agent_task_queue_summary(tasks),
        "tasks": tasks,
        "blockers": [],
        "llm_intervention_contract": llm_intervention_contract,
        "reference_chain_policy": reference_chain_policy,
        "ui_contract": build_queue_ui_contract(),
        "primary_action": build_queue_primary_action(tasks),
        "next_action": {
            "id": "dispatch_agent_tasks",
            "label": "检查后进入真实 Agent 执行队列",
        },
        "path": AGENT_TASK_QUEUE_PATH.as_posix(),
        "updated_at": timestamp,
    }


def build_agent_task(
    index: int,
    dispatch: Any,
    plan: dict[str, Any],
    timestamp: str,
    llm_intervention_contract: dict[str, Any],
    reference_chain_policy: dict[str, Any],
) -> dict[str, Any]:
    dispatch_item = dispatch if isinstance(dispatch, dict) else {"task": str(dispatch)}
    owner_agent = str(dispatch_item.get("agent_id") or dispatch_item.get("role") or f"agent_{index:02d}")
    role = str(dispatch_item.get("role") or owner_agent)
    title = str(dispatch_item.get("task") or dispatch_item.get("title") or dispatch_item.get("goal") or f"Agent task {index}")
    internal_skill_bindings = build_task_internal_skill_bindings(plan, dispatch_item, owner_agent, role)
    task_reference_chain_policy = build_task_reference_chain_policy(
        reference_chain_policy,
        internal_skill_bindings,
        owner_agent,
        role,
        title,
    )
    task = {
        "id": f"agent_task_{index:02d}",
        "source_dispatch_id": dispatch_item.get("agent_id") or "",
        "owner_agent": owner_agent,
        "role": role,
        "title": title,
        "summary": str(dispatch_item.get("summary") or title),
        "status": "queued",
        "can_execute": False,
        "next_action": "dispatch_review_required",
        "dispatch_readiness": {
            "status": "blocked",
            "blockers": [dispatch_review_required_blocker()],
        },
        "dispatch_review": {
            "status": "pending",
            "evidence_level": "local_file",
        },
        "input_evidence": build_task_input_evidence(plan),
        "output_requirements": build_output_requirements(plan, dispatch_item),
        "internal_skill_bindings": internal_skill_bindings,
        "llm_intervention_handoff": build_task_llm_intervention_handoff(
            llm_intervention_contract,
            internal_skill_bindings,
        ),
        "blockers": [],
        "risk_flags": normalize_list(plan.get("risks")),
        "audit_log": [
            {
                "event": "task_created_from_supervisor_plan",
                "actor": "product_workbench",
                "timestamp": timestamp,
                "source_supervisor_plan_version": plan.get("version", 0),
            }
        ],
    }
    if task_reference_chain_policy:
        task["reference_chain_policy"] = task_reference_chain_policy
    task["primary_action"] = build_task_primary_action(task)
    return task


def build_empty_queue_primary_action(can_create: bool) -> dict[str, Any]:
    if can_create:
        return {
            "id": "create_agent_task_queue",
            "label": "创建 Agent 任务队列",
            "reason": "SupervisorPlan 已批准，可以先生成可审阅任务队列。",
            "enabled": True,
            "writes_formal_layer": False,
        }
    return {
        "id": "approve_supervisor_plan",
        "label": "先批准 SupervisorPlan",
        "reason": "还没有可派发的已批准计划，不能创建任务队列。",
        "enabled": False,
        "writes_formal_layer": False,
    }


def build_queue_primary_action(tasks: list[Any]) -> dict[str, Any]:
    task_dicts = [task for task in tasks if isinstance(task, dict)]
    if not task_dicts:
        return {
            "id": "none",
            "label": "暂无可执行动作",
            "reason": "任务队列为空。",
            "enabled": False,
            "writes_formal_layer": False,
        }
    for task in task_dicts:
        action = task.get("primary_action") if isinstance(task.get("primary_action"), dict) else {}
        if action.get("id") != "review_execution_result":
            return {
                **action,
                "task_id": task.get("id", ""),
                "task_title": task.get("title", ""),
            }
    action = task_dicts[0].get("primary_action") if isinstance(task_dicts[0].get("primary_action"), dict) else {}
    return {
        **action,
        "task_id": task_dicts[0].get("id", ""),
        "task_title": task_dicts[0].get("title", ""),
    }


def build_task_primary_action(task: dict[str, Any]) -> dict[str, Any]:
    status = str(task.get("status") or "queued")
    if status == "queued":
        return {
            "id": "dispatch_review_required",
            "label": "打开派工审阅",
            "reason": "这个任务还在草案层，不能直接执行；先确认是否真的要派给这个 Agent。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "dispatch_review",
        }
    if status == "reviewed_for_dispatch":
        return {
            "id": "select_execution_backend",
            "label": "选择执行后端",
            "reason": "派工已批准，下一步需要选择 StatsPAI、Python、StataMCP 或 Codex 等执行后端。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "backend_selection",
        }
    if status == "backend_selected":
        return {
            "id": "execute_agent_task",
            "label": "开始真实执行",
            "reason": "后端已选择，可以运行本地执行、脚本生成或统计适配器；产物仍进入审阅层。",
            "enabled": bool(task.get("can_execute")),
            "writes_formal_layer": False,
            "target": "agent_task_execution",
        }
    if status == "succeeded":
        return {
            "id": "review_execution_result",
            "label": "查看运行结果",
            "reason": "任务已产生结果，下一步是审阅产物、日志和 evaluator 结论。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "execution_result_review",
        }
    if status == "reviewed_for_draft":
        return {
            "id": "draft_literature_review",
            "label": "进入草稿综述",
            "reason": "候选来源种子包已通过人工审阅，可以进入草稿综述；引用仍保持候选状态，不能写入正式层。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_literature_review",
        }
    if status == "draft_literature_review_ready":
        return {
            "id": "review_draft_literature_review",
            "label": "审阅草稿综述",
            "reason": "草稿层文献综述已生成，下一步审阅引用候选、缺失证据和正式层边界。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_literature_review_review",
        }
    if status == "citation_verification_ready":
        return {
            "id": "verify_citations",
            "label": "进入引用核验",
            "reason": "草稿综述已通过人工审阅，下一步逐条核对作者、年份、题名、期刊和 DOI 或稳定链接。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "citation_verification_tasks",
        }
    if status == "citation_verification_complete":
        return {
            "id": "generate_verified_literature_package",
            "label": "生成已核验文献包",
            "reason": "全部候选引用已记录核验证据，可以生成可追溯文献包。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "verified_literature_package",
        }
    if status == "verified_literature_package_ready":
        return {
            "id": "review_verified_literature_package",
            "label": "审阅已核验文献包",
            "reason": "文献来源已形成可追溯包，下一步由人工决定是否进入论文草稿引用层。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "verified_literature_package_review",
        }
    if status == "verified_literature_package_approved":
        return {
            "id": "generate_manuscript_citation_plan",
            "label": "生成论文引用计划",
            "reason": "已核验文献包通过人工审阅，可以生成草稿层引用计划；正式正文仍需单独审批。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "manuscript_citation_plan",
        }
    if status == "manuscript_citation_plan_ready":
        return {
            "id": "review_manuscript_citation_plan",
            "label": "审阅论文引用计划",
            "reason": "引用计划已生成，下一步审阅每条来源将进入哪个论文章节和论证位置。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "manuscript_citation_plan_review",
        }
    if status == "manuscript_citation_plan_approved":
        return {
            "id": "generate_draft_section_plan",
            "label": "生成章节草稿计划",
            "reason": "引用计划已通过审阅，下一步可以把已核验来源映射到章节草稿任务。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_section_plan",
        }
    if status == "draft_section_plan_ready":
        return {
            "id": "review_draft_section_plan",
            "label": "审阅章节草稿计划",
            "reason": "章节草稿计划已生成，下一步审阅章节边界、引用绑定和写作任务。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_section_plan_review",
        }
    if status == "draft_section_plan_approved":
        return {
            "id": "generate_draft_section_tasks",
            "label": "生成章节草稿任务包",
            "reason": "章节草稿计划已通过审阅，下一步把章节边界和引用绑定拆成可执行草稿任务。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_section_tasks",
        }
    if status == "draft_section_tasks_ready":
        return {
            "id": "review_draft_section_tasks",
            "label": "审阅章节草稿任务包",
            "reason": "章节草稿任务包已生成，下一步审阅每个章节任务的范围、引用绑定和证据要求。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "draft_section_tasks_review",
        }
    if status == "rejected":
        return {
            "id": "replace_literature_search",
            "label": "更换检索方案",
            "reason": "候选来源种子包已被拒绝，需要重新生成检索式或更换来源。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "reference_seed_revision",
        }
    if status == "blocked_by_backend_unavailable":
        return {
            "id": "choose_fallback_backend",
            "label": "选择备用后端",
            "reason": "当前执行后端不可用，先切换到可用后端或重试。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "backend_selection",
        }
    if status in {"blocked", "needs_revision"}:
        return {
            "id": "revise_dispatch_task",
            "label": "修改任务",
            "reason": "派工被拒绝或要求修改，先调整任务边界再继续。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "dispatch_revision",
        }
    return {
        "id": str(task.get("next_action") or "review_task_state"),
        "label": "查看任务状态",
        "reason": "当前任务状态需要人工查看后决定下一步。",
        "enabled": False,
        "writes_formal_layer": False,
        "target": "task_state",
    }


def default_llm_intervention_product_chain() -> list[str]:
    return [
        "topic_intake",
        "supervisor_plan",
        "skill_selection",
        "agent_task_queue",
        "literature_search",
        "data_variables",
        "method_design",
        "execution_experiment",
        "writing",
        "review_export",
    ]


def default_llm_intervention_stage_handoffs() -> list[dict[str, Any]]:
    return [
        {
            "stage": "topic_intake",
            "llm_role": "解析研究题目、数据线索、方法倾向和成功标准。",
            "deterministic_owner": "research_question_service",
            "handoff_condition": "写入 ResearchQuestion / TopicSession 草案。",
            "human_gate": "confirm_research_question",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "no_subagent_before_topic_confirmed",
            "control_returns_to_user_when": "题目、数据线索和研究边界需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "supervisor_plan",
            "llm_role": "生成研究路线、风险、证据要求和子 Agent 分工。",
            "deterministic_owner": "supervisor_plan_service",
            "handoff_condition": "写入 needs_review 或 approved SupervisorPlan；不改写正式研究状态。",
            "human_gate": "review_supervisor_plan",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "spawn_sidecar_agents_after_plan_review",
            "control_returns_to_user_when": "SupervisorPlan 需要 approve、revise 或 reject。",
            "writes_formal_layer": False,
        },
        {
            "stage": "skill_selection",
            "llm_role": "解释为什么选择 Skill，并列出缺失证据。",
            "deterministic_owner": "internal_skill_registry",
            "handoff_condition": "Skill id、来源、适用理由和执行边界写入 plan 和 queue。",
            "human_gate": "review_internal_skill_before_execution",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "method_or_literature_agents_can_recommend_but_not_merge_canonical_rules",
            "control_returns_to_user_when": "高风险 Skill 或正式层写回前需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "agent_task_queue",
            "llm_role": "把研究路线拆成子 Agent 任务摘要和阻塞项。",
            "deterministic_owner": "agent_task_queue_service",
            "handoff_condition": "任务队列持久化为 local_file，默认不可执行。",
            "human_gate": "dispatch_review_required",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "dispatch_agents_only_after_global_review_button",
            "control_returns_to_user_when": "队列生成后等待派工审阅。",
            "writes_formal_layer": False,
        },
        {
            "stage": "literature_search",
            "llm_role": "生成检索式、重排文献、提炼文献缺口和引用候选。",
            "deterministic_owner": "literature_search_service",
            "handoff_condition": "写入 LiteratureSeedPackage、query graph 和 citation verification queue。",
            "human_gate": "review_literature_seed_package",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "literature_agents_can_search_in_parallel_with_citation_verifier",
            "control_returns_to_user_when": "种子文献和引用可信度需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "data_variables",
            "llm_role": "解释变量角色候选、样本口径和字段含义。",
            "deterministic_owner": "data_profile_and_variable_role_service",
            "handoff_condition": "字段画像、变量候选和缺失证据写入草案层。",
            "human_gate": "review_variable_role_set",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "data_agent_profiles_first_method_agent_waits_for_roles",
            "control_returns_to_user_when": "因变量、处理变量、控制变量或样本口径需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "method_design",
            "llm_role": "解释识别策略、方法门、前置条件和稳健性路线。",
            "deterministic_owner": "method_workflow_service",
            "handoff_condition": "写入 DesignSpec / RunPlan 草案和 method gate checklist。",
            "human_gate": "review_design_spec_and_run_plan",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "method_agent_may_request_stats_backend_schema_before_execution",
            "control_returns_to_user_when": "识别假设、方法选择或运行计划需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "execution_experiment",
            "llm_role": "解释执行失败、诊断日志、下一轮修复和 evaluator 结果。",
            "deterministic_owner": "execution_backend_router",
            "handoff_condition": "StatsPAI / Python / StataMCP / Codex 后端产生日志、结果和证据文件。",
            "human_gate": "review_execution_result",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "execution_agent_runs_after_backend_selection_reviewer_checks_outputs",
            "control_returns_to_user_when": "运行产物、失败原因或 evaluator 结论需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "writing",
            "llm_role": "生成研究报告、exploratory 论文草案和修订建议。",
            "deterministic_owner": "manuscript_draft_service",
            "handoff_condition": "只写草案层 manuscript 和 evidence binding。",
            "human_gate": "review_manuscript_draft",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "writer_agent_works_after_results_reviewer_can_request_revision",
            "control_returns_to_user_when": "草案段落、论断强度和证据绑定需要确认。",
            "writes_formal_layer": False,
        },
        {
            "stage": "review_export",
            "llm_role": "按 Journal Skill 做审稿门、格式门和导出预检。",
            "deterministic_owner": "review_export_service",
            "handoff_condition": "写入 ReviewExport gates、PDF/DOCX 预检和复现包清单。",
            "human_gate": "export_preflight_review",
            "formal_boundary": "draft_only_until_human_review",
            "agent_team_policy": "reviewer_and_export_agents_check_package_before_formal_promotion",
            "control_returns_to_user_when": "导出预检和正式层晋升需要确认。",
            "writes_formal_layer": False,
        },
    ]


def build_llm_intervention_contract(plan: dict[str, Any] | None) -> dict[str, Any]:
    raw_contract = plan.get("llm_intervention_plan") if isinstance(plan, dict) else None
    contract = raw_contract if isinstance(raw_contract, dict) else {}
    product_chain = [
        str(stage)
        for stage in normalize_list(contract.get("product_chain"))
        if str(stage)
    ] or default_llm_intervention_product_chain()
    default_handoffs = {item["stage"]: item for item in default_llm_intervention_stage_handoffs()}
    stage_handoffs = merge_llm_stage_handoffs(
        product_chain,
        default_handoffs,
        [
            item
            for item in normalize_list(contract.get("stage_handoffs"))
            if isinstance(item, dict)
        ],
    )
    return {
        "contract_version": str(contract.get("contract_version") or "llm_intervention.v1"),
        "default_policy": str(
            contract.get("default_policy") or "llm_plans_deterministic_executes_human_promotes"
        ),
        "product_chain": product_chain,
        "stage_handoffs": stage_handoffs,
    }


def merge_llm_stage_handoffs(
    product_chain: list[str],
    default_handoffs: dict[str, dict[str, Any]],
    custom_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = dict(default_handoffs)
    custom_order: list[str] = []
    for item in custom_items:
        stage = str(item.get("stage") or "agent_task_queue")
        base = default_handoffs.get(stage, {})
        merged[stage] = {**base, **item}
        if stage not in product_chain and stage not in custom_order:
            custom_order.append(stage)
    return [
        normalize_llm_stage_handoff(merged[stage])
        for stage in [*product_chain, *custom_order]
        if stage in merged
    ]


def normalize_llm_stage_handoff(item: dict[str, Any]) -> dict[str, Any]:
    stage = str(item.get("stage") or "agent_task_queue")
    base = {
        handoff["stage"]: handoff
        for handoff in default_llm_intervention_stage_handoffs()
    }.get(stage, {})
    merged = {**base, **item}
    return {
        "stage": str(merged.get("stage") or "agent_task_queue"),
        "llm_role": str(merged.get("llm_role") or "生成可审阅判断，不直接改写正式层。"),
        "deterministic_owner": str(merged.get("deterministic_owner") or "agent_task_queue_service"),
        "handoff_condition": str(merged.get("handoff_condition") or "写入本地状态文件，等待人工确认。"),
        "human_gate": str(merged.get("human_gate") or "dispatch_review_required"),
        "formal_boundary": str(merged.get("formal_boundary") or "draft_only_until_human_review"),
        "agent_team_policy": str(merged.get("agent_team_policy") or "single_agent_until_human_gate"),
        "control_returns_to_user_when": str(merged.get("control_returns_to_user_when") or "需要人工确认下一步。"),
        "writes_formal_layer": bool(merged.get("writes_formal_layer") is True),
    }


def build_task_llm_intervention_handoff(
    llm_intervention_contract: dict[str, Any],
    internal_skill_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    first_skill = internal_skill_bindings[0] if internal_skill_bindings else {}
    stage = "skill_selection" if first_skill else "agent_task_queue"
    handoff = find_llm_stage_handoff(llm_intervention_contract, stage)
    result: dict[str, Any] = {
        "stage": handoff["stage"],
        "llm_role": handoff["llm_role"],
        "deterministic_owner": handoff["deterministic_owner"],
        "handoff_condition": handoff["handoff_condition"],
        "human_gate": handoff["human_gate"],
        "formal_boundary": handoff["formal_boundary"],
    }
    if first_skill:
        result.update(
            {
                "selected_skill_id": first_skill.get("skill_id") or first_skill.get("id"),
                "selected_skill_name": first_skill.get("name"),
                "selected_skill_reason": first_skill.get("why_this_skill")
                or first_skill.get("semantic_selection_reason")
                or first_skill.get("matched_reason", ""),
                "selection_source": first_skill.get("selection_source", ""),
            }
        )
    return result


def find_llm_stage_handoff(contract: dict[str, Any], stage: str) -> dict[str, str]:
    for handoff in normalize_list(contract.get("stage_handoffs")):
        if isinstance(handoff, dict) and handoff.get("stage") == stage:
            return normalize_llm_stage_handoff(handoff)
    for handoff in default_llm_intervention_stage_handoffs():
        if handoff.get("stage") == stage:
            return handoff
    return default_llm_intervention_stage_handoffs()[-1]


def build_reference_chain_policy(plan: dict[str, Any] | None) -> dict[str, Any]:
    raw_policy = plan.get("reference_chain_policy") if isinstance(plan, dict) else None
    policy = raw_policy if isinstance(raw_policy, dict) else {}
    sources = build_reference_chain_sources(policy.get("sources"))
    source_priority = [
        str(source_id)
        for source_id in normalize_list(policy.get("source_priority"))
        if str(source_id).strip()
    ] or [source["id"] for source in sources]
    return {
        "contract_version": str(policy.get("contract_version") or "reference_chain.v1"),
        "status": str(policy.get("status") or "needs_review"),
        "default_policy": str(
            policy.get("default_policy")
            or "recursive_search_requires_verified_citations_before_formal_writeback"
        ),
        "max_depth": int(policy.get("max_depth") or 2),
        "max_iterations": int(policy.get("max_iterations") or 5),
        "source_priority": source_priority,
        "sources": sources,
        "required_artifacts": normalize_list(policy.get("required_artifacts"))
        or [
            "LiteratureSeedPackage",
            "search_query_graph",
            "citation_verification_queue",
            "source_relevance_review",
        ],
        "candidate_reference_states": normalize_list(policy.get("candidate_reference_states"))
        or ["candidate", "verified", "rejected"],
        "draft_citation_policy": str(
            policy.get("draft_citation_policy")
            or "candidate_references_may_enter_draft_with_visible_review_state"
        ),
        "formal_writeback_gate": str(policy.get("formal_writeback_gate") or "review_literature_seed_package"),
        "writes_formal_layer": False,
    }


def build_reference_chain_sources(raw_sources: Any) -> list[dict[str, str]]:
    default_sources = [
        {
            "id": "arxiv",
            "label": "arXiv",
            "trigger": "需要英文工作论文、方法线索或最新开放论文。",
            "mode": "automated_search",
        },
        {
            "id": "scholar",
            "label": "Google Scholar",
            "trigger": "需要追踪引用网络、核心文献和英文发表版本。",
            "mode": "browser_or_manual_assisted_search",
        },
        {
            "id": "cnki",
            "label": "CNKI",
            "trigger": "需要中文制度背景、本土文献和中文关键词扩展。",
            "mode": "manual_assisted_or_browser_assisted_search",
        },
        {
            "id": "zotero",
            "label": "Zotero",
            "trigger": "需要读取用户已有文献库或已整理 reference bank。",
            "mode": "local_connector_or_export_import",
        },
        {
            "id": "local_notes",
            "label": "Local notes",
            "trigger": "需要读取项目笔记、历史研究材料或本地证据包。",
            "mode": "local_file_search",
        },
    ]
    overrides = {
        str(source.get("id")): source
        for source in normalize_list(raw_sources)
        if isinstance(source, dict) and source.get("id")
    }
    result: list[dict[str, str]] = []
    for source in default_sources:
        merged = {**source, **overrides.get(source["id"], {})}
        result.append(
            {
                "id": str(merged.get("id") or source["id"]),
                "label": str(merged.get("label") or source["label"]),
                "trigger": str(merged.get("trigger") or source["trigger"]),
                "mode": str(merged.get("mode") or source["mode"]),
                "review_state": str(merged.get("review_state") or "candidate"),
            }
        )
    return result


def build_task_reference_chain_policy(
    reference_chain_policy: dict[str, Any],
    internal_skill_bindings: list[dict[str, Any]],
    owner_agent: str,
    role: str,
    title: str,
) -> dict[str, Any]:
    if not is_reference_chain_task(internal_skill_bindings, owner_agent, role, title):
        return {}
    task_policy = dict(reference_chain_policy)
    task_policy["status"] = str(task_policy.get("status") or "needs_review")
    task_policy["scope"] = "task_literature_reference_chain"
    task_policy["control_returns_to_user_when"] = "种子文献、引用可信度或正式综述写回需要确认。"
    return task_policy


def is_reference_chain_task(
    internal_skill_bindings: list[dict[str, Any]],
    owner_agent: str,
    role: str,
    title: str,
) -> bool:
    task_text = " ".join([owner_agent, role, title]).lower()
    if "literature" in task_text or "文献" in task_text or "引用" in task_text:
        return True
    for binding in internal_skill_bindings:
        skill_text = " ".join(
            [
                str(binding.get("skill_id") or ""),
                str(binding.get("stage") or ""),
                str(binding.get("name") or ""),
            ]
        ).lower()
        if "recursive_research_search" in skill_text or "literature" in skill_text or "citation" in skill_text:
            return True
    return False


def build_task_internal_skill_bindings(
    plan: dict[str, Any],
    dispatch_item: dict[str, Any],
    owner_agent: str,
    role: str,
) -> list[dict[str, Any]]:
    dispatch_id = str(dispatch_item.get("agent_id") or owner_agent)
    normalized_candidates = {
        normalize_agent_role_name(dispatch_id),
        normalize_agent_role_name(owner_agent),
        normalize_agent_role_name(role),
    }
    bindings: list[dict[str, Any]] = []
    for skill in normalize_list(plan.get("recommended_internal_skills")):
        if not isinstance(skill, dict):
            continue
        targets = [str(target) for target in normalize_list(skill.get("dispatch_targets"))]
        if targets and dispatch_id not in targets and owner_agent not in targets and role not in targets:
            continue
        if not targets:
            owner = normalize_agent_role_name(skill.get("owner_agent"))
            allowed = {
                normalize_agent_role_name(agent)
                for agent in normalize_list(skill.get("allowed_agents"))
            }
            if owner not in normalized_candidates and not allowed.intersection(normalized_candidates):
                continue
        bindings.append(compact_task_internal_skill_binding(skill))
    return bindings


def compact_task_internal_skill_binding(skill: dict[str, Any]) -> dict[str, Any]:
    semantic_reason = skill.get("semantic_selection_reason") or skill.get("matched_reason", "")
    return {
        "id": skill.get("id"),
        "skill_id": skill.get("skill_id"),
        "name": skill.get("name"),
        "owner_agent": skill.get("owner_agent"),
        "stage": skill.get("stage"),
        "risk_level": skill.get("risk_level", "medium"),
        "status": skill.get("status", "checklist"),
        "matched_reason": skill.get("matched_reason", ""),
        "selection_source": skill.get("selection_source", "registry_rule_match"),
        "semantic_selection_reason": semantic_reason,
        "why_this_skill": semantic_reason,
        "llm_semantic_judgment": skill.get("llm_semantic_judgment") or {},
        "expected_artifacts": normalize_list(skill.get("expected_artifacts")),
        "execution_boundary": skill.get("execution_boundary") or "review_before_execution",
        "skill_sources": [
            source for source in normalize_list(skill.get("skill_sources")) if isinstance(source, dict)
        ],
        "can_execute_without_human_review": bool(skill.get("can_execute_without_human_review", False)),
        "quality_gates": skill.get("quality_gates") or {},
        "human_confirmation": skill.get("human_confirmation") or {},
        "benchmark": skill.get("benchmark") or {},
        "formal_write_targets": normalize_list(skill.get("formal_write_targets")),
        "source_policy": skill.get("source_policy", ""),
        "reference_chain_policy": skill.get("reference_chain_policy") or {},
        "canonical_policy": skill.get("canonical_policy") or {},
        "next_action": "review_internal_skill_before_execution",
    }


def build_task_input_evidence(plan: dict[str, Any]) -> dict[str, Any]:
    input_evidence = plan.get("input_evidence") if isinstance(plan.get("input_evidence"), dict) else {}
    return {
        "supervisor_plan": {
            "path": "state/product/supervisor_plan.json",
            "version": plan.get("version", 0),
            "evidence_level": plan.get("evidence_level", "local_execution"),
        },
        "research_question": plan.get("input_research_question") or {},
        "state_paths": input_evidence,
    }


def build_output_requirements(plan: dict[str, Any], dispatch_item: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_outputs = normalize_list(dispatch_item.get("output_requirements"))
    if explicit_outputs:
        return [item if isinstance(item, dict) else {"requirement": str(item)} for item in explicit_outputs]
    requirements = normalize_list(plan.get("evidence_requirements"))
    return [
        item if isinstance(item, dict) else {"requirement": str(item)}
        for item in requirements
    ]


def compact_supervisor_plan_source(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not plan:
        return {
            "exists": False,
            "path": "state/product/supervisor_plan.json",
        }
    return {
        "exists": True,
        "id": plan.get("id", "supervisor_plan"),
        "version": int(plan.get("version", 0)),
        "status": plan.get("status", "unknown"),
        "can_dispatch": bool(plan.get("can_dispatch")),
        "path": plan.get("path") or "state/product/supervisor_plan.json",
        "objective": plan.get("objective", ""),
        "research_question": (plan.get("input_research_question") or {}).get("question", ""),
    }


def build_queue_ui_contract() -> dict[str, Any]:
    return {
        "summary_first": True,
        "details_collapsed_by_default": True,
        "primary_object": "agent_task",
        "hidden_by_default": [
            "input_evidence",
            "output_requirements",
            "internal_skill_bindings",
            "llm_intervention_contract",
            "reference_chain_policy",
            "risk_flags",
            "audit_log",
        ],
    }


def build_agent_task_queue_response(project: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    queue = normalize_agent_task_queue(queue)
    return {
        "_meta": {
            "evidence_level": queue.get("evidence_level", "local_file"),
            "service": "agent_task_queue_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "agent_task_queue": queue,
    }


def normalize_agent_task_queue(queue: dict[str, Any]) -> dict[str, Any]:
    queue.setdefault("llm_intervention_contract", build_llm_intervention_contract(None))
    queue.setdefault("reference_chain_policy", build_reference_chain_policy(None))
    queue.setdefault("ui_contract", build_queue_ui_contract())
    tasks = normalize_list(queue.get("tasks"))
    if tasks:
        for task in tasks:
            if isinstance(task, dict):
                ensure_task_dispatch_audit_fields(
                    task,
                    queue["llm_intervention_contract"],
                    queue["reference_chain_policy"],
                )
        queue["summary"] = build_agent_task_queue_summary(tasks)
        queue["primary_action"] = build_queue_primary_action(tasks)
    return queue


def ensure_task_dispatch_audit_fields(
    task: dict[str, Any],
    llm_intervention_contract: dict[str, Any],
    reference_chain_policy: dict[str, Any],
) -> None:
    status = str(task.get("status") or "queued")
    task.setdefault("can_execute", False)
    internal_skill_bindings = [
        binding
        for binding in normalize_list(task.get("internal_skill_bindings"))
        if isinstance(binding, dict)
    ]
    task.setdefault(
        "llm_intervention_handoff",
        build_task_llm_intervention_handoff(
            llm_intervention_contract,
            internal_skill_bindings,
        ),
    )
    task_reference_chain_policy = build_task_reference_chain_policy(
        reference_chain_policy,
        internal_skill_bindings,
        str(task.get("owner_agent") or ""),
        str(task.get("role") or ""),
        str(task.get("title") or ""),
    )
    if task_reference_chain_policy:
        task.setdefault("reference_chain_policy", task_reference_chain_policy)
    if status == "reviewed_for_dispatch":
        task.setdefault("next_action", "select_execution_backend")
        task.setdefault("dispatch_readiness", {"status": "reviewed_for_dispatch", "blockers": []})
    elif status == "blocked":
        task.setdefault("next_action", "revise_dispatch_task")
        task.setdefault(
            "dispatch_readiness",
            {
                "status": "blocked",
                "blockers": task.get("blockers") or [dispatch_review_required_blocker()],
            },
        )
    else:
        task.setdefault("next_action", "dispatch_review_required")
        task.setdefault(
            "dispatch_readiness",
            {
                "status": "blocked",
                "blockers": [dispatch_review_required_blocker()],
            },
        )
    task.setdefault(
        "dispatch_review",
        {
            "status": "pending",
            "evidence_level": "local_file",
        },
    )
    task["primary_action"] = build_task_primary_action(task)


def build_agent_task_queue_summary(tasks: list[Any]) -> dict[str, Any]:
    task_dicts = [task for task in tasks if isinstance(task, dict)]
    skill_bindings = [
        binding
        for task in task_dicts
        for binding in normalize_list(task.get("internal_skill_bindings"))
        if isinstance(binding, dict)
    ]
    return {
        "total_tasks": len(task_dicts),
        "queued_count": len([task for task in task_dicts if task.get("status") == "queued"]),
        "blocked_count": len([task for task in task_dicts if task.get("blockers")]),
        "dispatch_reviewed_count": len(
            [task for task in task_dicts if task.get("status") == "reviewed_for_dispatch"]
        ),
        "needs_revision_count": len([task for task in task_dicts if task.get("status") == "needs_revision"]),
        "owner_agents": unique_preserve_order([str(task.get("owner_agent", "")) for task in task_dicts]),
        "internal_skill_count": len(skill_bindings),
        "high_risk_internal_skill_count": len(
            [binding for binding in skill_bindings if binding.get("risk_level") == "high"]
        ),
    }


def dispatch_review_required_blocker() -> dict[str, str]:
    return {
        "code": "dispatch_review_required",
        "label": "等待人工派工审阅",
        "description": "队列草案不能直接执行，必须先确认这个子 Agent 任务是否应该派发。",
    }


def normalize_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _load_required_queue(project_root: Path) -> dict[str, Any]:
    queue = load_saved_agent_task_queue(project_root)
    if not queue:
        raise AgentTaskQueueBlockedError(
            "agent_task_queue_required",
            "Agent Task Queue must exist before this operation.",
        )
    return queue


def _find_agent_task(queue: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in queue.get("tasks", []):
        if isinstance(task, dict) and task.get("id") == task_id:
            return task
    raise AgentTaskQueueBlockedError(
        "agent_task_not_found",
        f"Agent task {task_id} does not exist.",
    )


def select_project_agent_task_backend(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    backend_id: str,
) -> dict[str, Any]:
    from Product.backend.execution_backend_service import (
        ExecutionBackendSelectionError,
        select_execution_backend,
    )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    select_execution_backend(task, backend_id)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = utc_now()
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return build_agent_task_queue_response(project, queue)


def execute_project_agent_task(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    from Product.backend.execution_backend_service import execute_agent_task_with_backend

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    selected_backend = task.get("selected_backend") if isinstance(task.get("selected_backend"), dict) else {}
    if not selected_backend.get("id"):
        raise AgentTaskQueueBlockedError(
            "execution_backend_required",
            "Select an execution backend before executing this agent task.",
        )
    result = execute_agent_task_with_backend(task, project_root)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = utc_now()
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["execution_result"] = result
    return response


def review_project_reference_seed_package(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_REFERENCE_SEED_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_reference_seed_review_action",
            f"Unsupported reference seed review action: {action}.",
        )
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    execution_result = task.get("execution_result") if isinstance(task.get("execution_result"), dict) else {}
    if execution_result.get("execution_kind") != "reference_chain_seed_package":
        raise AgentTaskQueueBlockedError(
            "reference_seed_package_required",
            "Reference seed package execution result is required before review.",
        )

    timestamp = utc_now()
    review = build_reference_seed_package_review(action, note, timestamp)
    task["reference_seed_review"] = review
    task["can_execute"] = False
    result_review = (
        execution_result.get("result_review")
        if isinstance(execution_result.get("result_review"), dict)
        else {}
    )
    result_review["last_review_action"] = action
    result_review["can_enter_formal_layer"] = False
    result_review["claims_verified_citations"] = False
    execution_result["result_review"] = result_review
    execution_result["formal_write_allowed"] = False
    execution_result["writes_formal_layer"] = False
    task["execution_result"] = execution_result

    if action == "approve_for_draft":
        task["status"] = "reviewed_for_draft"
        task["next_action"] = "draft_literature_review"
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "needs_revision"
        task["next_action"] = "revise_literature_search"
        task["blockers"] = [
            {
                "code": "reference_seed_needs_revision",
                "label": "候选来源需要修改",
                "description": note or "人工要求修改候选来源种子包。",
            }
        ]
    else:
        task["status"] = "rejected"
        task["next_action"] = "replace_literature_search"
        task["blockers"] = [
            {
                "code": "reference_seed_rejected",
                "label": "候选来源已拒绝",
                "description": note or "人工拒绝了候选来源种子包。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "reference_seed_package_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "note": note,
            "review_gate": "review_literature_seed_package",
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["reference_seed_review"] = review
    return response


def generate_project_draft_literature_review(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    seed_review = task.get("reference_seed_review") if isinstance(task.get("reference_seed_review"), dict) else {}
    if seed_review.get("status") != "approved_for_draft":
        raise AgentTaskQueueBlockedError(
            "reference_seed_review_required",
            "Approved reference seed package review is required before drafting a literature review.",
        )
    execution_result = task.get("execution_result") if isinstance(task.get("execution_result"), dict) else {}
    if execution_result.get("execution_kind") != "reference_chain_seed_package":
        raise AgentTaskQueueBlockedError(
            "reference_seed_package_required",
            "Reference seed package execution result is required before drafting a literature review.",
        )
    seed_artifact_path = str(execution_result.get("artifact_path") or "")
    seed_artifact = project_root / seed_artifact_path
    if not seed_artifact_path or not seed_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "reference_seed_package_missing",
            "Reference seed package file is missing.",
        )

    package = json.loads(seed_artifact.read_text(encoding="utf-8"))
    timestamp = utc_now()
    draft_artifact_path = seed_artifact.parent / "draft_literature_review.md"
    draft_text = build_draft_literature_review_markdown(package, task)
    draft_artifact_path.write_text(draft_text, encoding="utf-8")
    relative_draft_path = draft_artifact_path.relative_to(project_root).as_posix()
    draft = build_draft_literature_review_record(package, seed_artifact_path, relative_draft_path, timestamp)
    task["draft_literature_review"] = draft
    task["status"] = "draft_literature_review_ready"
    task["next_action"] = "review_draft_literature_review"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "draft_literature_review_generated",
            "actor": "system",
            "timestamp": timestamp,
            "source_artifact_path": seed_artifact_path,
            "artifact_path": relative_draft_path,
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["draft_literature_review"] = draft
    return response


def review_project_draft_literature_review(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_DRAFT_LITERATURE_REVIEW_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_draft_literature_review_review_action",
            f"Unsupported draft literature review action: {action}.",
        )
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    draft = task.get("draft_literature_review") if isinstance(task.get("draft_literature_review"), dict) else {}
    if draft.get("status") != "draft_ready":
        raise AgentTaskQueueBlockedError(
            "draft_literature_review_required",
            "Draft literature review is required before opening citation verification tasks.",
        )

    timestamp = utc_now()
    review = build_draft_literature_review_review(action, note, timestamp)
    task["draft_literature_review_review"] = review
    draft["last_review_action"] = action
    draft["formal_write_allowed"] = False
    draft["claims_verified_citations"] = False
    task["draft_literature_review"] = draft
    task["can_execute"] = False

    if action == "approve_for_citation_verification":
        package = load_draft_literature_review_source_package(project_root, draft)
        task["citation_verification_tasks"] = build_citation_verification_tasks(package, draft, timestamp)
        task["status"] = "citation_verification_ready"
        task["next_action"] = "verify_citations"
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "draft_literature_review_needs_revision"
        task["next_action"] = "revise_draft_literature_review"
        task["blockers"] = [
            {
                "code": "draft_literature_review_needs_revision",
                "label": "草稿综述需要修订",
                "description": note or "人工要求修改草稿综述结构或文献方向。",
            }
        ]
    else:
        task["status"] = "draft_literature_review_rejected"
        task["next_action"] = "replace_literature_review_draft"
        task["blockers"] = [
            {
                "code": "draft_literature_review_rejected",
                "label": "草稿综述已拒绝",
                "description": note or "人工拒绝了草稿综述，需要回到文献种子包或重写草稿。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "draft_literature_review_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "note": note,
            "review_gate": "review_draft_literature_review",
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["draft_literature_review_review"] = review
    response["citation_verification_tasks"] = task.get("citation_verification_tasks", [])
    return response


def record_project_citation_verification_evidence(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    citation_task_id: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    normalized_evidence = build_citation_verification_evidence_record(evidence)
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    citation_tasks = task.get("citation_verification_tasks")
    if not isinstance(citation_tasks, list) or not citation_tasks:
        raise AgentTaskQueueBlockedError(
            "citation_verification_task_not_found",
            "Citation verification tasks are not open for this agent task.",
        )

    citation_task = next(
        (
            item
            for item in citation_tasks
            if isinstance(item, dict) and item.get("id") == citation_task_id
        ),
        None,
    )
    if citation_task is None:
        raise AgentTaskQueueBlockedError(
            "citation_verification_task_not_found",
            f"Citation verification task not found: {citation_task_id}.",
        )

    timestamp = utc_now()
    citation_task["status"] = "verified"
    citation_task["citation_state"] = "verified"
    citation_task["review_state"] = "source_verified"
    citation_task["evidence_record"] = normalized_evidence
    citation_task["evidence_level"] = "verified_source_record"
    citation_task["formal_write_allowed"] = False
    citation_task["writes_formal_layer"] = False
    citation_task["claims_verified_citations"] = True
    citation_task["verified_at"] = timestamp

    summary = build_citation_verification_summary(citation_tasks)
    task["citation_verification_summary"] = summary
    task["can_execute"] = False

    if summary["pending_count"] == 0 and summary["needs_revision_count"] == 0:
        log_record = write_citation_verification_log(project_root, task, citation_tasks, timestamp)
        task["status"] = "citation_verification_complete"
        task["next_action"] = "generate_verified_literature_package"
        task["blockers"] = []
        task["citation_verification_log"] = log_record
    else:
        task["status"] = "citation_verification_ready"
        task["next_action"] = "verify_citations"
        task["blockers"] = [
            {
                "code": "citation_verification_pending",
                "label": "引用核验未完成",
                "description": f"还有 {summary['pending_count']} 条候选引用需要补充来源证据。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "citation_verification_evidence_recorded",
            "actor": "human",
            "timestamp": timestamp,
            "citation_task_id": citation_task_id,
            "connector": normalized_evidence["connector"],
            "evidence_level": "verified_source_record",
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["citation_verification_summary"] = summary
    response["citation_task"] = citation_task
    return response


def generate_project_verified_literature_package(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    if task.get("status") != "citation_verification_complete":
        raise AgentTaskQueueBlockedError(
            "citation_verification_complete_required",
            "Complete citation verification is required before generating a verified literature package.",
        )

    log_record = task.get("citation_verification_log") if isinstance(task.get("citation_verification_log"), dict) else {}
    log_artifact_path = str(log_record.get("artifact_path") or "")
    if not log_artifact_path:
        raise AgentTaskQueueBlockedError(
            "citation_verification_log_required",
            "Citation verification log is required before generating a verified literature package.",
        )
    log_artifact = project_root / log_artifact_path
    if not log_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "citation_verification_log_required",
            "Citation verification log file is missing.",
        )

    log = json.loads(log_artifact.read_text(encoding="utf-8"))
    if not log.get("claims_verified_citations") or not normalize_list(log.get("records")):
        raise AgentTaskQueueBlockedError(
            "citation_verification_log_required",
            "Citation verification log does not contain verified citation records.",
        )

    timestamp = utc_now()
    package_artifact_path = Path("Results/json/verified_literature_package.json")
    package = build_verified_literature_package_record(task, log, log_artifact_path, timestamp)
    absolute_package_artifact = project_root / package_artifact_path
    absolute_package_artifact.parent.mkdir(parents=True, exist_ok=True)
    absolute_package_artifact.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    package_summary = {
        "status": "verified_literature_package_ready",
        "schema_version": package["schema_version"],
        "artifact_path": str(package_artifact_path),
        "source_log_artifact_path": log_artifact_path,
        "verified_reference_count": package["verified_reference_count"],
        "claims_verified_citations": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_verified_literature_package",
        "next_action_label": "审阅已核验文献包",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    task["verified_literature_package"] = package_summary
    task["status"] = "verified_literature_package_ready"
    task["next_action"] = "review_verified_literature_package"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "verified_literature_package_generated",
            "actor": "system",
            "timestamp": timestamp,
            "source_log_artifact_path": log_artifact_path,
            "artifact_path": str(package_artifact_path),
            "verified_reference_count": package["verified_reference_count"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["verified_literature_package"] = package_summary
    return response


def review_project_verified_literature_package(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_VERIFIED_LITERATURE_PACKAGE_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_verified_literature_package_review_action",
            f"Unsupported verified literature package review action: {action}.",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    package_summary = task.get("verified_literature_package") if isinstance(task.get("verified_literature_package"), dict) else {}
    package_artifact_path = str(package_summary.get("artifact_path") or "")
    package_artifact = project_root / package_artifact_path
    if task.get("status") != "verified_literature_package_ready" or not package_artifact_path or not package_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "verified_literature_package_required",
            "Verified literature package is required before review.",
        )

    timestamp = utc_now()
    review = build_verified_literature_package_review(action, note, timestamp)
    task["verified_literature_package_review"] = review
    package_summary["review_status"] = review["status"]
    package_summary["review_gate"] = review["review_gate"]
    package_summary["manuscript_citation_plan_allowed"] = review["manuscript_citation_plan_allowed"]
    package_summary["formal_write_allowed"] = False
    task["verified_literature_package"] = package_summary

    package = json.loads(package_artifact.read_text(encoding="utf-8"))
    package["review"] = review
    package["formal_write_allowed"] = False
    package["manuscript_citation_plan_allowed"] = review["manuscript_citation_plan_allowed"]
    package_artifact.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")

    if action == "approve_for_manuscript_citations":
        task["status"] = "verified_literature_package_approved"
        task["next_action"] = "generate_manuscript_citation_plan"
        task["can_execute"] = False
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "verified_literature_package_needs_revision"
        task["next_action"] = "revise_verified_literature_package"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "verified_literature_package_needs_revision",
                "label": "文献包需要修订",
                "description": note or "按审阅意见补充或替换引用来源。",
            }
        ]
    else:
        task["status"] = "verified_literature_package_rejected"
        task["next_action"] = "replace_verified_literature_package"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "verified_literature_package_rejected",
                "label": "文献包已拒绝",
                "description": note or "重新生成或补充已核验文献包。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "verified_literature_package_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "note": note,
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["verified_literature_package_review"] = review
    return response


def generate_project_manuscript_citation_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    review = task.get("verified_literature_package_review") if isinstance(task.get("verified_literature_package_review"), dict) else {}
    package_summary = task.get("verified_literature_package") if isinstance(task.get("verified_literature_package"), dict) else {}
    package_artifact_path = str(package_summary.get("artifact_path") or "")
    package_artifact = project_root / package_artifact_path
    if (
        task.get("status") != "verified_literature_package_approved"
        or review.get("status") != "approved_for_manuscript_citations"
        or not review.get("manuscript_citation_plan_allowed")
        or not package_artifact_path
        or not package_artifact.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "verified_literature_package_review_required",
            "Approved verified literature package review is required before generating a manuscript citation plan.",
        )

    package = json.loads(package_artifact.read_text(encoding="utf-8"))
    timestamp = utc_now()
    plan_artifact_path = Path("Results/json/manuscript_citation_plan.json")
    plan = build_manuscript_citation_plan_record(task, package, package_artifact_path, review, timestamp)
    absolute_plan_artifact = project_root / plan_artifact_path
    absolute_plan_artifact.parent.mkdir(parents=True, exist_ok=True)
    absolute_plan_artifact.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    plan_summary = {
        "status": "manuscript_citation_plan_ready",
        "schema_version": plan["schema_version"],
        "artifact_path": str(plan_artifact_path),
        "source_artifact_path": package_artifact_path,
        "source_review_gate": plan["source_review_gate"],
        "generated_from_review_status": plan["generated_from_review_status"],
        "citation_binding_count": plan["citation_binding_count"],
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_manuscript_citation_plan",
        "next_action_label": "审阅论文引用计划",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    task["manuscript_citation_plan"] = plan_summary
    task["status"] = "manuscript_citation_plan_ready"
    task["next_action"] = "review_manuscript_citation_plan"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "manuscript_citation_plan_generated",
            "actor": "system",
            "timestamp": timestamp,
            "source_artifact_path": package_artifact_path,
            "artifact_path": str(plan_artifact_path),
            "citation_binding_count": plan["citation_binding_count"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["manuscript_citation_plan"] = plan_summary
    return response


def review_project_manuscript_citation_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_MANUSCRIPT_CITATION_PLAN_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_manuscript_citation_plan_review_action",
            f"Unsupported manuscript citation plan review action: {action}.",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    plan_summary = task.get("manuscript_citation_plan") if isinstance(task.get("manuscript_citation_plan"), dict) else {}
    plan_artifact_path = str(plan_summary.get("artifact_path") or "")
    plan_artifact = project_root / plan_artifact_path
    if task.get("status") != "manuscript_citation_plan_ready" or not plan_artifact_path or not plan_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "manuscript_citation_plan_required",
            "Manuscript citation plan is required before review.",
        )

    timestamp = utc_now()
    review = build_manuscript_citation_plan_review(action, note, timestamp)
    task["manuscript_citation_plan_review"] = review
    plan_summary["review_status"] = review["status"]
    plan_summary["review_gate"] = review["review_gate"]
    plan_summary["draft_section_plan_allowed"] = review["draft_section_plan_allowed"]
    plan_summary["formal_write_allowed"] = False
    task["manuscript_citation_plan"] = plan_summary

    plan = json.loads(plan_artifact.read_text(encoding="utf-8"))
    plan["review"] = review
    plan["formal_write_allowed"] = False
    plan["draft_section_plan_allowed"] = review["draft_section_plan_allowed"]
    plan_artifact.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    if action == "approve_for_draft_sections":
        task["status"] = "manuscript_citation_plan_approved"
        task["next_action"] = "generate_draft_section_plan"
        task["can_execute"] = False
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "manuscript_citation_plan_needs_revision"
        task["next_action"] = "revise_manuscript_citation_plan"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "manuscript_citation_plan_needs_revision",
                "label": "论文引用计划需要修订",
                "description": note or "按审阅意见调整引用绑定、章节归属或论证用途。",
            }
        ]
    else:
        task["status"] = "manuscript_citation_plan_rejected"
        task["next_action"] = "replace_manuscript_citation_plan"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "manuscript_citation_plan_rejected",
                "label": "论文引用计划已拒绝",
                "description": note or "需要重新生成或替换引用计划。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "manuscript_citation_plan_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "status": review["status"],
            "artifact_path": plan_artifact_path,
            "draft_section_plan_allowed": review["draft_section_plan_allowed"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["manuscript_citation_plan_review"] = review
    return response


def generate_project_draft_section_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    review = task.get("manuscript_citation_plan_review") if isinstance(task.get("manuscript_citation_plan_review"), dict) else {}
    citation_plan_summary = task.get("manuscript_citation_plan") if isinstance(task.get("manuscript_citation_plan"), dict) else {}
    citation_plan_artifact_path = str(citation_plan_summary.get("artifact_path") or "")
    citation_plan_artifact = project_root / citation_plan_artifact_path
    if (
        task.get("status") != "manuscript_citation_plan_approved"
        or review.get("status") != "approved_for_draft_sections"
        or not review.get("draft_section_plan_allowed")
        or not citation_plan_artifact_path
        or not citation_plan_artifact.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "manuscript_citation_plan_review_required",
            "Approved manuscript citation plan review is required before generating a draft section plan.",
        )

    citation_plan = json.loads(citation_plan_artifact.read_text(encoding="utf-8"))
    timestamp = utc_now()
    draft_section_plan_artifact_path = Path("Results/json/draft_section_plan.json")
    draft_section_plan = build_draft_section_plan_record(
        task,
        citation_plan,
        citation_plan_artifact_path,
        review,
        timestamp,
    )
    absolute_artifact_path = project_root / draft_section_plan_artifact_path
    absolute_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_artifact_path.write_text(json.dumps(draft_section_plan, ensure_ascii=False, indent=2), encoding="utf-8")

    plan_summary = {
        "status": "draft_section_plan_ready",
        "schema_version": draft_section_plan["schema_version"],
        "artifact_path": str(draft_section_plan_artifact_path),
        "source_artifact_path": citation_plan_artifact_path,
        "source_review_gate": draft_section_plan["source_review_gate"],
        "generated_from_review_status": draft_section_plan["generated_from_review_status"],
        "section_count": len(draft_section_plan["sections"]),
        "citation_binding_count": draft_section_plan["citation_binding_count"],
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_draft_section_plan",
        "next_action_label": "审阅章节草稿计划",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    task["draft_section_plan"] = plan_summary
    task["status"] = "draft_section_plan_ready"
    task["next_action"] = "review_draft_section_plan"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "draft_section_plan_generated",
            "actor": "system",
            "timestamp": timestamp,
            "source_artifact_path": citation_plan_artifact_path,
            "artifact_path": str(draft_section_plan_artifact_path),
            "section_count": len(draft_section_plan["sections"]),
            "citation_binding_count": draft_section_plan["citation_binding_count"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["draft_section_plan"] = plan_summary
    return response


def review_project_draft_section_plan(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_DRAFT_SECTION_PLAN_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_draft_section_plan_review_action",
            f"Unsupported draft section plan review action: {action}.",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    plan_summary = task.get("draft_section_plan") if isinstance(task.get("draft_section_plan"), dict) else {}
    plan_artifact_path = str(plan_summary.get("artifact_path") or "")
    plan_artifact = project_root / plan_artifact_path
    if task.get("status") != "draft_section_plan_ready" or not plan_artifact_path or not plan_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "draft_section_plan_required",
            "Draft section plan is required before review.",
        )

    timestamp = utc_now()
    review = build_draft_section_plan_review(action, note, timestamp)
    task["draft_section_plan_review"] = review
    plan_summary["review_status"] = review["status"]
    plan_summary["review_gate"] = review["review_gate"]
    plan_summary["section_task_generation_allowed"] = review["section_task_generation_allowed"]
    plan_summary["formal_write_allowed"] = False
    task["draft_section_plan"] = plan_summary

    plan = json.loads(plan_artifact.read_text(encoding="utf-8"))
    plan["review"] = review
    plan["formal_write_allowed"] = False
    plan["section_task_generation_allowed"] = review["section_task_generation_allowed"]
    plan_artifact.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    if action == "approve_for_section_tasks":
        task["status"] = "draft_section_plan_approved"
        task["next_action"] = "generate_draft_section_tasks"
        task["can_execute"] = False
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "draft_section_plan_needs_revision"
        task["next_action"] = "revise_draft_section_plan"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "draft_section_plan_needs_revision",
                "label": "章节草稿计划需要修订",
                "description": note or "按审阅意见调整章节边界、引用绑定或写作任务。",
            }
        ]
    else:
        task["status"] = "draft_section_plan_rejected"
        task["next_action"] = "replace_draft_section_plan"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "draft_section_plan_rejected",
                "label": "章节草稿计划已拒绝",
                "description": note or "需要重新生成或替换章节草稿计划。",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "draft_section_plan_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "status": review["status"],
            "artifact_path": plan_artifact_path,
            "section_task_generation_allowed": review["section_task_generation_allowed"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["draft_section_plan_review"] = review
    return response


def generate_project_draft_section_tasks(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    review = task.get("draft_section_plan_review") if isinstance(task.get("draft_section_plan_review"), dict) else {}
    plan_summary = task.get("draft_section_plan") if isinstance(task.get("draft_section_plan"), dict) else {}
    plan_artifact_path = str(plan_summary.get("artifact_path") or "")
    plan_artifact = project_root / plan_artifact_path
    if (
        task.get("status") != "draft_section_plan_approved"
        or review.get("status") != "approved_for_section_tasks"
        or not review.get("section_task_generation_allowed")
        or not plan_artifact_path
        or not plan_artifact.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "draft_section_plan_review_required",
            "Approved draft section plan review is required before generating draft section tasks.",
        )

    plan = json.loads(plan_artifact.read_text(encoding="utf-8"))
    timestamp = utc_now()
    section_tasks_artifact_path = Path("Results/json/draft_section_tasks.json")
    section_tasks = build_draft_section_tasks_record(
        task,
        plan,
        plan_artifact_path,
        review,
        timestamp,
    )
    absolute_artifact_path = project_root / section_tasks_artifact_path
    absolute_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_artifact_path.write_text(json.dumps(section_tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    task_summary = {
        "status": "draft_section_tasks_ready",
        "schema_version": section_tasks["schema_version"],
        "artifact_path": str(section_tasks_artifact_path),
        "source_artifact_path": plan_artifact_path,
        "source_review_gate": section_tasks["source_review_gate"],
        "generated_from_review_status": section_tasks["generated_from_review_status"],
        "task_count": len(section_tasks["tasks"]),
        "citation_binding_count": section_tasks["citation_binding_count"],
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_draft_section_tasks",
        "next_action_label": "审阅章节草稿任务包",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    task["draft_section_tasks"] = task_summary
    task["status"] = "draft_section_tasks_ready"
    task["next_action"] = "review_draft_section_tasks"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "draft_section_tasks_generated",
            "actor": "system",
            "timestamp": timestamp,
            "source_artifact_path": plan_artifact_path,
            "artifact_path": str(section_tasks_artifact_path),
            "task_count": len(section_tasks["tasks"]),
            "citation_binding_count": section_tasks["citation_binding_count"],
            "formal_write_allowed": False,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["draft_section_tasks"] = task_summary
    return response


def build_reference_seed_package_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_draft":
        status = "approved_for_draft"
        next_action = "draft_literature_review"
        next_action_label = "进入草稿综述"
        draft_layer_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_literature_search"
        next_action_label = "要求修订候选来源"
        draft_layer_allowed = False
    else:
        status = "rejected"
        next_action = "replace_literature_search"
        next_action_label = "拒绝种子包并重新检索"
        draft_layer_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_literature_seed_package",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "reference_state": "candidate",
        "draft_layer_allowed": draft_layer_allowed,
        "formal_write_allowed": False,
        "claims_verified_citations": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "local_file",
    }


def build_verified_literature_package_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_manuscript_citations":
        status = "approved_for_manuscript_citations"
        next_action = "generate_manuscript_citation_plan"
        next_action_label = "生成论文引用计划"
        manuscript_citation_plan_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_verified_literature_package"
        next_action_label = "要求修订文献包"
        manuscript_citation_plan_allowed = False
    else:
        status = "rejected"
        next_action = "replace_verified_literature_package"
        next_action_label = "拒绝文献包"
        manuscript_citation_plan_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_verified_literature_package",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "citation_state": "verified_source_record",
        "manuscript_citation_plan_allowed": manuscript_citation_plan_allowed,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "verified_source_record",
    }


def build_manuscript_citation_plan_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_draft_sections":
        status = "approved_for_draft_sections"
        next_action = "generate_draft_section_plan"
        next_action_label = "生成章节草稿计划"
        draft_section_plan_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_manuscript_citation_plan"
        next_action_label = "要求修订引用计划"
        draft_section_plan_allowed = False
    else:
        status = "rejected"
        next_action = "replace_manuscript_citation_plan"
        next_action_label = "拒绝引用计划"
        draft_section_plan_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_manuscript_citation_plan",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "citation_state": "section_binding_plan",
        "draft_section_plan_allowed": draft_section_plan_allowed,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "verified_source_record",
    }


def build_draft_section_plan_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_section_tasks":
        status = "approved_for_section_tasks"
        next_action = "generate_draft_section_tasks"
        next_action_label = "生成章节草稿任务包"
        section_task_generation_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_draft_section_plan"
        next_action_label = "要求修订章节计划"
        section_task_generation_allowed = False
    else:
        status = "rejected"
        next_action = "replace_draft_section_plan"
        next_action_label = "拒绝章节计划"
        section_task_generation_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_draft_section_plan",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "draft_state": "section_task_plan",
        "section_task_generation_allowed": section_task_generation_allowed,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "verified_source_record",
    }


def build_draft_literature_review_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_citation_verification":
        status = "approved_for_citation_verification"
        next_action = "verify_citations"
        next_action_label = "进入引用核验"
        citation_verification_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_draft_literature_review"
        next_action_label = "要求修订草稿综述"
        citation_verification_allowed = False
    else:
        status = "rejected"
        next_action = "replace_literature_review_draft"
        next_action_label = "拒绝草稿综述"
        citation_verification_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_draft_literature_review",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "citation_state": "candidate",
        "citation_verification_allowed": citation_verification_allowed,
        "formal_write_allowed": False,
        "claims_verified_citations": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "local_file",
    }


def load_draft_literature_review_source_package(project_root: Path, draft: dict[str, Any]) -> dict[str, Any]:
    source_artifact_path = str(draft.get("source_artifact_path") or "")
    source_artifact = project_root / source_artifact_path
    if not source_artifact_path or not source_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "reference_seed_package_missing",
            "Reference seed package file is missing for citation verification.",
        )
    return json.loads(source_artifact.read_text(encoding="utf-8"))


def build_citation_verification_tasks(
    package: dict[str, Any],
    draft: dict[str, Any],
    timestamp: str,
) -> list[dict[str, Any]]:
    candidate_queries = [item for item in normalize_list(package.get("candidate_queries")) if isinstance(item, dict)]
    if not candidate_queries:
        candidate_queries = [
            {
                "source_id": "draft_literature_review",
                "source_label": "草稿综述",
                "query": str(package.get("research_question") or draft.get("research_question") or ""),
                "mode": "fallback",
                "review_state": "candidate",
            }
        ]

    tasks: list[dict[str, Any]] = []
    for index, query in enumerate(candidate_queries, start=1):
        source_id = str(query.get("source_id") or f"candidate_source_{index:02d}")
        source_label = str(query.get("source_label") or source_id)
        tasks.append(
            {
                "id": f"citation_verification_{index:02d}",
                "status": "pending",
                "source_id": source_id,
                "source_label": source_label,
                "query": str(query.get("query") or ""),
                "mode": str(query.get("mode") or "candidate"),
                "review_state": str(query.get("review_state") or "candidate"),
                "citation_state": "candidate",
                "required_checks": CITATION_VERIFICATION_REQUIRED_CHECKS,
                "required_connectors": ["cnki", "scholar", "zotero", "local_notes"],
                "source_artifact_path": str(draft.get("source_artifact_path") or ""),
                "draft_artifact_path": str(draft.get("artifact_path") or ""),
                "formal_write_allowed": False,
                "writes_formal_layer": False,
                "claims_verified_citations": False,
                "can_enter_formal_layer": False,
                "evidence_level": "candidate",
                "created_at": timestamp,
            }
        )
    return tasks


def build_citation_verification_evidence_record(evidence: dict[str, Any]) -> dict[str, Any]:
    missing = []
    for field in CITATION_VERIFICATION_EVIDENCE_REQUIRED_FIELDS:
        value = evidence.get(field)
        if field == "authors":
            if not normalize_list(value):
                missing.append(field)
        elif value is None or str(value).strip() == "":
            missing.append(field)
    if missing:
        raise AgentTaskQueueBlockedError(
            "citation_verification_evidence_incomplete",
            f"Citation verification evidence is missing required fields: {', '.join(missing)}.",
        )

    timestamp = utc_now()
    authors = [str(author).strip() for author in normalize_list(evidence.get("authors")) if str(author).strip()]
    return {
        "schema_version": "citation_verification_evidence.v1",
        "connector": str(evidence.get("connector") or "").strip(),
        "authors": authors,
        "year": str(evidence.get("year") or "").strip(),
        "title": str(evidence.get("title") or "").strip(),
        "venue": str(evidence.get("venue") or "").strip(),
        "doi_or_stable_url": str(evidence.get("doi_or_stable_url") or "").strip(),
        "relevance": str(evidence.get("relevance") or "").strip(),
        "evidence_url": str(evidence.get("evidence_url") or "").strip(),
        "note": str(evidence.get("note") or "").strip(),
        "required_checks_satisfied": CITATION_VERIFICATION_REQUIRED_CHECKS,
        "verified_at": timestamp,
        "formal_write_allowed": False,
        "claims_verified_citations": True,
    }


def build_citation_verification_summary(citation_tasks: list[dict[str, Any]]) -> dict[str, Any]:
    total_count = len(citation_tasks)
    verified_count = sum(1 for item in citation_tasks if isinstance(item, dict) and item.get("status") == "verified")
    needs_revision_count = sum(1 for item in citation_tasks if isinstance(item, dict) and item.get("status") == "needs_revision")
    pending_count = max(total_count - verified_count - needs_revision_count, 0)
    return {
        "total_count": total_count,
        "verified_count": verified_count,
        "pending_count": pending_count,
        "needs_revision_count": needs_revision_count,
        "formal_write_allowed": False,
        "claims_verified_citations": pending_count == 0 and needs_revision_count == 0 and total_count > 0,
    }


def write_citation_verification_log(
    project_root: Path,
    task: dict[str, Any],
    citation_tasks: list[dict[str, Any]],
    timestamp: str,
) -> dict[str, Any]:
    log_path = Path("Results/json/citation_verification_log.json")
    records = [
        item.get("evidence_record", {})
        for item in citation_tasks
        if isinstance(item, dict) and isinstance(item.get("evidence_record"), dict)
    ]
    payload = {
        "schema_version": "citation_verification_log.v1",
        "evidence_id": "citation_verification_log",
        "status": "verified",
        "source_task_id": str(task.get("id") or ""),
        "verified_count": len(records),
        "total_count": len(citation_tasks),
        "claims_verified_citations": True,
        "formal_write_allowed": False,
        "records": records,
        "created_at": timestamp,
    }
    absolute_log_path = project_root / log_path
    absolute_log_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "schema_version": payload["schema_version"],
        "status": payload["status"],
        "artifact_path": str(log_path),
        "verified_count": payload["verified_count"],
        "claims_verified_citations": True,
        "formal_write_allowed": False,
        "created_at": timestamp,
    }


def build_verified_literature_package_record(
    task: dict[str, Any],
    verification_log: dict[str, Any],
    source_log_artifact_path: str,
    timestamp: str,
) -> dict[str, Any]:
    records = [item for item in normalize_list(verification_log.get("records")) if isinstance(item, dict)]
    references = [
        build_verified_reference_entry(index, record)
        for index, record in enumerate(records, start=1)
    ]
    return {
        "schema_version": "p1.verified_literature_package.v1",
        "status": "verified_literature_package_ready",
        "source_task_id": str(task.get("id") or verification_log.get("source_task_id") or ""),
        "source_log_artifact_path": source_log_artifact_path,
        "verified_reference_count": len(references),
        "claims_verified_citations": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "evidence_level": "verified_source_record",
        "verified_references": references,
        "usage_boundary": "这份文献包只证明来源元数据已经核验，可供后续草稿和人工审阅使用；写入正式层仍需单独批准。",
        "created_at": timestamp,
    }


def build_verified_reference_entry(index: int, record: dict[str, Any]) -> dict[str, Any]:
    authors = [str(author).strip() for author in normalize_list(record.get("authors")) if str(author).strip()]
    year = str(record.get("year") or "").strip()
    title = str(record.get("title") or "").strip()
    venue = str(record.get("venue") or "").strip()
    citation_text = format_verified_citation_text(authors, year, title, venue)
    return {
        "id": f"verified_reference_{index:02d}",
        "authors": authors,
        "year": year,
        "title": title,
        "venue": venue,
        "doi_or_stable_url": str(record.get("doi_or_stable_url") or "").strip(),
        "relevance": str(record.get("relevance") or "").strip(),
        "evidence_url": str(record.get("evidence_url") or "").strip(),
        "connector": str(record.get("connector") or "").strip(),
        "citation_text": citation_text,
        "evidence_level": "verified_source_record",
        "verified_at": str(record.get("verified_at") or "").strip(),
        "formal_write_allowed": False,
        "claims_verified_citations": True,
    }


def build_manuscript_citation_plan_record(
    task: dict[str, Any],
    package: dict[str, Any],
    source_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    references = [item for item in normalize_list(package.get("verified_references")) if isinstance(item, dict)]
    bindings = [
        build_manuscript_citation_binding(index, reference)
        for index, reference in enumerate(references, start=1)
    ]
    return {
        "schema_version": "p1.manuscript_citation_plan.v1",
        "status": "manuscript_citation_plan_ready",
        "source_task_id": str(task.get("id") or package.get("source_task_id") or ""),
        "source_artifact_path": source_artifact_path,
        "source_review_gate": "review_verified_literature_package",
        "generated_from_review_status": str(review.get("status") or ""),
        "citation_binding_count": len(bindings),
        "citation_bindings": bindings,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "draft_layer": "manuscript_citation_plan",
        "next_action": "review_manuscript_citation_plan",
        "next_action_label": "审阅论文引用计划",
        "usage_boundary": "这份计划只说明已核验来源如何进入草稿层论文写作；正式正文、正式参考文献和导出包仍需后续人工审批。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_manuscript_citation_binding(index: int, reference: dict[str, Any]) -> dict[str, Any]:
    target_sections = infer_citation_target_sections(index, reference)
    return {
        "id": f"citation_binding_{index:02d}",
        "reference_id": str(reference.get("id") or f"verified_reference_{index:02d}"),
        "citation_text": str(reference.get("citation_text") or ""),
        "title": str(reference.get("title") or ""),
        "authors": normalize_list(reference.get("authors")),
        "year": str(reference.get("year") or ""),
        "venue": str(reference.get("venue") or ""),
        "doi_or_stable_url": str(reference.get("doi_or_stable_url") or ""),
        "connector": str(reference.get("connector") or ""),
        "evidence_url": str(reference.get("evidence_url") or ""),
        "evidence_level": "verified_source_record",
        "target_sections": target_sections,
        "citation_purpose": citation_purpose_for_sections(target_sections),
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "requires_human_review": True,
    }


def infer_citation_target_sections(index: int, reference: dict[str, Any]) -> list[str]:
    relevance = str(reference.get("relevance") or "").lower()
    title = str(reference.get("title") or "").lower()
    if index == 1:
        return ["introduction", "literature_review"]
    if "method" in title or "identification" in title or "estimate" in title:
        return ["empirical_strategy"]
    if relevance in {"method", "identification", "design"}:
        return ["empirical_strategy"]
    return ["literature_review", "theory_and_hypotheses"]


def citation_purpose_for_sections(sections: list[str]) -> str:
    if "empirical_strategy" in sections:
        return "支持方法选择、识别设定或稳健性要求。"
    if "introduction" in sections:
        return "支持研究动机、贡献定位和问题重要性。"
    return "支持文献脉络、理论机制或已有经验证据。"


def build_draft_section_plan_record(
    task: dict[str, Any],
    manuscript_plan: dict[str, Any],
    source_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    bindings = [item for item in normalize_list(manuscript_plan.get("citation_bindings")) if isinstance(item, dict)]
    sections = build_draft_section_entries(bindings)
    return {
        "schema_version": "p1.draft_section_plan.v1",
        "status": "draft_section_plan_ready",
        "source_task_id": str(task.get("id") or manuscript_plan.get("source_task_id") or ""),
        "source_artifact_path": source_artifact_path,
        "source_review_gate": "review_manuscript_citation_plan",
        "generated_from_review_status": str(review.get("status") or ""),
        "draft_layer": "draft_section_plan",
        "section_count": len(sections),
        "citation_binding_count": len(bindings),
        "sections": sections,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_draft_section_plan",
        "next_action_label": "审阅章节草稿计划",
        "usage_boundary": "这份计划只拆分章节草稿任务和引用绑定；正式正文、正式参考文献和导出包仍需后续人工审批。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_draft_section_entries(bindings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    section_order = [
        ("introduction", "引言", "交代问题重要性、研究贡献和核心结论走向。"),
        ("literature_review", "文献综述", "整理相关文献、研究缺口和本文定位。"),
        ("theory_and_hypotheses", "理论机制与假设", "组织理论机制、作用路径和可检验假设。"),
        ("empirical_strategy", "研究设计与识别策略", "说明变量、模型、识别假设和稳健性要求。"),
    ]
    section_bindings: dict[str, list[dict[str, Any]]] = {section_id: [] for section_id, _, _ in section_order}
    for binding in bindings:
        for section_id in normalize_list(binding.get("target_sections")):
            if section_id in section_bindings:
                section_bindings[section_id].append(binding)

    sections = []
    for section_id, title, purpose in section_order:
        bound = section_bindings[section_id]
        sections.append(
            {
                "section_id": section_id,
                "section_title": title,
                "purpose": purpose,
                "citation_binding_ids": [str(binding.get("id") or "") for binding in bound if binding.get("id")],
                "citation_count": len(bound),
                "draft_task": draft_section_task_for(section_id),
                "requires_human_review": True,
                "formal_write_allowed": False,
            }
        )
    return sections


def draft_section_task_for(section_id: str) -> str:
    tasks = {
        "introduction": "先写研究问题、贡献定位和核心结论草稿，并标注每条引用的论证用途。",
        "literature_review": "按研究脉络组织已核验来源，写出文献缺口和本文边际贡献草稿。",
        "theory_and_hypotheses": "把文献证据转成理论机制和可检验假设草稿。",
        "empirical_strategy": "把方法类引用绑定到模型设定、识别假设和稳健性检查草稿。",
    }
    return tasks.get(section_id, "生成章节草稿任务，并保留人工审阅门。")


def build_draft_section_tasks_record(
    task: dict[str, Any],
    plan: dict[str, Any],
    source_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    sections = [item for item in normalize_list(plan.get("sections")) if isinstance(item, dict)]
    section_tasks = [
        build_draft_section_task_entry(section, index)
        for index, section in enumerate(sections, start=1)
    ]
    return {
        "schema_version": "p1.draft_section_tasks.v1",
        "status": "draft_section_tasks_ready",
        "source_task_id": str(task.get("id") or plan.get("source_task_id") or ""),
        "source_artifact_path": source_artifact_path,
        "source_review_gate": "review_draft_section_plan",
        "generated_from_review_status": str(review.get("status") or ""),
        "draft_layer": "draft_section_tasks",
        "task_count": len(section_tasks),
        "citation_binding_count": sum(item["citation_count"] for item in section_tasks),
        "tasks": section_tasks,
        "review": {
            "status": "pending",
            "review_gate": "review_draft_section_tasks",
            "reviewer": "human",
            "formal_write_allowed": False,
            "writes_formal_layer": False,
        },
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_draft_section_tasks",
        "next_action_label": "审阅章节草稿任务包",
        "usage_boundary": "这份任务包只安排章节草稿写作任务；正式正文和正式参考文献仍需后续人工审批。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_draft_section_task_entry(section: dict[str, Any], index: int) -> dict[str, Any]:
    section_id = str(section.get("section_id") or f"section_{index:02d}")
    binding_ids = [
        str(binding_id)
        for binding_id in normalize_list(section.get("citation_binding_ids"))
        if str(binding_id)
    ]
    return {
        "id": f"draft_section_task_{index:02d}",
        "section_id": section_id,
        "section_title": str(section.get("section_title") or "未命名章节"),
        "purpose": str(section.get("purpose") or ""),
        "writing_task": str(section.get("draft_task") or draft_section_task_for(section_id)),
        "citation_binding_ids": binding_ids,
        "citation_count": len(binding_ids),
        "required_inputs": [
            "draft_section_plan",
            "verified_literature_package",
            "manuscript_citation_plan",
        ],
        "output_artifacts": [f"Manuscripts/sections/{section_id}.md"],
        "status": "queued",
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
    }


def format_verified_citation_text(authors: list[str], year: str, title: str, venue: str) -> str:
    author_text = ", ".join(authors) if authors else "Unknown author"
    segments = [author_text]
    if year:
        segments.append(f"({year})")
    if title:
        segments.append(title)
    if venue:
        segments.append(venue)
    return ". ".join(segment.strip(". ") for segment in segments if segment).strip() + "."


def build_draft_literature_review_record(
    package: dict[str, Any],
    seed_artifact_path: str,
    draft_artifact_path: str,
    timestamp: str,
) -> dict[str, Any]:
    candidate_queries = normalize_list(package.get("candidate_queries"))
    return {
        "status": "draft_ready",
        "schema_version": "p1.draft_literature_review.v1",
        "draft_layer": "exploratory",
        "artifact_path": draft_artifact_path,
        "source_artifact_path": seed_artifact_path,
        "source_review_gate": "review_literature_seed_package",
        "research_question": str(package.get("research_question") or ""),
        "candidate_query_count": len(candidate_queries),
        "citation_state": "candidate",
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "claims_verified_citations": False,
        "next_action": "review_draft_literature_review",
        "next_action_label": "审阅草稿综述",
        "limitations": "这份文献综述来自候选来源种子包，只能作为草稿层材料；引用、作者、年份、期刊和 DOI 仍需人工或连接器核验。",
        "created_at": timestamp,
        "evidence_level": "local_file",
    }


def build_draft_literature_review_markdown(package: dict[str, Any], task: dict[str, Any]) -> str:
    question = str(package.get("research_question") or task.get("summary") or task.get("title") or "").strip()
    candidate_queries = [item for item in normalize_list(package.get("candidate_queries")) if isinstance(item, dict)]
    source_lines = []
    for query in candidate_queries:
        source_lines.append(
            "- "
            f"{query.get('source_label') or query.get('source_id')}: "
            f"`{query.get('query') or ''}`；"
            f"模式={query.get('mode') or 'candidate'}；"
            f"状态={query.get('review_state') or 'candidate'}。"
        )
    if not source_lines:
        source_lines.append("- 暂无候选检索式；需要回到 reference chain 重新生成种子包。")
    return "\n".join(
        [
            "# 文献综述草稿",
            "",
            f"研究题目：{question}",
            "",
            "## 1. 研究问题定位",
            "",
            f"本草稿围绕“{question}”展开。当前材料用于确认相关文献方向、变量线索和方法规范，不直接进入正式论文层。",
            "",
            "## 2. 候选检索式",
            "",
            *source_lines,
            "",
            "## 3. 初步综述结构",
            "",
            "1. 先整理与研究题目直接相关的核心实证研究，确认主要因变量、自变量和控制变量的常见设定。",
            "2. 再追踪数据来源和制度背景文献，判断现有数据是否支持题目要求的样本、时间和层级。",
            "3. 最后进入方法规范检查，确认是否需要 DID、IV、RDD、PSM、DML 或其他识别门。",
            "",
            "## 4. 待补证据",
            "",
            "- CNKI、Google Scholar、Zotero 和本地笔记中的候选文献需要继续核验。",
            "- 每条引用进入正式层前，需要核对作者、年份、题名、期刊/工作论文版本和 DOI 或稳定链接。",
            "- 当前还没有声明任何引用已验证，也没有写回正式论文。",
            "",
            "## 5. 草稿层边界",
            "",
            "这份文档由候选来源种子包生成，只能作为 exploratory / draft 材料。进入正式层前必须经过文献相关性审阅、引用元数据核验和人工确认。",
            "",
        ]
    )
