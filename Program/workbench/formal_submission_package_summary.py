from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute


DEFAULT_SOURCE_MANIFEST = "Results/json/formal_submission_package_manifest.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_submission_package_summary.json"
DEFAULT_OUTPUT_SUMMARY = "state/product/formal_submission_package_summary.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_submission_package_summary.md"
PROTECTED_FORMAL_STATE_FILES = [
    "research_question.json",
    "variable_roles.json",
    "variable_role_set.json",
    "design_spec.json",
    "run_plan.json",
    "supervisor_plan.json",
    "agent_task_queue.json",
    "writeback_approvals.json",
]


def build_formal_submission_package_summary(
    project_root: Path,
    *,
    source_manifest_path: Path,
    formal_state_before: dict[str, str] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_protected_formal_state(project_root)
    source_manifest = load_json(source_manifest_path)
    source_manifest_sha256 = sha256_file(source_manifest_path) if source_manifest_path.exists() else None
    package_manifest_path = resolve_project_path(project_root, str(source_manifest.get("package_manifest") or ""))
    package_manifest = load_json(package_manifest_path) if package_manifest_path else {}
    artifacts = build_artifacts(project_root, source_manifest, package_manifest)
    consistency_checks = build_consistency_checks(source_manifest, package_manifest, artifacts)
    blocking_reasons = build_blocking_reasons(
        source_manifest_path=source_manifest_path,
        source_manifest=source_manifest,
        package_manifest_path=package_manifest_path,
        package_manifest=package_manifest,
        artifacts=artifacts,
        consistency_checks=consistency_checks,
    )
    status = build_status(blocking_reasons)
    ready = status == "ready_for_manual_acceptance"
    after = snapshot_protected_formal_state(project_root)
    summary = {
        "schema_version": "p6.formal_submission_package_summary.v1",
        "generated_at": utc_now(),
        "status": status,
        "ready_for_manual_acceptance": ready,
        "source_manifest": {
            "path": relative_or_absolute(source_manifest_path, project_root),
            "exists": source_manifest_path.exists(),
            "sha256": source_manifest_sha256,
            "status": source_manifest.get("status"),
            "schema_version": source_manifest.get("schema_version"),
        },
        "package_manifest": {
            "path": relative_or_absolute(package_manifest_path, project_root) if package_manifest_path else None,
            "exists": package_manifest_path.exists() if package_manifest_path else False,
            "status": package_manifest.get("status"),
            "schema_version": package_manifest.get("schema_version"),
        },
        "artifacts": artifacts,
        "visible_summary": build_visible_summary(ready, artifacts, source_manifest, blocking_reasons),
        "open_targets": build_open_targets(project_root, artifacts) if ready else [],
        "manual_acceptance": build_manual_acceptance(source_manifest, ready),
        "consistency_checks": consistency_checks,
        "blocking_reasons": blocking_reasons,
        "boundary_flags": {
            "this_command_opened_files": False,
            "this_command_rendered_pdf": False,
            "this_command_rendered_docx": False,
            "this_command_wrote_final_outputs": False,
            "this_command_wrote_formal_research_state": False,
        },
        "formal_state_guard": diff_protected_formal_state(before, after),
        "next_action": build_next_action(ready, blocking_reasons),
    }
    return summary, 0 if ready else 2


def build_artifacts(
    project_root: Path,
    source_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    source_artifacts = source_manifest.get("artifacts") or {}
    package_artifacts = package_manifest.get("artifacts") or {}
    return {
        "paper_pdf": build_artifact(project_root, "paper_pdf", source_artifacts, package_artifacts, "application/pdf"),
        "paper_docx": build_artifact(
            project_root,
            "paper_docx",
            source_artifacts,
            package_artifacts,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    }


def build_artifact(
    project_root: Path,
    artifact_id: str,
    source_artifacts: dict[str, Any],
    package_artifacts: dict[str, Any],
    media_type: str,
) -> dict[str, Any]:
    expected = source_artifacts.get(artifact_id) or {}
    package_expected = package_artifacts.get(artifact_id) or {}
    raw_path = expected.get("path") or package_expected.get("path")
    path = resolve_project_path(project_root, str(raw_path or ""))
    exists = path.exists() if path else False
    return {
        "id": artifact_id,
        "path": relative_or_absolute(path, project_root) if path else None,
        "type": media_type,
        "exists": exists,
        "bytes": path.stat().st_size if exists and path else None,
        "sha256": sha256_file(path) if exists and path else None,
        "expected_bytes": expected.get("bytes"),
        "expected_sha256": expected.get("sha256"),
        "package_expected_bytes": package_expected.get("bytes"),
        "package_expected_sha256": package_expected.get("sha256"),
        "source_report": expected.get("source_report") or package_expected.get("source_report"),
    }


def build_consistency_checks(
    source_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    return {
        "source_manifest_ready": source_manifest.get("status") == "formal_submission_package_ready",
        "package_manifest_ready": package_manifest.get("status") == "formal_submission_package_ready",
        "paper_pdf_exists": artifacts["paper_pdf"].get("exists") is True,
        "paper_docx_exists": artifacts["paper_docx"].get("exists") is True,
        "paper_pdf_hash_matches_submission_manifest": match_optional_hash(
            artifacts["paper_pdf"].get("sha256"), artifacts["paper_pdf"].get("expected_sha256")
        ),
        "paper_docx_hash_matches_submission_manifest": match_optional_hash(
            artifacts["paper_docx"].get("sha256"), artifacts["paper_docx"].get("expected_sha256")
        ),
        "paper_pdf_bytes_match_submission_manifest": match_optional_number(
            artifacts["paper_pdf"].get("bytes"), artifacts["paper_pdf"].get("expected_bytes")
        ),
        "paper_docx_bytes_match_submission_manifest": match_optional_number(
            artifacts["paper_docx"].get("bytes"), artifacts["paper_docx"].get("expected_bytes")
        ),
        "paper_pdf_hash_matches_package_manifest": match_optional_hash(
            artifacts["paper_pdf"].get("sha256"), artifacts["paper_pdf"].get("package_expected_sha256")
        ),
        "paper_docx_hash_matches_package_manifest": match_optional_hash(
            artifacts["paper_docx"].get("sha256"), artifacts["paper_docx"].get("package_expected_sha256")
        ),
    }


def build_blocking_reasons(
    *,
    source_manifest_path: Path,
    source_manifest: dict[str, Any],
    package_manifest_path: Path | None,
    package_manifest: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    consistency_checks: dict[str, bool],
) -> list[str]:
    reasons: list[str] = []
    if not source_manifest_path.exists():
        reasons.append("submission_manifest_missing")
    if source_manifest.get("status") != "formal_submission_package_ready":
        reasons.append("submission_manifest_not_ready")
    if not package_manifest_path or not package_manifest_path.exists():
        reasons.append("package_manifest_missing")
    if package_manifest_path and package_manifest_path.exists() and package_manifest.get("status") != "formal_submission_package_ready":
        reasons.append("package_manifest_not_ready")
    if artifacts["paper_pdf"].get("exists") is not True:
        reasons.append("paper_pdf_missing")
    if artifacts["paper_docx"].get("exists") is not True:
        reasons.append("paper_docx_missing")
    for check_name, passed in consistency_checks.items():
        if not passed and check_name not in {
            "source_manifest_ready",
            "package_manifest_ready",
            "paper_pdf_exists",
            "paper_docx_exists",
        }:
            reasons.append(build_consistency_blocker(check_name))
    return reasons


def build_consistency_blocker(check_name: str) -> str:
    return {
        "paper_pdf_hash_matches_submission_manifest": "paper_pdf_hash_mismatch:submission_manifest",
        "paper_docx_hash_matches_submission_manifest": "paper_docx_hash_mismatch:submission_manifest",
        "paper_pdf_bytes_match_submission_manifest": "paper_pdf_bytes_mismatch:submission_manifest",
        "paper_docx_bytes_match_submission_manifest": "paper_docx_bytes_mismatch:submission_manifest",
        "paper_pdf_hash_matches_package_manifest": "paper_pdf_hash_mismatch:package_manifest",
        "paper_docx_hash_matches_package_manifest": "paper_docx_hash_mismatch:package_manifest",
    }[check_name]


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "ready_for_manual_acceptance"
    if any(reason in {"submission_manifest_missing", "submission_manifest_not_ready"} for reason in blocking_reasons):
        return "blocked_by_submission_manifest"
    if any(reason.endswith("_missing") for reason in blocking_reasons):
        return "blocked_by_package_artifacts"
    if any("mismatch" in reason for reason in blocking_reasons):
        return "blocked_by_package_consistency"
    return "blocked_by_package_manifest"


def build_visible_summary(
    ready: bool,
    artifacts: dict[str, dict[str, Any]],
    source_manifest: dict[str, Any],
    blocking_reasons: list[str],
) -> list[dict[str, str]]:
    return [
        {
            "id": "package_status",
            "label": "正式包状态",
            "value": "可进入人工验收" if ready else "需要修复后再验收",
        },
        {
            "id": "final_files",
            "label": "最终文件",
            "value": f"PDF {artifacts['paper_pdf'].get('bytes') or 0} bytes / DOCX {artifacts['paper_docx'].get('bytes') or 0} bytes",
        },
        {
            "id": "provenance",
            "label": "来源",
            "value": source_manifest.get("package_manifest") or "未找到包内 manifest",
        },
        {
            "id": "consistency",
            "label": "一致性",
            "value": "文件指纹与 manifest 一致" if ready else "；".join(blocking_reasons),
        },
        {
            "id": "next_manual_action",
            "label": "下一步",
            "value": "打开 PDF 和 DOCX，按验收清单逐项确认" if ready else "先修复 blocker，再重新生成 summary",
        },
    ]


def build_open_targets(project_root: Path, artifacts: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    targets = []
    for artifact_id, label, target_type in [
        ("paper_pdf", "打开 PDF", "pdf"),
        ("paper_docx", "打开 DOCX", "docx"),
    ]:
        artifact = artifacts[artifact_id]
        path = str(artifact.get("path") or "")
        absolute_path = str((project_root / path).resolve()) if path else ""
        targets.append(
            {
                "id": artifact_id,
                "label": label,
                "path": path,
                "absolute_path": absolute_path,
                "type": target_type,
                "media_type": artifact.get("type"),
                "exists": artifact.get("exists"),
                "bytes": artifact.get("bytes"),
                "sha256": artifact.get("sha256"),
                "open_command": ["open", path],
            }
        )
    return targets


def build_manual_acceptance(source_manifest: dict[str, Any], ready: bool) -> dict[str, Any]:
    manifest_acceptance = source_manifest.get("manual_acceptance") or {}
    checklist = manifest_acceptance.get("checklist") or []
    return {
        "status": "pending_manual_acceptance" if ready else "blocked",
        "next_action": "open_and_review_pdf_docx" if ready else "repair_package_inputs",
        "checklist": checklist,
    }


def build_next_action(ready: bool, blocking_reasons: list[str]) -> dict[str, Any]:
    if ready:
        return {
            "id": "open_and_review_pdf_docx",
            "label": "打开 PDF/DOCX 做人工验收",
            "description": "产品层可以展示两个打开入口；人工确认后再进入正式验收写回节点。",
        }
    return {
        "id": "repair_formal_package_summary_inputs",
        "label": "修复正式包验收入口输入",
        "description": "先修复 manifest、最终文件或指纹不一致，再重新生成产品层 summary。",
        "blocking_reasons": blocking_reasons,
    }


def write_formal_submission_package_summary_outputs(
    report_path: Path,
    summary_path: Path,
    review_path: Path,
    summary: dict[str, Any],
) -> tuple[Path, Path, Path]:
    for path in [report_path, summary_path, review_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    report_path.write_text(payload, encoding="utf-8")
    summary_path.write_text(payload, encoding="utf-8")
    review_path.write_text(render_review_markdown(summary), encoding="utf-8")
    return report_path, summary_path, review_path


def render_review_markdown(summary: dict[str, Any]) -> str:
    target_lines = "\n".join(
        f"- `{target.get('id')}`：`{target.get('path')}` / bytes={target.get('bytes')} / sha256=`{target.get('sha256')}`"
        for target in summary.get("open_targets") or []
    )
    if not target_lines:
        target_lines = "- 当前无可打开验收入口"
    summary_lines = "\n".join(
        f"- **{item.get('label')}**：{item.get('value')}" for item in summary.get("visible_summary") or []
    )
    checklist_lines = "\n".join(
        f"- [ ] {item.get('label')}" for item in (summary.get("manual_acceptance") or {}).get("checklist", [])
    )
    if not checklist_lines:
        checklist_lines = "- [ ] 修复 blocker 后重新生成验收入口"
    blocker_lines = "\n".join(f"- `{item}`" for item in summary.get("blocking_reasons") or []) or "- 无"
    return f"""# P6-E 正式包产品验收入口

## 当前状态

- 状态：`{summary.get("status")}`
- 可进入人工验收：`{str(summary.get("ready_for_manual_acceptance")).lower()}`
- 来源 manifest：`{summary.get("source_manifest", {}).get("path")}`
- 打开文件：`{str(summary.get("boundary_flags", {}).get("this_command_opened_files")).lower()}`
- 渲染 PDF：`{str(summary.get("boundary_flags", {}).get("this_command_rendered_pdf")).lower()}`
- 渲染 DOCX：`{str(summary.get("boundary_flags", {}).get("this_command_rendered_docx")).lower()}`
- 写正式研究状态：`{str(summary.get("boundary_flags", {}).get("this_command_wrote_formal_research_state")).lower()}`

## 产品可见摘要

{summary_lines}

## 打开入口

{target_lines}

## 人工验收清单

{checklist_lines}

## 阻断原因

{blocker_lines}
"""


def load_json(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def snapshot_protected_formal_state(project_root: Path) -> dict[str, str]:
    state_dir = project_root / "state" / "product"
    snapshot: dict[str, str] = {}
    for name in PROTECTED_FORMAL_STATE_FILES:
        path = state_dir / name
        if path.exists():
            snapshot[name] = path.read_text(encoding="utf-8")
    return snapshot


def diff_protected_formal_state(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed_paths = sorted({*before.keys(), *after.keys()} - {name for name in before if before.get(name) == after.get(name)})
    return {"changed": bool(changed_paths), "changed_paths": changed_paths}


def match_optional_hash(actual: Any, expected: Any) -> bool:
    return bool(actual and expected and actual == expected)


def match_optional_number(actual: Any, expected: Any) -> bool:
    return actual is not None and expected is not None and int(actual) == int(expected)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
