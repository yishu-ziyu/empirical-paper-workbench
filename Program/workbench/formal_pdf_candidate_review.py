from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader

from workbench.export import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_CANDIDATE_REPORT = "Results/json/formal_pdf_candidate_report.json"
DEFAULT_REVIEW_REPORT = "Results/json/formal_pdf_candidate_review.json"
DEFAULT_REVIEW_DOC = "Reviews/formal_pdf_candidate_review.md"
DEFAULT_FINAL_PREFLIGHT = "Results/json/formal_pdf_final_writeback_preflight.json"


def build_formal_pdf_candidate_review(
    project_root: Path,
    *,
    candidate_report_path: Path,
    output_report_path: Path,
    output_review_path: Path,
    output_final_preflight_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    candidate = load_optional_json(candidate_report_path)
    candidate_pdf_path = resolve_project_path(project_root, str(candidate.get("output_pdf") or ""))
    candidate_qmd_path = resolve_project_path(project_root, str(candidate.get("output_qmd") or ""))

    pdf_metadata = inspect_pdf(candidate_pdf_path, project_root)
    machine_review = build_machine_review(candidate, candidate_pdf_path, candidate_qmd_path, pdf_metadata)
    blocking_reasons = machine_review["blocking_checks"]
    ready = not blocking_reasons
    after = snapshot_formal_state(project_root)

    status = "ready_for_final_approval_review" if ready else "blocked_by_pdf_candidate_review"
    report = {
        "schema_version": "p5.formal_pdf_candidate_review.v1",
        "generated_at": utc_now(),
        "status": status,
        "candidate_layer_only": True,
        "source_candidate_report": relative_or_absolute(candidate_report_path, project_root),
        "candidate_pdf": relative_or_absolute(candidate_pdf_path, project_root) if candidate_pdf_path else None,
        "candidate_qmd": relative_or_absolute(candidate_qmd_path, project_root) if candidate_qmd_path else None,
        "output_report": relative_or_absolute(output_report_path, project_root),
        "output_review": relative_or_absolute(output_review_path, project_root),
        "output_final_preflight": relative_or_absolute(output_final_preflight_path, project_root),
        "section_count": len(candidate.get("sections") or []),
        "sections": candidate.get("sections") or [],
        "pdf_metadata": pdf_metadata,
        "machine_review": machine_review,
        "blocking_reasons": blocking_reasons,
        "requires_human_approval": True,
        "can_request_final_approval": ready,
        "final_pdf_approved": False,
        "final_writeback_allowed": False,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "agent_team_schedule": {
            "call_when": "before_pdf_candidate_review",
            "attempted_in_current_codex_session": True,
            "current_session_result": "blocked_by_agent_thread_limit",
            "called_agents": ["ReviewerAgent", "VerifierAgent", "ExportAgent"],
            "recall_when": "after_pdf_candidate_review_and_final_preflight_written",
            "next_call_when": "before_final_pdf_or_docx_approval",
            "integration_owner": "MainAgent",
        },
        "next_action": build_next_action(ready, blocking_reasons),
        "write_boundary": (
            "本节点只生成候选 PDF 审阅报告和最终写回预检；不移动候选 PDF，"
            "不生成最终 PDF/docx，不写 state/product 正式状态。"
        ),
    }
    final_preflight = build_final_preflight(project_root, report, output_report_path)
    return report, final_preflight, 0 if ready else 2


def build_machine_review(
    candidate: dict[str, Any],
    candidate_pdf_path: Path | None,
    candidate_qmd_path: Path | None,
    pdf_metadata: dict[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "candidate_report_ready",
        candidate.get("status") == "pdf_candidate_ready",
        "candidate_report_not_pdf_ready",
    )
    add_check(checks, "candidate_layer_only", candidate.get("candidate_layer_only") is True)
    add_check(checks, "candidate_did_not_write_formal_state", candidate.get("this_command_wrote_formal_state") is False)
    add_check(checks, "candidate_did_not_write_final_outputs", candidate.get("this_command_wrote_final_outputs") is False)
    add_check(checks, "candidate_formal_state_guard_clean", not candidate.get("formal_state_guard", {}).get("changed"))
    add_check(checks, "candidate_pdf_exists", bool(candidate_pdf_path and candidate_pdf_path.exists()))
    add_check(checks, "candidate_qmd_exists", bool(candidate_qmd_path and candidate_qmd_path.exists()))
    add_check(checks, "candidate_pdf_readable", pdf_metadata.get("status") == "readable")
    add_check(checks, "candidate_has_sections", bool(candidate.get("sections")))
    add_check(checks, "candidate_render_succeeded", candidate.get("render_result", {}).get("returncode") in (0, None))
    return {
        "status": "passed" if all(item["passed"] for item in checks) else "blocked",
        "checks": checks,
        "blocking_checks": [item["blocking_reason"] for item in checks if not item["passed"]],
    }


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    blocking_reason: str | None = None,
) -> None:
    checks.append(
        {
            "id": check_id,
            "passed": bool(passed),
            "blocking_reason": blocking_reason or check_id,
        }
    )


def inspect_pdf(path: Path | None, project_root: Path) -> dict[str, Any]:
    if path is None:
        return {"status": "missing", "path": None, "pages": 0, "bytes": 0}
    if not path.exists():
        return {"status": "missing", "path": relative_or_absolute(path, project_root), "pages": 0, "bytes": 0}
    try:
        reader = PdfReader(str(path))
        info = reader.metadata or {}
        return {
            "status": "readable",
            "path": relative_or_absolute(path, project_root),
            "pages": len(reader.pages),
            "bytes": path.stat().st_size,
            "title": str(info.get("/Title") or ""),
            "author": str(info.get("/Author") or ""),
        }
    except Exception as exc:  # pragma: no cover - defensive for malformed PDFs in user projects.
        return {
            "status": "unreadable",
            "path": relative_or_absolute(path, project_root),
            "pages": 0,
            "bytes": path.stat().st_size,
            "error": str(exc),
        }


def build_final_preflight(project_root: Path, review_report: dict[str, Any], output_report_path: Path) -> dict[str, Any]:
    ready = bool(review_report.get("can_request_final_approval"))
    return {
        "schema_version": "p5.formal_pdf_final_writeback_preflight.v1",
        "generated_at": review_report.get("generated_at"),
        "status": "ready_for_human_final_approval" if ready else "blocked_by_pdf_candidate_review",
        "source_review": relative_or_absolute(output_report_path, project_root),
        "candidate_pdf": review_report.get("candidate_pdf"),
        "candidate_qmd": review_report.get("candidate_qmd"),
        "requires_human_approval": True,
        "can_request_final_approval": ready,
        "final_writeback_allowed": False,
        "final_pdf_approved": False,
        "blocking_reasons": review_report.get("blocking_reasons") or [],
        "approval_contract": {
            "required_before_final_writeback": [
                "human_pdf_candidate_review",
                "final_output_scope_reviewed",
                "formal_state_guard_confirmed",
            ],
            "approval_path": "state/product/writeback_approvals.json",
            "ready_for_approval": ready,
            "canonical_write_policy": "候选 PDF 只有人工批准后才能进入最终 PDF/docx 写回节点。",
        },
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": review_report.get("formal_state_guard"),
        "next_action": review_report.get("next_action"),
    }


def build_next_action(ready: bool, blocking_reasons: list[str]) -> dict[str, Any]:
    if ready:
        return {
            "id": "human_review_pdf_candidate",
            "label": "人工审阅 PDF 候选稿并决定是否进入最终批准",
            "requires_human": True,
        }
    return {
        "id": "repair_pdf_candidate",
        "label": "修复 PDF 候选稿或重跑候选渲染",
        "requires_human": True,
        "blocking_reasons": blocking_reasons,
    }


def write_formal_pdf_candidate_review_outputs(
    report_path: Path,
    review_path: Path,
    final_preflight_path: Path,
    report: dict[str, Any],
    final_preflight: dict[str, Any],
) -> tuple[Path, Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    final_preflight_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review_markdown(report, final_preflight), encoding="utf-8")
    final_preflight_path.write_text(json.dumps(final_preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path, review_path, final_preflight_path


def render_review_markdown(report: dict[str, Any], final_preflight: dict[str, Any]) -> str:
    checks = "\n".join(
        f"- [{'x' if item.get('passed') else ' '}] `{item.get('id')}`"
        for item in report.get("machine_review", {}).get("checks", [])
    )
    if not checks:
        checks = "- 当前没有机器审阅检查。"
    sections = "\n".join(
        f"- {item.get('section')}：`{item.get('source_path')}`"
        for item in report.get("sections", [])
    )
    if not sections:
        sections = "- 当前没有章节清单。"
    return f"""# P5-E4 PDF 候选稿审阅

## 当前状态

- 状态：`{report.get("status")}`
- 候选 PDF：`{report.get("candidate_pdf")}`
- 候选 QMD：`{report.get("candidate_qmd")}`
- PDF 页数：`{report.get("pdf_metadata", {}).get("pages")}`
- PDF 可读状态：`{report.get("pdf_metadata", {}).get("status")}`
- 最终写回预检：`{report.get("output_final_preflight")}`
- 正式层写回：`{str(report.get("this_command_wrote_formal_state")).lower()}`
- 最终产物写回：`{str(report.get("this_command_wrote_final_outputs")).lower()}`

## 机器审阅检查

{checks}

## 章节清单

{sections}

## 人工审阅入口

- 先审阅候选 PDF 的章节顺序、表图引用、证据边界、页眉页脚、引用列表和复现说明。
- 通过后进入 `{final_preflight.get("next_action", {}).get("id")}`。
- 当前命令不会把候选 PDF 晋升为最终 PDF，也不会写入正式状态。

## Agent Team 调用节奏

- 调用点：候选 PDF 审阅前调用 ReviewerAgent / VerifierAgent / ExportAgent。
- 当前会话结果：`{report.get("agent_team_schedule", {}).get("current_session_result")}`
- 收回点：审阅报告和最终写回预检写出后收回，由主线程集成状态。
"""


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
