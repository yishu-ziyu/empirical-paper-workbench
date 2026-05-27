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


VALID_DECISIONS = {
    "accept": "formal_submission_package_accepted",
    "defer": "pending_human_manual_acceptance",
    "needs_revision": "formal_submission_package_needs_revision",
    "reject": "formal_submission_package_rejected",
}
DEFAULT_SUMMARY = "state/product/formal_submission_package_summary.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_submission_package_manual_acceptance.json"
DEFAULT_OUTPUT_STATE = "state/product/formal_submission_package_manual_acceptance.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_submission_package_manual_acceptance.md"


def build_formal_submission_package_manual_acceptance(
    project_root: Path,
    *,
    summary_path: Path,
    decision: str,
    actor: str,
    note: str,
    formal_state_before: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int]:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Invalid formal package manual acceptance decision: {decision}")

    before = formal_state_before or snapshot_protected_formal_state(project_root)
    summary = load_json(summary_path)
    accepted_artifacts = build_accepted_artifacts(project_root, summary)
    blocking_reasons = build_blocking_reasons(summary_path, summary, accepted_artifacts)
    after = snapshot_protected_formal_state(project_root)

    if blocking_reasons:
        return {
            "schema_version": "p6.formal_submission_package_manual_acceptance.v1",
            "generated_at": utc_now(),
            "source_summary": build_source_summary(project_root, summary_path, summary),
            "status": "blocked_by_submission_package_summary",
            "decision": decision,
            "actor": actor,
            "note": note,
            "accepted": False,
            "needs_revision": False,
            "accepted_artifacts": accepted_artifacts,
            "blocking_reasons": blocking_reasons,
            "boundary_flags": build_boundary_flags(),
            "formal_state_guard": diff_protected_formal_state(before, after),
            "next_action": {
                "id": "refresh_formal_submission_package_summary",
                "label": "刷新正式包验收摘要",
                "description": "正式包摘要尚未 ready，先修复阻断项后再记录人工验收。",
            },
        }, 2

    status = VALID_DECISIONS[decision]
    accepted = decision == "accept"
    needs_revision = decision == "needs_revision"
    return {
        "schema_version": "p6.formal_submission_package_manual_acceptance.v1",
        "generated_at": utc_now(),
        "source_summary": build_source_summary(project_root, summary_path, summary),
        "status": status,
        "decision": decision,
        "actor": actor,
        "note": note,
        "accepted": accepted,
        "needs_revision": needs_revision,
        "accepted_artifacts": accepted_artifacts,
        "blocking_reasons": [],
        "boundary_flags": build_boundary_flags(),
        "formal_state_guard": diff_protected_formal_state(before, after),
        "next_action": build_next_action(decision),
    }, 0


def build_source_summary(project_root: Path, summary_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative_or_absolute(summary_path, project_root),
        "exists": summary_path.exists(),
        "status": summary.get("status"),
        "ready_for_manual_acceptance": summary.get("ready_for_manual_acceptance"),
        "sha256": sha256_file(summary_path) if summary_path.exists() else None,
    }


def build_accepted_artifacts(project_root: Path, summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = summary.get("artifacts") or {}
    return {
        "paper_pdf": build_artifact(project_root, artifacts.get("paper_pdf") or {}),
        "paper_docx": build_artifact(project_root, artifacts.get("paper_docx") or {}),
    }


def build_artifact(project_root: Path, artifact: dict[str, Any]) -> dict[str, Any]:
    raw_path = artifact.get("path")
    path = resolve_project_path(project_root, str(raw_path or ""))
    exists = path.exists() if path else False
    sha256 = sha256_file(path) if path and exists else None
    bytes_count = path.stat().st_size if path and exists else None
    return {
        "path": relative_or_absolute(path, project_root) if path else raw_path,
        "exists": exists,
        "bytes": bytes_count,
        "sha256": sha256,
        "summary_bytes": artifact.get("bytes"),
        "summary_sha256": artifact.get("sha256"),
        "hash_matches_summary": sha256 == artifact.get("sha256") if sha256 and artifact.get("sha256") else False,
        "bytes_match_summary": bytes_count == artifact.get("bytes") if bytes_count is not None else False,
    }


def build_blocking_reasons(
    summary_path: Path,
    summary: dict[str, Any],
    accepted_artifacts: dict[str, dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if not summary_path.exists():
        reasons.append("summary_missing")
    if summary.get("status") != "ready_for_manual_acceptance":
        reasons.append("summary_not_ready_for_manual_acceptance")
    if summary.get("ready_for_manual_acceptance") is not True:
        reasons.append("summary_ready_flag_false")
    if summary.get("formal_state_guard", {}).get("changed"):
        reasons.append("summary_formal_state_guard_changed")
    for artifact_id, artifact in accepted_artifacts.items():
        if artifact.get("exists") is not True:
            reasons.append(f"{artifact_id}_missing")
        if artifact.get("hash_matches_summary") is not True:
            reasons.append(f"{artifact_id}_hash_mismatch:summary")
        if artifact.get("bytes_match_summary") is not True:
            reasons.append(f"{artifact_id}_bytes_mismatch:summary")
    return reasons


def build_boundary_flags() -> dict[str, bool]:
    return {
        "this_command_opened_files": False,
        "this_command_rendered_pdf": False,
        "this_command_rendered_docx": False,
        "this_command_wrote_final_outputs": False,
        "this_command_wrote_formal_research_state": False,
    }


def build_next_action(decision: str) -> dict[str, str]:
    if decision == "accept":
        return {
            "id": "freeze_submission_package_acceptance",
            "label": "冻结正式包人工验收记录",
            "description": "正式 PDF 和 DOCX 已被人工接受，下一步进入产品化展示或外部分发记录。",
        }
    if decision == "defer":
        return {
            "id": "open_and_review_pdf_docx",
            "label": "打开 PDF 和 DOCX 人工审阅",
            "description": "正式包已 ready，等待用户打开 PDF 和 DOCX 后做接受、退回或拒绝决定。",
        }
    if decision == "needs_revision":
        return {
            "id": "revise_formal_submission_package",
            "label": "修订正式投稿包",
            "description": "按人工意见修订正式包后，重新生成 summary 并再次验收。",
        }
    return {
        "id": "stop_formal_submission_package",
        "label": "停止本轮正式包验收",
        "description": "保留拒绝原因和验收记录，不继续分发当前正式包。",
    }


def write_formal_submission_package_manual_acceptance_outputs(
    report_path: Path,
    state_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    report_path.write_text(payload, encoding="utf-8")
    state_path.write_text(payload, encoding="utf-8")
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    return report_path, state_path, review_path


def render_review_markdown(report: dict[str, Any]) -> str:
    blockers = report.get("blocking_reasons") or []
    blocker_lines = "\n".join(f"- `{item}`" for item in blockers) if blockers else "- 无"
    artifacts = report.get("accepted_artifacts") or {}
    pdf = artifacts.get("paper_pdf") or {}
    docx = artifacts.get("paper_docx") or {}
    return f"""# P6-H4 正式包人工验收记录

## 当前状态

- 状态：`{report.get("status")}`
- 决策：`{report.get("decision")}`
- 验收人：`{report.get("actor")}`
- 已接受：`{str(report.get("accepted")).lower()}`
- 需要修订：`{str(report.get("needs_revision")).lower()}`
- PDF：`{pdf.get("path")}` / `{pdf.get("sha256")}`
- DOCX：`{docx.get("path")}` / `{docx.get("sha256")}`
- 本命令写最终产物：`{str((report.get("boundary_flags") or {}).get("this_command_wrote_final_outputs")).lower()}`
- 本命令写正式研究状态：`{str((report.get("boundary_flags") or {}).get("this_command_wrote_formal_research_state")).lower()}`

## 阻断原因

{blocker_lines}

## 人工意见

{report.get("note") or "无"}

## 下一步

- `{(report.get("next_action") or {}).get("id")}`：{(report.get("next_action") or {}).get("description")}
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
