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


DEFAULT_PROVENANCE_LOCK_REPORT = "Results/json/formal_package_provenance_lock_check.json"
DEFAULT_FINAL_WRITEBACK_REPORT = "Results/json/formal_pdf_final_writeback.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_package_candidate_snapshot_freeze.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_package_candidate_snapshot_freeze.md"
DEFAULT_OUTPUT_SNAPSHOT = "Submissions/formal_package/provenance/approved_candidate_snapshot.json"


def build_formal_package_candidate_snapshot_freeze(
    project_root: Path,
    *,
    provenance_lock_report_path: Path,
    final_writeback_report_path: Path,
    output_snapshot_path: Path,
    formal_state_before: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None, int]:
    before = formal_state_before or snapshot_protected_formal_state(project_root)
    provenance_lock = load_json(provenance_lock_report_path)
    final_writeback = load_json(final_writeback_report_path)

    approved_snapshot = build_approved_candidate_snapshot(
        project_root,
        provenance_lock=provenance_lock,
        final_writeback=final_writeback,
    )
    blocking_reasons = build_blocking_reasons(
        project_root,
        provenance_lock=provenance_lock,
        final_writeback=final_writeback,
        approved_snapshot=approved_snapshot,
    )
    snapshot = None if blocking_reasons else approved_snapshot
    after = snapshot_protected_formal_state(project_root)
    status = "blocked_by_provenance_lock" if blocking_reasons else "approved_candidate_snapshot_frozen"
    report = {
        "schema_version": "p6.formal_package_candidate_snapshot_freeze.v1",
        "generated_at": utc_now(),
        "status": status,
        "snapshot_written": snapshot is not None,
        "snapshot": {
            "path": relative_or_absolute(output_snapshot_path, project_root),
            "exists_after_write": snapshot is not None,
        },
        "provenance_lock": {
            "path": relative_or_absolute(provenance_lock_report_path, project_root),
            "status": provenance_lock.get("status"),
            "can_continue_manual_acceptance": (
                provenance_lock.get("final_package_acceptance") or {}
            ).get("can_continue_manual_acceptance"),
            "blocking_reasons": provenance_lock.get("blocking_reasons") or [],
            "warning_reasons": provenance_lock.get("warning_reasons") or [],
        },
        "final_writeback": {
            "path": relative_or_absolute(final_writeback_report_path, project_root),
            "status": final_writeback.get("status"),
            "source_candidate_pdf": final_writeback.get("source_candidate_pdf"),
            "source_candidate_pdf_sha256": final_writeback.get("source_candidate_pdf_sha256"),
            "source_candidate_pdf_bytes": final_writeback.get("source_candidate_pdf_bytes"),
            "final_pdf": final_writeback.get("final_pdf"),
            "final_pdf_sha256": final_writeback.get("final_pdf_sha256"),
            "final_pdf_bytes": final_writeback.get("final_pdf_bytes"),
        },
        "approved_candidate_snapshot": approved_snapshot,
        "blocking_reasons": blocking_reasons,
        "warning_reasons_resolved_as": [] if blocking_reasons else ["candidate_source_authority_frozen"],
        "boundary_flags": {
            "this_command_rendered_pdf": False,
            "this_command_rendered_docx": False,
            "this_command_wrote_final_outputs": False,
            "this_command_wrote_formal_state": False,
            "this_command_wrote_provenance_snapshot": snapshot is not None,
        },
        "formal_state_guard": diff_protected_formal_state(before, after),
        "next_actions": build_next_actions(blocking_reasons),
    }
    return report, snapshot, 2 if blocking_reasons else 0


def build_approved_candidate_snapshot(
    project_root: Path,
    *,
    provenance_lock: dict[str, Any],
    final_writeback: dict[str, Any],
) -> dict[str, Any]:
    final_pdf_path = resolve_project_path(project_root, str(final_writeback.get("final_pdf") or ""))
    current_candidate = provenance_lock.get("candidate_source_lock") or {}
    return {
        "schema_version": "p6.approved_candidate_snapshot.v1",
        "generated_at": utc_now(),
        "status": "approved_candidate_snapshot_frozen",
        "authority": "formal_pdf_final_writeback",
        "approved_candidate": {
            "source_candidate_path_at_writeback": final_writeback.get("source_candidate_pdf"),
            "sha256": final_writeback.get("source_candidate_pdf_sha256"),
            "bytes": final_writeback.get("source_candidate_pdf_bytes"),
        },
        "recovered_from": {
            "path": relative_or_absolute(final_pdf_path, project_root) if final_pdf_path else None,
            "exists": final_pdf_path.exists() if final_pdf_path else False,
            "sha256": sha256_file(final_pdf_path) if final_pdf_path and final_pdf_path.exists() else None,
            "bytes": final_pdf_path.stat().st_size if final_pdf_path and final_pdf_path.exists() else None,
            "reason": "final_pdf_hash_matches_recorded_candidate_source",
        },
        "current_candidate": {
            "path": current_candidate.get("path"),
            "exists": current_candidate.get("exists"),
            "sha256": current_candidate.get("current_sha256"),
            "bytes": current_candidate.get("current_bytes"),
            "authoritative_for_current_formal_package": False,
            "treatment": "historical_candidate_or_next_draft",
            "warning_reasons": current_candidate.get("warning_reasons") or [],
        },
    }


def build_blocking_reasons(
    project_root: Path,
    *,
    provenance_lock: dict[str, Any],
    final_writeback: dict[str, Any],
    approved_snapshot: dict[str, Any],
) -> list[str]:
    blocking_reasons: list[str] = []
    acceptance = provenance_lock.get("final_package_acceptance") or {}
    final_artifact_lock = provenance_lock.get("final_artifact_lock") or {}
    if acceptance.get("can_continue_manual_acceptance") is not True:
        blocking_reasons.append("provenance_lock_not_acceptance_ready")
    if final_artifact_lock.get("status") != "consistent":
        blocking_reasons.append("provenance_lock_not_acceptance_ready")
    if final_writeback.get("status") not in {"final_pdf_written", "final_pdf_already_written"}:
        blocking_reasons.append("final_writeback_not_complete")

    final_pdf_path = resolve_project_path(project_root, str(final_writeback.get("final_pdf") or ""))
    recorded_candidate_sha = final_writeback.get("source_candidate_pdf_sha256")
    recovered_sha = (approved_snapshot.get("recovered_from") or {}).get("sha256")
    if not final_pdf_path or not final_pdf_path.exists() or not recorded_candidate_sha:
        blocking_reasons.append("approved_candidate_bytes_unavailable")
    elif recovered_sha != recorded_candidate_sha:
        blocking_reasons.append("approved_candidate_bytes_unavailable")
    return dedupe(blocking_reasons)


def write_formal_package_candidate_snapshot_freeze_outputs(
    report_path: Path,
    review_path: Path,
    snapshot_path: Path,
    report: dict[str, Any],
    snapshot: dict[str, Any] | None,
) -> tuple[Path, Path, Path | None]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    if snapshot is None:
        return report_path, review_path, None
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report_path, review_path, snapshot_path


def render_review_markdown(report: dict[str, Any]) -> str:
    snapshot = report.get("approved_candidate_snapshot") or {}
    recovered = snapshot.get("recovered_from") or {}
    current = snapshot.get("current_candidate") or {}
    lines = [
        "# Formal Package Candidate Snapshot Freeze",
        "",
        f"- status: `{report.get('status')}`",
        f"- snapshot_written: `{str(report.get('snapshot_written')).lower()}`",
        f"- approved_candidate_sha256: `{(snapshot.get('approved_candidate') or {}).get('sha256')}`",
        f"- recovered_from: `{recovered.get('path')}`",
        f"- current_candidate: `{current.get('path')}`",
        f"- current_candidate_treatment: `{current.get('treatment')}`",
        f"- final_outputs_changed: `{str((report.get('boundary_flags') or {}).get('this_command_wrote_final_outputs')).lower()}`",
        f"- formal_state_changed: `{str((report.get('formal_state_guard') or {}).get('changed')).lower()}`",
        "",
        "## Blocking Reasons",
        "",
    ]
    blocking_reasons = report.get("blocking_reasons") or []
    lines.extend([f"- `{reason}`" for reason in blocking_reasons] or ["- none"])
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend([f"- {item.get('action')}: {item.get('reason')}" for item in report.get("next_actions") or []])
    return "\n".join(lines) + "\n"


def build_next_actions(blocking_reasons: list[str]) -> list[dict[str, str]]:
    if blocking_reasons:
        return [
            {
                "action": "rerun_provenance_lock_check_after_fixing_final_artifacts",
                "reason": "candidate authority cannot be frozen until final package artifacts are acceptance-ready",
            }
        ]
    return [
        {
            "action": "continue_manual_acceptance_with_approved_candidate_snapshot",
            "reason": "the approved candidate bytes are now represented by a stable provenance sidecar",
        }
    ]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return project_root / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
