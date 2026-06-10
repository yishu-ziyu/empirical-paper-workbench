from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from Product.backend.codex_provider import local_codex_status
from Product.backend.project_service import project_api_view, register_project_root, utc_now
from Product.backend.research_question_service import save_current_research_question
from Product.backend.supervisor_plan_service import (
    build_default_reference_chain_policy,
    load_saved_supervisor_plan,
    normalize_supervisor_plan,
    supervisor_plan_state_path,
)


TOPIC_WORKSPACE_ROOT = Path("workspaces")


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
    provider = local_codex_status()
    generated = build_topic_intake_supervisor_generated(normalized_topic)
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
            "evidence_level": "topic_intake",
            "next_action": {
                "id": "review_supervisor_plan",
                "label": "审阅路线后创建 Agent Task Queue",
            },
        }
    )
    plan["decision_events"] = [
        *plan.get("decision_events", []),
        {
            "actor": "product_workbench",
            "action": "topic_intake_supervisor_plan",
            "timestamp": timestamp,
            "note": "题目已登记为本地项目，SupervisorPlan 等待人工审阅。",
        },
    ]

    path = supervisor_plan_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "_meta": {
            "evidence_level": "topic_intake",
            "service": "topic_intake_service",
            "generated_at": timestamp,
        },
        "project": project_api_view(project),
        "research_question": research_question,
        "supervisor_plan": plan,
    }


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


def build_topic_intake_supervisor_generated(topic: str) -> dict[str, Any]:
    reference_policy = build_default_reference_chain_policy()
    return {
        "stage_plan": [
            {
                "id": "task-brief",
                "title": "确认研究题目和边界",
                "owner": "Supervisor",
                "status": "ready",
                "reason": "先固定题目、对象、数据线索和成功标准，避免后续 Agent 自行改题。",
                "inputs": ["用户输入题目", "补充说明", "本地项目状态"],
                "outputs": ["ResearchQuestion", "TaskBrief", "边界条件清单"],
            },
            {
                "id": "recursive-evidence-search",
                "title": "递归搜索文献、变量和数据线索",
                "owner": "LiteratureAgent",
                "status": "draft",
                "reason": "题目需要先连接文献脉络、可用数据、候选变量和缺失证据，再决定方法路线。",
                "inputs": ["ResearchQuestion", "CNKI/Scholar/Zotero/本地笔记来源策略"],
                "outputs": ["LiteratureSeedPackage", "search_query_graph", "citation_verification_queue"],
            },
            {
                "id": "data-variable-profile",
                "title": "建立数据与变量画像",
                "owner": "DataAgent",
                "status": "draft",
                "reason": "变量角色必须由真实字段、样本口径和缺失情况支撑。",
                "inputs": ["候选数据源", "字段字典", "文献变量定义"],
                "outputs": ["VariableRoleSet 草案", "字段质量报告", "缺失证据清单"],
            },
            {
                "id": "method-design-gates",
                "title": "设计方法门和前置检验",
                "owner": "MethodAgent",
                "status": "empty",
                "reason": "根据数据结构和文献规范选择 OLS/FE/DID/IV/RDD/PSM/DML 等方法门。",
                "inputs": ["VariableRoleSet 草案", "样本结构", "目标期刊规范"],
                "outputs": ["DesignSpec 草案", "方法前置条件", "稳健性任务清单"],
            },
            {
                "id": "execution-preflight",
                "title": "执行预检与草案产物路线",
                "owner": "ExecutionAgent",
                "status": "empty",
                "reason": "真实跑码前先确认环境、后端、产物目录和审计链。",
                "inputs": ["DesignSpec 草案", "本地后端状态", "可复现目录结构"],
                "outputs": ["RunPlan 草案", "preflight_report", "artifact_manifest"],
            },
        ],
        "subagent_dispatch": [
            {
                "agent_id": "LiteratureAgent",
                "role": "LiteratureAgent",
                "task": "递归检索题目的文献、变量定义、数据线索和缺失证据",
                "summary": "用递归研究搜索把题目连接到文献、数据、方法和下一轮缺口。",
                "output_requirements": [
                    {"artifact": "LiteratureSeedPackage", "review_state": "needs_human_review"},
                    {"artifact": "search_query_graph", "review_state": "draft"},
                    {"artifact": "citation_verification_queue", "review_state": "needs_human_review"},
                ],
            },
            {
                "agent_id": "DataAgent",
                "role": "DataAgent",
                "task": "根据题目和文献线索建立候选数据与变量画像",
                "summary": "只生成 VariableRoleSet 草案，不写入正式变量角色。",
                "output_requirements": [
                    {"artifact": "VariableProfileDraft", "review_state": "draft"},
                    {"artifact": "missing_data_evidence_queue", "review_state": "needs_human_review"},
                ],
            },
            {
                "agent_id": "MethodAgent",
                "role": "MethodAgent",
                "task": "基于变量画像和研究问题提出方法门与前置检验",
                "summary": "给出 DesignSpec 草案和方法规范门，不直接启动回归。",
                "output_requirements": [
                    {"artifact": "DesignSpecDraft", "review_state": "draft"},
                    {"artifact": "method_gate_checklist", "review_state": "needs_human_review"},
                ],
            },
            {
                "agent_id": "ExecutionAgent",
                "role": "ExecutionAgent",
                "task": "准备执行预检、产物目录和可复现包约束",
                "summary": "检查后端与目录，不改写正式 RunPlan。",
                "output_requirements": [
                    {"artifact": "PreflightReport", "review_state": "draft"},
                    {"artifact": "ArtifactManifestDraft", "review_state": "draft"},
                ],
            },
        ],
        "evidence_requirements": [
            "题目中的核心概念需要被文献或用户说明界定。",
            "变量角色需要绑定真实字段、样本口径、时间范围和缺失率。",
            "方法设计需要说明前置假设、诊断检验和失败时的降级路线。",
            "引用进入正式综述前必须经过候选、核验、人工确认三态。",
        ],
        "risks": [
            "题目可能需要外部数据或中文文献补证，不能只依赖当前空项目目录。",
            "变量自动选择只能进入草案层，正式变量角色需要人工确认。",
            "方法门必须等待数据结构画像，不能提前承诺因果识别。",
        ],
        "human_gates": [
            "审阅 SupervisorPlan 后创建 Agent Task Queue。",
            "审阅 LiteratureSeedPackage 后进入草稿综述。",
            "审阅 VariableRoleSet 草案后写入正式变量角色。",
            "审阅 DesignSpec 和 RunPlan 后开始真实执行。",
        ],
        "internal_skill_judgments": [
            {
                "skill_id": "recursive_research_search",
                "reason": "用户从题目出发，需要系统沿着题目、文献、变量、数据、方法和缺失证据做递归扩展。",
                "evidence_fit": "第一轮证据不足时，递归搜索能把缺失文献、候选变量和数据线索转成下一轮任务。",
                "agent_fit": "LiteratureAgent 负责主搜索，DataAgent 和 MethodAgent 消化变量和方法缺口。",
                "risk_note": "搜索结果只能进入候选证据和草案层，不直接写入正式综述。",
                "human_review_note": "引用核验、中文文献补证和正式写回必须由用户确认。",
                "confidence": "high",
            }
        ],
        "reference_chain_policy": reference_policy,
        "next_action": {
            "id": "review_supervisor_plan",
            "label": "审阅路线后创建 Agent Task Queue",
        },
    }
