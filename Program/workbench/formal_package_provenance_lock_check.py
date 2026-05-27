from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute
from workbench.formal_submission_package_summary import (
    diff_protected_formal_state,
    snapshot_protected_formal_state,
)


DEFAULT_FINAL_WRITEBACK_REPORT = "Results/json/formal_pdf_final_writeback.json"
DEFAULT_DOCX_EXPORT_REPORT = "Results/json/formal_docx_export.json"
DEFAULT_SUBMISSION_MANIFEST_REPORT = "Results/json/formal_submission_package_manifest.json"
DEFAULT_SUBMISSION_SUMMARY_REPORT = "Results/json/formal_submission_package_summary.json"
DEFAULT_PACKAGE_MANIFEST = "Submissions/formal_package/manifest.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_package_provenance_lock_check.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_package_provenance_lock_check.md"


def build_formal_package_provenance_lock_check(
    project_root: Path,
    *,
    final_writeback_report_path: Path,
    docx_export_report_path: Path,
    submission_manifest_report_path: Path,
    submission_summary_report_path: Path,
    package_manifest_path: Path,
    formal_state_before: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_protected_formal_state(project_root)
    final_writeback = load_json(final_writeback_report_path)
    docx_export = load_json(docx_export_report_path)
    submission_manifest = load_json(submission_manifest_report_path)
    submission_summary = load_json(submission_summary_report_path)
    package_manifest = load_json(package_manifest_path)

    candidate_source_lock = build_candidate_source_lock(project_root, final_writeback)
    final_artifact_lock = build_final_artifact_lock(
        project_root,
        final_writeback=final_writeback,
        docx_export=docx_export,
        submission_manifest=submission_manifest,
        package_manifest=package_manifest,
    )
    acceptance_lock = build_acceptance_lock(submission_manifest, submission_summary, package_manifest)
    blocking_reasons = [
        *final_artifact_lock["blocking_reasons"],
        *acceptance_lock["blocking_reasons"],
    ]
    warning_reasons = candidate_source_lock["warning_reasons"]
    status = build_status(
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        final_artifact_status=final_artifact_lock["status"],
        acceptance_status=acceptance_lock["status"],
    )
    can_continue_manual_acceptance = not blocking_reasons
    after = snapshot_protected_formal_state(project_root)
    report = {
        "schema_version": "p6.formal_package_provenance_lock_check.v1",
        "generated_at": utc_now(),
        "status": status,
        "final_package_acceptance": {
            "can_continue_manual_acceptance": can_continue_manual_acceptance,
            "status": "available" if can_continue_manual_acceptance else "blocked",
        },
        "final_writeback": {
            "path": relative_or_absolute(final_writeback_report_path, project_root),
            "exists": final_writeback_report_path.exists(),
            "status": final_writeback.get("status"),
            "source_candidate_pdf": final_writeback.get("source_candidate_pdf"),
            "source_candidate_pdf_sha256": final_writeback.get("source_candidate_pdf_sha256"),
            "final_pdf": final_writeback.get("final_pdf"),
            "final_pdf_sha256": final_writeback.get("final_pdf_sha256"),
        },
        "candidate_source_lock": candidate_source_lock,
        "final_artifact_lock": final_artifact_lock,
        "acceptance_lock": acceptance_lock,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
        "boundary_flags": {
            "this_command_rendered_pdf": False,
            "this_command_rendered_docx": False,
            "this_command_wrote_final_outputs": False,
            "this_command_wrote_formal_state": False,
        },
        "formal_state_guard": diff_protected_formal_state(before, after),
        "next_actions": build_next_actions(blocking_reasons, warning_reasons),
    }
    return report, 0 if not blocking_reasons else 2


def build_candidate_source_lock(project_root: Path, final_writeback: dict[str, Any]) -> dict[str, Any]:
    candidate_path = resolve_project_path(project_root, str(final_writeback.get("source_candidate_pdf") or ""))
    recorded_sha = final_writeback.get("source_candidate_pdf_sha256")
    recorded_bytes = final_writeback.get("source_candidate_pdf_bytes")
    exists = candidate_path.exists() if candidate_path else False
    current_sha = sha256_file(candidate_path) if exists and candidate_path else None
    current_bytes = candidate_path.stat().st_size if exists and candidate_path else None
    warning_reasons: list[str] = []
    if not exists:
        warning_reasons.append("candidate_pdf_missing_for_provenance_lock")
    elif recorded_sha and current_sha != recorded_sha:
        warning_reasons.append("candidate_pdf_drifted_from_final_writeback_source")
        if recorded_bytes is not None and current_bytes == int(recorded_bytes):
            warning_reasons.append("candidate_pdf_same_size_but_hash_changed")
    elif not recorded_sha:
        warning_reasons.append("candidate_pdf_recorded_hash_missing")
    return {
        "status": "locked" if not warning_reasons else "drifted",
        "path": relative_or_absolute(candidate_path, project_root) if candidate_path else None,
        "exists": exists,
        "recorded_bytes": recorded_bytes,
        "current_bytes": current_bytes,
        "recorded_sha256": recorded_sha,
        "current_sha256": current_sha,
        "warning_reasons": warning_reasons,
    }


def build_final_artifact_lock(
    project_root: Path,
    *,
    final_writeback: dict[str, Any],
    docx_export: dict[str, Any],
    submission_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
) -> dict[str, Any]:
    artifacts = (submission_manifest.get("artifacts") or {}) | (package_manifest.get("artifacts") or {})
    pdf = build_artifact_lock(
        project_root,
        artifact_id="paper_pdf",
        path_value=str(final_writeback.get("final_pdf") or artifact_path(artifacts, "paper_pdf")),
        expected_hashes=[
            final_writeback.get("final_pdf_sha256"),
            artifact_hash(submission_manifest, "paper_pdf"),
            artifact_hash(package_manifest, "paper_pdf"),
        ],
        expected_bytes=[
            final_writeback.get("final_pdf_bytes"),
            artifact_bytes(submission_manifest, "paper_pdf"),
            artifact_bytes(package_manifest, "paper_pdf"),
        ],
        mismatch_prefixes=[
            "final_writeback",
            "submission_manifest",
            "package_manifest",
        ],
    )
    docx = build_artifact_lock(
        project_root,
        artifact_id="paper_docx",
        path_value=str(docx_export.get("docx") or artifact_path(artifacts, "paper_docx")),
        expected_hashes=[
            docx_export.get("docx_sha256"),
            artifact_hash(submission_manifest, "paper_docx"),
            artifact_hash(package_manifest, "paper_docx"),
        ],
        expected_bytes=[
            docx_export.get("docx_bytes"),
            artifact_bytes(submission_manifest, "paper_docx"),
            artifact_bytes(package_manifest, "paper_docx"),
        ],
        mismatch_prefixes=[
            "docx_export",
            "submission_manifest",
            "package_manifest",
        ],
    )
    blocking_reasons = [*pdf["blocking_reasons"], *docx["blocking_reasons"]]
    return {
        "status": "consistent" if not blocking_reasons else "broken",
        "artifacts": {
            "paper_pdf": pdf,
            "paper_docx": docx,
        },
        "blocking_reasons": blocking_reasons,
    }


def build_artifact_lock(
    project_root: Path,
    *,
    artifact_id: str,
    path_value: str,
    expected_hashes: list[Any],
    expected_bytes: list[Any],
    mismatch_prefixes: list[str],
) -> dict[str, Any]:
    path = resolve_project_path(project_root, path_value)
    exists = path.exists() if path else False
    current_sha = sha256_file(path) if exists and path else None
    current_bytes = path.stat().st_size if exists and path else None
    blocking_reasons: list[str] = []
    if not exists:
        blocking_reasons.append(f"{artifact_id}_missing")
    for expected_hash, prefix in zip(expected_hashes, mismatch_prefixes, strict=True):
        if expected_hash and current_sha and expected_hash != current_sha:
            blocking_reasons.append(f"{artifact_id}_hash_mismatch:{prefix}")
    for expected_size, prefix in zip(expected_bytes, mismatch_prefixes, strict=True):
        if expected_size is not None and current_bytes is not None and int(expected_size) != int(current_bytes):
            blocking_reasons.append(f"{artifact_id}_bytes_mismatch:{prefix}")
    return {
        "path": relative_or_absolute(path, project_root) if path else None,
        "exists": exists,
        "bytes": current_bytes,
        "sha256": current_sha,
        "blocking_reasons": blocking_reasons,
    }


def build_acceptance_lock(
    submission_manifest: dict[str, Any],
    submission_summary: dict[str, Any],
    package_manifest: dict[str, Any],
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    if submission_manifest.get("status") != "formal_submission_package_ready":
        blocking_reasons.append("formal_submission_package_manifest_not_ready")
    if package_manifest.get("status") != "formal_submission_package_ready":
        blocking_reasons.append("package_manifest_not_ready")
    if submission_summary.get("status") != "ready_for_manual_acceptance":
        blocking_reasons.append("formal_submission_package_summary_not_ready")
    if submission_summary.get("ready_for_manual_acceptance") is not True:
        blocking_reasons.append("formal_submission_package_summary_not_acceptance_ready")
    return {
        "status": "ready" if not blocking_reasons else "blocked",
        "submission_manifest_status": submission_manifest.get("status"),
        "package_manifest_status": package_manifest.get("status"),
        "submission_summary_status": submission_summary.get("status"),
        "ready_for_manual_acceptance": submission_summary.get("ready_for_manual_acceptance"),
        "blocking_reasons": blocking_reasons,
    }


def build_status(
    *,
    blocking_reasons: list[str],
    warning_reasons: list[str],
    final_artifact_status: str,
    acceptance_status: str,
) -> str:
    if not blocking_reasons and warning_reasons:
        return "ready_for_manual_acceptance_with_provenance_warning"
    if not blocking_reasons:
        return "provenance_locked"
    if final_artifact_status == "broken":
        return "blocked_by_final_package_integrity"
    if acceptance_status == "blocked":
        return "blocked_by_acceptance_summary"
    return "blocked_by_provenance_lock"


def build_next_actions(blocking_reasons: list[str], warning_reasons: list[str]) -> list[dict[str, str]]:
    if blocking_reasons:
        return [
            {
                "id": "repair_formal_package_integrity",
                "label": "修复正式包完整性后重新校验",
                "description": "先处理最终 PDF/DOCX、manifest 或 summary 的阻断项，再重新运行 P6-H1。",
            }
        ]
    if warning_reasons:
        return [
            {
                "id": "freeze_approved_candidate_snapshot",
                "label": "冻结已批准候选稿快照",
                "description": "把最终写回时使用的候选稿指纹作为权威快照保存，当前候选稿另列为后续草案。",
            },
            {
                "id": "rerun_short_final_writeback_chain",
                "label": "重跑短链路写回",
                "description": "如果当前候选稿才是新的权威草案，重新走最终批准、PDF 写回、DOCX 导出和 manifest 生成。",
            },
            {
                "id": "demote_current_candidate_as_historical",
                "label": "把当前候选稿降级为历史草案",
                "description": "保留当前 paper_candidate.pdf，但明确它不是本次 formal package 的来源。",
            },
        ]
    return [
        {
            "id": "manual_acceptance",
            "label": "进入人工验收",
            "description": "正式包和候选来源已锁定，可以打开 PDF/DOCX 做人工阅读验收。",
        }
    ]


def write_formal_package_provenance_lock_check_outputs(
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
    blockers = "\n".join(f"- `{item}`" for item in report.get("blocking_reasons") or []) or "- 无"
    warnings = "\n".join(f"- `{item}`" for item in report.get("warning_reasons") or []) or "- 无"
    next_actions = "\n".join(
        f"- `{item.get('id')}`：{item.get('label')}。{item.get('description')}"
        for item in report.get("next_actions") or []
    )
    candidate = report.get("candidate_source_lock") or {}
    artifact = report.get("final_artifact_lock") or {}
    return f"""# P6-H1 正式包来源锁校验

## 当前状态

- 状态：`{report.get("status")}`
- 可继续人工验收：`{str((report.get("final_package_acceptance") or {}).get("can_continue_manual_acceptance")).lower()}`
- 候选来源锁：`{candidate.get("status")}`
- 最终产物锁：`{artifact.get("status")}`
- 写正式产物：`{str((report.get("boundary_flags") or {}).get("this_command_wrote_final_outputs")).lower()}`
- 写正式研究状态：`{str((report.get("boundary_flags") or {}).get("this_command_wrote_formal_state")).lower()}`

## 候选稿指纹

- 路径：`{candidate.get("path")}`
- 记录 bytes：`{candidate.get("recorded_bytes")}`
- 当前 bytes：`{candidate.get("current_bytes")}`
- 记录 sha256：`{candidate.get("recorded_sha256")}`
- 当前 sha256：`{candidate.get("current_sha256")}`

## 阻断项

{blockers}

## 警告项

{warnings}

## 下一步选项

{next_actions}
"""


def artifact_path(payload: dict[str, Any], artifact_id: str) -> str | None:
    return ((payload.get("artifacts") or {}).get(artifact_id) or {}).get("path")


def artifact_hash(payload: dict[str, Any], artifact_id: str) -> str | None:
    return ((payload.get("artifacts") or {}).get(artifact_id) or {}).get("sha256")


def artifact_bytes(payload: dict[str, Any], artifact_id: str) -> int | None:
    return ((payload.get("artifacts") or {}).get(artifact_id) or {}).get("bytes")


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
