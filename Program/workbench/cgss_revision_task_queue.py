from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_revision_task_queue.v1"
DEFAULT_LITERATURE_SEED_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_literature_seed_package.json")
DEFAULT_LITERATURE_REVIEW_PACKET_PATH = Path(
    "Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json"
)
DEFAULT_METHOD_STRUCTURE_GATE_PACKET_PATH = Path(
    "Results/json/cgss_social_capital_happiness_method_structure_gate_packet.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_revision_task_queue.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_revision_task_queue(
    literature_seed_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
    method_structure_gate_packet: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    topic = (
        literature_seed_package.get("topic")
        or literature_review_packet.get("topic")
        or method_structure_gate_packet.get("topic")
        or ""
    )
    queue = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_artifacts": build_source_artifacts(
            literature_seed_package,
            literature_review_packet,
            method_structure_gate_packet,
            source_paths,
        ),
        "boundary_flags": {
            "wrote_formal_manuscript": False,
            "wrote_state_product": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "wrote_agent_task_queue_json": False,
        },
    }

    blocking_reasons = input_blocking_reasons(
        literature_seed_package,
        literature_review_packet,
        method_structure_gate_packet,
    )
    if blocking_reasons:
        queue.update(
            {
                "status": "blocked_missing_revision_inputs",
                "blocking_reasons": blocking_reasons,
                "agent_packets": [],
                "agent_task_queue": [],
                "promotion": {
                    "allowed": False,
                    "required_decision": "repair_revision_input_packets",
                },
            }
        )
        return queue

    agent_packets = [
        build_literature_agent_packet(literature_seed_package, literature_review_packet),
        build_method_agent_packet(method_structure_gate_packet),
        build_writer_agent_packet(literature_review_packet, method_structure_gate_packet),
        build_reviewer_agent_packet(literature_seed_package, literature_review_packet, method_structure_gate_packet),
    ]
    queue.update(
        {
            "status": "needs_human_revision_queue_approval",
            "blocking_reasons": ["revision_queue_needs_human_approval"],
            "agent_packets": agent_packets,
            "agent_task_queue": [task for packet in agent_packets for task in packet["tasks"]],
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_cgss_revision_task_queue",
                "would_enable": [
                    "agent_draft_review_packets",
                    "human_reviewer_round",
                    "draft_section_revision_briefs",
                ],
            },
        }
    )
    return queue


def build_source_artifacts(
    literature_seed_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
    method_structure_gate_packet: dict[str, Any],
    source_paths: dict[str, str],
) -> dict[str, dict[str, str]]:
    return {
        "literature_seed_package": {
            "path": source_paths.get("literature_seed_package", str(DEFAULT_LITERATURE_SEED_PACKAGE_PATH)),
            "schema_version": literature_seed_package.get("schema_version", ""),
            "status": literature_seed_package.get("status", ""),
        },
        "literature_review_draft_packet": {
            "path": source_paths.get("literature_review_packet", str(DEFAULT_LITERATURE_REVIEW_PACKET_PATH)),
            "schema_version": literature_review_packet.get("schema_version", ""),
            "status": literature_review_packet.get("status", ""),
        },
        "method_structure_gate_packet": {
            "path": source_paths.get("method_structure_gate_packet", str(DEFAULT_METHOD_STRUCTURE_GATE_PACKET_PATH)),
            "schema_version": method_structure_gate_packet.get("schema_version", ""),
            "status": method_structure_gate_packet.get("status", ""),
        },
    }


def input_blocking_reasons(
    literature_seed_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
    method_structure_gate_packet: dict[str, Any],
) -> list[str]:
    reasons = []
    if literature_seed_package.get("status") != "needs_human_literature_review":
        reasons.append("literature_seed_package_not_ready")
    if not literature_seed_package.get("seed_sources"):
        reasons.append("literature_seed_sources_missing")
    if literature_review_packet.get("status") != "needs_human_literature_review_draft_approval":
        reasons.append("literature_review_draft_packet_not_ready")
    if not literature_review_packet.get("paragraph_blocks"):
        reasons.append("literature_review_paragraph_blocks_missing")
    if method_structure_gate_packet.get("status") != "needs_human_method_structure_approval":
        reasons.append("method_structure_gate_packet_not_ready")
    if not method_structure_gate_packet.get("method_claim_gates"):
        reasons.append("method_claim_gates_missing")
    return reasons


def build_literature_agent_packet(
    literature_seed_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
) -> dict[str, Any]:
    open_dependencies = literature_review_packet.get("open_dependencies", [])
    paragraph_blocks = literature_review_packet.get("paragraph_blocks", [])
    tasks = [
        make_task(
            "literature.verify_open_seed_sources",
            "LiteratureAgent",
            "核验未批准文献与 CGSS 官方来源",
            "逐条处理 open dependency，补齐访问日期、DOI/Zotero 元数据和中文文献人工核验结论。",
            ["literature_seed_package.seed_sources", "literature_review_draft_packet.open_dependencies"],
            "Reviews/agent_packets/literatureagent/cgss_source_verification.md",
        ),
        make_task(
            "literature.revise_review_blocks",
            "LiteratureAgent",
            "审阅文献综述段落块",
            "检查理论、测量、中国经验和方法衔接四类段落是否仍停留在候选层，并提出草案层修订建议。",
            ["literature_review_draft_packet.paragraph_blocks", "literature_seed_package.coverage"],
            "Reviews/agent_packets/literatureagent/cgss_literature_revision_brief.md",
        ),
    ]
    return make_agent_packet(
        "LiteratureAgent",
        {
            "seed_source_count": len(literature_seed_package.get("seed_sources", [])),
            "coverage": literature_seed_package.get("coverage", []),
            "open_source_ids": [item.get("source_id", "") for item in open_dependencies],
            "paragraph_block_ids": [item.get("id", "") for item in paragraph_blocks],
        },
        tasks,
        ["source_verification_recorded", "paragraph_blocks_reviewed", "no_formal_bibliography_write"],
        ["Manuscripts/sections", "Data/literature/processed/verified_bibliography.csv", "state/product"],
    )


def build_method_agent_packet(method_structure_gate_packet: dict[str, Any]) -> dict[str, Any]:
    claim_gates = method_structure_gate_packet.get("method_claim_gates", {})
    blocked_methods = [item.get("method", "") for item in claim_gates.get("blocked_method_families", [])]
    tasks = [
        make_task(
            "method.decide_primary_ordered_outcome_model",
            "MethodAgent",
            "审阅 OLS 与 Ordered Logit 的主模型角色",
            "基于当前主结果门禁，给出 OLS/Ordered Logit 在正文和稳健性中的推荐排布。",
            ["method_structure_gate_packet.method_claim_gates.main_result_gate"],
            "Reviews/agent_packets/methodagent/cgss_primary_model_decision.md",
        ),
        make_task(
            "method.review_blocked_causal_methods",
            "MethodAgent",
            "复核暂不进入的因果方法族",
            "检查 DID、IV、RDD、PSM、DML 等方法族的阻断理由，避免在正文中写入未获支持的因果设计。",
            ["method_structure_gate_packet.method_claim_gates.blocked_method_families"],
            "Reviews/agent_packets/methodagent/cgss_blocked_method_review.md",
        ),
    ]
    return make_agent_packet(
        "MethodAgent",
        {
            "claim_boundary": claim_gates.get("main_result_gate", {}).get("claim_boundary", ""),
            "supported_claim_types": [item.get("claim_type", "") for item in claim_gates.get("supported_claims", [])],
            "blocked_method_families": blocked_methods,
            "human_decisions": claim_gates.get("human_decisions", []),
        },
        tasks,
        ["claim_boundary_confirmed", "blocked_methods_remain_out_of_formal_design", "human_model_decision_recorded"],
        ["DesignSpec", "RunPlan", "state/product"],
    )


def build_writer_agent_packet(
    literature_review_packet: dict[str, Any],
    method_structure_gate_packet: dict[str, Any],
) -> dict[str, Any]:
    target_sections = list(method_structure_gate_packet.get("section_standards", {}).keys())
    tasks = [
        make_task(
            "writer.prepare_section_revision_briefs",
            "WriterAgent",
            "生成章节级修订简报",
            "把文献段落、方法门禁和章节证据要求转成草案层写作工单，不直接写正式论文正文。",
            ["literature_review_draft_packet.paragraph_blocks", "method_structure_gate_packet.section_standards"],
            "Reviews/agent_packets/writeragent/cgss_section_revision_briefs.md",
        ),
        make_task(
            "writer.prepare_claim_wording_guardrails",
            "WriterAgent",
            "生成论断措辞边界",
            "把 positive conditional association、有序模型稳健性和禁止因果措辞写成草案层写作约束。",
            ["method_structure_gate_packet.method_claim_gates.supported_claims"],
            "Reviews/agent_packets/writeragent/cgss_claim_wording_guardrails.md",
        ),
    ]
    return make_agent_packet(
        "WriterAgent",
        {
            "paragraph_block_count": len(literature_review_packet.get("paragraph_blocks", [])),
            "target_sections": target_sections,
        },
        tasks,
        ["section_briefs_ready", "claim_wording_guardrails_ready", "formal_manuscript_not_written"],
        ["Manuscripts/sections", "Manuscripts/generated", "state/product"],
    )


def build_reviewer_agent_packet(
    literature_seed_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
    method_structure_gate_packet: dict[str, Any],
) -> dict[str, Any]:
    tasks = [
        make_task(
            "reviewer.audit_revision_queue",
            "ReviewerAgent",
            "审计四类 Agent 修订队列",
            "复核每条任务是否有输入、输出、人工批准条件和正式层保护边界。",
            ["revision_task_queue.agent_packets"],
            "Reviews/agent_packets/revieweragent/cgss_revision_queue_audit.md",
        ),
        make_task(
            "reviewer.prepare_human_approval_checklist",
            "ReviewerAgent",
            "生成人工批准检查清单",
            "把文献、方法和写作任务压缩成人工审阅前必须确认的清单。",
            [
                "literature_seed_package.status",
                "literature_review_draft_packet.status",
                "method_structure_gate_packet.status",
            ],
            "Reviews/agent_packets/revieweragent/cgss_human_approval_checklist.md",
        ),
    ]
    return make_agent_packet(
        "ReviewerAgent",
        {
            "input_statuses": {
                "literature_seed_package": literature_seed_package.get("status", ""),
                "literature_review_draft_packet": literature_review_packet.get("status", ""),
                "method_structure_gate_packet": method_structure_gate_packet.get("status", ""),
            }
        },
        tasks,
        ["human_approval_required", "draft_layer_only", "no_agent_task_queue_json_written"],
        ["state/product/agent_task_queue.json", "DesignSpec", "RunPlan", "formal manuscript"],
    )


def make_agent_packet(
    agent: str,
    input_summary: dict[str, Any],
    tasks: list[dict[str, Any]],
    acceptance_checks: list[str],
    must_not_write: list[str],
) -> dict[str, Any]:
    return {
        "agent": agent,
        "input_summary": input_summary,
        "tasks": tasks,
        "acceptance_checks": acceptance_checks,
        "write_boundary": {
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "must_not_write": must_not_write,
        },
    }


def make_task(
    task_id: str,
    agent: str,
    title: str,
    objective: str,
    evidence_inputs: list[str],
    output_target: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "agent": agent,
        "title": title,
        "objective": objective,
        "evidence_inputs": evidence_inputs,
        "output_target": output_target,
        "status": "queued_for_human_approved_revision",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
    }


def write_revision_task_queue_review(
    project_root: Path,
    queue: dict[str, Any],
    review_path: Path,
) -> Path:
    absolute_review = project_root / review_path
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.write_text(render_review(queue), encoding="utf-8")
    return absolute_review


def render_review(queue: dict[str, Any]) -> str:
    lines = [
        "# CGSS 审稿式修订任务队列",
        "",
        f"- 题目：{queue.get('topic', '')}",
        f"- schema：`{queue['schema_version']}`",
        f"- 状态：`{queue['status']}`",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product/agent_task_queue.json：否",
        "- 写入 DesignSpec / RunPlan：否",
    ]
    if queue.get("blocking_reasons"):
        lines.extend(["", "## 当前需要处理"])
        for reason in queue["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if queue["status"].startswith("blocked"):
        lines.extend(["", "## 队列 JSON", "```json", json.dumps(queue, ensure_ascii=False, indent=2), "```"])
        return "\n".join(lines) + "\n"

    lines.extend(["", "## Agent 队列"])
    for packet in queue["agent_packets"]:
        lines.extend(["", f"### {packet['agent']}"])
        for task in packet["tasks"]:
            lines.append(f"- `{task['task_id']}`：{task['title']} -> `{task['output_target']}`")
    lines.extend(["", "## 人工批准后才可进入"])
    for item in queue["promotion"]["would_enable"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## 队列 JSON", "```json", json.dumps(queue, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"
