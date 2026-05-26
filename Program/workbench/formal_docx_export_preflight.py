from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


APPROVAL_KEY = "formal_pdf_candidate"
DEFAULT_FINAL_WRITEBACK_REPORT = "Results/json/formal_pdf_final_writeback.json"
DEFAULT_APPROVAL_REPORT = "Results/json/formal_pdf_final_approval.json"
DEFAULT_APPROVAL_LEDGER = "state/product/writeback_approvals.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_docx_export_preflight.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_docx_export_preflight.md"
DEFAULT_EXPECTED_DOCX = "Submissions/formal_package/paper.docx"


def build_formal_docx_export_preflight(
    project_root: Path,
    *,
    final_writeback_report_path: Path,
    approval_report_path: Path,
    approval_ledger_path: Path,
    expected_docx_path: Path,
    pandoc_bin: str = "pandoc",
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    final_writeback = load_json(final_writeback_report_path)
    approval_report = load_json(approval_report_path)
    approval_ledger = load_json(approval_ledger_path)
    ledger_entry = (approval_ledger.get("final_pdf_approvals") or {}).get(APPROVAL_KEY) or {}

    final_pdf = resolve_project_path(project_root, str(final_writeback.get("final_pdf") or ""))
    candidate_qmd = resolve_project_path(project_root, str(final_writeback.get("source_candidate_qmd") or ""))
    pandoc_info = inspect_pandoc(pandoc_bin)
    blocking_reasons = build_blocking_reasons(
        final_writeback=final_writeback,
        approval_report=approval_report,
        ledger_entry=ledger_entry,
        final_pdf=final_pdf,
        candidate_qmd=candidate_qmd,
        pandoc_info=pandoc_info,
    )
    status = build_status(blocking_reasons)
    export_command = build_export_command(candidate_qmd, expected_docx_path, project_root)
    after = snapshot_formal_state(project_root)
    can_export_docx = not blocking_reasons

    return {
        "schema_version": "p6.formal_docx_export_preflight.v1",
        "generated_at": utc_now(),
        "status": status,
        "source_final_pdf_writeback": relative_or_absolute(final_writeback_report_path, project_root),
        "source_approval_report": relative_or_absolute(approval_report_path, project_root),
        "source_approval_ledger": relative_or_absolute(approval_ledger_path, project_root),
        "source_candidate_qmd": relative_or_absolute(candidate_qmd, project_root) if candidate_qmd else None,
        "final_pdf": relative_or_absolute(final_pdf, project_root) if final_pdf else None,
        "expected_docx": relative_or_absolute(expected_docx_path, project_root),
        "can_export_docx": can_export_docx,
        "blocking_reasons": blocking_reasons,
        "export_command": export_command,
        "pandoc": pandoc_info,
        "this_command_wrote_docx": False,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(blocking_reasons),
    }, 0 if can_export_docx else 2


def build_blocking_reasons(
    *,
    final_writeback: dict[str, Any],
    approval_report: dict[str, Any],
    ledger_entry: dict[str, Any],
    final_pdf: Path | None,
    candidate_qmd: Path | None,
    pandoc_info: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if final_writeback.get("status") not in {"final_pdf_written", "final_pdf_already_written"}:
        reasons.append("final_pdf_writeback_not_complete")
    if final_writeback.get("final_writeback_authorized") is not True:
        reasons.append("final_writeback_not_authorized")
    if final_writeback.get("this_command_wrote_docx") is not False:
        reasons.append("previous_step_docx_boundary_unclear")
    if final_writeback.get("formal_state_guard", {}).get("changed"):
        reasons.append("formal_state_changed_in_final_pdf_writeback")
    if approval_report.get("status") != "approved_for_final_writeback":
        reasons.append("final_approval_not_authorized")
    if approval_report.get("can_enter_p6") is not True:
        reasons.append("approval_report_cannot_enter_p6")
    if ledger_entry.get("status") != "approved":
        reasons.append("approval_ledger_not_approved")
    if ledger_entry.get("can_enter_p6") is not True:
        reasons.append("approval_ledger_cannot_enter_p6")
    if ledger_entry.get("final_writeback_authorized") is not True:
        reasons.append("approval_ledger_not_authorized")
    if final_pdf is None or not final_pdf.exists():
        reasons.append("final_pdf_missing")
    if candidate_qmd is None or not candidate_qmd.exists():
        reasons.append("candidate_qmd_missing")
    if not pandoc_info.get("available"):
        reasons.append("pandoc_unavailable")
    return reasons


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "ready_for_docx_export"
    if any(reason.startswith("final_pdf") or reason.startswith("final_writeback") for reason in blocking_reasons):
        return "blocked_by_final_pdf_writeback"
    if any("approval" in reason or "enter_p6" in reason for reason in blocking_reasons):
        return "blocked_by_final_approval"
    if "pandoc_unavailable" in blocking_reasons:
        return "blocked_by_docx_toolchain"
    return "blocked_by_docx_inputs"


def build_export_command(candidate_qmd: Path | None, expected_docx: Path, project_root: Path) -> list[str]:
    source = relative_or_absolute(candidate_qmd, project_root) if candidate_qmd else ""
    output = relative_or_absolute(expected_docx, project_root)
    return [
        "python3",
        "Program/export_docx.py",
        "--project-root",
        ".",
        "--source",
        source,
        "--output",
        output,
    ]


def inspect_pandoc(pandoc_bin: str) -> dict[str, Any]:
    path = shutil.which(pandoc_bin)
    if path is None:
        return {
            "available": False,
            "path": None,
            "version": None,
            "checked_bin": pandoc_bin,
        }
    result = subprocess.run([path, "--version"], text=True, capture_output=True)
    version = result.stdout.splitlines()[0] if result.stdout else None
    return {
        "available": result.returncode == 0,
        "path": path,
        "version": version,
        "checked_bin": pandoc_bin,
    }


def build_next_action(blocking_reasons: list[str]) -> dict[str, str]:
    if not blocking_reasons:
        return {
            "id": "run_formal_docx_export",
            "label": "执行正式 docx 导出",
            "description": "docx 预检已通过。下一节点可以读取本报告并生成 formal package 的 paper.docx。",
        }
    return {
        "id": "repair_formal_docx_export_inputs",
        "label": "修复 docx 导出输入",
        "description": "先修复最终 PDF 写回、批准账本、候选 QMD 或 pandoc 工具链，再重新运行 P6-B。",
    }


def write_formal_docx_export_preflight_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def render_review_markdown(report: dict[str, Any]) -> str:
    blockers = report.get("blocking_reasons") or []
    blocker_lines = "\n".join(f"- `{item}`" for item in blockers) if blockers else "- 无"
    command = " ".join(report.get("export_command") or [])
    pandoc = report.get("pandoc") or {}
    return f"""# P6-B docx 导出预检

## 当前状态

- 状态：`{report.get("status")}`
- 可执行 docx 导出：`{str(report.get("can_export_docx")).lower()}`
- 最终 PDF：`{report.get("final_pdf")}`
- 候选 QMD：`{report.get("source_candidate_qmd")}`
- 预期 docx：`{report.get("expected_docx")}`
- pandoc：`{pandoc.get("version")}` (`{pandoc.get("path")}`)
- 写入 docx：`{str(report.get("this_command_wrote_docx")).lower()}`
- 写入正式研究状态：`{str(report.get("this_command_wrote_formal_state")).lower()}`

## 计划导出命令

```bash
{command}
```

## 阻断原因

{blocker_lines}

## 下一步

- `{report.get("next_action", {}).get("id")}`：{report.get("next_action", {}).get("description")}
"""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
