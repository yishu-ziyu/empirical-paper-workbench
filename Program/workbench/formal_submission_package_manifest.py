from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_P6A_REPORT = "Results/json/formal_pdf_final_writeback.json"
DEFAULT_P6B_REPORT = "Results/json/formal_docx_export_preflight.json"
DEFAULT_P6C_REPORT = "Results/json/formal_docx_export.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_submission_package_manifest.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_submission_package_acceptance.md"
DEFAULT_PACKAGE_MANIFEST = "Submissions/formal_package/manifest.json"
DEFAULT_PACKAGE_ROOT = "Submissions/formal_package"


def build_formal_submission_package_manifest(
    project_root: Path,
    *,
    p6a_report_path: Path,
    p6b_report_path: Path,
    p6c_report_path: Path,
    package_manifest_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    p6a = load_json(p6a_report_path)
    p6b = load_json(p6b_report_path)
    p6c = load_json(p6c_report_path)

    paper_pdf = resolve_project_path(project_root, str(p6a.get("final_pdf") or p6c.get("final_pdf") or ""))
    paper_docx = resolve_project_path(project_root, str(p6c.get("docx") or p6b.get("expected_docx") or ""))
    package_root = project_root / DEFAULT_PACKAGE_ROOT
    artifacts = build_artifacts(
        project_root=project_root,
        paper_pdf=paper_pdf,
        paper_docx=paper_docx,
        p6a_report_path=p6a_report_path,
        p6c_report_path=p6c_report_path,
    )
    input_reports = build_input_reports(project_root, p6a_report_path, p6b_report_path, p6c_report_path, p6a, p6b, p6c)
    consistency_checks = build_consistency_checks(
        p6a=p6a,
        p6b=p6b,
        p6c=p6c,
        artifacts=artifacts,
    )
    blocking_reasons = build_blocking_reasons(
        p6a=p6a,
        p6b=p6b,
        p6c=p6c,
        artifacts=artifacts,
        consistency_checks=consistency_checks,
    )
    status = build_status(blocking_reasons)
    package_manifest_written = False

    after = snapshot_formal_state(project_root)
    report = {
        "schema_version": "p6.formal_submission_package_manifest.v1",
        "generated_at": utc_now(),
        "status": status,
        "package_root": relative_or_absolute(package_root, project_root),
        "package_manifest": relative_or_absolute(package_manifest_path, project_root),
        "package_manifest_written": package_manifest_written,
        "artifacts": artifacts,
        "input_reports": input_reports,
        "consistency_checks": consistency_checks,
        "manual_acceptance": build_manual_acceptance(),
        "reproduce_commands": build_reproduce_commands(),
        "blocking_reasons": blocking_reasons,
        "boundary_flags": {
            "this_command_rendered_pdf": False,
            "this_command_rendered_docx": False,
            "this_command_wrote_final_outputs": False,
            "this_command_wrote_formal_state": False,
        },
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(blocking_reasons),
    }
    if not blocking_reasons:
        write_package_manifest(package_manifest_path, build_package_manifest(report))
        report["package_manifest_written"] = True
    return report, 0 if not blocking_reasons else 2


def build_artifacts(
    *,
    project_root: Path,
    paper_pdf: Path | None,
    paper_docx: Path | None,
    p6a_report_path: Path,
    p6c_report_path: Path,
) -> dict[str, dict[str, Any]]:
    return {
        "paper_pdf": build_artifact(project_root, paper_pdf, p6a_report_path),
        "paper_docx": build_artifact(project_root, paper_docx, p6c_report_path),
    }


def build_artifact(project_root: Path, path: Path | None, source_report: Path) -> dict[str, Any]:
    exists = path.exists() if path else False
    return {
        "path": relative_or_absolute(path, project_root) if path else None,
        "exists": exists,
        "bytes": path.stat().st_size if exists and path else None,
        "sha256": sha256_file(path) if exists and path else None,
        "source_report": relative_or_absolute(source_report, project_root),
    }


def build_input_reports(
    project_root: Path,
    p6a_report_path: Path,
    p6b_report_path: Path,
    p6c_report_path: Path,
    p6a: dict[str, Any],
    p6b: dict[str, Any],
    p6c: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "p6a": build_input_report(project_root, p6a_report_path, p6a),
        "p6b": build_input_report(project_root, p6b_report_path, p6b),
        "p6c": build_input_report(project_root, p6c_report_path, p6c),
    }


def build_input_report(project_root: Path, path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative_or_absolute(path, project_root),
        "exists": path.exists(),
        "schema_version": payload.get("schema_version"),
        "status": payload.get("status"),
        "blocking_reasons": payload.get("blocking_reasons") or [],
    }


def build_consistency_checks(
    *,
    p6a: dict[str, Any],
    p6b: dict[str, Any],
    p6c: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    paper_pdf = artifacts["paper_pdf"]
    paper_docx = artifacts["paper_docx"]
    return {
        "pdf_hash_matches_p6a": match_optional_hash(paper_pdf.get("sha256"), p6a.get("final_pdf_sha256")),
        "docx_hash_matches_p6c": match_optional_hash(paper_docx.get("sha256"), p6c.get("docx_sha256")),
        "pdf_bytes_match_p6a": match_optional_number(paper_pdf.get("bytes"), p6a.get("final_pdf_bytes")),
        "docx_bytes_match_p6c": match_optional_number(paper_docx.get("bytes"), p6c.get("docx_bytes")),
        "p6b_expected_docx_matches_p6c": bool(p6b.get("expected_docx") and p6b.get("expected_docx") == p6c.get("docx")),
        "p6c_final_pdf_matches_p6a": bool(p6c.get("final_pdf") and p6c.get("final_pdf") == p6a.get("final_pdf")),
        "p6c_candidate_qmd_matches_p6a": bool(
            p6c.get("source_candidate_qmd") and p6c.get("source_candidate_qmd") == p6a.get("source_candidate_qmd")
        ),
    }


def match_optional_hash(actual: Any, expected: Any) -> bool:
    return bool(actual and expected and actual == expected)


def match_optional_number(actual: Any, expected: Any) -> bool:
    return actual is not None and expected is not None and int(actual) == int(expected)


def build_blocking_reasons(
    *,
    p6a: dict[str, Any],
    p6b: dict[str, Any],
    p6c: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    consistency_checks: dict[str, bool],
) -> list[str]:
    reasons: list[str] = []
    if p6a.get("status") not in {"final_pdf_written", "final_pdf_already_written"}:
        reasons.append("p6a_final_pdf_not_written")
    if p6b.get("status") != "ready_for_docx_export":
        reasons.append("p6b_docx_preflight_not_ready")
    if p6b.get("can_export_docx") is not True:
        reasons.append("p6b_docx_preflight_cannot_export")
    if p6c.get("status") != "docx_exported":
        reasons.append("p6c_docx_export_not_exported")
    if artifacts["paper_pdf"].get("exists") is not True:
        reasons.append("paper_pdf_missing")
    if artifacts["paper_docx"].get("exists") is not True:
        reasons.append("paper_docx_missing")
    if p6a.get("formal_state_guard", {}).get("changed"):
        reasons.append("p6a_formal_state_changed")
    if p6b.get("formal_state_guard", {}).get("changed"):
        reasons.append("p6b_formal_state_changed")
    if p6c.get("formal_state_guard", {}).get("changed"):
        reasons.append("p6c_formal_state_changed")
    if p6c.get("this_command_wrote_pdf") is not False:
        reasons.append("p6c_pdf_boundary_unclear")
    if p6c.get("this_command_wrote_docx") is not True:
        reasons.append("p6c_docx_write_not_confirmed")
    for check_name, passed in consistency_checks.items():
        if not passed:
            reasons.append(build_consistency_blocker(check_name))
    return reasons


def build_consistency_blocker(check_name: str) -> str:
    return {
        "pdf_hash_matches_p6a": "paper_pdf_hash_mismatch:p6a",
        "docx_hash_matches_p6c": "paper_docx_hash_mismatch:p6c",
        "pdf_bytes_match_p6a": "paper_pdf_bytes_mismatch:p6a",
        "docx_bytes_match_p6c": "paper_docx_bytes_mismatch:p6c",
        "p6b_expected_docx_matches_p6c": "p6b_expected_docx_mismatch:p6c",
        "p6c_final_pdf_matches_p6a": "p6c_final_pdf_mismatch:p6a",
        "p6c_candidate_qmd_matches_p6a": "p6c_candidate_qmd_mismatch:p6a",
    }[check_name]


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "formal_submission_package_ready"
    if any(reason.endswith("_missing") for reason in blocking_reasons):
        return "blocked_by_package_artifacts"
    if any("mismatch" in reason for reason in blocking_reasons):
        return "blocked_by_package_consistency"
    if any(reason.startswith("p6c_") for reason in blocking_reasons):
        return "blocked_by_docx_export"
    if any(reason.startswith("p6b_") for reason in blocking_reasons):
        return "blocked_by_docx_preflight"
    return "blocked_by_final_pdf_writeback"


def build_manual_acceptance() -> dict[str, Any]:
    return {
        "human_status": "pending_manual_acceptance",
        "checklist": [
            {"id": "open_pdf", "label": "打开 PDF，确认页面可读、标题和章节存在"},
            {"id": "open_docx", "label": "打开 DOCX，确认正文、标题和引用字段可读"},
            {"id": "fingerprints", "label": "核对 PDF/DOCX sha256 与 manifest 一致"},
            {"id": "p6_reports", "label": "复核 P6-A/P6-B/P6-C 报告均为 ready/exported"},
            {"id": "formal_state", "label": "确认本节点没有改写正式研究状态"},
        ],
    }


def build_reproduce_commands() -> list[list[str]]:
    return [
        ["python3", "Program/formal_pdf_final_writeback.py", "--project-root", "."],
        ["python3", "Program/formal_docx_export_preflight.py", "--project-root", "."],
        ["python3", "Program/formal_docx_export.py", "--project-root", "."],
        ["python3", "Program/formal_submission_package_manifest.py", "--project-root", "."],
    ]


def build_next_action(blocking_reasons: list[str]) -> dict[str, str]:
    if not blocking_reasons:
        return {
            "id": "manual_submission_package_acceptance",
            "label": "人工验收正式投稿包",
            "description": "打开 PDF 和 DOCX，按 manifest 核对文件指纹、来源报告和复现命令。",
        }
    return {
        "id": "repair_submission_package_inputs",
        "label": "修复正式投稿包输入",
        "description": "先修复 P6-A/P6-B/P6-C 报告、最终 PDF/docx 或文件指纹不一致，再重新汇总 manifest。",
    }


def build_package_manifest(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": report["schema_version"],
        "generated_at": report["generated_at"],
        "status": report["status"],
        "package_root": report["package_root"],
        "artifacts": report["artifacts"],
        "input_reports": report["input_reports"],
        "consistency_checks": report["consistency_checks"],
        "manual_acceptance": report["manual_acceptance"],
        "reproduce_commands": report["reproduce_commands"],
    }


def write_formal_submission_package_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def write_package_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def render_review_markdown(report: dict[str, Any]) -> str:
    blockers = report.get("blocking_reasons") or []
    blocker_lines = "\n".join(f"- `{item}`" for item in blockers) if blockers else "- 无"
    artifact_lines = "\n".join(
        f"- `{name}`：`{artifact.get('path')}` / bytes={artifact.get('bytes')} / sha256=`{artifact.get('sha256')}`"
        for name, artifact in (report.get("artifacts") or {}).items()
    )
    checklist_lines = "\n".join(
        f"- [ ] {item.get('label')}" for item in (report.get("manual_acceptance") or {}).get("checklist", [])
    )
    command_lines = "\n".join(f"- `{' '.join(command)}`" for command in report.get("reproduce_commands") or [])
    return f"""# P6-D 正式投稿包人工验收

## 当前状态

- 状态：`{report.get("status")}`
- 包目录：`{report.get("package_root")}`
- 包内 manifest：`{report.get("package_manifest")}`
- 包内 manifest 已写入：`{str(report.get("package_manifest_written")).lower()}`
- 渲染 PDF：`{str(report.get("boundary_flags", {}).get("this_command_rendered_pdf")).lower()}`
- 渲染 DOCX：`{str(report.get("boundary_flags", {}).get("this_command_rendered_docx")).lower()}`
- 写最终产物：`{str(report.get("boundary_flags", {}).get("this_command_wrote_final_outputs")).lower()}`
- 写正式研究状态：`{str(report.get("boundary_flags", {}).get("this_command_wrote_formal_state")).lower()}`

## 最终文件

{artifact_lines}

## 人工验收清单

{checklist_lines}

## 复现命令

{command_lines}

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
