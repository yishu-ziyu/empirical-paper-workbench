from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_quality import REQUIRED_SECTIONS


SECTION_TARGETS = {
    "Abstract": {
        "target": "100 English words or concise Chinese equivalent",
        "agent": "ManuscriptAgent",
        "purpose": "用最短篇幅交代问题、数据、方法和核心发现。",
    },
    "Introduction": {
        "target": "1800-3000 English words / 4-6 pages",
        "agent": "ManuscriptAgent",
        "purpose": "把研究问题、核心结论、贡献和文章结构一次讲清楚。",
    },
    "Literature and Contribution": {
        "target": "1000-1800 English words / 2-4 pages",
        "agent": "LiteratureAgent",
        "purpose": "把相邻文献、方法文献和本文增量绑定到可核验证据。",
    },
    "Institutional Background / Theory / Context": {
        "target": "800-1500 English words / 2-4 pages",
        "agent": "DomainAgent",
        "purpose": "解释变量关系成立的制度背景、理论机制和研究边界。",
    },
    "Data and Measurement": {
        "target": "800-1500 English words / 2-3 pages",
        "agent": "DataAgent",
        "purpose": "说明数据来源、样本构造、变量定义、缺失处理和描述统计。",
    },
    "Empirical Strategy": {
        "target": "1200-2000 English words / 3-5 pages",
        "agent": "MethodAgent",
        "purpose": "写清识别式、估计方程、关键假设、标准误和方法规范门。",
    },
    "Main Results": {
        "target": "2000-3500 English words / 4-7 pages",
        "agent": "ExecutionAgent",
        "purpose": "围绕主表和主图解释估计结果、经济含义和量级。",
    },
    "Robustness / Mechanisms / Heterogeneity": {
        "target": "1500-3000 English words / 3-6 pages",
        "agent": "MethodAgent",
        "purpose": "组织稳健性、机制检验、异质性和敏感性分析。",
    },
    "Conclusion": {
        "target": "500-800 English words / 1-2 pages",
        "agent": "ManuscriptAgent",
        "purpose": "收束发现、贡献、局限和下一步研究。",
    },
    "References": {
        "target": "Verified bibliography only",
        "agent": "LiteratureAgent",
        "purpose": "只接纳经过 Zotero/CNKI/DOI/OpenAlex/S2 核验的条目。",
    },
}


def build_paper_expansion_plan(project_root: Path, quality_report: dict[str, Any]) -> dict[str, Any]:
    section_checks = quality_report.get("section_checks", {})
    missing_sections = section_checks.get("missing_sections", [])
    verdict = quality_report.get("verdict", [])
    next_tasks = quality_report.get("recommended_next_tasks", [])
    draft_path = str(quality_report.get("draft_path") or "")

    section_plan = []
    for section in REQUIRED_SECTIONS:
        target = SECTION_TARGETS[section]
        section_plan.append(
            {
                "section": section,
                "status": "needs_build" if section in missing_sections else "needs_expansion",
                "target_length": target["target"],
                "agent": target["agent"],
                "purpose": target["purpose"],
                "inputs": build_section_inputs(section),
                "output": f"Manuscripts/sections/{slugify(section)}.md",
            }
        )

    return {
        "schema_version": "p4.paper_expansion_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": quality_report.get("profile", "general_working_paper"),
        "source_quality_report": "Results/json/paper_quality_report.json",
        "source_draft": draft_path,
        "paper_package_goal": {
            "primary_output": "PDF-first working paper package",
            "route": [
                "manuscript_expansion",
                "literature_evidence_gate",
                "method_gate",
                "reviewer_revision_loop",
                "replication_package_gate",
            ],
        },
        "current_verdict": verdict,
        "section_expansion_plan": section_plan,
        "agent_task_queue": normalize_agent_task_queue(next_tasks),
        "release_gate": {
            "required_before_review": [
                "all_required_sections_present",
                "verified_bibliography_and_contribution_matrix",
                "method_gate_report",
                "reviewer_scorecard_and_revision_log",
                "replication_readme_and_manifest",
            ],
            "profile_specific": {
                "aer_like": [
                    "abstract_at_or_under_100_words",
                    "jel_codes",
                    "keywords",
                    "data_and_code_availability_statement",
                ]
            },
        },
    }


def write_paper_expansion_plan(project_root: Path, plan: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def build_structured_manuscript(project_root: Path, plan: dict[str, Any], source_draft_path: Path | None) -> str:
    source_text = source_draft_path.read_text(encoding="utf-8") if source_draft_path and source_draft_path.exists() else ""
    title = extract_title(source_text) or "实证研究工作论文"
    source_brief = extract_source_brief(source_text)

    lines = [
        f"# {title}",
        "",
        "## Abstract",
        "",
        "This working paper studies the relationship between the stated research question, the available data, and the selected empirical design. The next writing round will bind the main coefficient, verified literature, and method-gate evidence into a compact AER-like abstract.",
        "",
        "JEL: J24, J31, O33",
        "",
        "Keywords: empirical research; labor market; technology; causal inference; reproducibility",
        "",
        "## Introduction",
        "",
        source_brief,
        "",
        "本节下一轮写作目标：用 4-6 页完成研究问题、核心事实、主要结果、贡献定位和全文路线。写作时优先绑定已核验文献、主回归表、研究设计门禁和复现包证据。",
        "",
        "## Literature and Contribution",
        "",
        "本节由 LiteratureAgent 接管，先建立 `verified_bibliography.csv` 和 `contribution_matrix.md`。文献入口包括 CNKI/CSSCI、Zotero 本地库、DOI/Crossref、OpenAlex、Semantic Scholar，以及必要的人工 Google Scholar 追引。",
        "",
        "写作任务：区分相邻主题文献、方法文献、数据来源文献和本文贡献位置；每条进入正文的文献都要绑定来源、检索式、检索日期、核验状态和证据角色。",
        "",
        "## Institutional Background / Theory / Context",
        "",
        "本节解释研究对象所处的制度背景、理论机制和可观察变量之间的关系。下一轮需要补齐政策背景、行业背景、劳动力市场机制，以及变量为何能够承载研究问题。",
        "",
        "## Data and Measurement",
        "",
        "本节由 DataAgent 接管，输出数据来源表、样本筛选流程、变量字典、缺失值画像、描述统计和数据血缘。当前草稿中的数据线索会进入数据画像任务，而不是散落在正文里。",
        "",
        "## Empirical Strategy",
        "",
        "本节由 MethodAgent 接管，输出 DesignSpec、估计方程、识别假设、标准误选择、前置条件检查和 `method_gate_report.json`。如果方法族是 DID / IV / RDD / PSM / DML，对应的专业检查清单进入主链路。",
        "",
        "## Main Results",
        "",
        "本节由 ExecutionAgent 接管，绑定主回归表、图表、估计量、标准误、样本量和经济量级。写作重点是把结果解释成研究发现，并让每个数字能追溯到 run artifact。",
        "",
        "## Robustness / Mechanisms / Heterogeneity",
        "",
        "本节组织稳健性、机制、异质性和敏感性分析。方法规范门会把必做检查转成任务，例如 DID 的平行趋势与敏感性分析、IV 的弱工具诊断、RDD 的带宽敏感性和协变量调整。",
        "",
        "## Conclusion",
        "",
        "本节收束研究发现、理论贡献、政策含义和下一步研究。最终版只保留已经通过证据绑定和审稿式修订循环的结论。",
        "",
        "## Data and Code Availability",
        "",
        "Replication materials will be organized as a PDF-first paper package with README, master script, data provenance, software versions, expected outputs, and artifact manifest. Restricted or local-only data will be described with access conditions and reproducibility boundaries.",
        "",
        "## References",
        "",
        "References will be populated from the verified bibliography package.",
        "",
        "## Appendix: Agent Task Queue",
        "",
    ]

    for task in plan.get("agent_task_queue", []):
        lines.extend(
            [
                f"### {task['id']}",
                "",
                f"- Agent: {task['agent']}",
                f"- Goal: {task['reason']}",
                f"- Inputs: {', '.join(str(item) for item in task.get('inputs', [])) or 'quality report'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_structured_manuscript(path: Path, manuscript: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manuscript, encoding="utf-8")
    return path


def build_supervisor_context_bundle(
    project_root: Path,
    quality_report: dict[str, Any],
    expansion_plan: dict[str, Any],
    output_plan_path: Path,
    output_manuscript_path: Path,
) -> dict[str, Any]:
    context_sources = [
        "Results/json/paper_quality_report.json",
        relative_or_absolute(output_plan_path, project_root),
        relative_or_absolute(output_manuscript_path, project_root),
    ]
    for candidate in [
        project_root / "state" / "product" / "research_question.json",
        project_root / "state" / "product" / "variable_role_set.json",
        project_root / "state" / "product" / "design_spec.json",
        project_root / "state" / "product" / "run_plan.json",
        project_root / "Results" / "json" / "method_execution_result.json",
        project_root / "Results" / "json" / "statspai_execution_result.json",
    ]:
        if candidate.exists():
            context_sources.append(relative_or_absolute(candidate, project_root))

    return {
        "schema_version": "p4.paper_supervisor_context.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "supervisor_role": "research_orchestrator",
        "profile": quality_report.get("profile", "general_working_paper"),
        "write_boundary": "Auto Mode 可以生成和修改草案层研究计划、章节草稿、审稿意见和 patch proposal；正式层稿件、canonical 方法库和最终 PDF 必须经过人工确认后写回。",
        "context_sources": context_sources,
        "execution_backends": [
            {
                "id": "statspai",
                "role": "agent-native method engine",
                "responsibility": "调用结构化统计和因果推断函数，产出机器可读结果、图表和发表级表格。",
            },
            {
                "id": "python",
                "role": "deterministic local execution",
                "responsibility": "执行数据画像、质量门、轻量 OLS/诊断、清单和可复现脚本。",
            },
            {
                "id": "stata_mcp",
                "role": "Stata-compatible execution",
                "responsibility": "在需要 Stata 生态或 do-file 复现时执行 Stata 命令并保存日志。",
            },
            {
                "id": "local_codex",
                "role": "LLM supervisor and subagent router",
                "responsibility": "根据证据和质量门生成研究路线、Agent Task Queue、章节草稿、审稿意见和修订计划。",
            },
        ],
        "agent_task_queue": expansion_plan.get("agent_task_queue", []),
        "release_gate": expansion_plan.get("release_gate", {}),
        "current_verdict": quality_report.get("verdict", []),
        "task_prompt": build_supervisor_task_prompt(quality_report, expansion_plan),
    }


def write_supervisor_context_bundle(path: Path, bundle: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def normalize_agent_task_queue(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue = []
    for order, task in enumerate(tasks, start=1):
        queue.append(
            {
                "order": order,
                "id": task.get("id"),
                "agent": task.get("agent"),
                "reason": task.get("reason"),
                "inputs": task.get("inputs", []),
                "status": "ready",
            }
        )
    return queue


def build_supervisor_task_prompt(quality_report: dict[str, Any], expansion_plan: dict[str, Any]) -> str:
    verdict = ", ".join(quality_report.get("verdict", []))
    tasks = "\n".join(
        f"- {task.get('id')}: {task.get('agent')} -> {task.get('reason')}"
        for task in expansion_plan.get("agent_task_queue", [])
    )
    return (
        "你是本地 Codex Supervisor，负责把当前实证研究推进为 PDF-first paper package。\n"
        "请读取上下文来源，只基于本地文件和可核验证据工作；需要新证据时，把它写成 Agent Task Queue 项，"
        "不要把未核验内容写入正式层。\n\n"
        f"当前质量门 verdict: {verdict}\n\n"
        "Agent Task Queue:\n"
        f"{tasks}\n\n"
        "输出要求：\n"
        "1. 给出下一轮研究路线和依赖顺序。\n"
        "2. 为 LiteratureAgent / DataAgent / MethodAgent / ExecutionAgent / ManuscriptAgent / ReviewerAgent 分配任务。\n"
        "3. 明确每个任务的输入证据、输出文件、验收门和人工确认点。\n"
        "4. 所有章节写作先进入草案层；正式层写回等待人工确认。\n"
    )


def build_section_inputs(section: str) -> list[str]:
    shared = ["paper_quality_report.json", "source_draft"]
    if section == "Literature and Contribution":
        return shared + ["verified_bibliography.csv", "contribution_matrix.md"]
    if section == "Empirical Strategy":
        return shared + ["DesignSpec", "method_gate_report.json"]
    if section == "Data and Measurement":
        return shared + ["VariableRoleSet", "dataset_profile"]
    if section in {"Main Results", "Robustness / Mechanisms / Heterogeneity"}:
        return shared + ["run artifacts", "tables", "figures"]
    return shared


def extract_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("#").strip()
    return None


def extract_source_brief(text: str) -> str:
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip() and not paragraph.strip().startswith("#")
    ]
    if not paragraphs:
        return "本项目已经进入论文包主链路：先形成完整 working paper 结构，再由文献、方法、执行和审稿 Agent 逐段补齐。"
    brief = " ".join(paragraphs[:3])
    return f"当前研究草稿提供的起点是：{brief}"


def slugify(section: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", section.lower()).strip("-")
    return slug or "section"


def relative_or_absolute(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)
