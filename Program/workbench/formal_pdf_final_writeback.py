from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


APPROVAL_KEY = "formal_pdf_candidate"
DEFAULT_CANDIDATE_REPORT = "Results/json/formal_pdf_candidate_report.json"
DEFAULT_FINAL_PREFLIGHT = "Results/json/formal_pdf_final_writeback_preflight.json"
DEFAULT_APPROVAL_REPORT = "Results/json/formal_pdf_final_approval.json"
DEFAULT_APPROVAL_LEDGER = "state/product/writeback_approvals.json"
DEFAULT_REPORT_PATH = "Results/json/formal_pdf_final_writeback.json"
DEFAULT_REVIEW_PATH = "Reviews/formal_pdf_final_writeback.md"
DEFAULT_OUTPUT_PDF = "Submissions/formal_package/paper.pdf"


def build_formal_pdf_final_writeback(
    project_root: Path,
    *,
    candidate_report_path: Path,
    final_preflight_path: Path,
    approval_report_path: Path,
    approval_ledger_path: Path,
    output_pdf_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    inputs = load_inputs(
        candidate_report_path=candidate_report_path,
        final_preflight_path=final_preflight_path,
        approval_report_path=approval_report_path,
        approval_ledger_path=approval_ledger_path,
    )
    blocking_reasons = build_blocking_reasons(project_root, inputs)
    status = build_status(blocking_reasons)
    candidate_pdf = resolve_project_path(
        project_root,
        str((inputs.get("candidate_report") or {}).get("output_pdf") or ""),
    )
    candidate_qmd = resolve_project_path(
        project_root,
        str((inputs.get("candidate_report") or {}).get("output_qmd") or ""),
    )

    wrote_final_pdf = False
    source_sha = None
    final_sha = None
    source_bytes = None
    final_bytes = None
    if not blocking_reasons and candidate_pdf is not None:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
        if output_pdf_path.exists():
            candidate_hash = sha256_file(candidate_pdf)
            output_hash = sha256_file(output_pdf_path)
            if candidate_hash != output_hash:
                blocking_reasons.append("final_pdf_exists_with_different_hash")
                status = "blocked_by_existing_final_pdf"
            else:
                source_sha = candidate_hash
                final_sha = output_hash
                source_bytes = candidate_pdf.stat().st_size
                final_bytes = output_pdf_path.stat().st_size
                status = "final_pdf_already_written"
        if not blocking_reasons and not output_pdf_path.exists():
            shutil.copyfile(candidate_pdf, output_pdf_path)
            wrote_final_pdf = True
            source_sha = sha256_file(candidate_pdf)
            final_sha = sha256_file(output_pdf_path)
            source_bytes = candidate_pdf.stat().st_size
            final_bytes = output_pdf_path.stat().st_size

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p6.formal_pdf_final_writeback.v1",
        "generated_at": utc_now(),
        "status": status,
        "source_candidate_report": relative_or_absolute(candidate_report_path, project_root),
        "source_final_preflight": relative_or_absolute(final_preflight_path, project_root),
        "source_approval_report": relative_or_absolute(approval_report_path, project_root),
        "source_approval_ledger": relative_or_absolute(approval_ledger_path, project_root),
        "source_candidate_pdf": relative_or_absolute(candidate_pdf, project_root) if candidate_pdf else None,
        "source_candidate_qmd": relative_or_absolute(candidate_qmd, project_root) if candidate_qmd else None,
        "final_pdf": relative_or_absolute(output_pdf_path, project_root),
        "final_pdf_exists": output_pdf_path.exists(),
        "source_candidate_pdf_sha256": source_sha,
        "final_pdf_sha256": final_sha,
        "source_candidate_pdf_bytes": source_bytes,
        "final_pdf_bytes": final_bytes,
        "blocking_reasons": blocking_reasons,
        "final_writeback_authorized": not blocking_reasons,
        "this_command_wrote_final_pdf": wrote_final_pdf,
        "this_command_wrote_docx": False,
        "this_command_wrote_formal_state": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(blocking_reasons),
    }, 0 if not blocking_reasons else 2


def load_inputs(
    *,
    candidate_report_path: Path,
    final_preflight_path: Path,
    approval_report_path: Path,
    approval_ledger_path: Path,
) -> dict[str, Any]:
    return {
        "candidate_report": load_json(candidate_report_path),
        "final_preflight": load_json(final_preflight_path),
        "approval_report": load_json(approval_report_path),
        "approval_ledger": load_json(approval_ledger_path),
    }


def build_blocking_reasons(project_root: Path, inputs: dict[str, Any]) -> list[str]:
    candidate_report = inputs.get("candidate_report") or {}
    final_preflight = inputs.get("final_preflight") or {}
    approval_report = inputs.get("approval_report") or {}
    approval_ledger = inputs.get("approval_ledger") or {}
    ledger_entry = (approval_ledger.get("final_pdf_approvals") or {}).get(APPROVAL_KEY) or {}
    reasons: list[str] = []

    if candidate_report.get("status") != "pdf_candidate_ready":
        reasons.append("candidate_report_not_ready")
    if candidate_report.get("candidate_layer_only") is not True:
        reasons.append("candidate_report_not_candidate_layer")
    if final_preflight.get("status") != "ready_for_human_final_approval":
        reasons.append("final_preflight_not_ready")
    if final_preflight.get("can_request_final_approval") is not True:
        reasons.append("final_preflight_not_approval_ready")
    if final_preflight.get("formal_state_guard", {}).get("changed"):
        reasons.append("formal_state_changed_in_preflight")
    if approval_report.get("status") != "approved_for_final_writeback":
        reasons.append("final_approval_not_authorized")
    if approval_report.get("can_enter_p6") is not True:
        reasons.append("approval_report_cannot_enter_p6")
    if approval_report.get("final_writeback_authorized") is not True:
        reasons.append("approval_report_not_authorized")
    if ledger_entry.get("status") != "approved":
        reasons.append("approval_ledger_not_approved")
    if ledger_entry.get("can_enter_p6") is not True:
        reasons.append("approval_ledger_cannot_enter_p6")
    if ledger_entry.get("final_writeback_authorized") is not True:
        reasons.append("approval_ledger_not_authorized")

    expected_pdf = str(candidate_report.get("output_pdf") or "")
    expected_qmd = str(candidate_report.get("output_qmd") or "")
    candidate_pdf = resolve_project_path(project_root, expected_pdf)
    candidate_qmd = resolve_project_path(project_root, expected_qmd)
    if candidate_pdf is None or not candidate_pdf.exists():
        reasons.append("candidate_pdf_missing")
    if candidate_qmd is None or not candidate_qmd.exists():
        reasons.append("candidate_qmd_missing")

    for source_name, source in [
        ("final_preflight", final_preflight),
        ("approval_report", approval_report),
        ("approval_ledger", ledger_entry),
    ]:
        source_pdf = source.get("candidate_pdf")
        source_qmd = source.get("candidate_qmd")
        if source_pdf and expected_pdf and source_pdf != expected_pdf:
            if "candidate_pdf_mismatch" not in reasons:
                reasons.append("candidate_pdf_mismatch")
            reasons.append(f"candidate_pdf_mismatch:{source_name}")
        if source_qmd and expected_qmd and source_qmd != expected_qmd:
            if "candidate_qmd_mismatch" not in reasons:
                reasons.append("candidate_qmd_mismatch")
            reasons.append(f"candidate_qmd_mismatch:{source_name}")

    return reasons


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "final_pdf_written"
    if any(reason.startswith("candidate_") and "mismatch" in reason for reason in blocking_reasons):
        return "blocked_by_candidate_integrity"
    if any("approval" in reason or "enter_p6" in reason for reason in blocking_reasons):
        return "blocked_by_final_approval"
    if any(reason in {"candidate_pdf_missing", "candidate_qmd_missing", "candidate_report_not_ready"} for reason in blocking_reasons):
        return "blocked_by_candidate_integrity"
    return "blocked_by_final_preflight"


def build_next_action(blocking_reasons: list[str]) -> dict[str, str]:
    if not blocking_reasons:
        return {
            "id": "docx_export_preflight",
            "label": "进入 docx 导出预检",
            "description": "最终 PDF 已写入正式包。下一节点检查 docx 工具链和投稿包导出条件。",
        }
    return {
        "id": "repair_final_pdf_writeback_inputs",
        "label": "修复最终 PDF 写回输入",
        "description": "先修复批准账本、候选 PDF 或最终写回预检，再重新运行 P6-A。",
    }


def write_formal_pdf_final_writeback_outputs(
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
    llm_provider_snapshot = (
        report.get("llm_provider_snapshot") if isinstance(report.get("llm_provider_snapshot"), dict) else {}
    )
    primary_provider = (
        llm_provider_snapshot.get("primary_provider") if isinstance(llm_provider_snapshot.get("primary_provider"), dict) else {}
    )
    llm_lines = ""
    if primary_provider:
        llm_lines = f"""
## LLM 判断来源

- Provider：`{primary_provider.get("provider_name") or primary_provider.get("provider_id")}`
- Model：`{primary_provider.get("model")}`
- 选择来源：`{llm_provider_snapshot.get("selection", {}).get("source") if isinstance(llm_provider_snapshot.get("selection"), dict) else ""}`
- 预检摘要：{report.get("llm_preflight_summary") or "无"}
- 人工审阅提示：{report.get("llm_preflight_human_review_note") or "无"}
"""
    return f"""# P6-A 最终 PDF 写回

## 当前状态

- 状态：`{report.get("status")}`
- 候选 PDF：`{report.get("source_candidate_pdf")}`
- 最终 PDF：`{report.get("final_pdf")}`
- 候选 PDF sha256：`{report.get("source_candidate_pdf_sha256")}`
- 最终 PDF sha256：`{report.get("final_pdf_sha256")}`
- 写入最终 PDF：`{str(report.get("this_command_wrote_final_pdf")).lower()}`
- 写入 docx：`{str(report.get("this_command_wrote_docx")).lower()}`
- 写入正式研究状态：`{str(report.get("this_command_wrote_formal_state")).lower()}`

## 阻断原因

{blocker_lines}
{llm_lines}

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
