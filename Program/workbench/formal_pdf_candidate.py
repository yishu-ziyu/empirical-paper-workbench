from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import pdf_export_preflight, relative_or_absolute, run_export_command
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_PREFLIGHT_REPORT = "Results/json/formal_pdf_export_preflight.json"
DEFAULT_SOURCE_MAP = "Results/json/formal_manuscript_source_map.json"
DEFAULT_REPORT_PATH = "Results/json/formal_pdf_candidate_report.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_pdf_candidate.md"
DEFAULT_QMD_PATH = "Submissions/formal_package/manuscript/paper_candidate.qmd"
DEFAULT_PDF_PATH = "Submissions/formal_package/paper_candidate.pdf"
DEFAULT_REPRODUCE_SCRIPT = "Submissions/formal_package/reproducibility/render_pdf_candidate.sh"
DEFAULT_LOG_PATH = "Results/logs/formal_pdf_candidate_render.log"

PLACEHOLDER_MARKERS = ["source_placeholder_ready", "章节源占位"]


def build_formal_pdf_candidate(
    project_root: Path,
    *,
    preflight_report_path: Path,
    source_map_path: Path,
    output_report_path: Path,
    output_review_path: Path,
    output_qmd_path: Path,
    output_pdf_path: Path,
    reproduce_script_path: Path,
    render_mode: str,
    log_path: Path | None = None,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    log_path = log_path or project_root / DEFAULT_LOG_PATH
    preflight = load_optional_json(preflight_report_path)
    if not preflight.get("can_export_pdf_candidate"):
        report = build_blocked_report(
            project_root,
            before,
            preflight_report_path,
            source_map_path,
            output_report_path,
            output_qmd_path,
            output_pdf_path,
            reproduce_script_path,
            status="blocked_by_pdf_preflight",
            blocking_reasons=preflight.get("blocking_reasons") or ["pdf_preflight_not_ready"],
            preflight_status=preflight.get("status"),
        )
        return report, 2

    source_map = load_json(source_map_path)
    section_sources_path = resolve_project_path(
        project_root,
        str(source_map.get("section_sources_path") or preflight.get("section_sources_path") or ""),
    )
    if section_sources_path is None or not section_sources_path.exists():
        report = build_blocked_report(
            project_root,
            before,
            preflight_report_path,
            source_map_path,
            output_report_path,
            output_qmd_path,
            output_pdf_path,
            reproduce_script_path,
            status="blocked_by_section_sources",
            blocking_reasons=["section_sources_index_missing"],
            preflight_status=preflight.get("status"),
        )
        return report, 2

    section_sources = load_json(section_sources_path)
    sections = list(section_sources.get("sections") or [])
    section_payloads, section_issues = load_section_payloads(project_root, sections)
    if section_issues:
        report = build_blocked_report(
            project_root,
            before,
            preflight_report_path,
            source_map_path,
            output_report_path,
            output_qmd_path,
            output_pdf_path,
            reproduce_script_path,
            status="blocked_by_section_sources",
            blocking_reasons=sorted(set(section_issues)),
            preflight_status=preflight.get("status"),
        )
        return report, 2

    write_qmd_candidate(output_qmd_path, section_payloads)
    command = [
        "quarto",
        "render",
        str(output_qmd_path),
        "--to",
        "pdf",
        "--output",
        output_pdf_path.name,
    ]
    export_preflight = pdf_export_preflight(project_root, output_qmd_path, output_pdf_path)
    write_reproduce_script(
        reproduce_script_path,
        project_root,
        preflight_report_path,
        source_map_path,
        output_report_path,
        output_review_path,
        output_qmd_path,
        output_pdf_path,
        reproduce_script_path,
    )

    render_result: dict[str, Any] = {
        "attempted": False,
        "returncode": None,
        "log_path": relative_or_absolute(log_path, project_root),
    }
    status = "candidate_source_ready"
    exit_code = 0
    if render_mode == "auto" and export_preflight.get("status") == "ready":
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        completed = run_export_command(command, log_path, cwd=output_pdf_path.parent)
        render_result.update(
            {
                "attempted": True,
                "returncode": completed.returncode,
                "stdout_excerpt": completed.stdout[-2000:],
                "stderr_excerpt": completed.stderr[-2000:],
            }
        )
        if completed.returncode == 0 and output_pdf_path.exists():
            status = "pdf_candidate_ready"
        else:
            status = "render_failed"
            exit_code = completed.returncode or 1
    elif render_mode == "auto":
        status = "candidate_source_ready_toolchain_blocked"
    elif render_mode != "source-only":
        raise ValueError(f"Unsupported render_mode: {render_mode}")

    after = snapshot_formal_state(project_root)
    report = {
        "schema_version": "p5.formal_pdf_candidate.v1",
        "generated_at": utc_now(),
        "status": status,
        "candidate_layer_only": True,
        "can_render_pdf_candidate": export_preflight.get("status") == "ready",
        "render_mode": render_mode,
        "preflight_report": relative_or_absolute(preflight_report_path, project_root),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "section_sources_path": relative_or_absolute(section_sources_path, project_root),
        "output_report": relative_or_absolute(output_report_path, project_root),
        "output_review": relative_or_absolute(output_review_path, project_root),
        "output_qmd": relative_or_absolute(output_qmd_path, project_root),
        "output_pdf": relative_or_absolute(output_pdf_path, project_root),
        "output_pdf_exists": output_pdf_path.exists(),
        "reproduce_script": relative_or_absolute(reproduce_script_path, project_root),
        "render_log": relative_or_absolute(log_path, project_root),
        "section_count": len(section_payloads),
        "sections": [
            {
                "section": item["section"],
                "source_path": item["source_path"],
                "agent": item.get("agent"),
                "target_length": item.get("target_length"),
                "evidence_requirements": item.get("evidence_requirements", []),
            }
            for item in section_payloads
        ],
        "export_preflight": export_preflight,
        "render_command": command,
        "render_result": render_result,
        "blocking_reasons": [] if status != "candidate_source_ready_toolchain_blocked" else ["pdf_toolchain_not_ready"],
        "final_pdf_approved": False,
        "can_promote_to_final": False,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": {
            "call_when": "before_candidate_pdf_render",
            "attempted_in_current_codex_session": True,
            "current_session_result": "blocked_by_agent_thread_limit",
            "called_agents": ["ExportAgent", "VerifierAgent"],
            "recall_when": "after_candidate_report_and_review_doc_written",
            "next_call_when": "before_human_approval_or_final_export",
            "integration_owner": "MainAgent",
        },
        "next_action": {
            "id": "human_pdf_candidate_review",
            "label": "人工审阅 PDF 候选稿",
            "requires_human": True,
        },
        "write_boundary": (
            "本节点只生成 PDF 候选稿、QMD 候选源、审阅报告和复跑脚本；"
            "不写 state/product 正式状态，不批准最终 PDF/docx。"
        ),
    }
    return report, exit_code


def build_blocked_report(
    project_root: Path,
    before: dict[str, dict[str, Any]],
    preflight_report_path: Path,
    source_map_path: Path,
    output_report_path: Path,
    output_qmd_path: Path,
    output_pdf_path: Path,
    reproduce_script_path: Path,
    *,
    status: str,
    blocking_reasons: list[str],
    preflight_status: str | None,
) -> dict[str, Any]:
    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_pdf_candidate.v1",
        "generated_at": utc_now(),
        "status": status,
        "candidate_layer_only": True,
        "can_render_pdf_candidate": False,
        "preflight_status": preflight_status,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "preflight_report": relative_or_absolute(preflight_report_path, project_root),
        "source_map": relative_or_absolute(source_map_path, project_root),
        "output_report": relative_or_absolute(output_report_path, project_root),
        "output_qmd": relative_or_absolute(output_qmd_path, project_root),
        "output_pdf": relative_or_absolute(output_pdf_path, project_root),
        "output_pdf_exists": output_pdf_path.exists(),
        "reproduce_script": relative_or_absolute(reproduce_script_path, project_root),
        "section_count": 0,
        "sections": [],
        "final_pdf_approved": False,
        "can_promote_to_final": False,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": {
            "call_when": "after_pdf_preflight_repaired",
            "attempted_in_current_codex_session": True,
            "current_session_result": "blocked_by_agent_thread_limit",
            "called_agents": ["ExportAgent", "VerifierAgent"],
            "integration_owner": "MainAgent",
        },
        "next_action": {
            "id": "repair_pdf_preflight_inputs",
            "label": "先修复 PDF 预检输入",
            "requires_human": True,
        },
        "write_boundary": (
            "预检未通过时，本节点只写阻断报告和审阅文档；不生成 QMD/PDF 候选稿，"
            "不写 state/product 正式状态。"
        ),
    }


def write_formal_pdf_candidate_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review_doc(report), encoding="utf-8")
    return report_path, review_path


def load_section_payloads(project_root: Path, sections: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    payloads: list[dict[str, Any]] = []
    issues: list[str] = []
    for section in sorted(sections, key=lambda item: int(item.get("order") or 0)):
        source_path = resolve_project_path(project_root, str(section.get("source_path") or ""))
        if source_path is None or not source_path.exists():
            issues.append("section_source_missing")
            continue
        text = source_path.read_text(encoding="utf-8")
        if section.get("status") != "source_draft_ready":
            issues.append("section_not_source_draft_ready")
        if any(marker in text for marker in PLACEHOLDER_MARKERS):
            issues.append("section_source_placeholder")
        payload = dict(section)
        payload["source_path"] = relative_or_absolute(source_path, project_root)
        payload["text"] = text
        payloads.append(payload)
    return payloads, issues


def write_qmd_candidate(path: Path, section_payloads: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "---",
        'title: "Formal Paper Candidate"',
        'author: "Local Empirical Research OS"',
        "format:",
        "  pdf:",
        "    pdf-engine: xelatex",
        "    toc: true",
        "    number-sections: true",
        "    keep-tex: true",
        "mainfont: Times New Roman",
        "CJKmainfont: Songti SC",
        "header-includes:",
        "  - \\usepackage{xeCJK}",
        "  - \\setCJKmainfont{Songti SC}",
        "---",
        "",
        "<!-- candidate_layer_only: true -->",
        "<!-- final_pdf_approved: false -->",
        "",
    ]
    for item in section_payloads:
        text = item["text"].strip()
        parts.extend(
            [
                f"<!-- source_path: {item['source_path']} -->",
                f"<!-- agent: {item.get('agent')} -->",
                f"<!-- target_length: {item.get('target_length')} -->",
                text,
                "",
            ]
        )
    path.write_text("\n".join(parts), encoding="utf-8")


def write_reproduce_script(
    path: Path,
    project_root: Path,
    preflight_report_path: Path,
    source_map_path: Path,
    output_report_path: Path,
    output_review_path: Path,
    output_qmd_path: Path,
    output_pdf_path: Path,
    reproduce_script_path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            'cd "$(dirname "$0")/../../.."',
            "",
            "python3 Program/formal_pdf_candidate.py \\",
            "  --project-root . \\",
            f"  --preflight-report {relative_or_absolute(preflight_report_path, project_root)} \\",
            f"  --source-map {relative_or_absolute(source_map_path, project_root)} \\",
            f"  --output-report {relative_or_absolute(output_report_path, project_root)} \\",
            f"  --output-review {relative_or_absolute(output_review_path, project_root)} \\",
            f"  --output-qmd {relative_or_absolute(output_qmd_path, project_root)} \\",
            f"  --output-pdf {relative_or_absolute(output_pdf_path, project_root)} \\",
            f"  --reproduce-script {relative_or_absolute(reproduce_script_path, project_root)} \\",
            "  --render-mode auto",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def render_review_doc(report: dict[str, Any]) -> str:
    sections = "\n".join(
        f"- {item['section']}：`{item['source_path']}`，agent={item.get('agent')}"
        for item in report.get("sections", [])
    )
    if not sections:
        sections = "- 当前未进入章节组装。"
    return f"""# P5-E3 PDF 候选稿

## 当前状态

- 状态：`{report.get("status")}`
- 候选层：`{str(report.get("candidate_layer_only")).lower()}`
- QMD 候选源：`{report.get("output_qmd")}`
- PDF 候选稿：`{report.get("output_pdf")}`
- PDF 是否存在：`{str(report.get("output_pdf_exists")).lower()}`
- 复跑脚本：`{report.get("reproduce_script")}`
- 正式层写回：`{str(report.get("this_command_wrote_formal_state")).lower()}`
- 最终产物写回：`{str(report.get("this_command_wrote_final_outputs")).lower()}`

## 章节来源

{sections}

## 渲染记录

- 渲染模式：`{report.get("render_mode")}`
- 渲染日志：`{report.get("render_log")}`
- 阻断原因：`{report.get("blocking_reasons")}`

## Agent Team 调用节奏

- 调用点：候选 PDF 渲染前调用 ExportAgent / VerifierAgent 做只读复核。
- 当前会话结果：`{report.get("agent_team_schedule", {}).get("current_session_result")}`
- 收回点：候选报告、审阅文档和复跑脚本写出后收回，由主线程集成状态。

## 人工审阅

下一步是人工审阅 PDF 候选稿：检查章节顺序、排版、证据边界、表图引用和正式层写回条件。
"""


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_json(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
