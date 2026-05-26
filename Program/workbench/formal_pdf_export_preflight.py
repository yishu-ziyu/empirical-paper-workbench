from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_SOURCE_MAP = "Results/json/formal_manuscript_source_map.json"
DEFAULT_REPORT_PATH = "Results/json/formal_pdf_export_preflight.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_pdf_export_preflight.md"
DEFAULT_TASKS_PATH = "Submissions/formal_package/reproducibility/pdf_export_preflight_tasks.json"
DEFAULT_PDF_CANDIDATE = "Submissions/formal_package/paper.pdf"

PLACEHOLDER_MARKERS = [
    "source_placeholder_ready",
    "章节源占位",
]

EVIDENCE_REGISTRY: dict[str, list[str]] = {
    "approved_findings": ["Results/json/approved_findings.json"],
    "method_gate_report": ["Results/json/method_gate_report.json"],
    "verified_bibliography": ["Data/literature/processed/verified_bibliography.csv"],
    "research_question": ["state/product/research_question.json"],
    "contribution_matrix": ["Data/literature/processed/contribution_matrix.md"],
    "citation_verification_log": ["Results/json/citation_verification_log.json"],
    "domain_notes": ["Results/json/domain_notes.json"],
    "verified_context_sources": ["Results/json/verified_context_sources.json"],
    "variable_role_set": [
        "Submissions/formal_package/evidence/variable_role_set.json",
        "state/product/variable_role_set.json",
    ],
    "data_profile": [
        "Results/json/project_snapshot.json",
        "Results/json/cfps_robot_project_snapshot.json",
    ],
    "sample_profile": ["Results/json/sample_profile.json"],
    "design_spec": ["state/product/design_spec.json"],
    "method_diagnostics_report": ["Results/json/method_diagnostics_report.json"],
    "method_execution_result": ["Results/json/method_execution_result.json"],
    "regression_tables": ["Results/json/regression_tables.json"],
    "figure_manifest": ["Results/json/figure_manifest.json"],
    "robustness_matrix": ["Results/json/robustness_matrix.json"],
    "limitations_register": ["Results/json/limitations_register.json"],
    "reviewer_scorecard_report": ["Results/json/reviewer_scorecard_report.json"],
}


def build_formal_pdf_export_preflight(
    project_root: Path,
    source_map_path: Path,
    *,
    output_report_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    source_map, source_map_missing = load_optional_json(source_map_path)
    blocking_reasons: list[str] = []

    if source_map_missing:
        blocking_reasons.append("source_map_missing")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_source_map",
            blocking_reasons=blocking_reasons,
        )

    source_map_ready = (
        source_map.get("status") == "formal_manuscript_sources_ready"
        and bool(source_map.get("can_prepare_pdf_preflight"))
    )
    if not source_map_ready:
        blocking_reasons.append("source_map_not_ready_for_pdf_preflight")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_source_map",
            blocking_reasons=blocking_reasons,
            source_map=source_map,
        )

    section_sources_path = resolve_project_path(
        project_root,
        str(source_map.get("section_sources_path") or ""),
    )
    if section_sources_path is None or not section_sources_path.exists():
        blocking_reasons.append("section_sources_index_missing")
        return build_blocked_report(
            project_root,
            source_map_path,
            output_report_path,
            before,
            status="blocked_by_source_map",
            blocking_reasons=blocking_reasons,
            source_map=source_map,
        )

    section_sources = load_json(section_sources_path)
    sections = list(section_sources.get("sections") or [])
    section_checks = build_section_checks(project_root, sections)
    evidence_checks = build_evidence_checks(project_root, sections)
    blocking_reasons.extend(build_content_blockers(section_checks, evidence_checks))
    next_review_tasks = build_next_review_tasks(section_checks, evidence_checks)
    ready = not blocking_reasons

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_pdf_export_preflight.v1",
        "generated_at": utc_now(),
        "preflight_report": relative_or_absolute(output_report_path, project_root),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "section_sources_path": relative_or_absolute(section_sources_path, project_root),
        "output_pdf_candidate": DEFAULT_PDF_CANDIDATE,
        "status": "ready_for_pdf_export_review" if ready else "blocked_by_source_gaps",
        "can_export_pdf_candidate": ready,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "section_checks": section_checks,
        "evidence_checks": evidence_checks,
        "next_review_tasks": next_review_tasks,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(ready, next_review_tasks),
        "next_action": build_next_action(ready),
        "write_boundary": (
            "本节点只检查正式稿章节源和证据是否达到 PDF-first 候选渲染条件；"
            "不生成 PDF/docx，不写正式论文，也不修改 state/product 正式状态。"
        ),
    }


def build_blocked_report(
    project_root: Path,
    source_map_path: Path,
    output_report_path: Path,
    before: dict[str, dict[str, Any]],
    *,
    status: str,
    blocking_reasons: list[str],
    source_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    after = snapshot_formal_state(project_root)
    section_sources_path = source_map.get("section_sources_path") if source_map else None
    return {
        "schema_version": "p5.formal_pdf_export_preflight.v1",
        "generated_at": utc_now(),
        "preflight_report": relative_or_absolute(output_report_path, project_root),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "section_sources_path": section_sources_path,
        "output_pdf_candidate": DEFAULT_PDF_CANDIDATE,
        "status": status,
        "can_export_pdf_candidate": False,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "section_checks": [],
        "evidence_checks": [],
        "next_review_tasks": [
            {
                "id": "repair_formal_manuscript_source_map",
                "agent": "VerifierAgent",
                "source": "formal_pdf_export_preflight",
                "source_artifact": relative_or_absolute(output_report_path, project_root),
                "issue": sorted(set(blocking_reasons)),
                "action": "先修复正式稿源清单和章节源索引，再进入 PDF 导出预检。",
                "review_status": "open",
            }
        ],
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "final_outputs_written": [],
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": build_agent_team_schedule(False, []),
        "next_action": build_next_action(False),
        "write_boundary": (
            "本节点只检查正式稿章节源和证据是否达到 PDF-first 候选渲染条件；"
            "不生成 PDF/docx，不写正式论文，也不修改 state/product 正式状态。"
        ),
    }


def build_section_checks(project_root: Path, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for section in sections:
        issues: list[str] = []
        path = resolve_project_path(project_root, str(section.get("source_path") or ""))
        text = ""
        if path is None or not path.exists():
            issues.append("section_source_missing")
        else:
            text = path.read_text(encoding="utf-8")

        if section.get("status") == "source_placeholder_ready":
            issues.append("section_source_placeholder")
        if any(marker in text for marker in PLACEHOLDER_MARKERS):
            issues.append("section_source_placeholder")
        if not section.get("target_length"):
            issues.append("section_target_length_missing")

        checks.append(
            {
                "section": section.get("section"),
                "source_path": section.get("source_path"),
                "agent": section.get("agent"),
                "target_length": section.get("target_length"),
                "status": "failed" if issues else "passed",
                "issues": sorted(set(issues)),
            }
        )
    return checks


def build_evidence_checks(project_root: Path, sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required_by: dict[str, set[str]] = defaultdict(set)
    for section in sections:
        section_name = str(section.get("section") or "unknown_section")
        for evidence_id in section.get("evidence_requirements") or []:
            required_by[str(evidence_id)].add(section_name)

    checks: list[dict[str, Any]] = []
    for evidence_id in sorted(required_by):
        candidate_paths = EVIDENCE_REGISTRY.get(evidence_id, [f"Results/json/{evidence_id}.json"])
        existing_paths = [
            relative_path
            for relative_path in candidate_paths
            if (project_root / relative_path).exists()
        ]
        checks.append(
            {
                "id": evidence_id,
                "status": "passed" if existing_paths else "failed",
                "candidate_paths": candidate_paths,
                "existing_paths": existing_paths,
                "required_by_sections": sorted(required_by[evidence_id]),
                "issues": [] if existing_paths else ["required_evidence_missing"],
            }
        )
    return checks


def build_content_blockers(
    section_checks: list[dict[str, Any]],
    evidence_checks: list[dict[str, Any]],
) -> list[str]:
    blockers: list[str] = []
    if any("section_source_missing" in check["issues"] for check in section_checks):
        blockers.append("section_source_missing")
    if any("section_source_placeholder" in check["issues"] for check in section_checks):
        blockers.append("section_source_placeholders_remaining")
    if any("section_target_length_missing" in check["issues"] for check in section_checks):
        blockers.append("section_target_length_missing")
    if any(check["status"] == "failed" for check in evidence_checks):
        blockers.append("required_evidence_missing")
    return blockers


def build_next_review_tasks(
    section_checks: list[dict[str, Any]],
    evidence_checks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for check in section_checks:
        if check["status"] == "passed":
            continue
        section_slug = slug_task(str(check.get("section") or "section"))
        tasks.append(
            {
                "id": f"fill_section_{section_slug}",
                "agent": check.get("agent") or "ManuscriptAgent",
                "source": "formal_pdf_export_preflight",
                "source_section": check.get("section"),
                "source_path": check.get("source_path"),
                "issue": check.get("issues", []),
                "action": "补写章节源，移除占位内容，并绑定目标长度与证据。",
                "review_status": "open",
            }
        )

    for check in evidence_checks:
        if check["status"] == "passed":
            continue
        tasks.append(
            {
                "id": f"supply_evidence_{slug_task(check['id'])}",
                "agent": infer_agent_for_evidence(check["id"]),
                "source": "formal_pdf_export_preflight",
                "evidence_id": check["id"],
                "required_by_sections": check.get("required_by_sections", []),
                "candidate_paths": check.get("candidate_paths", []),
                "issue": check.get("issues", []),
                "action": "补齐该证据文件，或在 evidence registry 中登记可验证替代来源。",
                "review_status": "open",
            }
        )
    return tasks


def write_formal_pdf_export_preflight_outputs(
    report_path: Path,
    review_path: Path,
    tasks_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")

    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    tasks_path.write_text(json.dumps(build_tasks_payload(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path, review_path, tasks_path


def build_tasks_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "p5.pdf_export_preflight_tasks.v1",
        "generated_at": utc_now(),
        "source_preflight": report.get("preflight_report"),
        "can_export_pdf_candidate": report.get("can_export_pdf_candidate"),
        "tasks": report.get("next_review_tasks", []),
    }


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P5-D PDF 导出预检",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Can export PDF candidate: `{str(report.get('can_export_pdf_candidate')).lower()}`",
        f"- Source map: `{report.get('source_map')}`",
        f"- Section source index: `{report.get('section_sources_path')}`",
        "- 正式层写回：未发生",
        "- 未生成最终 PDF/docx",
        "",
        "## 阻断原因",
        "",
    ]
    blockers = report.get("blocking_reasons") or []
    lines.extend(f"- `{reason}`" for reason in blockers) if blockers else lines.append("- 无")

    lines.extend(["", "## 章节源检查", ""])
    section_checks = report.get("section_checks") or []
    if section_checks:
        for check in section_checks:
            issues = ", ".join(check.get("issues") or ["none"])
            lines.append(f"- `{check.get('section')}`: `{check.get('status')}` ({issues})")
    else:
        lines.append("- 未执行章节源检查。")

    lines.extend(["", "## 证据检查", ""])
    evidence_checks = report.get("evidence_checks") or []
    if evidence_checks:
        for check in evidence_checks:
            lines.append(f"- `{check.get('id')}`: `{check.get('status')}`")
    else:
        lines.append("- 未执行证据检查。")

    lines.extend(["", "## 待处理任务", ""])
    tasks = report.get("next_review_tasks") or []
    if tasks:
        for task in tasks:
            lines.append(f"- `{task.get('id')}` / {task.get('agent')}: {task.get('action')}")
    else:
        lines.append("- 无。可以进入 PDF 候选渲染。")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def build_agent_team_schedule(ready: bool, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    agents = ["ExportAgent", "VerifierAgent", "ReviewerAgent"]
    agents.extend(str(task.get("agent")) for task in tasks if task.get("agent"))
    return {
        "call_when": "before_formal_pdf_export_preflight",
        "called_agents": sorted(set(agents)),
        "recall_when": "after_formal_pdf_export_preflight_written",
        "next_call_when": "before_pdf_candidate_render_or_formal_export",
        "integration_owner": "MainAgent",
        "boundary": "Agent Team 只检查 PDF 候选渲染准入；正式论文、PDF/docx 和 state/product 仍需人工确认。",
        "ready": ready,
    }


def build_next_action(ready: bool) -> dict[str, str]:
    if ready:
        return {
            "id": "render_pdf_candidate",
            "label": "渲染 PDF 候选稿",
            "description": "用已通过预检的章节源和证据生成 PDF 候选稿，仍保留人工验收门。",
        }
    return {
        "id": "resolve_pdf_export_preflight_tasks",
        "label": "补齐 PDF 预检任务",
        "description": "先处理章节源占位、缺失证据或源清单问题，再重新运行 PDF 导出预检。",
    }


def infer_agent_for_evidence(evidence_id: str) -> str:
    if evidence_id in {"verified_bibliography", "citation_verification_log", "contribution_matrix"}:
        return "LiteratureAgent"
    if evidence_id in {"method_gate_report", "method_diagnostics_report", "design_spec", "robustness_matrix"}:
        return "MethodAgent"
    if evidence_id in {"variable_role_set", "data_profile", "sample_profile"}:
        return "DataAgent"
    if evidence_id in {"method_execution_result", "regression_tables", "figure_manifest"}:
        return "ExecutionAgent"
    if evidence_id in {"approved_findings", "limitations_register", "reviewer_scorecard_report"}:
        return "ReviewerAgent"
    return "VerifierAgent"


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_optional_json(path: Path) -> tuple[dict[str, Any], bool]:
    if not path.exists():
        return {}, True
    return load_json(path), False


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def slug_task(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in value)
    return "_".join(part for part in slug.split("_") if part)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
