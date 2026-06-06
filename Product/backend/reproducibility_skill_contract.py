from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now


REPRODUCIBILITY_CONTRACT_PATH = Path("state/product/reproducibility_skill_contract.json")
REPRODUCIBILITY_CONTRACT_DOC_PATH = Path("docs/workflows/reproducibility-skill-contract.md")


def reproducibility_contract_state_path(project_root: Path) -> Path:
    return project_root / REPRODUCIBILITY_CONTRACT_PATH


def reproducibility_contract_doc_path(project_root: Path) -> Path:
    return project_root / REPRODUCIBILITY_CONTRACT_DOC_PATH


def build_reproducible_research_skill_contract() -> dict[str, Any]:
    return {
        "id": "reproducibility_skill_contract",
        "schema_version": "p0.reproducible_research_skill_contract.v1",
        "status": "ready_for_agent_queue",
        "evidence_level": "local_file",
        "source_material": {
            "name": "论文复现与可复现研究",
            "product_meaning": "把 CoPaper-like 复现能力放进执行完成后的质量门，而不是只作为教程材料。",
            "borrowed_patterns": [
                "复现 Skill：论文 PDF + 复现包 -> 复现报告",
                "标准化输出：save_table/save_figure 和结构化 sidecar",
                "Agent 审阅循环：执行者、复现者、审稿者分工",
                "一键复现：一个命令跑完清洗、分析、稳健性和导出",
            ],
        },
        "placement": {
            "insert_after": "method_execution_result",
            "insert_before": "formal_export_preflight",
            "auto_mode_boundary": "Auto Mode 可以跑到导出预检，但不能静默提升到正式层。",
            "next_gate": "human_reproducibility_review",
        },
        "quality_principles": [
            {
                "id": "version_control",
                "label": "版本控制",
                "requirement": "记录 git commit、dirty status 和关键输入输出文件摘要。",
            },
            {
                "id": "environment_lock",
                "label": "环境锁定",
                "requirement": "记录 Python/R/Stata 版本、依赖清单和执行后端。",
            },
            {
                "id": "immutable_raw_data",
                "label": "原始数据不可变",
                "requirement": "原始数据只读，清洗结果写入处理后数据目录。",
            },
            {
                "id": "code_as_documentation",
                "label": "代码即文档",
                "requirement": "每个脚本必须声明输入、输出、用途和产物路径。",
            },
            {
                "id": "one_command_reproduction",
                "label": "一键复现",
                "requirement": "提供单一入口命令，能重建表格、图形、结果 JSON 和论文候选稿。",
            },
        ],
        "project_structure_mapping": {
            "raw_data": "Data/Raw",
            "processed_data": "Data/Final",
            "analysis_code": "Program",
            "cleaning_code": "Program/clean",
            "robustness_code": "Program/robustness",
            "tables": "Results/tab",
            "figures": "Results/fig",
            "json_results": "Results/json",
            "logs": "Results/logs",
            "manuscript": "Manuscripts",
            "formal_package": "Submissions/formal_package",
        },
        "skill_lanes": build_reproducibility_skill_lanes(),
        "agent_tasks": build_reproducibility_agent_tasks(),
        "acceptance_gates": [
            {
                "id": "raw_data_immutable",
                "label": "原始数据未被改写",
                "owner_agent": "VerifierAgent",
            },
            {
                "id": "all_outputs_manifested",
                "label": "表格、图形、JSON、日志均进入 manifest",
                "owner_agent": "ReproAgent",
            },
            {
                "id": "one_command_reproduce_available",
                "label": "存在一键复现入口和说明",
                "owner_agent": "ExecutionAgent",
            },
            {
                "id": "peer_review_findings_recorded",
                "label": "复现报告经过审稿 Agent 质询",
                "owner_agent": "ReviewerAgent",
            },
            {
                "id": "human_review_before_formal_export",
                "label": "人工确认后才允许进入正式导出",
                "owner_agent": "Supervisor",
            },
        ],
        "updated_at": utc_now(),
    }


def build_reproducibility_product_capability() -> dict[str, Any]:
    return {
        "id": "cap_reproducibility_contract",
        "namespace": "product",
        "name": "reproducibility_contract",
        "category": "reproducibility",
        "description": "Build the reproducible research contract and handoff doc before formal export.",
        "risk_level": "medium",
        "cost_model": "local_cpu_time",
        "allowed_roles": ["supervisor", "repro_agent", "verifier_agent", "execution_agent"],
        "adapter_path": "Product.backend.reproducibility_skill_contract.write_reproducibility_skill_contract",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_root": {"type": "string"},
            },
            "required": ["project_root"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "state_path": {"type": "string"},
                "doc_path": {"type": "string"},
            },
        },
        "status": "executable",
    }


def build_reproducibility_skill_lanes() -> list[dict[str, Any]]:
    return [
        {
            "id": "reproduction_skill",
            "owner_agent": "ReproAgent",
            "purpose": "从论文、代码和结果产物生成复现报告。",
            "inputs": ["paper_pdf", "replication_package", "run_manifest"],
            "outputs": ["reproducibility_report.md", "comparison_tables", "figure_reproduction"],
            "evidence_level": "local_execution",
        },
        {
            "id": "environment_lock",
            "owner_agent": "VerifierAgent",
            "purpose": "锁定本次运行环境，避免同一代码在不同环境下不可复现。",
            "inputs": ["requirements.txt", "python_version", "stata_version", "r_lockfile"],
            "outputs": ["environment_manifest.json"],
            "evidence_level": "local_file",
        },
        {
            "id": "standard_outputs",
            "owner_agent": "ExecutionAgent",
            "purpose": "强制表格、图形、JSON 结果和日志都走标准路径。",
            "inputs": ["method_execution_result", "analysis_scripts"],
            "outputs": ["Results/tab", "Results/fig", "Results/json", "Results/logs"],
            "evidence_level": "local_execution",
        },
        {
            "id": "one_command_reproduce",
            "owner_agent": "ExecutionAgent",
            "purpose": "生成或验证一个命令跑完整条研究链路。",
            "inputs": ["workflow_contract", "run_plan", "scripts"],
            "outputs": ["reproduce_command", "run_manifest.json"],
            "evidence_level": "local_execution",
        },
        {
            "id": "agent_peer_review_loop",
            "owner_agent": "ReviewerAgent",
            "purpose": "让审稿 Agent 对复现报告、方法门和论文草稿提出可执行修订。",
            "inputs": ["reproducibility_report.md", "method_gate_packet", "draft_pdf"],
            "outputs": ["reviewer_scorecard.json", "revision_work_orders"],
            "evidence_level": "local_file",
        },
    ]


def build_reproducibility_agent_tasks() -> list[dict[str, Any]]:
    return [
        _task(
            "repro_env_lock",
            "锁定运行环境",
            "VerifierAgent",
            "记录 Python/R/Stata、依赖和执行后端，形成 environment_manifest.json。",
            ["method_execution_result", "execution_backend"],
            ["environment_manifest.json"],
            "environment_lock_required",
        ),
        _task(
            "repro_standard_outputs",
            "核对标准化产物",
            "ExecutionAgent",
            "确认表格、图形、JSON、日志都在标准目录，并带 sidecar 元数据。",
            ["run_plan", "method_execution_result"],
            ["Results/tab", "Results/fig", "Results/json", "Results/logs"],
            "standard_outputs_required",
        ),
        _task(
            "repro_one_command",
            "生成一键复现入口",
            "ExecutionAgent",
            "生成或验证一个命令重跑清洗、分析、稳健性和导出预检。",
            ["workflow_contract", "analysis_scripts"],
            ["reproduce_command", "run_manifest.json"],
            "one_command_required",
        ),
        _task(
            "repro_audit_manifest",
            "生成复现审计清单",
            "ReproAgent",
            "汇总 git 状态、输入文件摘要、输出文件摘要、命令和日志。",
            ["environment_manifest.json", "run_manifest.json", "artifact_manifest"],
            ["reproducibility_report.md"],
            "audit_manifest_required",
        ),
        _task(
            "repro_peer_review",
            "审稿式复现质询",
            "ReviewerAgent",
            "对复现报告和论文草稿提出方法、证据、文字结构上的修订单。",
            ["reproducibility_report.md", "draft_pdf", "method_gate_packet"],
            ["reviewer_scorecard.json", "revision_work_orders"],
            "reviewer_challenge_required",
        ),
    ]


def _task(
    task_id: str,
    title: str,
    owner_agent: str,
    purpose: str,
    inputs: list[str],
    outputs: list[str],
    blocking_gate: str,
) -> dict[str, Any]:
    return {
        "id": task_id,
        "title": title,
        "owner_agent": owner_agent,
        "purpose": purpose,
        "inputs": inputs,
        "output_requirements": outputs,
        "blocking_gate": blocking_gate,
        "status": "queued_after_method_execution",
        "max_minutes": 20,
    }


def write_reproducibility_skill_contract(project_root: Path) -> dict[str, str]:
    contract = build_reproducible_research_skill_contract()
    state_path = reproducibility_contract_state_path(project_root)
    doc_path = reproducibility_contract_doc_path(project_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
    doc_path.write_text(build_reproducibility_contract_markdown(contract), encoding="utf-8")
    return {
        "state_path": REPRODUCIBILITY_CONTRACT_PATH.as_posix(),
        "doc_path": REPRODUCIBILITY_CONTRACT_DOC_PATH.as_posix(),
    }


def build_reproducibility_contract_markdown(contract: dict[str, Any]) -> str:
    task_lines = "\n".join(
        f"- `{task['id']}`: {task['title']} / {task['owner_agent']} / <= {task['max_minutes']} min"
        for task in contract["agent_tasks"]
    )
    gate_lines = "\n".join(
        f"- `{gate['id']}`: {gate['label']} ({gate['owner_agent']})"
        for gate in contract["acceptance_gates"]
    )
    principle_lines = "\n".join(
        f"- `{item['id']}`: {item['label']}。{item['requirement']}"
        for item in contract["quality_principles"]
    )
    return f"""# 复现研究能力契约

## 进入主线的位置

`{contract['placement']['insert_after']}` 之后，`{contract['placement']['insert_before']}` 之前。

这意味着：模型和结果跑完以后，系统必须先过复现研究门，再进入正式导出预检。

## 五条质量原则

{principle_lines}

## Agent 任务节点

{task_lines}

## 验收门

{gate_lines}

## 产品边界

{contract['placement']['auto_mode_boundary']}
"""
