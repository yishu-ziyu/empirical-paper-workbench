from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_reviewer_revision_loop.v1"
DEFAULT_PAPER_PATH = Path("Manuscripts/generated/cgss_social_capital_happiness_paper.md")
DEFAULT_PAPER_ASSEMBLY_PATH = Path("Results/json/cgss_social_capital_happiness_paper_assembly.json")
DEFAULT_METHOD_GATE_PATH = Path("Results/json/cgss_social_capital_happiness_method_gate.json")
DEFAULT_RESULTS_EVIDENCE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_LITERATURE_PACKET_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_REVIEWER_REPORT_PATH = Path("Reviews/cgss_social_capital_happiness_reviewer_report.md")
DEFAULT_REVISION_TASK_QUEUE_PATH = Path("Reviews/cgss_social_capital_happiness_revision_task_queue.md")
DEFAULT_PAPER_REV1_PATH = Path("Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_text_or_empty(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_cgss_reviewer_revision_loop(
    *,
    paper_markdown: str,
    paper_assembly: dict[str, Any],
    method_gate: dict[str, Any],
    results_evidence: dict[str, Any],
    literature_packet: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_artifacts": {
            "paper": source_paths.get("paper", str(DEFAULT_PAPER_PATH)),
            "paper_assembly": source_paths.get("paper_assembly", str(DEFAULT_PAPER_ASSEMBLY_PATH)),
            "method_gate": source_paths.get("method_gate", str(DEFAULT_METHOD_GATE_PATH)),
            "results_evidence": source_paths.get("results_evidence", str(DEFAULT_RESULTS_EVIDENCE_PATH)),
            "literature_packet": source_paths.get("literature_packet", str(DEFAULT_LITERATURE_PACKET_PATH)),
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
        },
    }
    blocking_reasons = input_blocking_reasons(
        paper_markdown,
        paper_assembly,
        method_gate,
        results_evidence,
        literature_packet,
    )
    if blocking_reasons:
        return {
            **base,
            "status": "blocked_revision_loop_inputs_not_ready",
            "blocking_reasons": blocking_reasons,
            "reviewer_report": {"findings": []},
            "revision_task_queue": {"tasks": [], "formal_writeback_allowed": False},
            "paper_rev1_markdown": "",
            "next_tasks": ["repair_revision_loop_inputs"],
        }

    findings = reviewer_findings(paper_assembly, method_gate, literature_packet)
    queue = revision_task_queue(findings, method_gate)
    rev1 = render_rev1(paper_markdown, findings, queue, results_evidence, method_gate, literature_packet)
    return {
        **base,
        "status": "needs_human_revision_review",
        "blocking_reasons": [],
        "reviewer_report": {
            "status": "needs_human_reviewer_review",
            "findings": findings,
        },
        "revision_task_queue": queue,
        "paper_rev1_markdown": rev1,
        "agent_team_schedule": {
            "call_when": "after_method_gate_review_pack_is_available",
            "called_agents": ["ReviewerAgent", "MethodAgent", "LiteratureAgent", "WriterAgent"],
            "recall_when": "after_reviewer_report_revision_queue_and_rev1_are_written",
            "next_call_when": "before_paper_package_manifest",
            "boundary": "审稿式修订循环只写草案层产物，不写正式论文层。",
        },
        "next_tasks": [
            "human_review_reviewer_report",
            "approve_or_revise_revision_task_queue",
            "package_draft_paper_after_human_review",
        ],
    }


def input_blocking_reasons(
    paper_markdown: str,
    paper_assembly: dict[str, Any],
    method_gate: dict[str, Any],
    results_evidence: dict[str, Any],
    literature_packet: dict[str, Any],
) -> list[str]:
    reasons = []
    if not paper_markdown.strip():
        reasons.append("exploratory_paper_missing")
    if paper_assembly.get("status") != "needs_human_exploratory_paper_review":
        reasons.append("paper_assembly_not_review_ready")
    if method_gate.get("status") not in {"needs_human_method_gate_review", "method_gate_suggested_needs_human_review"}:
        reasons.append("method_gate_not_review_ready")
    if results_evidence.get("status") != "ready_for_paper_draft_input":
        reasons.append("results_evidence_not_ready")
    if literature_packet.get("status") != "needs_human_literature_review_draft_approval":
        reasons.append("literature_packet_not_reviewable")
    return reasons


def reviewer_findings(
    paper_assembly: dict[str, Any],
    method_gate: dict[str, Any],
    literature_packet: dict[str, Any],
) -> list[dict[str, Any]]:
    chars = paper_assembly.get("paper_metrics", {}).get("chinese_characters", 0)
    gate_status = method_gate.get("gate_status", "")
    open_literature = len(literature_packet.get("open_dependencies", []))
    return [
        {
            "area": "paper_structure",
            "severity": "major",
            "finding": f"完整探索性稿已形成，但当前约 {chars} 个中文字符，仍低于正式论文包长度标准。",
            "required_action": "按引言、文献、数据、方法、结果、稳健性和结论逐节扩写。",
        },
        {
            "area": "literature_review",
            "severity": "major",
            "finding": f"文献综述仍包含 {open_literature} 类人工核验依赖，候选引用不能直接进入正式参考文献。",
            "required_action": "核验 DOI、CNKI/Zotero 元数据、CGSS 官方来源和中文核心文献。",
        },
        {
            "area": "data_and_variables",
            "severity": "minor",
            "finding": "CGSS2023、幸福感题项、社会资本题项和控制变量已经进入证据包，但正式稿仍需变量表。",
            "required_action": "补齐题项原文、编码方向、缺失处理、样本筛选和描述性统计。",
        },
        {
            "area": "identification_strategy",
            "severity": "major",
            "finding": f"方法门状态为 {gate_status}；当前只能支持条件相关，不能写成因果识别。",
            "required_action": "明确 OLS/Ordered Logit 的主次关系，并加入横截面识别边界。",
        },
        {
            "area": "result_interpretation",
            "severity": "minor",
            "finding": "OLS 与 Ordered Logit 结果方向一致，但需要避免把系数解释成政策处理效应。",
            "required_action": "结果段落保留数字绑定，并解释有序模型系数的含义边界。",
        },
        {
            "area": "robustness_gap",
            "severity": "major",
            "finding": "稳健性、异质性和机制检验尚未真实执行。",
            "required_action": "排队分项社会资本、替代控制、地区/城乡异质性和机制路径检验。",
        },
        {
            "area": "submission_standard_gap",
            "severity": "major",
            "finding": "当前仍是探索性草稿，未满足投稿级参考文献、表格、附录和复现说明标准。",
            "required_action": "在 paper package 中补齐可复现 README、结果证据包、方法门和审稿队列。",
        },
        {
            "area": "human_judgment_required",
            "severity": "critical",
            "finding": "主模型定位、引用采信、稳健性优先级和因果表述必须人工审阅。",
            "required_action": "人工决定是否批准进入正式层或继续草案修订。",
        },
    ]


def revision_task_queue(findings: list[dict[str, Any]], method_gate: dict[str, Any]) -> dict[str, Any]:
    risks = method_gate.get("risk_register", [])
    tasks = [
        task(
            "writer.expand_core_sections_to_formal_length",
            "WriterAgent",
            "扩写核心章节到正式论文长度",
            ["paper_structure", "submission_standard_gap"],
            "Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md",
        ),
        task(
            "literature.verify_candidate_citations",
            "LiteratureAgent",
            "核验候选引用和中文文献来源",
            ["literature_review"],
            "Reviews/cgss_social_capital_happiness_literature_verification_queue.md",
        ),
        task(
            "data.add_variable_table_and_sample_flow",
            "DataAgent",
            "补齐变量表、样本筛选和描述性统计",
            ["data_and_variables"],
            "Reviews/cgss_social_capital_happiness_data_variable_revision.md",
        ),
        task(
            "method.address_reverse_causality_and_omitted_variables",
            "MethodAgent",
            "处理反向因果与遗漏变量风险的文字和补证计划",
            ["identification_strategy", "human_judgment_required"],
            "Reviews/cgss_social_capital_happiness_endogeneity_revision.md",
        ),
        task(
            "writer.expand_robustness_and_mechanism_plan",
            "WriterAgent",
            "扩写稳健性、异质性和机制检验计划",
            ["robustness_gap"],
            "Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md",
        ),
        task(
            "reviewer.audit_result_interpretation_wording",
            "ReviewerAgent",
            "审计结果解释和因果措辞边界",
            ["result_interpretation", "identification_strategy"],
            "Reviews/cgss_social_capital_happiness_reviewer_report.md",
        ),
    ]
    return {
        "schema_version": "p6.cgss_revision_task_queue.v2",
        "status": "needs_human_revision_queue_review",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_method_gate_risks": risks,
        "tasks": tasks,
        "acceptance_checks": [
            "reviewer_report_read_by_human",
            "revision_queue_approved_or_revised",
            "no_formal_manuscript_writeback",
            "candidate_citations_remain_marked_for_verification",
        ],
    }


def task(
    task_id: str,
    agent: str,
    title: str,
    source_findings: list[str],
    output_target: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "agent": agent,
        "title": title,
        "source_findings": source_findings,
        "output_target": output_target,
        "status": "queued_for_human_reviewed_revision",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
    }


def render_rev1(
    paper_markdown: str,
    findings: list[dict[str, Any]],
    queue: dict[str, Any],
    results_evidence: dict[str, Any],
    method_gate: dict[str, Any],
    literature_packet: dict[str, Any],
) -> str:
    ols = results_evidence.get("primary_result", {}).get("ols", {})
    ordered = results_evidence.get("primary_result", {}).get("ordered_logit", {})
    header = [
        "# 社会资本对居民主观幸福感的影响研究",
        "",
        "- Draft layer: `true`",
        "- Formal writeback: `false`",
        "- Status: `needs_human_revision_review`",
        "",
        "## Rev1 审稿式修订说明",
        "",
        "本 Rev1 是在探索性论文草稿、P6-K 方法规范门和结果证据包基础上生成的草案层修订稿。",
        "候选引用仍需人工核验；所有正式参考文献、正式论文层和产品状态均未写回。",
        (
            f"结果解释继续绑定结果证据包：OLS 系数 {format_number(ols.get('coef'))}，"
            f"Ordered Logit 系数 {format_number(ordered.get('coef'))}，样本量 {ols.get('nobs', '')}。"
        ),
        "方法边界：当前只能写条件相关，反向因果和遗漏变量风险必须保留在审稿修订队列中。",
        "",
        "### 本轮审稿重点",
    ]
    for finding in findings:
        header.append(f"- `{finding['area']}`：{finding['required_action']}")
    header.extend(["", "### 修订任务队列"])
    for item in queue["tasks"]:
        header.append(f"- `{item['task_id']}` -> {item['output_target']}")
    header.extend(["", "---", ""])

    body = strip_existing_title(paper_markdown)
    return "\n".join(header).rstrip() + "\n\n" + body.rstrip() + "\n"


def strip_existing_title(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return markdown


def format_number(value: Any) -> str:
    if value is None or value == "":
        return ""
    return f"{float(value):.4g}"


def write_cgss_reviewer_revision_outputs(
    project_root: Path,
    loop: dict[str, Any],
    reviewer_report_path: Path = DEFAULT_REVIEWER_REPORT_PATH,
    revision_task_queue_path: Path = DEFAULT_REVISION_TASK_QUEUE_PATH,
    paper_rev1_path: Path = DEFAULT_PAPER_REV1_PATH,
) -> dict[str, Path]:
    absolute_reviewer = project_root / reviewer_report_path
    absolute_queue = project_root / revision_task_queue_path
    absolute_rev1 = project_root / paper_rev1_path
    absolute_reviewer.parent.mkdir(parents=True, exist_ok=True)
    absolute_queue.parent.mkdir(parents=True, exist_ok=True)
    absolute_rev1.parent.mkdir(parents=True, exist_ok=True)
    absolute_reviewer.write_text(render_reviewer_report(loop), encoding="utf-8")
    absolute_queue.write_text(render_revision_queue(loop), encoding="utf-8")
    absolute_rev1.write_text(loop.get("paper_rev1_markdown", ""), encoding="utf-8")
    return {
        "reviewer_report": absolute_reviewer,
        "revision_task_queue": absolute_queue,
        "paper_rev1": absolute_rev1,
    }


def render_reviewer_report(loop: dict[str, Any]) -> str:
    lines = [
        "# CGSS 审稿式修订报告",
        "",
        f"- 状态：`{loop.get('status')}`",
        f"- 草案层：`{str(loop.get('draft_layer_only', False)).lower()}`",
        f"- 正式层写回：`{str(loop.get('formal_writeback_allowed', False)).lower()}`",
    ]
    if loop.get("blocking_reasons"):
        lines.extend(["", "## 阻断原因"])
        for reason in loop["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(["", "## 审稿发现"])
    for finding in loop["reviewer_report"]["findings"]:
        lines.extend(
            [
                f"### {finding['area']}",
                f"- 严重程度：`{finding['severity']}`",
                f"- 发现：{finding['finding']}",
                f"- 要求动作：{finding['required_action']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_revision_queue(loop: dict[str, Any]) -> str:
    queue = loop.get("revision_task_queue", {})
    lines = [
        "# CGSS 审稿式修订任务队列",
        "",
        f"- schema：`{queue.get('schema_version')}`",
        f"- 状态：`{queue.get('status')}`",
        f"- 草案层：`{str(queue.get('draft_layer_only', False)).lower()}`",
        f"- 正式层写回：`{str(queue.get('formal_writeback_allowed', False)).lower()}`",
        "",
        "## 方法门风险",
    ]
    for risk in queue.get("source_method_gate_risks", []):
        lines.append(f"- `{risk}`")
    lines.extend(["", "## 任务"])
    for item in queue.get("tasks", []):
        lines.extend(
            [
                f"### {item['task_id']}",
                f"- Agent：`{item['agent']}`",
                f"- 标题：{item['title']}",
                f"- 输出：`{item['output_target']}`",
                f"- 状态：`{item['status']}`",
                "- 写入正式层：否",
                "",
            ]
        )
    lines.extend(["## 验收检查"])
    for check in queue.get("acceptance_checks", []):
        lines.append(f"- `{check}`")
    return "\n".join(lines).rstrip() + "\n"
