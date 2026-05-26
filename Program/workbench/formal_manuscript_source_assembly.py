from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.formal_paper_package_manifest import PACKAGE_SECTION_SPECS
from workbench.paper_package import SECTION_TARGETS, relative_or_absolute, slugify
from workbench.paper_quality import REQUIRED_SECTIONS
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_SOURCE_MANIFEST = "Results/json/formal_paper_package_manifest.json"
DEFAULT_REPORT_PATH = "Results/json/formal_manuscript_source_map.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_manuscript_source_map.md"
DEFAULT_PACKAGE_ROOT = "Submissions/formal_package"
SECTION_SOURCES_FILENAME = "section_sources.json"


def build_formal_manuscript_source_map(
    project_root: Path,
    source_manifest: dict[str, Any],
    source_manifest_path: Path,
    package_root: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    blocking_reasons = build_blocking_reasons(project_root, source_manifest, package_root)
    ready = not blocking_reasons

    section_sources: list[dict[str, Any]] = []
    section_sources_path = package_root / "manuscript" / SECTION_SOURCES_FILENAME
    if ready:
        section_sources = build_section_sources(project_root, package_root)
        write_section_source_artifacts(project_root, package_root, source_manifest_path, section_sources)

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_manuscript_source_map.v1",
        "generated_at": utc_now(),
        "source_manifest": relative_or_absolute(source_manifest_path, project_root),
        "package_root": relative_or_absolute(package_root, project_root),
        "section_sources_path": relative_or_absolute(section_sources_path, project_root),
        "status": "formal_manuscript_sources_ready" if ready else "blocked_by_manifest",
        "blocking_reasons": blocking_reasons,
        "can_prepare_pdf_preflight": ready,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "section_sources": section_sources,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(ready),
        "next_action": build_next_action(ready),
    }


def build_blocking_reasons(project_root: Path, source_manifest: dict[str, Any], package_root: Path) -> list[str]:
    reasons: list[str] = []
    if source_manifest.get("status") != "formal_package_manifest_ready" or not source_manifest.get("can_build_package"):
        reasons.append("manifest_not_ready_for_source_assembly")
    if source_manifest.get("this_command_wrote_final_outputs"):
        reasons.append("manifest_claims_final_output_write")
    if source_manifest.get("formal_state_guard", {}).get("changed"):
        reasons.append("manifest_formal_state_changed")

    package_sections = {
        section.get("category"): section
        for section in source_manifest.get("package_sections", [])
        if section.get("category")
    }
    for spec in PACKAGE_SECTION_SPECS:
        category = spec["category"]
        section = package_sections.get(category)
        if section is None:
            reasons.append(f"manifest_missing_package_section:{category}")
            continue
        section_dir = project_root / str(section.get("directory") or package_root / spec["directory_name"])
        if not section_dir.exists():
            reasons.append(f"package_section_directory_missing:{category}")
    return reasons


def build_section_sources(project_root: Path, package_root: Path) -> list[dict[str, Any]]:
    sections_dir = package_root / "manuscript" / "sections"
    section_sources: list[dict[str, Any]] = []
    for order, section in enumerate(REQUIRED_SECTIONS, start=1):
        target = SECTION_TARGETS[section]
        source_path = sections_dir / f"{order:02d}-{slugify(section)}.md"
        section_sources.append(
            {
                "order": order,
                "section": section,
                "source_path": relative_or_absolute(source_path, project_root),
                "status": "source_placeholder_ready",
                "target_length": target["target"],
                "agent": target["agent"],
                "purpose": target["purpose"],
                "evidence_requirements": build_evidence_requirements(section),
                "can_write_final_paper": False,
            }
        )
    return section_sources


def build_evidence_requirements(section: str) -> list[str]:
    requirements = {
        "Abstract": ["approved_findings", "method_gate_report", "verified_bibliography"],
        "Introduction": ["research_question", "contribution_matrix", "approved_findings"],
        "Literature and Contribution": ["verified_bibliography", "contribution_matrix", "citation_verification_log"],
        "Institutional Background / Theory / Context": ["domain_notes", "verified_context_sources"],
        "Data and Measurement": ["variable_role_set", "data_profile", "sample_profile"],
        "Empirical Strategy": ["design_spec", "method_gate_report", "method_diagnostics_report"],
        "Main Results": ["method_execution_result", "regression_tables", "figure_manifest"],
        "Robustness / Mechanisms / Heterogeneity": ["robustness_matrix", "method_diagnostics_report"],
        "Conclusion": ["approved_findings", "limitations_register", "reviewer_scorecard_report"],
        "References": ["verified_bibliography", "citation_verification_log"],
    }
    return requirements.get(section, ["source_evidence"])


def write_section_source_artifacts(
    project_root: Path,
    package_root: Path,
    source_manifest_path: Path,
    section_sources: list[dict[str, Any]],
) -> tuple[Path, list[Path]]:
    manuscript_root = package_root / "manuscript"
    sections_dir = manuscript_root / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    written_paths: list[Path] = []
    for section_source in section_sources:
        path = project_root / section_source["source_path"]
        path.write_text(build_section_placeholder(source_manifest_path, section_source), encoding="utf-8")
        written_paths.append(path)

    section_sources_path = manuscript_root / SECTION_SOURCES_FILENAME
    section_sources_path.write_text(
        json.dumps(
            {
                "schema_version": "p5.formal_manuscript_section_sources.v1",
                "generated_at": utc_now(),
                "source_manifest": relative_or_absolute(source_manifest_path, project_root),
                "draft_layer_only": True,
                "formal_paper_write_allowed": False,
                "sections": section_sources,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return section_sources_path, written_paths


def build_section_placeholder(source_manifest_path: Path, section_source: dict[str, Any]) -> str:
    evidence = "\n".join(f"- `{item}`" for item in section_source["evidence_requirements"])
    return (
        f"# {section_source['section']}\n\n"
        f"- Status: `{section_source['status']}`\n"
        f"- Agent: `{section_source['agent']}`\n"
        f"- Target length: `{section_source['target_length']}`\n"
        f"- Source manifest: `{source_manifest_path.name}`\n"
        "- Final paper write: `false`\n\n"
        "## Purpose\n\n"
        f"{section_source['purpose']}\n\n"
        "## Evidence required before writing\n\n"
        f"{evidence}\n\n"
        "## Draft source\n\n"
        "本文件是正式论文包的章节源占位。下一轮由对应 Agent 读取证据后填充内容；"
        "在人工确认前不得把本文件视为正式终稿。\n"
    )


def write_formal_manuscript_source_map_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P5-C 正式稿源装配清单",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Can prepare PDF preflight: `{str(report.get('can_prepare_pdf_preflight')).lower()}`",
        f"- Source manifest: `{report.get('source_manifest')}`",
        f"- Section source index: `{report.get('section_sources_path')}`",
        "- 正式层写回：未发生",
        "- 最终 PDF/docx：未生成",
        "",
        "## 章节源",
        "",
    ]
    sources = report.get("section_sources") or []
    if sources:
        for source in sources:
            lines.append(
                f"- `{source['section']}` -> `{source['source_path']}` "
                f"({source['agent']}, {source['target_length']})"
            )
    else:
        lines.append("- 未生成章节源。")
    blockers = report.get("blocking_reasons") or []
    if blockers:
        lines.extend(["", "## 阻断原因", ""])
        lines.extend(f"- `{reason}`" for reason in blockers)
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_agent_team_schedule(ready: bool) -> dict[str, Any]:
    return {
        "call_when": "after_formal_package_manifest_before_source_assembly",
        "called_agents": [
            "ManuscriptAgent",
            "LiteratureAgent",
            "MethodAgent",
            "DataAgent",
            "ExecutionAgent",
            "VerifierAgent",
        ],
        "recall_when": "after_formal_manuscript_source_map_written",
        "next_call_when": "before_pdf_export_preflight",
        "integration_owner": "MainAgent",
        "boundary": "本节点只把正式包骨架映射为章节源占位和证据要求；不生成最终 PDF/docx，不写正式层状态。",
        "ready": ready,
    }


def build_next_action(ready: bool) -> dict[str, str]:
    if ready:
        return {
            "id": "run_pdf_export_preflight",
            "label": "运行 PDF 导出预检",
            "description": "检查章节源、文献、方法、结果和复现说明是否足够进入 PDF-first 导出。",
        }
    return {
        "id": "fix_formal_package_manifest",
        "label": "修复正式包 manifest",
        "description": "先让 P5-B manifest ready，并补齐正式包目录结构，再装配章节源。",
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
