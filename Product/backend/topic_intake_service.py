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
        raise TopicIntakeLLMUnavailableError(
            f"LLM Supervisor 未接通：{exc.code}。请检查本地模型或云端 provider 配置。"
        ) from exc
    except (SupervisorPlanExecutionError, json.JSONDecodeError, TypeError) as exc:
        raise TopicIntakeLLMUnavailableError(
            "LLM Supervisor 返回的研究计划无法解析。请重试或切换模型。"
        ) from exc
    if not isinstance(generated, dict):
        raise TopicIntakeLLMUnavailableError("LLM Supervisor 返回的研究计划不是 JSON 对象。")

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
