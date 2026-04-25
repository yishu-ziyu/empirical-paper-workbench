from __future__ import annotations

import json
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import build_evidence_inventory
from .orchestration_schema import HandoffPacket, OrchestrationManifest, ReviewPacket
from .project_adapter import detect_project_profile
from .workbench_paths import create_run_workspace


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_list(items: list[dict[str, Any]], key: str = "name", limit: int = 12) -> str:
    values = [str(item.get(key, "")) for item in items[:limit] if item.get(key)]
    return "\n".join(f"- {value}" for value in values) if values else "- No local files detected."


def artifact_rel(path: Path, project_root: Path) -> str:
    return str(path.relative_to(project_root))


def write_handoff(
    run_id: str,
    run_root: Path,
    project_root: Path,
    agent: str,
    stage: str,
    inputs: list[Path],
    outputs: list[Path],
    claims: list[str],
    risks: list[str],
    next_agent: str | None,
    metadata: dict[str, Any] | None = None,
) -> HandoffPacket:
    packet = HandoffPacket(
        run_id=run_id,
        agent=agent,
        stage=stage,
        inputs=[artifact_rel(path, project_root) for path in inputs],
        outputs=[artifact_rel(path, project_root) for path in outputs],
        claims=claims,
        risks=risks,
        next_agent=next_agent,
        metadata=metadata or {},
    )
    safe_name = agent.replace("Agent", "").lower()
    write_json(run_root / stage / f"{safe_name}_handoff.json", packet.to_dict())
    return packet


def build_literature_clusters(inventory: dict[str, Any]) -> dict[str, Any]:
    literature = inventory["literature_files"] + inventory["reference_files"]
    return {
        "robot_labor_reallocation": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["robot", "automation", "acemoglu", "autor"])
            or any(term in item["name"] for term in ["机器人", "自动化"])
        ],
        "matching_and_mismatch": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["matching", "mismatch", "search"])
            or any(term in item["name"] for term in ["匹配", "错配", "求职"])
        ],
        "identification_and_bartik": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["bartik", "iv", "instrument"])
            or any(term in item["name"] for term in ["识别", "工具变量"])
        ],
    }


def select_markdown_source(project_root: Path) -> Path | None:
    candidates = [
        project_root / "04_paper" / "论文v2.1_完整版.md",
        project_root / "04_paper" / "word_hqu_format" / "论文初稿_工业机器人冲击下的劳动者重新配置.md",
    ]
    candidates.extend(sorted((project_root / "04_paper").glob("*.md")))
    return next((path for path in candidates if path.exists()), None)


def read_manuscript_source(project_root: Path, inventory: dict[str, Any]) -> tuple[str, str | None]:
    source_path = select_markdown_source(project_root)
    if source_path is not None:
        return read_text(source_path), str(source_path.relative_to(project_root))
    section_texts = [
        read_text(project_root / item["path"])
        for item in inventory["manuscript_sections"]
        if read_text(project_root / item["path"])
    ]
    return "\n\n".join(section_texts), None


def normalize_markdown_for_run(text: str, project_root: Path) -> str:
    figures_root = project_root / "04_paper" / "figures"

    def replace_image(match: re.Match[str]) -> str:
        alt = match.group("alt")
        path = match.group("path")
        suffix = match.group("suffix") or ""
        if path.startswith(("/", "http://", "https://")):
            return match.group(0)
        if path.startswith("figures/"):
            return f"![{alt}]({figures_root / path.removeprefix('figures/')}){suffix}"
        return match.group(0)

    return re.sub(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)(?P<suffix>\{[^}]*\})?", replace_image, text)


def build_review_payload(draft_text: str, mode: str, source_markdown: str | None) -> dict[str, Any]:
    checks = [
        {
            "priority": "P0",
            "name": "source_of_truth",
            "passed": source_markdown == "04_paper/论文v2.1_完整版.md" or (source_markdown or "").startswith("04_paper/sections_v21"),
            "risk": "写作源必须以 sections_v21 或 论文v2.1_完整版.md 为准，word_hqu_format 只作为旧 Word 导出链参考。",
        },
        {
            "priority": "P1",
            "name": "concept_boundary",
            "passed": "严格" in draft_text and ("错配" in draft_text or "配置" in draft_text),
            "risk": "匹配效率、匹配质量代理、技能岗位错配三层边界需要在摘要、文献述评和结论中保持一致。",
        },
        {
            "priority": "P1",
            "name": "weak_iv_caution",
            "passed": "弱工具变量" in draft_text or "Stock-Yogo" in draft_text or "第一阶段" in draft_text,
            "risk": "Bartik IV 需要保留第一阶段和弱 IV 口径，不能写成已经彻底解决。",
        },
        {
            "priority": "P1",
            "name": "clds_causal_rank",
            "passed": "机制扩展" in draft_text and ("补充" in draft_text or "辅助" in draft_text),
            "risk": "CLDS 机制结果不是 Bartik IV 主识别，必须写成补充机制证据，不能和 CFPS+Bartik IV 同等因果等级。",
        },
        {
            "priority": "P1",
            "name": "bartik_exclusion_boundary",
            "passed": "排他" in draft_text or "识别边界" in draft_text or "外生" in draft_text,
            "risk": "Bartik 排他性需要说明产业结构可能反映制造业基础、开放程度和发展路径，不能写成天然外生。",
        },
        {
            "priority": "P1",
            "name": "result_claim_alignment",
            "passed": any(term in draft_text for term in ["表 4", "表4", "Table", "图 5", "图5"]),
            "risk": "每个核心结论需要挂到表格、图形或结果索引。",
        },
        {
            "priority": "P2",
            "name": "part_time_zero_result",
            "passed": "兼职" not in draft_text or "不显著" in draft_text or "证据不足" in draft_text,
            "risk": "兼职变量如果不显著，不能反向解释为支持正规就业导向。",
        },
        {
            "priority": "P2",
            "name": "reference_completeness",
            "passed": "暂无中文核心文献" not in draft_text and "待补充" not in draft_text,
            "risk": "参考文献不能保留“暂无中文核心文献，待补充”等未完成标记。",
        },
    ]
    failed = [item for item in checks if not item["passed"]]
    return {
        "decision": "revise_major" if len(failed) >= 2 else "revise_minor",
        "checks": checks,
        "source_markdown": source_markdown,
        "revision_requests": [item["risk"] for item in failed]
        or [
            "保留概念边界、弱 IV 谨慎口径、结果到论断的引用链，并在最终 Word 前再次检查摘要与结论。",
        ],
        "strengths": [
            "审阅对象来自真实论文 Markdown 源稿。" if mode == "live" else "审阅对象来自 dry-run 草稿。",
            "审阅者与写作者在 handoff 中保持逻辑分离。",
        ],
        "risks": [item["risk"] for item in checks if not item["passed"]],
    }


def write_real_review_files(review_report_path: Path, revision_plan_path: Path, review_payload: dict[str, Any]) -> None:
    check_lines = [
        f"- {item['priority']} {item['name']}: {'PASS' if item['passed'] else 'FAIL'} - {item['risk']}"
        for item in review_payload["checks"]
    ]
    failed_lines = [
        f"- {item['priority']} {item['name']}: {item['risk']}"
        for item in review_payload["checks"]
        if not item["passed"]
    ]
    write_text(
        review_report_path,
        "\n".join(
            [
                "# Review Report",
                "",
                "## Review Object",
                "",
                f"- mode: {review_payload.get('mode', 'unknown')}",
                f"- source_markdown: {review_payload.get('source_markdown') or 'section-assembled'}",
                "- source_policy: sections_v21 and 论文v2.1_完整版.md are the current writing sources; word_hqu_format is an export-chain source.",
                "",
                "## Decision",
                "",
                review_payload["decision"],
                "",
                "## Findings",
                "",
                *(failed_lines or ["- No blocking findings. Keep reviewer checks active before final submission."]),
                "",
                "## Checks",
                "",
                *check_lines,
                "",
                "## Revision Requests",
                "",
                *[f"- {item}" for item in review_payload["revision_requests"]],
            ]
        )
        + "\n",
    )
    write_text(
        revision_plan_path,
        "\n".join(
            [
                "# Revision Plan",
                "",
                "## Principles",
                "",
                "- Do not rewrite locked empirical results without explicit approval.",
                "- Fix source-of-truth, reference, and evidence-boundary issues before language polishing.",
                "- Keep CFPS+Bartik IV as main identification and CLDS as mechanism extension.",
                "",
                "## Action Items",
                "",
                *[f"{idx}. {item}" for idx, item in enumerate(review_payload["revision_requests"], start=1)],
                "",
                "## Recheck Gate",
                "",
                "- Recheck references, table/figure numbers, abstract numbers, weak-IV wording, CLDS causal rank, and HQU Word formatting.",
                "",
                "## Required Before Final Submission",
                "",
                "1. 更新 Word/WPS 目录域。",
                "2. 复核摘要、结论、弱 IV 表述是否一致。",
                "3. 确认每个实证结论均能追溯到结果表、图或日志。",
            ]
        )
        + "\n",
    )


def build_hqu_docx(project_root: Path, markdown: Path, output: Path, report: Path) -> dict[str, Any]:
    template = project_root / "05_reference" / "毕业论文格式规范" / "经济与金融学院本科毕业论文格式模板.docx"
    script = Path("/Users/mahaoxuan/.codex/skills/hqu-thesis-formatting/scripts/build_hqu_docx.py")
    archive_dir = output.parent / "archive_word_versions"
    if not template.exists():
        message = f"HQU template not found: {template}"
        write_text(output, message + "\n")
        write_text(report, f"# Formatting Report\n\nFAILED: {message}\n")
        return {"status": "failed", "returncode": 1, "error": message, "template": str(template)}
    if shutil.which("pandoc") is None:
        message = "pandoc is required for live HQU docx export but was not found in PATH"
        write_text(output, message + "\n")
        write_text(report, f"# Formatting Report\n\nFAILED: {message}\n")
        return {"status": "failed", "returncode": 1, "error": message, "template": str(template)}
    command = [
        "python3",
        str(script),
        "--markdown",
        str(markdown),
        "--template",
        str(template),
        "--output",
        str(output),
        "--archive-dir",
        str(archive_dir),
    ]
    process = subprocess.run(command, cwd=project_root, text=True, capture_output=True)
    status = "completed" if process.returncode == 0 and output.exists() else "failed"
    fallback: dict[str, Any] | None = None
    if status == "failed":
        fallback_output = output
        fallback_command = [
            "pandoc",
            str(markdown),
            "--from",
            "markdown+tex_math_dollars+raw_tex",
            "--reference-doc",
            str(template),
            "-o",
            str(fallback_output),
        ]
        fallback_process = subprocess.run(fallback_command, cwd=project_root, text=True, capture_output=True)
        fallback = {
            "command": fallback_command,
            "returncode": fallback_process.returncode,
            "stdout": fallback_process.stdout,
            "stderr": fallback_process.stderr,
        }
        if fallback_process.returncode == 0 and fallback_output.exists():
            status = "completed_with_reference_doc_fallback"
    write_text(
        report,
        "\n".join(
            [
                "# Formatting Report",
                "",
                f"- status: {status}",
                f"- template: {template}",
                f"- markdown: {markdown}",
                f"- output: {output}",
                f"- archive_dir: {archive_dir}",
                f"- returncode: {process.returncode}",
                "",
                "## stdout",
                "",
                process.stdout or "(empty)",
                "",
                "## stderr",
                "",
                process.stderr or "(empty)",
                "",
                "## fallback",
                "",
                json.dumps(fallback, ensure_ascii=False, indent=2) if fallback else "(not used)",
            ]
        )
        + "\n",
    )
    return {
        "status": status,
        "returncode": process.returncode,
        "command": command,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "fallback": fallback,
        "template": str(template),
    }


def run_workbench(project_root: Path, mode: str = "dry-run", user_goal: str = "") -> dict[str, Any]:
    project_root = project_root.resolve()
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    workspace = create_run_workspace(project_root, run_id)
    run_root = workspace.root
    profile = detect_project_profile(project_root)
    inventory = build_evidence_inventory(project_root, profile)
    artifacts: list[str] = []
    handoffs: list[HandoffPacket] = []

    def record(path: Path) -> Path:
        artifacts.append(artifact_rel(path, project_root))
        return path

    project_profile_path = record(run_root / "00_intake" / "project_profile.json")
    user_goal_path = record(run_root / "00_intake" / "user_goal.md")
    write_json(project_profile_path, profile)
    write_text(user_goal_path, user_goal or "No explicit user goal provided.")
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "PreparationAgent",
            "00_intake",
            [],
            [project_profile_path, user_goal_path],
            ["Project profile normalized for workbench execution."],
            [],
            "LiteratureAgent",
            {"layout": profile["layout"]},
        )
    )

    source_inventory_path = record(run_root / "01_sources" / "source_inventory.json")
    dataset_inventory_path = record(run_root / "01_sources" / "dataset_inventory.json")
    literature_inventory_path = record(run_root / "01_sources" / "literature_inventory.json")
    write_json(source_inventory_path, inventory)
    write_json(dataset_inventory_path, {"items": inventory["datasets"]})
    write_json(literature_inventory_path, {"items": inventory["literature_files"]})

    clusters = build_literature_clusters(inventory)
    literature_clusters_path = record(run_root / "02_literature" / "literature_clusters.json")
    literature_brief_path = record(run_root / "02_literature" / "core_literature_brief.md")
    claim_map_path = record(run_root / "02_literature" / "claim_evidence_map.json")
    write_json(literature_clusters_path, clusters)
    write_text(
        literature_brief_path,
        "\n".join(
            [
                "# Core Literature Brief",
                "",
                "The first thesis run treats robot labor reallocation, matching-quality proxies, and skill-post mismatch as separate evidence layers.",
                "",
                "## Detected Literature Clusters",
                "",
                f"- Robot and automation files: {len(clusters['robot_labor_reallocation'])}",
                f"- Matching and mismatch files: {len(clusters['matching_and_mismatch'])}",
                f"- Identification files: {len(clusters['identification_and_bartik'])}",
            ]
        ),
    )
    write_json(
        claim_map_path,
        {
            "claims": [
                {
                    "claim": "Strict matching efficiency is not directly identified.",
                    "evidence": ["05_reference/匹配效率概念与可测代理对照表.md"],
                },
                {
                    "claim": "The thesis should frame measurable outcomes as allocation quality, search-friction proxies, and mismatch.",
                    "evidence": ["04_paper/sections_v21", "05_reference"],
                },
            ]
        },
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "LiteratureAgent",
            "02_literature",
            [literature_inventory_path],
            [literature_clusters_path, literature_brief_path, claim_map_path],
            ["Literature evidence is separated into robot, matching, and identification clusters."],
            ["File-level inventory is not a substitute for full-text causal claim verification."],
            "ResearchStrategistAgent",
        )
    )

    research_plan_path = record(run_root / "03_strategy" / "research_plan.md")
    identification_plan_path = record(run_root / "03_strategy" / "identification_plan.md")
    empirical_plan_path = record(run_root / "03_strategy" / "empirical_plan.md")
    write_text(
        research_plan_path,
        "# Research Plan\n\nPrimary question: how industrial robot exposure affects worker allocation outcomes, job-search frictions, and skill-post mismatch.\n",
    )
    write_text(
        identification_plan_path,
        "# Identification Plan\n\nUse Bartik IV as the main identification strategy and keep weak-IV caveats explicit.\n",
    )
    write_text(
        empirical_plan_path,
        "# Empirical Plan\n\nUse CFPS for outcome-layer results, CLDS for mechanism-layer checks, and CGSS for concept calibration.\n",
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ResearchStrategistAgent",
            "03_strategy",
            [project_profile_path, literature_brief_path, claim_map_path],
            [research_plan_path, identification_plan_path, empirical_plan_path],
            ["Bartik IV remains the main identification path for the first thesis run."],
            ["Weak-IV language must stay cautious in draft and handoff files."],
            "ModelingAgent",
        )
    )

    modeling_report_path = record(run_root / "04_modeling" / "modeling_report.json")
    diagnostics_report_path = record(run_root / "04_modeling" / "diagnostics_report.md")
    write_json(
        modeling_report_path,
        {
            "mode": mode,
            "detected_code_files": inventory["code_files"],
            "execution_policy": "audit existing scripts in dry-run" if mode == "dry-run" else "live execution requires explicit script selection",
        },
    )
    write_text(
        diagnostics_report_path,
        "# Diagnostics Report\n\nDry-run records existing data, code, and result availability without mutating raw data.\n",
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ModelingAgent",
            "04_modeling",
            [empirical_plan_path],
            [modeling_report_path, diagnostics_report_path],
            ["Existing empirical scripts are indexed before new execution is attempted."],
            ["Dry-run does not prove empirical estimates are current."],
            "VisualizationAgent",
        )
    )

    results_index_path = record(run_root / "05_results" / "results_index.json")
    table_plan_path = record(run_root / "05_results" / "table_plan.md")
    figure_plan_path = record(run_root / "05_results" / "figure_plan.md")
    write_json(results_index_path, {"items": inventory["results_files"]})
    write_text(table_plan_path, "# Table Plan\n\nUse existing indexed thesis tables before generating new tables.\n")
    write_text(figure_plan_path, "# Figure Plan\n\nUse existing thesis figures and figure scripts as first-class artifacts.\n")
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "VisualizationAgent",
            "05_results",
            [modeling_report_path],
            [results_index_path, table_plan_path, figure_plan_path],
            ["Results are indexed before manuscript claims are rewritten."],
            ["Some visual artifacts may still be generated by another IDE and need later sync."],
            "WritingAgent",
        )
    )

    manuscript_source, manuscript_source_rel = read_manuscript_source(project_root, inventory)
    paper_draft_path = record(run_root / "06_writing" / "paper_draft.md")
    section_status_path = record(run_root / "06_writing" / "section_status.json")
    if mode == "live" and manuscript_source:
        write_text(paper_draft_path, normalize_markdown_for_run(manuscript_source, project_root))
    else:
        write_text(
            paper_draft_path,
            "\n".join(
                [
                    "# Paper Draft",
                    "",
                    "This draft is generated from inspected sources and preserves the matching-efficiency boundary.",
                    "",
                    "## Source Snapshot",
                    manuscript_source[:6000] if manuscript_source else "No manuscript source detected.",
                ]
            ),
        )
    write_json(
        section_status_path,
        {
            "sections_detected": [item["path"] for item in inventory["manuscript_sections"]],
            "source_markdown": manuscript_source_rel,
            "status": "drafted",
        },
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "WritingAgent",
            "06_writing",
            [research_plan_path, identification_plan_path, results_index_path, claim_map_path],
            [paper_draft_path, section_status_path],
            ["Draft generation must preserve concept boundaries and evidence references."],
            ["Generated draft requires independent review before final formatting."],
            "ReviewerAgent",
        )
    )

    review_report_path = record(run_root / "07_review" / "review_report.md")
    revision_plan_path = record(run_root / "07_review" / "revision_plan.md")
    reviewer_decision_path = record(run_root / "07_review" / "reviewer_decision.json")
    review_payload = build_review_payload(read_text(paper_draft_path), mode, manuscript_source_rel)
    review_payload["mode"] = mode
    review = ReviewPacket(
        run_id=run_id,
        reviewer="ReviewerAgent",
        target_agent="WritingAgent",
        target_artifact=artifact_rel(paper_draft_path, project_root),
        decision=review_payload["decision"],
        revision_requests=review_payload["revision_requests"],
        strengths=review_payload["strengths"],
        risks=review_payload["risks"],
    )
    write_real_review_files(review_report_path, revision_plan_path, review_payload)
    write_json(reviewer_decision_path, review.to_dict())
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ReviewerAgent",
            "07_review",
            [paper_draft_path],
            [review_report_path, revision_plan_path, reviewer_decision_path],
            ["Reviewer is independent from WritingAgent."],
            review.risks,
            "FormatterAgent",
        )
    )

    tex_path = record(run_root / "08_final" / "paper_draft.tex")
    docx_path = record(run_root / "08_final" / "paper_draft.docx")
    formatting_report_path = record(run_root / "08_final" / "formatting_report.md")
    write_text(tex_path, "\\section{Draft}\nGenerated draft placeholder for TeX export.\n")
    if mode == "live":
        formatting_result = build_hqu_docx(project_root, paper_draft_path, docx_path, formatting_report_path)
    else:
        write_text(docx_path, "DOCX export placeholder recorded by dry-run.\n")
        write_text(formatting_report_path, "# Formatting Report\n\nDry-run recorded the Word export path. Live mode will call the formatter.\n")
        formatting_result = {"status": "dry-run", "returncode": 0}
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "FormatterAgent",
            "08_final",
            [paper_draft_path, reviewer_decision_path],
            [tex_path, docx_path, formatting_report_path],
            ["Word output path is recorded for the A experience."],
            [] if formatting_result["status"] == "completed" else [f"Formatter status: {formatting_result['status']}"],
            None,
            {"formatting_result": formatting_result},
        )
    )

    manifest_path = run_root / "run_manifest.json"
    artifacts.append(artifact_rel(manifest_path, project_root))
    manifest = OrchestrationManifest(
        run_id=run_id,
        project_id=profile.get("title") or project_root.name,
        project_root=str(project_root),
        run_root=str(run_root),
        mode=mode,
        supervisor={
            "name": "Supervisor",
            "status": "completed",
            "created_at": utc_now(),
            "user_goal": user_goal,
        },
        agents=[
            {"name": packet.agent, "stage": packet.stage, "status": packet.status}
            for packet in handoffs
        ],
        review_loop={
            "writer": "WritingAgent",
            "reviewer": "ReviewerAgent",
            "decision": review.decision,
            "iterations": 1,
            "status": "completed",
        },
        artifacts=artifacts,
        status="completed",
    )
    write_json(manifest_path, manifest.to_dict())
    return manifest.to_dict()


def orchestrate_project(project_root: Path, run_live: bool = False) -> dict[str, Any]:
    mode = "live" if run_live else "dry-run"
    return run_workbench(project_root, mode=mode, user_goal="Legacy orchestration endpoint")
