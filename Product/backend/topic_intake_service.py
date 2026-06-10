from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import yaml

from Product.backend import llm_client
from Product.backend.project_service import project_api_view, register_project_root, utc_now
from Product.backend.research_question_service import save_current_research_question
from Product.backend.internal_agent_skill_registry import compact_internal_agent_skills_for_prompt
from Product.backend.supervisor_plan_service import (
    SupervisorPlanExecutionError,
    build_default_reference_chain_policy,
    load_saved_supervisor_plan,
    normalize_supervisor_plan,
    parse_supervisor_plan_output,
    supervisor_plan_raw_path,
    supervisor_plan_state_path,
)


TOPIC_WORKSPACE_ROOT = Path("workspaces")
TOPIC_INTAKE_LLM_TIMEOUT_SECONDS = int(os.getenv("EMPIRICAL_TOPIC_INTAKE_LLM_TIMEOUT_SECONDS", "30"))


class TopicIntakeLLMUnavailableError(RuntimeError):
    """Raised when topic intake cannot obtain a real LLM Supervisor plan."""


def ensure_topic_supervisor_plan(
    product_root: Path,
    repo_root: Path,
    topic: str,
    slug: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("Research topic cannot be empty.")

    normalized_slug = normalize_topic_slug(normalized_topic, slug)
    project_root = ensure_topic_project_root(product_root, normalized_slug, normalized_topic)
    project = register_project_root(
        product_root,
        repo_root,
        normalized_slug,
        normalized_topic,
        project_root,
        "zh",
    )
    research_question = save_current_research_question(
        product_root,
        repo_root,
        project["id"],
        normalized_topic,
        "user_input",
        note or "用户从研究入口登记题目。",
    )["research_question"]

    existing = load_saved_supervisor_plan(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    timestamp = utc_now()
    messages = build_topic_intake_supervisor_messages(
        project,
        research_question,
        normalized_topic,
        note,
    )
    try:
        raw_text, provider = llm_client.chat_completion_with_fallback(
            messages,
            temperature=0.2,
            timeout_seconds=TOPIC_INTAKE_LLM_TIMEOUT_SECONDS,
        )
        generated = parse_supervisor_plan_output(raw_text)
    except llm_client.LLMError as exc:
        return persist_topic_fallback_supervisor_plan(
            product_root,
            repo_root,
            project,
            project_root,
            research_question,
            normalized_topic,
            note,
            version,
            timestamp,
            str(exc.code),
            f"LLM Supervisor 未接通：{exc.code}。请检查本地模型或云端 provider 配置。",
        )
    except (SupervisorPlanExecutionError, json.JSONDecodeError, TypeError) as exc:
        return persist_topic_fallback_supervisor_plan(
            product_root,
            repo_root,
            project,
            project_root,
            research_question,
            normalized_topic,
            note,
            version,
            timestamp,
            "llm_plan_parse_failed",
            "LLM Supervisor 返回的研究计划无法解析。请重试或切换模型。",
        )
    if not isinstance(generated, dict):
        return persist_topic_fallback_supervisor_plan(
            product_root,
            repo_root,
            project,
            project_root,
            research_question,
            normalized_topic,
            note,
            version,
            timestamp,
            "llm_plan_not_object",
            "LLM Supervisor 返回的研究计划不是 JSON 对象。请重试或切换模型。",
        )

    raw_path = supervisor_plan_raw_path(project_root)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw_text, encoding="utf-8")

    plan = normalize_supervisor_plan(
        generated,
        project,
        f"围绕题目生成可审阅研究执行计划：{normalized_topic}",
        note or "题目进入产品主链路，先生成任务路线和 Agent 分工草案。",
        provider,
        research_question,
        build_empty_state("variable_roles"),
        build_empty_state("design_spec"),
        build_empty_state("run_plan"),
        version,
        timestamp,
    )
    plan.update(
        {
            "status": "needs_review",
            "can_dispatch": False,
            "intake_mode": "topic_to_project",
            "evidence_level": "llm_supervisor",
            "next_action": {
                "id": "review_supervisor_plan",
                "label": "审阅路线后创建 Agent Task Queue",
            },
        }
    )
    plan["decision_events"] = [
        *plan.get("decision_events", []),
        {
            "actor": "llm_supervisor",
            "action": "topic_intake_supervisor_plan",
            "timestamp": timestamp,
            "note": "题目已登记为本地项目，LLM Supervisor 已生成可审阅研究路线。",
        },
    ]

    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "_meta": {
            "evidence_level": "llm_supervisor",
            "service": "topic_intake_service",
            "llm_provider": provider,
            "generated_at": timestamp,
        },
        "project": project_api_view(project),
        "research_question": research_question,
        "supervisor_plan": plan,
    }


def persist_topic_preview_supervisor_plan(
    product_root: Path,
    repo_root: Path,
    topic: str,
    preview_plan: dict[str, Any],
    slug: str | None = None,
    note: str = "",
) -> dict[str, Any]:
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("Research topic cannot be empty.")

    normalized_slug = normalize_topic_slug(normalized_topic, slug)
    project_root = ensure_topic_project_root(product_root, normalized_slug, normalized_topic)
    project = register_project_root(
        product_root,
        repo_root,
        normalized_slug,
        normalized_topic,
        project_root,
        "zh",
    )
    research_question = save_current_research_question(
        product_root,
        repo_root,
        project["id"],
        normalized_topic,
        "user_input",
        note or "用户从研究入口登记题目。",
    )["research_question"]

    existing = load_saved_supervisor_plan(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    timestamp = utc_now()
    provider = {
        "provider_id": "review_surface",
        "provider_name": "SupervisorPlan review surface",
        "model": "current_preview",
        "api_type": "local_state",
    }
    generated = build_topic_preview_supervisor_plan(normalized_topic, preview_plan)
    plan = normalize_supervisor_plan(
        generated,
        project,
        f"围绕题目保存当前可审阅研究执行计划：{normalized_topic}",
        note or "用户已查看当前 SupervisorPlan 预览，批准前先落盘为项目级计划。",
        provider,
        research_question,
        build_empty_state("variable_roles"),
        build_empty_state("design_spec"),
        build_empty_state("run_plan"),
        version,
        timestamp,
    )
    plan.update(
        {
            "status": "needs_review",
            "can_dispatch": False,
            "intake_mode": "topic_to_project_preview",
            "evidence_level": "review_surface",
            "next_action": {
                "id": "review_supervisor_plan",
                "label": "审阅路线后创建 Agent Task Queue",
            },
        }
    )
    plan["decision_events"] = [
        *plan.get("decision_events", []),
        {
            "actor": "user",
            "action": "topic_preview_supervisor_plan_persisted",
            "timestamp": timestamp,
            "note": "当前审阅页 SupervisorPlan 已保存为项目级计划，未重新等待 LLM 生成。",
        },
    ]

    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "_meta": {
            "evidence_level": "review_surface",
            "service": "topic_intake_service",
            "llm_provider": provider,
            "generated_at": timestamp,
        },
        "project": project_api_view(project),
        "research_question": research_question,
        "supervisor_plan": plan,
    }


def build_topic_preview_supervisor_plan(topic: str, preview_plan: dict[str, Any]) -> dict[str, Any]:
    stage_plan = normalize_preview_stage_plan(preview_plan.get("stage_plan") or preview_plan.get("stages"))
    if not stage_plan:
        stage_plan = build_topic_fallback_supervisor_plan(topic, "当前预览计划缺少阶段树。")["stage_plan"]
    subagent_dispatch = normalize_preview_subagent_dispatch(
        preview_plan.get("subagent_dispatch"),
        stage_plan,
    )
    return {
        "stage_plan": stage_plan,
        "subagent_dispatch": subagent_dispatch,
        "evidence_requirements": normalize_string_list(
            preview_plan.get("evidence_requirements") or preview_plan.get("evidence_required")
        )
        or [
            "研究题目、证据要求、风险和派工顺序必须先保存为可审阅计划。",
            "变量、设计和运行计划必须等待后续人工确认。",
        ],
        "risks": normalize_string_list(preview_plan.get("risks"))
        or [
            "当前计划来自审阅页预览，尚未进入变量和方法正式层。",
            "创建队列后仍需逐项审阅 Agent 输出。",
        ],
        "human_gates": normalize_string_list(preview_plan.get("human_gates"))
        or [
            "用户批准 SupervisorPlan 后才能创建 Agent Task Queue。",
            "变量角色、方法设计和真实执行仍需后续确认。",
        ],
        "internal_skill_judgments": normalize_preview_internal_skill_judgments(
            preview_plan.get("internal_skill_judgments")
        ),
        "reference_chain_policy": preview_plan.get("reference_chain_policy")
        or build_default_reference_chain_policy(),
        "next_action": {
            "id": "review_supervisor_plan",
            "label": "审阅路线后创建 Agent Task Queue",
        },
    }


def normalize_preview_stage_plan(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    stages: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("task") or f"阶段 {index + 1}")
        owner = str(item.get("owner") or item.get("owner_agent") or item.get("role") or "Supervisor")
        stages.append(
            {
                "id": str(item.get("id") or f"stage-{index + 1}"),
                "title": title,
                "owner": owner,
                "status": str(item.get("status") or "draft"),
                "reason": str(item.get("reason") or item.get("summary") or "等待审阅后进入下一步。"),
                "inputs": normalize_string_list(item.get("inputs")),
                "outputs": normalize_string_list(item.get("outputs")),
            }
        )
    return stages


def normalize_preview_subagent_dispatch(value: Any, stage_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(value, list):
        normalized = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or item.get("owner") or f"Agent{index + 1}")
            normalized.append(
                {
                    "agent_id": str(item.get("agent_id") or role.lower()),
                    "role": role,
                    "task": str(item.get("task") or item.get("title") or "执行计划中的对应任务。"),
                    "summary": str(item.get("summary") or item.get("reason") or "来自当前 SupervisorPlan 预览。"),
                }
            )
        if normalized:
            return normalized

    dispatch: list[dict[str, Any]] = []
    seen: set[str] = set()
    for stage in stage_plan:
        owner = str(stage.get("owner") or "Supervisor")
        if owner in seen:
            continue
        seen.add(owner)
        dispatch.append(
            {
                "agent_id": re.sub(r"[^a-z0-9]+", "_", owner.lower()).strip("_") or "supervisor",
                "role": owner,
                "task": str(stage.get("title") or "执行计划中的对应任务。"),
                "summary": str(stage.get("reason") or "来自当前 SupervisorPlan 预览。"),
            }
        )
    return dispatch


def normalize_preview_internal_skill_judgments(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list) and value:
        return [item for item in value if isinstance(item, dict)]
    return [
        {
            "skill_id": "recursive_research_search",
            "reason": "题目进入队列前需要把研究问题、文献、变量、数据和方法缺口串起来。",
            "evidence_fit": "先生成候选证据包，再进入变量角色和方法门。",
            "agent_fit": "LiteratureAgent、DataAgent 和 MethodAgent 可以分工处理。",
            "risk_note": "当前只作为任务队列的草案层技能绑定。",
            "human_review_note": "正式变量、方法和论文层写回前必须人工确认。",
            "confidence": "medium",
        }
    ]


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def persist_topic_fallback_supervisor_plan(
    product_root: Path,
    repo_root: Path,
    project: dict[str, Any],
    project_root: Path,
    research_question: dict[str, Any],
    topic: str,
    note: str,
    version: int,
    timestamp: str,
    failure_code: str,
    failure_message: str,
) -> dict[str, Any]:
    llm_enrichment = {
        "status": "failed",
        "retryable": True,
        "failure_code": failure_code,
        "message": failure_message,
        "next_action": {
            "id": "retry_llm_supervisor_plan",
            "label": "重试 LLM Supervisor 增强计划",
        },
    }
    provider = {
        "provider_id": "unavailable",
        "provider_name": "LLM Supervisor unavailable",
        "model": "",
        "api_type": "none",
        "failure_code": failure_code,
    }
    generated = build_topic_fallback_supervisor_plan(topic, failure_message)
    plan = normalize_supervisor_plan(
        generated,
        project,
        f"围绕题目生成可审阅研究执行计划：{topic}",
        note or "题目已登记；LLM Supervisor 暂时不可用，先生成可重试 fallback 计划。",
        provider,
        research_question,
        build_empty_state("variable_roles"),
        build_empty_state("design_spec"),
        build_empty_state("run_plan"),
        version,
        timestamp,
    )
    plan.update(
        {
            "status": "needs_review",
            "can_dispatch": False,
            "intake_mode": "topic_to_project",
            "evidence_level": "topic_intake_fallback",
            "llm_enrichment": llm_enrichment,
            "next_action": {
                "id": "review_or_retry_supervisor_plan",
                "label": "审阅 fallback 路线或重试 LLM Supervisor",
            },
        }
    )
    plan["decision_events"] = [
        *plan.get("decision_events", []),
        {
            "actor": "system",
            "action": "topic_intake_fallback_supervisor_plan",
            "timestamp": timestamp,
            "note": failure_message,
        },
    ]

    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "_meta": {
            "evidence_level": "topic_intake_fallback",
            "service": "topic_intake_service",
            "llm_provider": provider,
            "llm_enrichment": llm_enrichment,
            "generated_at": timestamp,
        },
        "project": project_api_view(project),
        "research_question": research_question,
        "supervisor_plan": plan,
    }


def build_topic_fallback_supervisor_plan(topic: str, failure_message: str) -> dict[str, Any]:
    return {
        "stage_plan": [
            {
                "id": "task-brief",
                "title": "确认研究题目与边界",
                "owner": "Supervisor",
                "status": "needs_review",
                "reason": f"先把题目登记为项目，并确认研究对象、样本范围和成功标准：{topic}",
                "inputs": ["用户题目"],
                "outputs": ["ResearchQuestion", "TaskBrief"],
            },
            {
                "id": "recursive-search",
                "title": "递归搜索文献、变量和数据线索",
                "owner": "LiteratureAgent",
                "status": "blocked_by_llm_retry",
                "reason": "需要 LLM Supervisor 恢复后，把题目拆成检索词、核心文献、变量证据和数据候选。",
                "inputs": ["ResearchQuestion", "InternalSkillRegistry"],
                "outputs": ["LiteratureSeedPackage", "SearchQueryGraph"],
            },
            {
                "id": "variable-profile",
                "title": "建立变量画像草案",
                "owner": "DataAgent",
                "status": "locked_until_evidence",
                "reason": "变量角色必须绑定真实数据字段和文献依据，当前只保留任务占位。",
                "inputs": ["LiteratureSeedPackage", "DatasetCandidate"],
                "outputs": ["VariableRoleSet 草案"],
            },
            {
                "id": "method-gate",
                "title": "进入方法规范门",
                "owner": "MethodAgent",
                "status": "locked_until_variable_review",
                "reason": "方法选择需要依赖变量角色、样本结构和识别风险，不在题目登记阶段写入正式方案。",
                "inputs": ["VariableRoleSet 草案", "ResearchQuestion"],
                "outputs": ["DesignSpec 草案"],
            },
        ],
        "subagent_dispatch": [
            {
                "agent_id": "supervisor_route",
                "role": "Supervisor",
                "task": "重试 LLM Supervisor，并把 fallback 计划升级为语义计划。",
                "summary": failure_message,
            },
            {
                "agent_id": "literature_recursive_search",
                "role": "LiteratureAgent",
                "task": "围绕题目准备文献、数据线索和变量证据的递归搜索任务。",
                "summary": "只生成候选证据，不写入正式层。",
            },
            {
                "agent_id": "data_variable_profile",
                "role": "DataAgent",
                "task": "等待数据绑定后生成变量画像草案。",
                "summary": "变量角色需要人工审阅后才能进入正式状态。",
            },
        ],
        "evidence_requirements": [
            "研究题目必须拆成研究对象、解释变量、结果变量、样本范围和时间范围。",
            "变量角色必须有真实数据字段、字段含义、缺失率和文献依据。",
            "方法设计必须说明识别假设、内生性风险和必要稳健性检验。",
        ],
        "risks": [
            "LLM Supervisor 本轮未完成语义增强，当前计划只能作为入口和任务占位。",
            "尚未读取数据，不能把任何变量、模型或结论写入正式层。",
            "文献与引用尚未核验，不能生成正式文献综述。",
        ],
        "human_gates": [
            "确认题目和研究边界。",
            "重试 LLM Supervisor 或人工批准 fallback 路线进入任务队列。",
            "确认变量角色和方法设计后再允许真实执行。",
        ],
        "internal_skill_judgments": [
            {
                "skill_id": "recursive_research_search",
                "reason": "题目登记后下一步需要从研究问题递归展开文献、变量、数据和方法证据。",
                "evidence_fit": "当前只有题目，适合先形成可审阅的搜索图和证据缺口。",
                "agent_fit": "LiteratureAgent、DataAgent 和 MethodAgent 可以围绕同一证据链分工。",
                "risk_note": "LLM 未完成增强前，该 skill 只进入草案层和任务队列占位。",
                "human_review_note": "人工确认后才能把候选证据写入正式变量或方法状态。",
                "confidence": "medium",
            }
        ],
        "reference_chain_policy": {
            "source_priority": ["CNKI", "Google Scholar", "Zotero", "Local Notes", "Dataset Files"],
            "sources": [
                {"id": "CNKI", "label": "中国知网", "trigger": "中文实证文献", "mode": "manual_assisted"},
                {"id": "Google Scholar", "label": "Google Scholar", "trigger": "英文文献", "mode": "browser_assisted"},
                {"id": "Dataset Files", "label": "本地数据文件", "trigger": "变量字段和样本结构", "mode": "local_file"},
            ],
            "max_depth": 2,
            "max_iterations": 5,
            "draft_citation_policy": "候选引用必须标记为 draft，正式层写回前需要 DOI/来源核验。",
            "formal_writeback_gate": "human_review_required",
            "writes_formal_layer": False,
        },
        "next_action": {
            "id": "review_or_retry_supervisor_plan",
            "label": "审阅 fallback 路线或重试 LLM Supervisor",
        },
    }


def build_topic_intake_supervisor_messages(
    project: dict[str, Any],
    research_question: dict[str, Any],
    topic: str,
    note: str,
) -> list[dict[str, str]]:
    context = {
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "topic": topic,
        "note": note,
        "research_question": {
            "status": research_question.get("status"),
            "question": research_question.get("question"),
            "source": research_question.get("source"),
        },
        "internal_skill_registry": compact_internal_agent_skills_for_prompt(),
        "reference_chain_policy_template": build_default_reference_chain_policy(),
        "write_boundary": {
            "may_write": ["ResearchQuestion", "SupervisorPlan draft", "AgentTaskQueue after human review"],
            "must_not_write": ["VariableRoleSet", "DesignSpec", "RunPlan", "formal manuscript layer"],
        },
    }
    system = (
        "你是本地实证研究 OS 的 LLM Supervisor。你的任务是根据用户题目生成可审阅的研究路线、"
        "证据要求、风险、Agent 分工和内部 skill 选择理由。"
        "你必须围绕用户真实题目判断，不得复用固定案例，不得声称已经读取数据或完成分析。"
    )
    user = (
        "只输出 JSON，不要输出 Markdown。JSON 必须包含：stage_plan、subagent_dispatch、"
        "evidence_requirements、risks、human_gates、internal_skill_judgments、"
        "reference_chain_policy、next_action。\n"
        "internal_skill_judgments 必须解释为什么选择某个 skill，并且 skill_id 必须来自 "
        "internal_skill_registry.skills。每项包含 reason、evidence_fit、agent_fit、"
        "risk_note、human_review_note、confidence。\n"
        "reference_chain_policy 必须包含 source_priority、sources、max_depth、max_iterations、"
        "draft_citation_policy、formal_writeback_gate、writes_formal_layer；writes_formal_layer 必须为 false。\n"
        "stage_plan 至少 4 段，subagent_dispatch 至少 3 个 Agent。"
        "所有判断必须使用题目语义、证据缺口和方法风险，不能写入正式变量、设计或运行计划。\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def normalize_topic_slug(topic: str, slug: str | None = None) -> str:
    raw = (slug or "").strip() or topic
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", raw.lower()).strip("-")
    if normalized:
        return normalized[:64]
    digest = hashlib.sha1(topic.encode("utf-8")).hexdigest()[:10]
    return f"topic-{digest}"


def ensure_topic_project_root(product_root: Path, slug: str, topic: str) -> Path:
    project_root = (product_root / TOPIC_WORKSPACE_ROOT / slug).resolve()
    for rel in (
        "Data/Final",
        "Program",
        "Manuscripts/generated",
        "Reference",
        "Results/json",
        "Results/logs",
        "Submissions",
        "Tasks",
        "docs",
        "state/product",
    ):
        (project_root / rel).mkdir(parents=True, exist_ok=True)

    paper_payload = {
        "project": {
            "slug": slug,
            "title": topic,
            "language": "zh",
        },
        "research": {
            "question": topic,
            "status": "topic_intake",
            "source": "user_input",
        },
        "data": {
            "final_dataset": "Data/Final/analysis_sample.csv",
            "status": "not_bound",
        },
        "workflow": {
            "entry": "topic_intake",
            "writes_formal_layer": False,
        },
    }
    (project_root / "paper.yaml").write_text(
        yaml.safe_dump(paper_payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    runner_path = project_root / "Program" / "run_paper.py"
    if not runner_path.exists():
        runner_path.write_text(
            "\n".join(
                [
                    "from __future__ import annotations",
                    "",
                    "import json",
                    "from pathlib import Path",
                    "",
                    "",
                    "def main() -> None:",
                    "    root = Path(__file__).resolve().parents[1]",
                    "    output = root / 'Results' / 'json' / 'topic_intake_run.json'",
                    "    output.parent.mkdir(parents=True, exist_ok=True)",
                    "    output.write_text(json.dumps({'status': 'topic_intake_only'}, ensure_ascii=False, indent=2), encoding='utf-8')",
                    "",
                    "",
                    "if __name__ == '__main__':",
                    "    main()",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    readme_path = project_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            f"# {topic}\n\n这个目录由题目登记入口创建。正式变量、方法和运行计划需要人工确认后写入。\n",
            encoding="utf-8",
        )

    return project_root


def build_empty_state(state_id: str) -> dict[str, Any]:
    return {
        "id": state_id,
        "version": 0,
        "status": "empty",
        "evidence_level": "none",
    }
