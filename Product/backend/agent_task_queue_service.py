from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from Product.backend.internal_agent_skill_registry import normalize_agent_role_name
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.supervisor_plan_service import load_saved_supervisor_plan


AGENT_TASK_QUEUE_PATH = Path("state/product/agent_task_queue.json")
INTERNAL_SKILL_EXECUTION_PACKET_DIR = Path("state/product/internal_skill_execution_packets")
LLM_SUPERVISOR_ACTORS = {"llm_supervisor", "local_codex_supervisor"}
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
VALID_DRAFT_SECTION_TASKS_REVIEW_ACTIONS = {
    "approve_for_writer_agent",
    "needs_revision",
    "reject",
}
VALID_SECTION_DRAFTS_REVIEW_ACTIONS = {
    "approve_for_formal_writeback_preflight",
    "needs_revision",
    "reject",
}
VALID_FORMAL_WRITEBACK_PREFLIGHT_REVIEW_ACTIONS = {
    "approve_formal_writeback",
    "needs_revision",
    "reject",
}
VALID_FINAL_PDF_WRITEBACK_ACTIONS = {
    "approve",
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


def ensure_program_workbench_import_path() -> None:
    program_root = Path(__file__).resolve().parents[2] / "Program"
    program_root_text = str(program_root)
    if program_root_text not in sys.path:
        sys.path.insert(0, program_root_text)


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
    llm_intervention_handoff = build_task_llm_intervention_handoff(
        llm_intervention_contract,
        internal_skill_bindings,
    )
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
        "llm_intervention_handoff": llm_intervention_handoff,
        "llm_orchestration": build_task_llm_orchestration(
            llm_intervention_handoff,
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
    if status == "draft_section_tasks_approved":
        return {
            "id": "generate_section_drafts",
            "label": "生成章节草稿",
            "reason": "章节草稿任务包已通过人工审阅，可以交给 WriterAgent 生成草稿层章节；正式层仍保持锁定。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "section_drafts",
        }
    if status == "section_drafts_ready":
        return {
            "id": "review_section_drafts",
            "label": "审阅章节草稿",
            "reason": "章节草稿已生成，下一步由人工审阅内容、证据绑定和正式层写回边界。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "section_drafts_review",
        }
    if status == "formal_writeback_preflight_ready":
        return {
            "id": "review_formal_writeback_preflight",
            "label": "审阅正式写回预检",
            "reason": "章节草稿已通过审阅，系统已生成正式层候选写回清单；真正写入仍需下一道人工批准。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "formal_writeback_preflight",
        }
    if status == "formal_sections_written":
        return {
            "id": "prepare_export_preflight",
            "label": "准备导出预检",
            "reason": "正式章节已由人工批准写入，下一步检查 docx/PDF 导出所需的章节、引用和复现材料。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "export_preflight",
        }
    if status == "formal_export_preflight_ready":
        return {
            "id": "run_pdf_export_preflight",
            "label": "运行 PDF 导出预检",
            "reason": "导出预检已确认正式章节齐备，可以进入 PDF 候选包预检；这一步仍不生成最终论文文件。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "formal_pdf_export_preflight",
        }
    if status == "formal_export_preflight_blocked":
        return {
            "id": "resolve_export_preflight_blockers",
            "label": "处理导出阻断项",
            "reason": "导出预检发现章节或工具链缺口，需要先补齐再进入 PDF/DOCX 预检。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "export_preflight_blockers",
        }
    if status == "pdf_candidate_exported":
        return {
            "id": "review_pdf_candidate",
            "label": "审阅 PDF 候选稿",
            "reason": "PDF 候选稿已经生成，下一步检查排版、章节完整性、引用边界和复现说明。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "pdf_candidate_review",
        }
    if status == "pdf_candidate_reviewed":
        return {
            "id": "human_review_pdf_candidate",
            "label": "人工确认 PDF 候选稿",
            "reason": "PDF 候选稿机器审阅和最终写回预检已生成；下一步由人确认是否进入最终 PDF 批准。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "pdf_candidate_human_review",
        }
    if status == "pdf_candidate_final_approval_needs_revision":
        return {
            "id": "repair_pdf_candidate",
            "label": "修订 PDF 候选稿",
            "reason": "人工审阅要求修订候选 PDF，先修复候选稿再重新进入最终批准。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "pdf_candidate_review",
        }
    if status == "pdf_candidate_final_approval_rejected":
        return {
            "id": "repair_pdf_candidate",
            "label": "重做 PDF 候选稿",
            "reason": "本轮候选 PDF 已被拒绝，需要重新生成候选稿后再进入最终批准。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "pdf_candidate_review",
        }
    if status == "final_pdf_writeback_blocked":
        return {
            "id": "repair_final_pdf_writeback_inputs",
            "label": "修复最终 PDF 写回输入",
            "reason": "最终写回被批准账本、候选稿完整性或预检条件阻断，需要修复后重跑。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "final_pdf_writeback",
        }
    if status in {"final_pdf_written", "final_pdf_already_written"}:
        return {
            "id": "docx_export_preflight",
            "label": "进入 docx 导出预检",
            "reason": "最终 PDF 已进入正式包；下一步检查 docx 导出工具链和投稿包完整性。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "docx_export_preflight",
        }
    if status == "pdf_candidate_review_blocked":
        return {
            "id": "repair_pdf_candidate",
            "label": "修复 PDF 候选稿",
            "reason": "PDF 候选稿审阅发现缺口，需要先修复候选稿或来源章节。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "pdf_candidate_review",
        }
    if status == "formal_writeback_preflight_needs_revision":
        return {
            "id": "revise_formal_writeback_preflight",
            "label": "修订正式写回预检",
            "reason": "正式写回预检被要求修订，需要调整目标章节或草稿内容后再提交审批。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "formal_writeback_preflight",
        }
    if status == "formal_writeback_preflight_rejected":
        return {
            "id": "replace_section_drafts",
            "label": "重做章节草稿",
            "reason": "正式写回预检被拒绝，需要回到草稿层重新生成或替换章节内容。",
            "enabled": True,
            "writes_formal_layer": False,
            "target": "section_drafts",
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
        "source": build_llm_supervisor_source(plan),
    }


def build_llm_supervisor_source(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return {
            "source_actor": "",
            "source_action": "",
            "source_evidence_level": "none",
            "provider": {},
            "has_llm_supervisor_decision": False,
        }
    decision_events = [
        event
        for event in normalize_list(plan.get("decision_events"))
        if isinstance(event, dict)
    ]
    llm_events = [
        event
        for event in decision_events
        if str(event.get("actor") or "") in LLM_SUPERVISOR_ACTORS
    ]
    source_event = llm_events[-1] if llm_events else (decision_events[-1] if decision_events else {})
    provider = plan.get("provider") if isinstance(plan.get("provider"), dict) else {}
    evidence_level = str(plan.get("evidence_level") or "none")
    has_llm_supervisor_decision = bool(llm_events) and evidence_level in {
        "llm_supervisor",
        "local_execution",
    }
    return {
        "source_actor": str(source_event.get("actor") or ""),
        "source_action": str(source_event.get("action") or ""),
        "source_evidence_level": evidence_level,
        "provider": {
            key: provider.get(key)
            for key in ("provider_id", "provider_name", "provider", "model", "version")
            if provider.get(key)
        },
        "has_llm_supervisor_decision": has_llm_supervisor_decision,
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
        "required_for_execution": True,
    }
    source = llm_intervention_contract.get("source")
    if isinstance(source, dict):
        result.update(
            {
                "source_actor": source.get("source_actor", ""),
                "source_action": source.get("source_action", ""),
                "source_evidence_level": source.get("source_evidence_level", "none"),
                "source_provider": source.get("provider", {}),
                "has_llm_supervisor_decision": bool(source.get("has_llm_supervisor_decision")),
            }
        )
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


def build_task_llm_orchestration(
    llm_intervention_handoff: dict[str, Any],
    internal_skill_bindings: list[dict[str, Any]],
) -> dict[str, Any]:
    first_skill = internal_skill_bindings[0] if internal_skill_bindings else {}
    provider = llm_intervention_handoff.get("source_provider")
    if not isinstance(provider, dict):
        provider = {}
    selected_skill: dict[str, Any] = {}
    if first_skill:
        selected_skill = {
            "skill_id": first_skill.get("skill_id") or first_skill.get("id"),
            "name": first_skill.get("name", ""),
            "stage": first_skill.get("stage", ""),
            "risk_level": first_skill.get("risk_level", "medium"),
            "selection_source": first_skill.get("selection_source", ""),
        }
    canonical_policy = first_skill.get("canonical_policy") if isinstance(first_skill.get("canonical_policy"), dict) else {}
    auto_mode = canonical_policy.get("auto_mode") if isinstance(canonical_policy.get("auto_mode"), dict) else {}
    human_confirmation = (
        first_skill.get("human_confirmation") if isinstance(first_skill.get("human_confirmation"), dict) else {}
    )
    formal_write_allowed = bool(auto_mode.get("can_write_canonical") is True and first_skill.get("formal_write_targets"))
    default_human_gate = (
        "review_internal_skill_before_execution"
        if first_skill
        else str(llm_intervention_handoff.get("human_gate") or "dispatch_review_required")
    )
    default_output_boundary = (
        "draft_layer_only_until_human_review"
        if first_skill
        else str(llm_intervention_handoff.get("formal_boundary") or "draft_only_until_human_review")
    )
    return {
        "call_stage": str(llm_intervention_handoff.get("stage") or "agent_task_queue"),
        "llm_role": str(llm_intervention_handoff.get("llm_role") or ""),
        "deterministic_owner": str(llm_intervention_handoff.get("deterministic_owner") or ""),
        "current_provider": provider,
        "selected_skill": selected_skill,
        "selection_reason": str(
            first_skill.get("why_this_skill")
            or first_skill.get("semantic_selection_reason")
            or llm_intervention_handoff.get("selected_skill_reason")
            or ""
        ),
        "human_gate_required": True,
        "human_gate": str(first_skill.get("next_action") or default_human_gate),
        "human_confirmation_required_before": normalize_list(human_confirmation.get("required_before")),
        "output_boundary": "formal_layer_after_human_review"
        if formal_write_allowed
        else default_output_boundary,
        "formal_write_allowed": formal_write_allowed,
    }


def require_llm_intervention_handoff_before_execution(task: dict[str, Any]) -> dict[str, Any]:
    handoff = task.get("llm_intervention_handoff")
    if not isinstance(handoff, dict):
        raise AgentTaskQueueBlockedError(
            "llm_intervention_handoff_required",
            "Agent task must include an LLM Supervisor handoff before execution.",
        )
    if handoff.get("required_for_execution") is not True:
        raise AgentTaskQueueBlockedError(
            "llm_intervention_handoff_required",
            "Agent task LLM handoff must explicitly mark execution as gated by the Supervisor.",
        )
    if handoff.get("has_llm_supervisor_decision") is not True:
        raise AgentTaskQueueBlockedError(
            "llm_intervention_handoff_required",
            "Agent task execution requires a real LLM Supervisor decision, not only deterministic queue metadata.",
        )
    return handoff


def compact_llm_intervention_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": str(handoff.get("stage") or ""),
        "llm_role": str(handoff.get("llm_role") or ""),
        "human_gate": str(handoff.get("human_gate") or ""),
        "formal_boundary": str(handoff.get("formal_boundary") or ""),
        "source_actor": str(handoff.get("source_actor") or ""),
        "source_action": str(handoff.get("source_action") or ""),
        "source_evidence_level": str(handoff.get("source_evidence_level") or "none"),
        "source_provider": handoff.get("source_provider") if isinstance(handoff.get("source_provider"), dict) else {},
        "has_llm_supervisor_decision": bool(handoff.get("has_llm_supervisor_decision")),
        "required_for_execution": bool(handoff.get("required_for_execution")),
    }


def attach_llm_intervention_handoff_to_execution_result(
    task: dict[str, Any],
    result: dict[str, Any],
    handoff: dict[str, Any],
) -> None:
    compact_handoff = compact_llm_intervention_handoff(handoff)
    result["llm_intervention_handoff"] = compact_handoff
    execution_result = task.get("execution_result")
    if isinstance(execution_result, dict):
        execution_result["llm_intervention_handoff"] = compact_handoff
        task["execution_result"] = execution_result


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
    task.setdefault(
        "llm_orchestration",
        build_task_llm_orchestration(
            task["llm_intervention_handoff"],
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


def internal_skill_execution_packet_artifact_path(task_id: str) -> str:
    return (INTERNAL_SKILL_EXECUTION_PACKET_DIR / f"{task_id}.json").as_posix()


def build_internal_skill_execution_steps(task: dict[str, Any], skill: dict[str, Any]) -> list[dict[str, Any]]:
    owner_agent = str(task.get("owner_agent") or task.get("role") or skill.get("owner_agent") or "Agent")
    expected_artifacts = normalize_list(skill.get("expected_artifacts")) or ["skill_execution_notes"]
    return [
        {
            "id": "review_skill_reason_and_boundary",
            "label": "审阅 Skill 适配理由与正式层边界",
            "owner_agent": "Supervisor",
            "requires_human_review": True,
            "writes_formal_layer": False,
        },
        {
            "id": "collect_required_inputs",
            "label": "收集执行所需输入、证据和缺口",
            "owner_agent": owner_agent,
            "requires_human_review": False,
            "writes_formal_layer": False,
        },
        {
            "id": "run_skill_in_draft_layer",
            "label": "在草案层运行 Skill",
            "owner_agent": owner_agent,
            "expected_artifacts": expected_artifacts,
            "requires_human_review": False,
            "writes_formal_layer": False,
        },
        {
            "id": "return_to_human_review_gate",
            "label": "回到人工审阅门",
            "owner_agent": "Supervisor",
            "requires_human_review": True,
            "writes_formal_layer": False,
        },
    ]


def build_internal_skill_execution_packet(
    task: dict[str, Any],
    skill: dict[str, Any],
    queue: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    task_id = str(task.get("id") or "agent_task")
    expected_artifacts = normalize_list(skill.get("expected_artifacts")) or ["skill_execution_notes"]
    human_confirmation = skill.get("human_confirmation") if isinstance(skill.get("human_confirmation"), dict) else {}
    return {
        "schema_version": "internal_skill_execution_packet.v1",
        "status": "draft_execution_packet_ready",
        "task_id": task_id,
        "task_title": task.get("title", ""),
        "owner_agent": task.get("owner_agent", ""),
        "role": task.get("role", ""),
        "draft_layer": "exploratory",
        "selected_skill": {
            "id": skill.get("id", ""),
            "skill_id": skill.get("skill_id", ""),
            "name": skill.get("name", ""),
            "stage": skill.get("stage", ""),
            "risk_level": skill.get("risk_level", ""),
            "selection_source": skill.get("selection_source", ""),
            "why_this_skill": (
                skill.get("why_this_skill")
                or skill.get("semantic_selection_reason")
                or skill.get("matched_reason")
                or ""
            ),
            "source_policy": skill.get("source_policy", ""),
            "skill_sources": normalize_list(skill.get("skill_sources")),
        },
        "llm_semantic_judgment": skill.get("llm_semantic_judgment") or {},
        "execution_boundary": skill.get("execution_boundary") or "review_before_execution",
        "formal_boundary": "draft_only_until_human_review",
        "human_confirmation_required_before": normalize_list(
            human_confirmation.get("required_before")
        )
        or ["review_internal_skill_before_execution"],
        "review_gate": "review_internal_skill_before_execution",
        "expected_artifacts": expected_artifacts,
        "quality_gates": skill.get("quality_gates") or {},
        "canonical_policy": skill.get("canonical_policy") or {},
        "reference_chain_policy": (
            task.get("reference_chain_policy")
            or skill.get("reference_chain_policy")
            or queue.get("reference_chain_policy")
            or {}
        ),
        "agent_team_handoff": task.get("llm_intervention_handoff") or {},
        "execution_steps": build_internal_skill_execution_steps(task, skill),
        "artifact_path": internal_skill_execution_packet_artifact_path(task_id),
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "dispatch_review_required",
        "created_at": timestamp,
    }


def compact_internal_skill_execution_packet(packet: dict[str, Any]) -> dict[str, Any]:
    selected_skill = packet.get("selected_skill") if isinstance(packet.get("selected_skill"), dict) else {}
    return {
        "status": packet.get("status", "draft_execution_packet_ready"),
        "artifact_path": packet.get("artifact_path", ""),
        "skill_id": selected_skill.get("skill_id", ""),
        "skill_name": selected_skill.get("name", ""),
        "draft_layer": packet.get("draft_layer", "exploratory"),
        "expected_artifacts": normalize_list(packet.get("expected_artifacts")),
        "review_gate": packet.get("review_gate", "review_internal_skill_before_execution"),
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": packet.get("next_action", "dispatch_review_required"),
        "created_at": packet.get("created_at", ""),
    }


def generate_project_internal_skill_execution_packet(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    skill_bindings = [
        binding
        for binding in normalize_list(task.get("internal_skill_bindings"))
        if isinstance(binding, dict)
    ]
    if not skill_bindings:
        raise AgentTaskQueueBlockedError(
            "internal_skill_binding_required",
            "Agent task must include an internal skill binding before generating an execution packet.",
        )

    timestamp = utc_now()
    packet = build_internal_skill_execution_packet(task, skill_bindings[0], queue, timestamp)
    packet_path = project_root / str(packet["artifact_path"])
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    compact_packet = compact_internal_skill_execution_packet(packet)
    task["internal_skill_execution_packet"] = compact_packet
    task["next_action"] = "dispatch_review_required"
    task.setdefault("audit_log", []).append(
        {
            "event": "internal_skill_execution_packet_generated",
            "artifact_path": compact_packet["artifact_path"],
            "skill_id": compact_packet["skill_id"],
            "created_at": timestamp,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["primary_action"] = build_queue_primary_action(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")

    response = build_agent_task_queue_response(project, queue)
    response["internal_skill_execution_packet"] = compact_packet
    return response


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
    from Product.backend.execution_backend_service import (
        LLMExecutionPreflightError,
        execute_agent_task_with_backend,
    )

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
    try:
        llm_handoff = require_llm_intervention_handoff_before_execution(task)
    except AgentTaskQueueBlockedError as exc:
        if exc.code != "llm_intervention_handoff_required":
            raise
        _record_llm_intervention_handoff_blocked(task, exc, selected_backend)
        task["primary_action"] = build_task_primary_action(task)
        queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
        queue["updated_at"] = utc_now()
        path = agent_task_queue_state_path(project_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    try:
        result = execute_agent_task_with_backend(task, project_root)
    except LLMExecutionPreflightError as exc:
        _record_llm_execution_preflight_blocked(task, exc, selected_backend)
        task["primary_action"] = build_task_primary_action(task)
        queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
        queue["updated_at"] = utc_now()
        path = agent_task_queue_state_path(project_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
        raise AgentTaskQueueBlockedError(exc.code, str(exc)) from exc
    attach_llm_intervention_handoff_to_execution_result(task, result, llm_handoff)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = utc_now()
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["execution_result"] = result
    return response


def _record_llm_intervention_handoff_blocked(
    task: dict[str, Any],
    exc: AgentTaskQueueBlockedError,
    selected_backend: dict[str, Any],
) -> None:
    timestamp = utc_now()
    handoff = task.get("llm_intervention_handoff")
    if not isinstance(handoff, dict):
        handoff = {}
    handoff["execution_blocked"] = True
    handoff["block_reason"] = str(exc)
    handoff["next_action"] = "regenerate_or_confirm_supervisor_plan"
    handoff["formal_write_allowed"] = False
    task["llm_intervention_handoff"] = handoff
    task["error"] = {
        "code": exc.code,
        "message": str(exc),
        "student_message": "LLM Supervisor 交接未完成，暂不启动执行后端。请重新生成或确认 SupervisorPlan 后再执行。",
    }
    task.setdefault("audit_log", []).append({
        "event": "llm_intervention_handoff_blocked",
        "actor": "llm_supervisor",
        "timestamp": timestamp,
        "backend_id": selected_backend.get("id"),
        "method_id": task.get("method_id"),
        "error_code": exc.code,
        "formal_write_allowed": False,
    })


def _record_llm_execution_preflight_blocked(
    task: dict[str, Any],
    exc: Exception,
    selected_backend: dict[str, Any],
) -> None:
    timestamp = utc_now()
    error_code = str(getattr(exc, "code", "") or "llm_execution_preflight_required")
    message = str(exc)
    backend_id = str(selected_backend.get("id") or "")
    preflight = {
        "schema_version": "p6.llm_execution_preflight.v1",
        "task_id": str(task.get("id") or ""),
        "backend_id": backend_id,
        "method_id": str(task.get("method_id") or ""),
        "status": "blocked",
        "error_code": error_code,
        "message": message,
        "summary": "LLM 实验预检未完成",
        "backend_reason": "执行后端未启动；每次实验必须先经过 LLM Supervisor 的执行前判断。",
        "method_risk": ["模型层不可用时，系统不能形成执行前方法风险判断。"],
        "evidence_requirements": ["恢复 LLM Supervisor 后重新生成执行前预检。"],
        "human_review_note": "先配置或恢复 LLM provider，再重试本任务。",
        "next_action": "configure_llm_provider_or_retry",
        "provider": {},
        "artifact_path": "",
        "formal_write_allowed": False,
        "required_for_execution": True,
        "evidence_level": "llm_supervisor",
        "created_at": timestamp,
    }
    task["llm_execution_preflight"] = preflight
    task["error"] = {
        "code": error_code,
        "message": message,
        "student_message": "LLM 实验预检未完成，暂不启动执行后端。请检查模型配置后重试。",
    }
    task.setdefault("audit_log", []).append({
        "event": "llm_execution_preflight_blocked",
        "actor": "llm_supervisor",
        "timestamp": timestamp,
        "backend_id": backend_id,
        "method_id": task.get("method_id"),
        "error_code": error_code,
        "formal_write_allowed": False,
    })


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
        "section_count": len(section_tasks["tasks"]),
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


def review_project_draft_section_tasks(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_DRAFT_SECTION_TASKS_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_draft_section_tasks_review_action",
            f"Unsupported draft section tasks review action: {action}",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    task_summary = task.get("draft_section_tasks") if isinstance(task.get("draft_section_tasks"), dict) else {}
    task_artifact_path = str(task_summary.get("artifact_path") or "")
    task_artifact = project_root / task_artifact_path
    if task.get("status") != "draft_section_tasks_ready" or not task_artifact_path or not task_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "draft_section_tasks_required",
            "Draft section tasks are required before review.",
        )

    timestamp = utc_now()
    review = build_draft_section_tasks_review(action, note, timestamp)
    task["draft_section_tasks_review"] = review
    task_summary["review_status"] = review["status"]
    task_summary["review_gate"] = review["review_gate"]
    task_summary["writer_agent_allowed"] = review["writer_agent_allowed"]
    task_summary["formal_write_allowed"] = False
    task_summary["writes_formal_layer"] = False
    task["draft_section_tasks"] = task_summary

    artifact = json.loads(task_artifact.read_text(encoding="utf-8"))
    artifact["review"] = review
    artifact["writer_agent_allowed"] = review["writer_agent_allowed"]
    artifact["formal_write_allowed"] = False
    artifact["writes_formal_layer"] = False
    task_artifact.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")

    if action == "approve_for_writer_agent":
        task["status"] = "draft_section_tasks_approved"
        task["next_action"] = "generate_section_drafts"
        task["can_execute"] = False
        task["blockers"] = []
    elif action == "needs_revision":
        task["status"] = "draft_section_tasks_needs_revision"
        task["next_action"] = "revise_draft_section_tasks"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "draft_section_tasks_needs_revision",
                "message": "Draft section tasks need revision before WriterAgent can draft.",
            }
        ]
    else:
        task["status"] = "draft_section_tasks_rejected"
        task["next_action"] = "replace_draft_section_tasks"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "draft_section_tasks_rejected",
                "message": "Draft section tasks were rejected and must be replaced.",
            }
        ]

    task.setdefault("audit_log", []).append(
        {
            "event": "draft_section_tasks_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "status": review["status"],
            "artifact_path": task_artifact_path,
            "writer_agent_allowed": review["writer_agent_allowed"],
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
    response["draft_section_tasks_review"] = review
    return response


def generate_project_section_drafts(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    review = task.get("draft_section_tasks_review") if isinstance(task.get("draft_section_tasks_review"), dict) else {}
    tasks_summary = task.get("draft_section_tasks") if isinstance(task.get("draft_section_tasks"), dict) else {}
    tasks_artifact_path = str(tasks_summary.get("artifact_path") or "")
    tasks_artifact = project_root / tasks_artifact_path
    if (
        task.get("status") != "draft_section_tasks_approved"
        or review.get("status") != "approved_for_writer_agent"
        or not review.get("writer_agent_allowed")
        or not tasks_artifact_path
        or not tasks_artifact.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "draft_section_tasks_review_required",
            "Approved draft section tasks review is required before generating section drafts.",
        )

    task_package = json.loads(tasks_artifact.read_text(encoding="utf-8"))
    package_review = task_package.get("review") if isinstance(task_package.get("review"), dict) else {}
    if package_review.get("status") != "approved_for_writer_agent" or not task_package.get("writer_agent_allowed"):
        raise AgentTaskQueueBlockedError(
            "draft_section_tasks_review_required",
            "Draft section task package must record approved_for_writer_agent before WriterAgent can draft.",
        )

    timestamp = utc_now()
    drafts_artifact_path = Path("Results/json/section_drafts.json")
    drafts = build_section_drafts_record(task, task_package, tasks_artifact_path, review, timestamp)
    for section in drafts["sections"]:
        artifact_path = project_root / section["artifact_path"]
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            build_section_draft_markdown(section, task_package, task),
            encoding="utf-8",
        )
    absolute_drafts_artifact = project_root / drafts_artifact_path
    absolute_drafts_artifact.parent.mkdir(parents=True, exist_ok=True)
    absolute_drafts_artifact.write_text(json.dumps(drafts, ensure_ascii=False, indent=2), encoding="utf-8")

    draft_summary = {
        "status": "section_drafts_ready",
        "schema_version": drafts["schema_version"],
        "artifact_path": str(drafts_artifact_path),
        "source_artifact_path": tasks_artifact_path,
        "source_review_gate": drafts["source_review_gate"],
        "generated_from_review_status": drafts["generated_from_review_status"],
        "draft_layer": drafts["draft_layer"],
        "section_count": drafts["section_count"],
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_section_drafts",
        "next_action_label": "审阅章节草稿",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    task["section_drafts"] = draft_summary
    task["status"] = "section_drafts_ready"
    task["next_action"] = "review_section_drafts"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "section_drafts_generated",
            "actor": "WriterAgent",
            "timestamp": timestamp,
            "source_artifact_path": tasks_artifact_path,
            "artifact_path": str(drafts_artifact_path),
            "section_count": drafts["section_count"],
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
    response["section_drafts"] = draft_summary
    return response


def review_project_section_drafts(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_SECTION_DRAFTS_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_section_drafts_review_action",
            f"Unsupported section drafts review action: {action}",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    drafts_summary = task.get("section_drafts") if isinstance(task.get("section_drafts"), dict) else {}
    drafts_artifact_path = str(drafts_summary.get("artifact_path") or "")
    drafts_artifact = project_root / drafts_artifact_path
    if task.get("status") != "section_drafts_ready" or not drafts_artifact_path or not drafts_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "section_drafts_required",
            "Generated section drafts are required before review.",
        )

    timestamp = utc_now()
    review = build_section_drafts_review(action, note, timestamp)
    task["section_drafts_review"] = review
    drafts_summary["review_status"] = review["status"]
    drafts_summary["review_gate"] = review["review_gate"]
    drafts_summary["formal_writeback_preflight_allowed"] = review["formal_writeback_preflight_allowed"]
    drafts_summary["formal_write_allowed"] = False
    drafts_summary["writes_formal_layer"] = False
    task["section_drafts"] = drafts_summary

    drafts = json.loads(drafts_artifact.read_text(encoding="utf-8"))
    drafts["review"] = review
    drafts["formal_writeback_preflight_allowed"] = review["formal_writeback_preflight_allowed"]
    drafts["formal_write_allowed"] = False
    drafts["writes_formal_layer"] = False
    drafts_artifact.write_text(json.dumps(drafts, ensure_ascii=False, indent=2), encoding="utf-8")

    task.setdefault("audit_log", []).append(
        {
            "event": "section_drafts_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "status": review["status"],
            "artifact_path": drafts_artifact_path,
            "formal_writeback_preflight_allowed": review["formal_writeback_preflight_allowed"],
            "formal_write_allowed": False,
        }
    )

    if action == "approve_for_formal_writeback_preflight":
        preflight_artifact_path = Path("Results/json/section_draft_formal_writeback_preflight.json")
        preflight = build_formal_writeback_preflight_record(
            task,
            drafts,
            drafts_artifact_path,
            review,
            timestamp,
            project_root,
        )
        absolute_preflight_artifact = project_root / preflight_artifact_path
        absolute_preflight_artifact.parent.mkdir(parents=True, exist_ok=True)
        absolute_preflight_artifact.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

        preflight_summary = {
            "status": "formal_writeback_preflight_ready",
            "schema_version": preflight["schema_version"],
            "artifact_path": str(preflight_artifact_path),
            "source_artifact_path": drafts_artifact_path,
            "source_review_gate": preflight["source_review_gate"],
            "generated_from_review_status": preflight["generated_from_review_status"],
            "target_count": preflight["target_count"],
            "requires_human_review": True,
            "formal_write_allowed": False,
            "writes_formal_layer": False,
            "next_action": "review_formal_writeback_preflight",
            "next_action_label": "审阅正式写回预检",
            "created_at": timestamp,
            "evidence_level": "verified_source_record",
        }
        task["formal_writeback_preflight"] = preflight_summary
        task["status"] = "formal_writeback_preflight_ready"
        task["next_action"] = "review_formal_writeback_preflight"
        task["can_execute"] = False
        task["blockers"] = []
        task.setdefault("audit_log", []).append(
            {
                "event": "formal_writeback_preflight_created",
                "actor": "system",
                "timestamp": timestamp,
                "source_artifact_path": drafts_artifact_path,
                "artifact_path": str(preflight_artifact_path),
                "target_count": preflight["target_count"],
                "formal_write_allowed": False,
            }
        )
    elif action == "needs_revision":
        task["status"] = "section_drafts_needs_revision"
        task["next_action"] = "revise_section_drafts"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "section_drafts_needs_revision",
                "message": note or "Section drafts need revision before formal writeback preflight.",
            }
        ]
    else:
        task["status"] = "section_drafts_rejected"
        task["next_action"] = "replace_section_drafts"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "section_drafts_rejected",
                "message": note or "Section drafts were rejected and must be replaced.",
            }
        ]

    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["section_drafts_review"] = review
    if isinstance(task.get("formal_writeback_preflight"), dict):
        response["formal_writeback_preflight"] = task["formal_writeback_preflight"]
    return response


def review_project_formal_writeback_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_FORMAL_WRITEBACK_PREFLIGHT_REVIEW_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_formal_writeback_preflight_review_action",
            f"Unsupported formal writeback preflight review action: {action}",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    preflight_summary = task.get("formal_writeback_preflight") if isinstance(task.get("formal_writeback_preflight"), dict) else {}
    preflight_artifact_path = str(preflight_summary.get("artifact_path") or "")
    preflight_artifact = project_root / preflight_artifact_path
    if task.get("status") != "formal_writeback_preflight_ready" or not preflight_artifact_path or not preflight_artifact.exists():
        raise AgentTaskQueueBlockedError(
            "formal_writeback_preflight_required",
            "Formal writeback preflight is required before formal section writes.",
        )

    timestamp = utc_now()
    preflight = json.loads(preflight_artifact.read_text(encoding="utf-8"))
    review = build_formal_writeback_preflight_review(action, note, timestamp)
    preflight["review"] = review
    preflight["formal_write_allowed"] = review["formal_write_allowed"]
    preflight["writes_formal_layer"] = review["writes_formal_layer"]

    task["formal_writeback_preflight_review"] = review
    preflight_summary["review_status"] = review["status"]
    preflight_summary["review_gate"] = review["review_gate"]
    preflight_summary["formal_write_allowed"] = review["formal_write_allowed"]
    preflight_summary["writes_formal_layer"] = review["writes_formal_layer"]
    task["formal_writeback_preflight"] = preflight_summary

    task.setdefault("audit_log", []).append(
        {
            "event": "formal_writeback_preflight_reviewed",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "status": review["status"],
            "artifact_path": preflight_artifact_path,
            "formal_write_allowed": review["formal_write_allowed"],
            "writes_formal_layer": review["writes_formal_layer"],
        }
    )

    if action == "approve_formal_writeback":
        manifest_artifact_path = Path("Results/json/formal_writeback_manifest.json")
        manifest = write_formal_sections_from_preflight(
            project_root,
            task,
            preflight,
            preflight_artifact_path,
            review,
            timestamp,
            manifest_artifact_path,
        )
        preflight["status"] = "formal_writeback_approved"
        preflight["manifest_artifact_path"] = str(manifest_artifact_path)
        preflight["written_count"] = manifest["written_count"]
        preflight_artifact.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

        manifest_summary = {
            "status": manifest["status"],
            "schema_version": manifest["schema_version"],
            "artifact_path": str(manifest_artifact_path),
            "source_artifact_path": preflight_artifact_path,
            "review_status": review["status"],
            "written_count": manifest["written_count"],
            "target_count": manifest["target_count"],
            "writes_formal_layer": True,
            "created_at": timestamp,
            "evidence_level": "verified_source_record",
        }
        task["formal_writeback_manifest"] = manifest_summary
        task["status"] = "formal_sections_written"
        task["next_action"] = "prepare_export_preflight"
        task["can_execute"] = False
        task["blockers"] = []
        task.setdefault("audit_log", []).append(
            {
                "event": "formal_sections_written",
                "actor": "system",
                "timestamp": timestamp,
                "source_artifact_path": preflight_artifact_path,
                "artifact_path": str(manifest_artifact_path),
                "written_count": manifest["written_count"],
                "formal_write_allowed": True,
            }
        )
    elif action == "needs_revision":
        preflight["status"] = "needs_revision"
        preflight_artifact.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
        task["status"] = "formal_writeback_preflight_needs_revision"
        task["next_action"] = "revise_formal_writeback_preflight"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "formal_writeback_preflight_needs_revision",
                "message": note or "Formal writeback preflight needs revision before section writes.",
            }
        ]
    else:
        preflight["status"] = "rejected"
        preflight_artifact.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
        task["status"] = "formal_writeback_preflight_rejected"
        task["next_action"] = "replace_section_drafts"
        task["can_execute"] = False
        task["blockers"] = [
            {
                "code": "formal_writeback_preflight_rejected",
                "message": note or "Formal writeback preflight was rejected and section drafts must be replaced.",
            }
        ]

    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["formal_writeback_preflight_review"] = review
    if isinstance(task.get("formal_writeback_manifest"), dict):
        response["formal_writeback_manifest"] = task["formal_writeback_manifest"]
    return response


def generate_project_formal_export_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    manifest_summary = task.get("formal_writeback_manifest") if isinstance(task.get("formal_writeback_manifest"), dict) else {}
    manifest_artifact_path = str(manifest_summary.get("artifact_path") or "")
    manifest_path = project_root / manifest_artifact_path if manifest_artifact_path else None
    allowed_statuses = {
        "formal_sections_written",
        "formal_export_preflight_ready",
        "formal_export_preflight_blocked",
    }
    if (
        task.get("status") not in allowed_statuses
        or manifest_summary.get("status") != "formal_sections_written"
        or not manifest_path
        or not manifest_path.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "formal_sections_required",
            "Formal sections must be written before export preflight.",
        )

    timestamp = utc_now()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    preflight_artifact_path = Path("Results/json/agent_task_export_preflight.json")
    preflight_review_path = Path("Reviews/agent_task_export_preflight.md")
    preflight = build_formal_export_preflight_record(
        task,
        manifest,
        manifest_artifact_path,
        note,
        timestamp,
        project_root,
        preflight_review_path,
    )
    absolute_preflight_path = project_root / preflight_artifact_path
    absolute_preflight_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review_path = project_root / preflight_review_path
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.write_text(format_formal_export_preflight_review(preflight), encoding="utf-8")

    summary = {
        "schema_version": preflight["schema_version"],
        "status": preflight["status"],
        "source_task_id": preflight["source_task_id"],
        "source_review_gate": preflight["source_review_gate"],
        "artifact_path": str(preflight_artifact_path),
        "review_path": str(preflight_review_path),
        "section_count": preflight["section_count"],
        "missing_section_count": preflight["missing_section_count"],
        "blocker_count": len(preflight["blockers"]),
        "next_action": preflight["next_action"],
        "writes_formal_layer": preflight["writes_formal_layer"],
        "wrote_pdf": preflight["wrote_pdf"],
        "wrote_docx": preflight["wrote_docx"],
        "created_at": timestamp,
        "evidence_level": preflight["evidence_level"],
    }
    if preflight.get("llm_provider_snapshot"):
        summary["llm_provider_snapshot"] = preflight["llm_provider_snapshot"]
        summary["llm_preflight_summary"] = preflight.get("llm_preflight_summary", "")
        summary["llm_preflight_human_review_note"] = preflight.get("llm_preflight_human_review_note", "")
    task["formal_export_preflight"] = summary
    task["export_preflight_followups"] = preflight["agent_followups"]
    task["status"] = preflight["status"]
    task["next_action"] = preflight["next_action"]
    task["can_execute"] = False
    task["blockers"] = preflight["blockers"]
    task.setdefault("audit_log", []).append(
        {
            "event": "formal_export_preflight_generated",
            "actor": "system",
            "timestamp": timestamp,
            "artifact_path": str(preflight_artifact_path),
            "review_path": str(preflight_review_path),
            "status": preflight["status"],
            "next_action": preflight["next_action"],
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["formal_export_preflight"] = summary
    return response


def generate_project_pdf_candidate_export(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    preflight_summary = task.get("formal_export_preflight") if isinstance(task.get("formal_export_preflight"), dict) else {}
    preflight_artifact_path = str(preflight_summary.get("artifact_path") or "")
    preflight_path = project_root / preflight_artifact_path if preflight_artifact_path else None
    if (
        task.get("status") != "formal_export_preflight_ready"
        or preflight_summary.get("status") != "formal_export_preflight_ready"
        or not preflight_path
        or not preflight_path.exists()
    ):
        raise AgentTaskQueueBlockedError(
            "formal_export_preflight_required",
            "Ready formal export preflight is required before PDF candidate export.",
        )

    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("status") != "formal_export_preflight_ready" or normalize_list(preflight.get("blockers")):
        raise AgentTaskQueueBlockedError(
            "formal_export_preflight_required",
            "Ready formal export preflight is required before PDF candidate export.",
        )

    timestamp = utc_now()
    pdf_candidate_path = Path("Submissions/formal_package/paper_candidate.pdf")
    candidate_qmd_path = Path("Submissions/formal_package/manuscript/paper_candidate.qmd")
    manifest_artifact_path = Path("Submissions/formal_package/pdf_candidate_manifest.json")
    formal_candidate_report_path = Path("Results/json/formal_pdf_candidate_report.json")
    review_path = Path("Reviews/pdf_candidate_export_review.md")
    export_record = build_pdf_candidate_export_record(
        task,
        preflight,
        preflight_artifact_path,
        note,
        timestamp,
        project_root,
        pdf_candidate_path,
        candidate_qmd_path,
        formal_candidate_report_path,
        review_path,
    )

    absolute_pdf_path = project_root / pdf_candidate_path
    absolute_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    write_pdf_candidate_file(absolute_pdf_path, export_record)

    absolute_qmd_path = project_root / candidate_qmd_path
    absolute_qmd_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_qmd_path.write_text(format_pdf_candidate_qmd(export_record), encoding="utf-8")

    absolute_manifest_path = project_root / manifest_artifact_path
    absolute_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_manifest_path.write_text(json.dumps(export_record, ensure_ascii=False, indent=2), encoding="utf-8")

    formal_candidate_report = build_formal_pdf_candidate_report_from_queue_export(
        export_record,
        manifest_artifact_path,
        formal_candidate_report_path,
        absolute_pdf_path,
        absolute_qmd_path,
    )
    absolute_formal_candidate_report_path = project_root / formal_candidate_report_path
    absolute_formal_candidate_report_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_formal_candidate_report_path.write_text(
        json.dumps(formal_candidate_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    absolute_review_path = project_root / review_path
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.write_text(format_pdf_candidate_export_review(export_record), encoding="utf-8")

    summary = {
        "schema_version": export_record["schema_version"],
        "status": export_record["status"],
        "source_task_id": export_record["source_task_id"],
        "source_preflight_path": export_record["source_preflight_path"],
        "artifact_path": str(manifest_artifact_path),
        "review_path": str(review_path),
        "pdf_candidate_path": str(pdf_candidate_path),
        "candidate_qmd_path": str(candidate_qmd_path),
        "formal_candidate_report_path": str(formal_candidate_report_path),
        "wrote_pdf_candidate": True,
        "wrote_final_pdf": False,
        "wrote_docx": False,
        "writes_formal_layer": False,
        "next_action": "review_pdf_candidate",
        "created_at": timestamp,
        "evidence_level": export_record["evidence_level"],
    }
    if export_record.get("llm_provider_snapshot"):
        summary["llm_provider_snapshot"] = export_record["llm_provider_snapshot"]
        summary["llm_preflight_summary"] = export_record.get("llm_preflight_summary", "")
        summary["llm_preflight_human_review_note"] = export_record.get("llm_preflight_human_review_note", "")
    task["pdf_candidate_export"] = summary
    task["status"] = "pdf_candidate_exported"
    task["next_action"] = "review_pdf_candidate"
    task["can_execute"] = False
    task["blockers"] = []
    task.setdefault("audit_log", []).append(
        {
            "event": "pdf_candidate_exported",
            "actor": "system",
            "timestamp": timestamp,
            "artifact_path": str(manifest_artifact_path),
            "review_path": str(review_path),
            "pdf_candidate_path": str(pdf_candidate_path),
            "status": "pdf_candidate_exported",
            "next_action": "review_pdf_candidate",
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["pdf_candidate_export"] = summary
    return response


def generate_project_pdf_candidate_review(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    export_summary = task.get("pdf_candidate_export") if isinstance(task.get("pdf_candidate_export"), dict) else {}
    candidate_report_rel = str(export_summary.get("formal_candidate_report_path") or "")
    candidate_report_path = project_root / candidate_report_rel if candidate_report_rel else None
    if task.get("status") != "pdf_candidate_exported" or not candidate_report_path or not candidate_report_path.exists():
        raise AgentTaskQueueBlockedError(
            "pdf_candidate_export_required",
            "Reviewable PDF candidate export is required before candidate review.",
        )

    candidate_report = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    timestamp = utc_now()
    review_report_path = Path("Results/json/formal_pdf_candidate_review.json")
    review_doc_path = Path("Reviews/formal_pdf_candidate_review.md")
    final_preflight_path = Path("Results/json/formal_pdf_final_writeback_preflight.json")
    review_record = build_pdf_candidate_review_record(
        task,
        export_summary,
        candidate_report,
        candidate_report_rel,
        str(review_report_path),
        str(final_preflight_path),
        note,
        timestamp,
        project_root,
    )
    final_preflight = build_pdf_candidate_final_writeback_preflight(
        review_record,
        str(review_report_path),
        str(final_preflight_path),
        note,
        timestamp,
    )

    absolute_review_report_path = project_root / review_report_path
    absolute_review_report_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_report_path.write_text(json.dumps(review_record, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review_doc_path = project_root / review_doc_path
    absolute_review_doc_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_doc_path.write_text(format_pdf_candidate_review(review_record, final_preflight), encoding="utf-8")

    absolute_final_preflight_path = project_root / final_preflight_path
    absolute_final_preflight_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_final_preflight_path.write_text(json.dumps(final_preflight, ensure_ascii=False, indent=2), encoding="utf-8")

    ready = review_record.get("status") == "ready_for_final_approval_review"
    next_action = "human_review_pdf_candidate" if ready else "repair_pdf_candidate"
    summary = {
        "schema_version": review_record["schema_version"],
        "status": review_record["status"],
        "source_task_id": review_record["source_task_id"],
        "source_candidate_report": candidate_report_rel,
        "artifact_path": str(review_report_path),
        "review_path": str(review_doc_path),
        "final_preflight_path": str(final_preflight_path),
        "candidate_pdf": review_record["candidate_pdf"],
        "candidate_qmd": review_record["candidate_qmd"],
        "can_request_final_approval": ready,
        "blocking_reason_count": len(normalize_list(review_record.get("blocking_reasons"))),
        "writes_formal_layer": False,
        "wrote_final_outputs": False,
        "next_action": next_action,
        "created_at": timestamp,
        "evidence_level": review_record["evidence_level"],
    }
    if review_record.get("llm_provider_snapshot"):
        summary["llm_provider_snapshot"] = review_record["llm_provider_snapshot"]
        summary["llm_preflight_summary"] = review_record.get("llm_preflight_summary", "")
        summary["llm_preflight_human_review_note"] = review_record.get("llm_preflight_human_review_note", "")
    task["pdf_candidate_review"] = summary
    task["status"] = "pdf_candidate_reviewed" if ready else "pdf_candidate_review_blocked"
    task["next_action"] = next_action
    task["can_execute"] = False
    task["blockers"] = [] if ready else review_record.get("blockers", [])
    task.setdefault("audit_log", []).append(
        {
            "event": "pdf_candidate_reviewed",
            "actor": "system",
            "timestamp": timestamp,
            "artifact_path": str(review_report_path),
            "review_path": str(review_doc_path),
            "final_preflight_path": str(final_preflight_path),
            "status": summary["status"],
            "next_action": next_action,
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["pdf_candidate_review"] = summary
    return response


def review_project_final_pdf_writeback(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_FINAL_PDF_WRITEBACK_ACTIONS:
        raise AgentTaskQueueBlockedError(
            "invalid_final_pdf_writeback_action",
            f"Unsupported final PDF writeback action: {action}",
        )

    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(_load_required_queue(project_root))
    task = _find_agent_task(queue, task_id)
    review_summary = task.get("pdf_candidate_review") if isinstance(task.get("pdf_candidate_review"), dict) else {}
    final_preflight_rel = str(review_summary.get("final_preflight_path") or "")
    final_preflight_path = project_root / final_preflight_rel if final_preflight_rel else None
    if task.get("status") != "pdf_candidate_reviewed" or not final_preflight_path or not final_preflight_path.exists():
        raise AgentTaskQueueBlockedError(
            "pdf_candidate_review_required",
            "Reviewed PDF candidate and final writeback preflight are required before final PDF approval.",
        )

    ensure_program_workbench_import_path()
    from workbench.formal_pdf_final_approval import (  # type: ignore
        build_formal_pdf_final_approval,
        write_formal_pdf_final_approval_outputs,
    )
    from workbench.formal_pdf_final_writeback import (  # type: ignore
        build_formal_pdf_final_writeback,
        write_formal_pdf_final_writeback_outputs,
    )
    from workbench.paper_revision_round import snapshot_formal_state  # type: ignore

    timestamp = utc_now()
    final_preflight = json.loads(final_preflight_path.read_text(encoding="utf-8"))
    approval_report_rel = Path("Results/json/formal_pdf_final_approval.json")
    approval_review_rel = Path("Reviews/formal_pdf_final_approval.md")
    approval_ledger_rel = Path("state/product/writeback_approvals.json")
    approval_report, approval_exit_code = build_formal_pdf_final_approval(
        project_root,
        final_preflight,
        final_preflight_path,
        action=action,
        note=note,
        actor="human",
        approval_path=project_root / approval_ledger_rel,
        formal_state_before=snapshot_formal_state(project_root),
    )
    approval_report.update(build_export_llm_preflight_provenance_from_source(final_preflight))
    write_formal_pdf_final_approval_outputs(
        project_root / approval_report_rel,
        project_root / approval_review_rel,
        approval_report,
    )
    approval_summary = build_final_pdf_approval_summary(
        approval_report,
        str(approval_report_rel),
        str(approval_review_rel),
    )
    task["pdf_final_approval"] = approval_summary

    if approval_exit_code != 0 or action != "approve" or approval_report.get("can_enter_p6") is not True:
        if action == "needs_revision":
            task["status"] = "pdf_candidate_final_approval_needs_revision"
            task["next_action"] = "repair_pdf_candidate"
        elif action == "reject":
            task["status"] = "pdf_candidate_final_approval_rejected"
            task["next_action"] = "repair_pdf_candidate"
        else:
            task["status"] = "final_pdf_writeback_blocked"
            task["next_action"] = "repair_final_pdf_writeback_inputs"
        task["can_execute"] = False
        task["blockers"] = build_final_pdf_blockers(approval_report.get("blocking_reasons") or [])
        task.setdefault("audit_log", []).append(
            {
                "event": "formal_pdf_final_approval_recorded",
                "actor": "human",
                "timestamp": timestamp,
                "artifact_path": str(approval_report_rel),
                "review_path": str(approval_review_rel),
                "status": approval_summary["status"],
                "next_action": task["next_action"],
            }
        )
        task["primary_action"] = build_task_primary_action(task)
        return persist_agent_task_queue_response(project, project_root, queue, timestamp, task, approval_summary)

    writeback_report_rel = Path("Results/json/formal_pdf_final_writeback.json")
    writeback_review_rel = Path("Reviews/formal_pdf_final_writeback.md")
    final_pdf_rel = Path("Submissions/formal_package/paper.pdf")
    candidate_report_rel = str(review_summary.get("source_candidate_report") or "Results/json/formal_pdf_candidate_report.json")
    writeback_report, writeback_exit_code = build_formal_pdf_final_writeback(
        project_root,
        candidate_report_path=project_root / candidate_report_rel,
        final_preflight_path=final_preflight_path,
        approval_report_path=project_root / approval_report_rel,
        approval_ledger_path=project_root / approval_ledger_rel,
        output_pdf_path=project_root / final_pdf_rel,
        formal_state_before=snapshot_formal_state(project_root),
    )
    writeback_report.update(build_export_llm_preflight_provenance_from_source(final_preflight))
    write_formal_pdf_final_writeback_outputs(
        project_root / writeback_report_rel,
        project_root / writeback_review_rel,
        writeback_report,
    )
    writeback_summary = build_final_pdf_writeback_summary(
        writeback_report,
        str(writeback_report_rel),
        str(writeback_review_rel),
    )
    task["pdf_final_writeback"] = writeback_summary
    task["can_execute"] = False
    task["blockers"] = build_final_pdf_blockers(writeback_report.get("blocking_reasons") or [])
    if writeback_exit_code == 0:
        task["status"] = writeback_summary["status"]
        task["next_action"] = writeback_report.get("next_action", {}).get("id") or "docx_export_preflight"
        event = "formal_pdf_final_writeback_completed"
    else:
        task["status"] = "final_pdf_writeback_blocked"
        task["next_action"] = "repair_final_pdf_writeback_inputs"
        event = "formal_pdf_final_writeback_blocked"
    task.setdefault("audit_log", []).append(
        {
            "event": event,
            "actor": "human",
            "timestamp": timestamp,
            "approval_artifact_path": str(approval_report_rel),
            "artifact_path": str(writeback_report_rel),
            "review_path": str(writeback_review_rel),
            "final_pdf": writeback_summary["final_pdf"],
            "status": writeback_summary["status"],
            "next_action": task["next_action"],
        }
    )
    task["primary_action"] = build_task_primary_action(task)
    return persist_agent_task_queue_response(
        project,
        project_root,
        queue,
        timestamp,
        task,
        approval_summary,
        writeback_summary,
    )


def persist_agent_task_queue_response(
    project: dict[str, Any],
    project_root: Path,
    queue: dict[str, Any],
    timestamp: str,
    task: dict[str, Any],
    approval_summary: dict[str, Any],
    writeback_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    response = build_agent_task_queue_response(project, queue)
    response["pdf_final_approval"] = approval_summary
    if writeback_summary is not None:
        response["pdf_final_writeback"] = writeback_summary
    return response


def build_final_pdf_approval_summary(
    report: dict[str, Any],
    report_path: str,
    review_path: str,
) -> dict[str, Any]:
    summary = {
        "schema_version": report.get("schema_version"),
        "status": report.get("status"),
        "action": report.get("action"),
        "artifact_path": report_path,
        "review_path": review_path,
        "approval_path": report.get("approval_path"),
        "candidate_pdf": report.get("candidate_pdf"),
        "candidate_qmd": report.get("candidate_qmd"),
        "can_enter_p6": report.get("can_enter_p6") is True,
        "final_writeback_authorized": report.get("final_writeback_authorized") is True,
        "blocking_reason_count": len(normalize_list(report.get("blocking_reasons"))),
        "writes_formal_layer": report.get("this_command_wrote_formal_state") is True,
        "wrote_final_outputs": report.get("this_command_wrote_final_outputs") is True,
        "next_action": report.get("next_action", {}).get("id"),
        "created_at": report.get("generated_at"),
        "evidence_level": "local_file",
    }
    if report.get("llm_provider_snapshot"):
        summary["llm_provider_snapshot"] = report["llm_provider_snapshot"]
        summary["llm_preflight_summary"] = report.get("llm_preflight_summary", "")
        summary["llm_preflight_backend_reason"] = report.get("llm_preflight_backend_reason", "")
        summary["llm_preflight_human_review_note"] = report.get("llm_preflight_human_review_note", "")
        summary["llm_preflight_artifact_path"] = report.get("llm_preflight_artifact_path", "")
    return summary


def build_final_pdf_writeback_summary(
    report: dict[str, Any],
    report_path: str,
    review_path: str,
) -> dict[str, Any]:
    summary = {
        "schema_version": report.get("schema_version"),
        "status": report.get("status"),
        "artifact_path": report_path,
        "review_path": review_path,
        "source_candidate_report": report.get("source_candidate_report"),
        "source_final_preflight": report.get("source_final_preflight"),
        "source_approval_report": report.get("source_approval_report"),
        "source_candidate_pdf": report.get("source_candidate_pdf"),
        "final_pdf": report.get("final_pdf"),
        "final_pdf_exists": report.get("final_pdf_exists") is True,
        "source_candidate_pdf_sha256": report.get("source_candidate_pdf_sha256"),
        "final_pdf_sha256": report.get("final_pdf_sha256"),
        "final_writeback_authorized": report.get("final_writeback_authorized") is True,
        "blocking_reason_count": len(normalize_list(report.get("blocking_reasons"))),
        "wrote_final_pdf": report.get("this_command_wrote_final_pdf") is True,
        "wrote_docx": report.get("this_command_wrote_docx") is True,
        "writes_formal_layer": report.get("this_command_wrote_formal_state") is True,
        "next_action": report.get("next_action", {}).get("id"),
        "created_at": report.get("generated_at"),
        "evidence_level": "local_file",
    }
    if report.get("llm_provider_snapshot"):
        summary["llm_provider_snapshot"] = report["llm_provider_snapshot"]
        summary["llm_preflight_summary"] = report.get("llm_preflight_summary", "")
        summary["llm_preflight_backend_reason"] = report.get("llm_preflight_backend_reason", "")
        summary["llm_preflight_human_review_note"] = report.get("llm_preflight_human_review_note", "")
        summary["llm_preflight_artifact_path"] = report.get("llm_preflight_artifact_path", "")
    return summary


def build_final_pdf_blockers(reasons: list[str]) -> list[dict[str, str]]:
    return [{"code": reason, "message": final_pdf_blocker_message(reason)} for reason in reasons]


def final_pdf_blocker_message(reason: str) -> str:
    messages = {
        "final_preflight_not_ready": "最终写回预检还没有 ready。",
        "final_approval_not_requested_by_preflight": "预检没有请求最终人工批准。",
        "human_approval_not_required_by_preflight": "预检缺少人工批准要求。",
        "formal_state_changed_before_final_approval": "正式层状态在批准前发生变化。",
        "candidate_pdf_missing": "候选 PDF 缺失。",
        "candidate_qmd_missing": "候选 QMD 缺失。",
        "final_approval_not_authorized": "人工批准报告未授权最终写回。",
        "approval_ledger_not_approved": "审批账本未批准最终写回。",
        "candidate_pdf_mismatch": "候选 PDF 与审批对象不一致。",
        "candidate_qmd_mismatch": "候选 QMD 与审批对象不一致。",
        "final_pdf_exists_with_different_hash": "最终 PDF 已存在且内容不同，不能覆盖。",
    }
    return messages.get(reason, reason)


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


def build_draft_section_tasks_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_writer_agent":
        status = "approved_for_writer_agent"
        next_action = "generate_section_drafts"
        next_action_label = "生成章节草稿"
        writer_agent_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_draft_section_tasks"
        next_action_label = "要求修订章节任务包"
        writer_agent_allowed = False
    else:
        status = "rejected"
        next_action = "replace_draft_section_tasks"
        next_action_label = "拒绝章节任务包"
        writer_agent_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_draft_section_tasks",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "draft_state": "section_draft_tasks",
        "writer_agent_allowed": writer_agent_allowed,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "verified_source_record",
    }


def build_section_drafts_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_for_formal_writeback_preflight":
        status = "approved_for_formal_writeback_preflight"
        next_action = "review_formal_writeback_preflight"
        next_action_label = "审阅正式写回预检"
        preflight_allowed = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_section_drafts"
        next_action_label = "要求修订章节草稿"
        preflight_allowed = False
    else:
        status = "rejected"
        next_action = "replace_section_drafts"
        next_action_label = "拒绝章节草稿"
        preflight_allowed = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_section_drafts",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "draft_state": "section_drafts",
        "formal_writeback_preflight_allowed": preflight_allowed,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": next_action,
        "next_action_label": next_action_label,
        "evidence_level": "verified_source_record",
    }


def build_formal_writeback_preflight_review(action: str, note: str, timestamp: str) -> dict[str, Any]:
    if action == "approve_formal_writeback":
        status = "approved_formal_writeback"
        next_action = "prepare_export_preflight"
        next_action_label = "准备导出预检"
        formal_write_allowed = True
        writes_formal_layer = True
    elif action == "needs_revision":
        status = "needs_revision"
        next_action = "revise_formal_writeback_preflight"
        next_action_label = "要求修订正式写回预检"
        formal_write_allowed = False
        writes_formal_layer = False
    else:
        status = "rejected"
        next_action = "replace_section_drafts"
        next_action_label = "拒绝正式写回预检"
        formal_write_allowed = False
        writes_formal_layer = False
    return {
        "status": status,
        "action": action,
        "review_gate": "review_formal_writeback_preflight",
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "draft_state": "formal_writeback_preflight",
        "formal_write_allowed": formal_write_allowed,
        "writes_formal_layer": writes_formal_layer,
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
        "output_artifacts": [f"Manuscripts/drafts/sections/{safe_section_slug(section_id)}.md"],
        "status": "queued",
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
    }


def safe_section_slug(value: str) -> str:
    slug = "".join(
        char if char.isalnum() or char in {"_", "-"} else "_"
        for char in value.strip().lower()
    ).strip("_")
    return slug or "section"


def build_section_drafts_record(
    task: dict[str, Any],
    task_package: dict[str, Any],
    source_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
) -> dict[str, Any]:
    section_tasks = [
        item
        for item in normalize_list(task_package.get("tasks"))
        if isinstance(item, dict)
    ]
    sections = [
        build_section_draft_entry(section_task, index, timestamp)
        for index, section_task in enumerate(section_tasks, start=1)
    ]
    return {
        "schema_version": "p1.section_drafts.v1",
        "status": "section_drafts_ready",
        "source_task_id": str(task.get("id") or task_package.get("source_task_id") or ""),
        "source_artifact_path": source_artifact_path,
        "source_review_gate": "review_draft_section_tasks",
        "generated_from_review_status": str(review.get("status") or ""),
        "draft_layer": "section_drafts",
        "writer_agent": {
            "id": "WriterAgent",
            "mode": "draft_only",
            "allowed_by_review_gate": "review_draft_section_tasks",
        },
        "section_count": len(sections),
        "sections": sections,
        "review": {
            "status": "pending",
            "review_gate": "review_section_drafts",
            "reviewer": "human",
            "formal_write_allowed": False,
            "writes_formal_layer": False,
        },
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_section_drafts",
        "next_action_label": "审阅章节草稿",
        "usage_boundary": "WriterAgent 只生成草稿层章节；正式正文写回需要后续人工批准。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_section_draft_entry(section_task: dict[str, Any], index: int, timestamp: str) -> dict[str, Any]:
    section_id = str(section_task.get("section_id") or f"section_{index:02d}")
    section_slug = safe_section_slug(section_id)
    return {
        "id": f"section_draft_{index:02d}",
        "source_task_id": str(section_task.get("id") or ""),
        "section_id": section_id,
        "section_title": str(section_task.get("section_title") or "未命名章节"),
        "purpose": str(section_task.get("purpose") or ""),
        "writing_task": str(section_task.get("writing_task") or ""),
        "citation_binding_ids": [
            str(binding_id)
            for binding_id in normalize_list(section_task.get("citation_binding_ids"))
            if str(binding_id)
        ],
        "artifact_path": f"Manuscripts/drafts/sections/{section_slug}.md",
        "status": "draft_ready",
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_section_draft_markdown(
    section: dict[str, Any],
    task_package: dict[str, Any],
    task: dict[str, Any],
) -> str:
    citation_ids = normalize_list(section.get("citation_binding_ids"))
    citation_lines = "\n".join(f"- {binding_id}" for binding_id in citation_ids) or "- 暂无绑定引用"
    return "\n".join(
        [
            f"# {section['section_title']}",
            "",
            "草稿层章节",
            "",
            f"章节 ID：{section['section_id']}",
            f"来源任务：{section.get('source_task_id') or task.get('id') or ''}",
            f"正式层写回：未批准",
            "",
            "## 写作任务",
            section.get("writing_task") or "根据已批准章节任务包生成本节草稿。",
            "",
            "## 草稿正文",
            f"本节围绕“{section['section_title']}”展开。当前文本由 WriterAgent 根据章节任务包生成，用于后续人工审阅、修改和证据绑定检查。",
            "",
            "## 引用绑定",
            citation_lines,
            "",
            "## 审阅清单",
            "- 核对本节论断是否有已核验来源支撑。",
            "- 核对引用绑定是否进入正确论证位置。",
            "- 核对是否需要补充数据、方法或稳健性证据。",
            "- 人工批准前不写入正式正文。",
            "",
            f"来源任务包：{task_package.get('source_artifact_path') or 'Results/json/draft_section_tasks.json'}",
            "",
        ]
    )


def build_formal_writeback_preflight_record(
    task: dict[str, Any],
    drafts: dict[str, Any],
    source_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
    project_root: Path,
) -> dict[str, Any]:
    sections = [
        item
        for item in normalize_list(drafts.get("sections"))
        if isinstance(item, dict)
    ]
    targets = [
        build_formal_writeback_preflight_target(section, index, project_root)
        for index, section in enumerate(sections, start=1)
    ]
    return {
        "schema_version": "p1.formal_writeback_preflight.v1",
        "status": "formal_writeback_preflight_ready",
        "source_task_id": str(task.get("id") or drafts.get("source_task_id") or ""),
        "source_artifact_path": source_artifact_path,
        "source_review_gate": "review_section_drafts",
        "generated_from_review_status": str(review.get("status") or ""),
        "draft_layer": "section_drafts",
        "formal_layer": "manuscript_sections",
        "target_count": len(targets),
        "targets": targets,
        "required_checks": [
            "人工确认章节内容",
            "人工确认引用绑定",
            "人工确认正式目标文件",
            "人工确认不会覆盖正式层已有内容",
        ],
        "review": {
            "status": "pending",
            "review_gate": "review_formal_writeback_preflight",
            "reviewer": "human",
            "formal_write_allowed": False,
            "writes_formal_layer": False,
        },
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "next_action": "review_formal_writeback_preflight",
        "next_action_label": "审阅正式写回预检",
        "usage_boundary": "这份预检只列出草稿层章节到正式层候选文件的映射；人工批准正式写回前不会修改正式正文。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }


def build_formal_writeback_preflight_target(
    section: dict[str, Any],
    index: int,
    project_root: Path,
) -> dict[str, Any]:
    section_id = str(section.get("section_id") or f"section_{index:02d}")
    section_slug = safe_section_slug(section_id)
    formal_target_path = f"Manuscripts/sections/{section_slug}.md"
    draft_artifact_path = str(section.get("artifact_path") or "")
    return {
        "id": f"formal_writeback_target_{index:02d}",
        "section_id": section_id,
        "section_title": str(section.get("section_title") or "未命名章节"),
        "draft_artifact_path": draft_artifact_path,
        "formal_target_path": formal_target_path,
        "draft_exists": bool(draft_artifact_path and (project_root / draft_artifact_path).exists()),
        "formal_target_exists": (project_root / formal_target_path).exists(),
        "write_mode": "candidate_replace_or_create",
        "requires_human_review": True,
        "formal_write_allowed": False,
        "writes_formal_layer": False,
        "evidence_level": str(section.get("evidence_level") or "verified_source_record"),
    }


def write_formal_sections_from_preflight(
    project_root: Path,
    task: dict[str, Any],
    preflight: dict[str, Any],
    preflight_artifact_path: str,
    review: dict[str, Any],
    timestamp: str,
    manifest_artifact_path: Path,
) -> dict[str, Any]:
    targets = [
        target
        for target in normalize_list(preflight.get("targets"))
        if isinstance(target, dict)
    ]
    missing_sources = [
        str(target.get("draft_artifact_path") or "")
        for target in targets
        if not str(target.get("draft_artifact_path") or "")
        or not (project_root / str(target.get("draft_artifact_path") or "")).exists()
    ]
    if missing_sources:
        raise AgentTaskQueueBlockedError(
            "formal_writeback_source_missing",
            f"Formal writeback source drafts are missing: {', '.join(missing_sources)}",
        )

    written_targets: list[dict[str, Any]] = []
    for target in targets:
        draft_artifact_path = str(target.get("draft_artifact_path") or "")
        formal_target_path = str(target.get("formal_target_path") or "")
        if not formal_target_path:
            raise AgentTaskQueueBlockedError(
                "formal_writeback_target_missing",
                "Formal writeback target path is missing.",
            )
        draft_path = project_root / draft_artifact_path
        formal_path = project_root / formal_target_path
        previous_exists = formal_path.exists()
        draft_text = draft_path.read_text(encoding="utf-8")
        formal_text = draft_text.replace("正式层写回：未批准", "正式层写回：已批准")
        audit_header = (
            f"<!-- formal_writeback: approved_at={timestamp}; "
            f"source={draft_artifact_path}; gate={review['review_gate']} -->\n"
        )
        if not formal_text.startswith("<!-- formal_writeback:"):
            formal_text = audit_header + formal_text
        formal_path.parent.mkdir(parents=True, exist_ok=True)
        formal_path.write_text(formal_text, encoding="utf-8")
        written_targets.append(
            {
                "id": str(target.get("id") or ""),
                "section_id": str(target.get("section_id") or ""),
                "section_title": str(target.get("section_title") or "未命名章节"),
                "draft_artifact_path": draft_artifact_path,
                "formal_target_path": formal_target_path,
                "previous_exists": previous_exists,
                "write_mode": str(target.get("write_mode") or "candidate_replace_or_create"),
                "written": True,
                "written_at": timestamp,
                "evidence_level": str(target.get("evidence_level") or "verified_source_record"),
            }
        )

    manifest = {
        "schema_version": "p1.formal_writeback_manifest.v1",
        "status": "formal_sections_written",
        "source_task_id": str(task.get("id") or preflight.get("source_task_id") or ""),
        "source_artifact_path": preflight_artifact_path,
        "source_review_gate": "review_formal_writeback_preflight",
        "review": review,
        "formal_layer": "manuscript_sections",
        "target_count": len(targets),
        "written_count": len(written_targets),
        "targets": written_targets,
        "formal_write_allowed": True,
        "writes_formal_layer": True,
        "next_action": "prepare_export_preflight",
        "next_action_label": "准备导出预检",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    absolute_manifest = project_root / manifest_artifact_path
    absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
    absolute_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def build_formal_export_preflight_record(
    task: dict[str, Any],
    manifest: dict[str, Any],
    manifest_artifact_path: str,
    note: str,
    timestamp: str,
    project_root: Path,
    review_path: Path,
) -> dict[str, Any]:
    section_checks = [
        build_formal_export_section_check(target, index, project_root)
        for index, target in enumerate(normalize_list(manifest.get("targets")), start=1)
        if isinstance(target, dict)
    ]
    missing_sections = [check for check in section_checks if not check["exists"]]
    blockers = [
        {
            "code": "formal_section_missing",
            "message": f"正式章节文件缺失：{check['formal_target_path']}",
            "section_id": check["section_id"],
            "formal_target_path": check["formal_target_path"],
        }
        for check in missing_sections
    ]
    agent_followups = [
        {
            "id": f"export_preflight_followup_{index:02d}",
            "owner_agent": "ManuscriptAgent",
            "title": "补齐正式章节文件",
            "description": f"重新生成或恢复正式章节文件：{check['formal_target_path']}",
            "source_section_id": check["section_id"],
            "target_path": check["formal_target_path"],
            "required_before": "formal_pdf_export_preflight",
        }
        for index, check in enumerate(missing_sections, start=1)
    ]
    status = "formal_export_preflight_blocked" if blockers else "formal_export_preflight_ready"
    next_action = "resolve_export_preflight_blockers" if blockers else "run_pdf_export_preflight"
    pandoc_path = shutil.which("pandoc") or ""
    preflight = {
        "schema_version": "p1.agent_task_export_preflight.v1",
        "status": status,
        "source_task_id": str(task.get("id") or manifest.get("source_task_id") or ""),
        "source_artifact_path": manifest_artifact_path,
        "source_review_gate": "review_formal_writeback_preflight",
        "formal_layer": "manuscript_sections",
        "section_count": len(section_checks),
        "missing_section_count": len(missing_sections),
        "section_checks": section_checks,
        "blockers": blockers,
        "agent_followups": agent_followups,
        "targets": {
            "pdf_candidate": "Submissions/formal_package/paper_candidate.pdf",
            "pdf_final": "Submissions/formal_package/paper.pdf",
            "docx": "Submissions/formal_package/paper.docx",
            "preflight_review": str(review_path),
        },
        "toolchain": {
            "pandoc": {
                "available": bool(pandoc_path),
                "path": pandoc_path,
                "blocks_export": False,
                "note": "Pandoc availability is advisory here; PDF/DOCX generation happens in later export gates.",
            }
        },
        "outputs_written": {
            "pdf": False,
            "docx": False,
            "formal_state": False,
        },
        "writes_formal_layer": False,
        "wrote_pdf": False,
        "wrote_docx": False,
        "requires_human_review": False,
        "note": note,
        "next_action": next_action,
        "next_action_label": "处理导出阻断项" if blockers else "运行 PDF 导出预检",
        "usage_boundary": "导出预检只检查正式章节和导出目标，不生成 PDF/DOCX，也不改写正式正文。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    preflight.update(build_export_llm_preflight_provenance(task))
    return preflight


def build_export_llm_preflight_provenance(task: dict[str, Any]) -> dict[str, Any]:
    execution_result = task.get("execution_result") if isinstance(task.get("execution_result"), dict) else {}
    llm_preflight = execution_result.get("llm_execution_preflight")
    if not isinstance(llm_preflight, dict):
        llm_preflight = task.get("llm_execution_preflight")
    if not isinstance(llm_preflight, dict):
        return {}

    provider_snapshot = llm_preflight.get("provider_snapshot")
    if not isinstance(provider_snapshot, dict) or not provider_snapshot:
        return {}

    return {
        "llm_provider_snapshot": provider_snapshot,
        "llm_preflight_summary": str(llm_preflight.get("summary") or ""),
        "llm_preflight_backend_reason": str(llm_preflight.get("backend_reason") or ""),
        "llm_preflight_human_review_note": str(llm_preflight.get("human_review_note") or ""),
        "llm_preflight_artifact_path": str(llm_preflight.get("artifact_path") or ""),
    }


def build_export_llm_preflight_provenance_from_source(source: dict[str, Any]) -> dict[str, Any]:
    provider_snapshot = source.get("llm_provider_snapshot")
    if not isinstance(provider_snapshot, dict) or not provider_snapshot:
        return {}
    return {
        "llm_provider_snapshot": provider_snapshot,
        "llm_preflight_summary": str(source.get("llm_preflight_summary") or ""),
        "llm_preflight_backend_reason": str(source.get("llm_preflight_backend_reason") or ""),
        "llm_preflight_human_review_note": str(source.get("llm_preflight_human_review_note") or ""),
        "llm_preflight_artifact_path": str(source.get("llm_preflight_artifact_path") or ""),
    }


def build_formal_export_section_check(target: dict[str, Any], index: int, project_root: Path) -> dict[str, Any]:
    formal_target_path = str(target.get("formal_target_path") or "")
    absolute_target = project_root / formal_target_path if formal_target_path else None
    exists = bool(absolute_target and absolute_target.exists())
    return {
        "id": f"formal_export_section_check_{index:02d}",
        "section_id": str(target.get("section_id") or f"section_{index:02d}"),
        "section_title": str(target.get("section_title") or "未命名章节"),
        "formal_target_path": formal_target_path,
        "exists": exists,
        "bytes": absolute_target.stat().st_size if absolute_target and absolute_target.exists() else 0,
        "source_draft_artifact_path": str(target.get("draft_artifact_path") or ""),
        "evidence_level": str(target.get("evidence_level") or "verified_source_record"),
    }


def format_formal_export_preflight_review(preflight: dict[str, Any]) -> str:
    blockers = normalize_list(preflight.get("blockers"))
    section_checks = normalize_list(preflight.get("section_checks"))
    llm_provider_snapshot = (
        preflight.get("llm_provider_snapshot") if isinstance(preflight.get("llm_provider_snapshot"), dict) else {}
    )
    primary_provider = (
        llm_provider_snapshot.get("primary_provider")
        if isinstance(llm_provider_snapshot.get("primary_provider"), dict)
        else {}
    )
    selection = llm_provider_snapshot.get("selection") if isinstance(llm_provider_snapshot.get("selection"), dict) else {}
    lines = [
        "# 导出预检台",
        "",
        f"- 状态：{preflight.get('status')}",
        f"- 来源任务：{preflight.get('source_task_id')}",
        f"- 来源清单：{preflight.get('source_artifact_path')}",
        f"- 正式章节：{preflight.get('section_count')} 个",
        f"- 缺失章节：{preflight.get('missing_section_count')} 个",
        f"- 下一步：{preflight.get('next_action_label')}",
        "",
        "## 导出目标",
        f"- PDF 候选：{preflight.get('targets', {}).get('pdf_candidate')}",
        f"- PDF 终稿：{preflight.get('targets', {}).get('pdf_final')}",
        f"- DOCX：{preflight.get('targets', {}).get('docx')}",
        "",
    ]
    if primary_provider:
        lines.extend(
            [
                "## LLM 判断来源",
                f"- Provider：{primary_provider.get('provider_name') or primary_provider.get('provider_id')}",
                f"- Model：{primary_provider.get('model')}",
                f"- 选择来源：{selection.get('source') or 'unknown'}",
                f"- 预检摘要：{preflight.get('llm_preflight_summary') or '未记录'}",
                f"- 人工审阅提示：{preflight.get('llm_preflight_human_review_note') or '未记录'}",
                "",
            ]
        )
    lines.append("## 正式章节检查")
    for check in section_checks:
        if not isinstance(check, dict):
            continue
        status = "存在" if check.get("exists") else "缺失"
        lines.append(f"- {status}｜{check.get('section_title')}｜{check.get('formal_target_path')}")
    lines.extend(["", "## 阻断项"])
    if blockers:
        for blocker in blockers:
            if isinstance(blocker, dict):
                lines.append(f"- {blocker.get('message') or blocker.get('code')}")
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## 边界",
            "- 本预检不会生成 PDF。",
            "- 本预检不会生成 DOCX。",
            "- 本预检不会改写正式论文章节。",
            "",
        ]
    )
    return "\n".join(lines)


def build_pdf_candidate_export_record(
    task: dict[str, Any],
    preflight: dict[str, Any],
    source_preflight_path: str,
    note: str,
    timestamp: str,
    project_root: Path,
    pdf_candidate_path: Path,
    candidate_qmd_path: Path,
    formal_candidate_report_path: Path,
    review_path: Path,
) -> dict[str, Any]:
    section_checks = [check for check in normalize_list(preflight.get("section_checks")) if isinstance(check, dict)]
    sections = [
        build_pdf_candidate_section(section_check, project_root, index)
        for index, section_check in enumerate(section_checks, start=1)
        if section_check.get("exists")
    ]
    export_record = {
        "schema_version": "p1.agent_task_pdf_candidate_export.v1",
        "status": "pdf_candidate_exported",
        "source_task_id": str(task.get("id") or preflight.get("source_task_id") or ""),
        "source_preflight_path": source_preflight_path,
        "pdf_candidate_path": str(pdf_candidate_path),
        "candidate_qmd_path": str(candidate_qmd_path),
        "formal_candidate_report_path": str(formal_candidate_report_path),
        "review_path": str(review_path),
        "section_count": len(sections),
        "sections": sections,
        "outputs_written": {
            "pdf_candidate": True,
            "pdf_final": False,
            "docx": False,
            "formal_state": False,
        },
        "review": {
            "status": "needs_human_review",
            "review_gate": "review_pdf_candidate",
            "required_checks": [
                "章节顺序和标题是否正确",
                "关键表格和图是否有明确占位或引用",
                "引用与复现边界是否清楚",
                "是否允许进入正式 PDF/DOCX 导出",
            ],
        },
        "writes_formal_layer": False,
        "wrote_pdf_candidate": True,
        "wrote_final_pdf": False,
        "wrote_docx": False,
        "note": note,
        "next_action": "review_pdf_candidate",
        "next_action_label": "审阅 PDF 候选稿",
        "usage_boundary": "PDF 候选稿只供人工审阅，不代表最终投稿文件。",
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    export_record.update(build_export_llm_preflight_provenance_from_source(preflight))
    return export_record


def build_formal_pdf_candidate_report_from_queue_export(
    export_record: dict[str, Any],
    source_manifest_path: Path,
    formal_candidate_report_path: Path,
    absolute_pdf_path: Path,
    absolute_qmd_path: Path,
) -> dict[str, Any]:
    report = {
        "schema_version": "p5.formal_pdf_candidate.v1",
        "status": "pdf_candidate_ready",
        "source": "agent_task_queue",
        "source_task_id": export_record.get("source_task_id"),
        "source_preflight_path": export_record.get("source_preflight_path"),
        "source_manifest_path": str(source_manifest_path),
        "artifact_path": str(formal_candidate_report_path),
        "candidate_layer_only": True,
        "output_pdf": export_record.get("pdf_candidate_path"),
        "output_qmd": export_record.get("candidate_qmd_path"),
        "output_pdf_exists": absolute_pdf_path.exists(),
        "output_qmd_exists": absolute_qmd_path.exists(),
        "output_pdf_bytes": absolute_pdf_path.stat().st_size if absolute_pdf_path.exists() else 0,
        "output_qmd_bytes": absolute_qmd_path.stat().st_size if absolute_qmd_path.exists() else 0,
        "section_count": export_record.get("section_count"),
        "sections": [
            {
                "section": section.get("section_title"),
                "section_id": section.get("section_id"),
                "source_path": section.get("formal_target_path"),
                "evidence_level": section.get("evidence_level"),
            }
            for section in normalize_list(export_record.get("sections"))
            if isinstance(section, dict)
        ],
        "render_result": {
            "attempted": True,
            "returncode": 0 if absolute_pdf_path.exists() else 1,
            "renderer": "agent_task_queue_pdf_candidate",
        },
        "formal_state_guard": {"changed": False, "changed_paths": []},
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "next_action": {"id": "review_pdf_candidate", "label": "审阅 PDF 候选稿"},
        "usage_boundary": export_record.get("usage_boundary"),
        "created_at": export_record.get("created_at"),
        "evidence_level": "verified_source_record",
    }
    report.update(build_export_llm_preflight_provenance_from_source(export_record))
    return report


def build_pdf_candidate_review_record(
    task: dict[str, Any],
    export_summary: dict[str, Any],
    candidate_report: dict[str, Any],
    candidate_report_path: str,
    review_report_path: str,
    final_preflight_path: str,
    note: str,
    timestamp: str,
    project_root: Path,
) -> dict[str, Any]:
    candidate_pdf = str(candidate_report.get("output_pdf") or export_summary.get("pdf_candidate_path") or "")
    candidate_qmd = str(candidate_report.get("output_qmd") or export_summary.get("candidate_qmd_path") or "")
    pdf_path = project_root / candidate_pdf if candidate_pdf else None
    qmd_path = project_root / candidate_qmd if candidate_qmd else None
    blocking_reasons: list[str] = []
    blockers: list[dict[str, str]] = []
    if candidate_report.get("schema_version") != "p5.formal_pdf_candidate.v1":
        blocking_reasons.append("candidate_report_schema_mismatch")
    if candidate_report.get("status") != "pdf_candidate_ready":
        blocking_reasons.append("candidate_report_not_ready")
    if candidate_report.get("candidate_layer_only") is not True:
        blocking_reasons.append("candidate_layer_boundary_missing")
    if not pdf_path or not pdf_path.exists():
        blocking_reasons.append("candidate_pdf_missing")
    if not qmd_path or not qmd_path.exists():
        blocking_reasons.append("candidate_qmd_missing")
    if pdf_path and pdf_path.exists() and pdf_path.stat().st_size < 500:
        blocking_reasons.append("candidate_pdf_too_small")
    if (project_root / "Submissions/formal_package/paper.pdf").exists():
        blocking_reasons.append("final_pdf_already_exists")
    if (project_root / "Submissions/formal_package/paper.docx").exists():
        blocking_reasons.append("final_docx_already_exists")

    for reason in blocking_reasons:
        blockers.append({"code": reason, "message": pdf_candidate_review_blocker_message(reason)})

    ready = not blocking_reasons
    review_record = {
        "schema_version": "p5.formal_pdf_candidate_review.v1",
        "status": "ready_for_final_approval_review" if ready else "blocked_by_pdf_candidate_review",
        "source": "agent_task_queue",
        "source_task_id": str(task.get("id") or ""),
        "source_candidate_report": candidate_report_path,
        "artifact_path": review_report_path,
        "final_preflight_path": final_preflight_path,
        "candidate_pdf": candidate_pdf,
        "candidate_qmd": candidate_qmd,
        "candidate_pdf_exists": bool(pdf_path and pdf_path.exists()),
        "candidate_qmd_exists": bool(qmd_path and qmd_path.exists()),
        "candidate_pdf_bytes": pdf_path.stat().st_size if pdf_path and pdf_path.exists() else 0,
        "candidate_qmd_bytes": qmd_path.stat().st_size if qmd_path and qmd_path.exists() else 0,
        "review_checks": [
            {"id": "candidate_pdf_exists", "status": "passed" if pdf_path and pdf_path.exists() else "failed"},
            {"id": "candidate_qmd_exists", "status": "passed" if qmd_path and qmd_path.exists() else "failed"},
            {"id": "candidate_layer_only", "status": "passed" if candidate_report.get("candidate_layer_only") is True else "failed"},
            {"id": "no_final_outputs_written", "status": "passed" if "final_pdf_already_exists" not in blocking_reasons and "final_docx_already_exists" not in blocking_reasons else "failed"},
        ],
        "blocking_reasons": blocking_reasons,
        "blockers": blockers,
        "can_request_final_approval": ready,
        "writes_formal_layer": False,
        "wrote_final_outputs": False,
        "note": note,
        "next_action": {
            "id": "human_review_pdf_candidate" if ready else "repair_pdf_candidate",
            "label": "人工确认 PDF 候选稿" if ready else "修复 PDF 候选稿",
        },
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    review_record.update(build_export_llm_preflight_provenance_from_source(candidate_report))
    return review_record


def build_pdf_candidate_final_writeback_preflight(
    review_record: dict[str, Any],
    review_report_path: str,
    final_preflight_path: str,
    note: str,
    timestamp: str,
) -> dict[str, Any]:
    ready = review_record.get("status") == "ready_for_final_approval_review"
    final_preflight = {
        "schema_version": "p5.formal_pdf_final_writeback_preflight.v1",
        "status": "ready_for_human_final_approval" if ready else "blocked_by_pdf_candidate_review",
        "source": "agent_task_queue",
        "source_review": review_report_path,
        "source_candidate_report": review_record.get("source_candidate_report"),
        "artifact_path": final_preflight_path,
        "candidate_pdf": review_record.get("candidate_pdf"),
        "candidate_qmd": review_record.get("candidate_qmd"),
        "final_pdf": "Submissions/formal_package/paper.pdf",
        "final_docx": "Submissions/formal_package/paper.docx",
        "final_writeback_allowed": False,
        "can_request_final_approval": ready,
        "requires_human_approval": True,
        "can_enter_p6": False,
        "required_before_final_writeback": [
            "human_review_pdf_candidate",
            "formal_pdf_final_approval",
        ],
        "blocking_reasons": normalize_list(review_record.get("blocking_reasons")),
        "formal_state_guard": {
            "changed": False,
            "changed_paths": [],
        },
        "approval_contract": {
            "approval_key": "formal_pdf_candidate",
            "required_action": "approve",
            "writes_formal_layer": False,
            "writes_final_outputs_before_p6": False,
        },
        "note": note,
        "created_at": timestamp,
        "evidence_level": "verified_source_record",
    }
    final_preflight.update(build_export_llm_preflight_provenance_from_source(review_record))
    return final_preflight


def pdf_candidate_review_blocker_message(reason: str) -> str:
    messages = {
        "candidate_report_schema_mismatch": "候选稿报告结构不符合正式审阅链路。",
        "candidate_report_not_ready": "候选稿报告还没有进入可审阅状态。",
        "candidate_layer_boundary_missing": "候选稿没有明确标记为候选层，不能进入最终写回预检。",
        "candidate_pdf_missing": "PDF 候选稿文件缺失。",
        "candidate_qmd_missing": "PDF 候选源码文件缺失。",
        "candidate_pdf_too_small": "PDF 候选稿过小，可能没有真实内容。",
        "final_pdf_already_exists": "候选阶段已经存在最终 PDF，需要先确认来源。",
        "final_docx_already_exists": "候选阶段已经存在最终 DOCX，需要先确认来源。",
    }
    return messages.get(reason, reason)


def build_pdf_candidate_section(section_check: dict[str, Any], project_root: Path, index: int) -> dict[str, Any]:
    formal_target_path = str(section_check.get("formal_target_path") or "")
    section_path = project_root / formal_target_path if formal_target_path else None
    text = section_path.read_text(encoding="utf-8") if section_path and section_path.exists() else ""
    excerpt = " ".join(line.strip() for line in text.splitlines() if line.strip())[:900]
    return {
        "id": f"pdf_candidate_section_{index:02d}",
        "section_id": str(section_check.get("section_id") or f"section_{index:02d}"),
        "section_title": str(section_check.get("section_title") or "未命名章节"),
        "formal_target_path": formal_target_path,
        "bytes": section_check.get("bytes") or len(text.encode("utf-8")),
        "excerpt": excerpt,
        "evidence_level": str(section_check.get("evidence_level") or "verified_source_record"),
    }


def format_pdf_candidate_export_review(export_record: dict[str, Any]) -> str:
    required_checks = normalize_list(export_record.get("review", {}).get("required_checks"))
    llm_provider_snapshot = (
        export_record.get("llm_provider_snapshot")
        if isinstance(export_record.get("llm_provider_snapshot"), dict)
        else {}
    )
    primary_provider = (
        llm_provider_snapshot.get("primary_provider")
        if isinstance(llm_provider_snapshot.get("primary_provider"), dict)
        else {}
    )
    selection = llm_provider_snapshot.get("selection") if isinstance(llm_provider_snapshot.get("selection"), dict) else {}
    lines = [
        "# PDF 候选稿审阅",
        "",
        f"- 状态：{export_record.get('status')}",
        f"- 来源任务：{export_record.get('source_task_id')}",
        f"- 来源预检：{export_record.get('source_preflight_path')}",
        f"- PDF 候选稿：{export_record.get('pdf_candidate_path')}",
        f"- 候选清单：{export_record.get('review_path')}",
        "- 不覆盖终稿：paper.pdf / paper.docx 未写入。",
        "- 正式层：不改写正式论文章节。",
        "",
        "## 人工审阅清单",
    ]
    lines.extend(f"- {item}" for item in required_checks)
    if primary_provider:
        lines.extend(
            [
                "",
                "## LLM 判断来源",
                f"- Provider：{primary_provider.get('provider_name') or primary_provider.get('provider_id')}",
                f"- Model：{primary_provider.get('model')}",
                f"- 选择来源：{selection.get('source') or 'unknown'}",
                f"- 预检摘要：{export_record.get('llm_preflight_summary') or '未记录'}",
                f"- 人工审阅提示：{export_record.get('llm_preflight_human_review_note') or '未记录'}",
            ]
        )
    lines.extend(["", "## 边界", f"- {export_record.get('usage_boundary')}", ""])
    return "\n".join(lines)


def format_pdf_candidate_qmd(export_record: dict[str, Any]) -> str:
    lines = [
        "---",
        'title: "PDF 候选稿"',
        "format: pdf",
        "---",
        "",
        "# PDF 候选稿",
        "",
        "> 这是人工审阅候选稿，不是最终投稿文件。",
        "",
    ]
    for section in normalize_list(export_record.get("sections")):
        if not isinstance(section, dict):
            continue
        lines.extend(
            [
                f"## {section.get('section_title') or '未命名章节'}",
                "",
                str(section.get("excerpt") or ""),
                "",
                f"_来源：{section.get('formal_target_path') or 'unknown'}_",
                "",
            ]
        )
    return "\n".join(lines)


def format_pdf_candidate_review(review_record: dict[str, Any], final_preflight: dict[str, Any]) -> str:
    llm_provider_snapshot = (
        review_record.get("llm_provider_snapshot")
        if isinstance(review_record.get("llm_provider_snapshot"), dict)
        else {}
    )
    primary_provider = (
        llm_provider_snapshot.get("primary_provider")
        if isinstance(llm_provider_snapshot.get("primary_provider"), dict)
        else {}
    )
    selection = llm_provider_snapshot.get("selection") if isinstance(llm_provider_snapshot.get("selection"), dict) else {}
    lines = [
        "# PDF 候选稿机器审阅",
        "",
        f"- 状态：{review_record.get('status')}",
        f"- 来源候选报告：{review_record.get('source_candidate_report')}",
        f"- PDF 候选稿：{review_record.get('candidate_pdf')}",
        f"- QMD 候选源码：{review_record.get('candidate_qmd')}",
        f"- 最终写回预检：{final_preflight.get('artifact_path')}",
        "- 正式层：不写入 paper.pdf / paper.docx。",
        "",
        "## 审阅检查",
    ]
    for check in normalize_list(review_record.get("review_checks")):
        if not isinstance(check, dict):
            continue
        lines.append(f"- {check.get('id')}：{check.get('status')}")
    blockers = normalize_list(review_record.get("blockers"))
    if primary_provider:
        lines.extend(
            [
                "",
                "## LLM 判断来源",
                f"- Provider：{primary_provider.get('provider_name') or primary_provider.get('provider_id')}",
                f"- Model：{primary_provider.get('model')}",
                f"- 选择来源：{selection.get('source') or 'unknown'}",
                f"- 预检摘要：{review_record.get('llm_preflight_summary') or '未记录'}",
                f"- 人工审阅提示：{review_record.get('llm_preflight_human_review_note') or '未记录'}",
            ]
        )
    if blockers:
        lines.extend(["", "## 阻断项"])
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(f"- {blocker.get('message') or blocker.get('code')}")
    else:
        lines.extend(["", "## 下一步", "- 候选稿已进入最终写回预检，等待人工确认是否请求最终 PDF 批准。"])
    return "\n".join(lines)


def write_pdf_candidate_file(path: Path, export_record: dict[str, Any]) -> None:
    lines = [
        "Local Empirical Research OS",
        "PDF 候选稿（人工审阅版）",
        f"状态：{export_record.get('status')}",
        f"来源预检：{export_record.get('source_preflight_path')}",
        f"审阅动作：{export_record.get('next_action')}",
        "边界：只生成候选稿，不写入最终 PDF/DOCX。",
        "",
    ]
    for section in normalize_list(export_record.get("sections")):
        if not isinstance(section, dict):
            continue
        lines.extend(
            [
                str(section.get("section_title") or "Untitled section"),
                str(section.get("formal_target_path") or ""),
                str(section.get("excerpt") or "")[:420],
                "",
            ]
        )
    if len(lines) < 18:
        lines.extend(["正式导出前需要人工审阅。"] * (18 - len(lines)))
    try:
        write_reportlab_pdf_candidate_file(path, lines)
    except Exception:
        path.write_bytes(build_simple_pdf_bytes(lines))


def write_reportlab_pdf_candidate_file(path: Path, lines: list[str]) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    font_name = "SongtiCandidate"
    font_path = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    pdf = canvas.Canvas(str(path), pagesize=A4, pageCompression=0)
    pdf.setTitle("PDF 候选稿（人工审阅版）")
    width, height = A4
    left = 42
    top = height - 52
    line_height = 18
    y = top
    pdf.setFont(font_name, 12)
    for line in lines:
        wrapped = wrap_pdf_line(line, 58)
        for part in wrapped:
            if y < 54:
                pdf.showPage()
                pdf.setFont(font_name, 12)
                y = top
            pdf.drawString(left, y, part)
            y -= line_height
    pdf.setFont(font_name, 9)
    pdf.drawRightString(width - left, 32, "候选稿仅供审阅；通过后再进入正式导出。")
    pdf.save()


def wrap_pdf_line(text: str, limit: int) -> list[str]:
    if not text:
        return [""]
    return [text[index : index + limit] for index in range(0, len(text), limit)]


def build_simple_pdf_bytes(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 13 Tf", "72 748 Td"]
    first_line = True
    for line in lines[:42]:
        if not first_line:
            content_lines.append("0 -17 Td")
        content_lines.append(f"{pdf_literal(line[:96])} Tj")
        first_line = False
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("ascii", errors="ignore")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream",
    ]
    body = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(body)


def pdf_literal(text: str) -> str:
    safe = "".join(ch if 32 <= ord(ch) <= 126 else "?" for ch in text)
    safe = safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"({safe})"


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
