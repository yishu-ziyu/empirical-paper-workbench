from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_verification.v1"
EXECUTOR_SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_executor.v1"
DEFAULT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_verification.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_verification.md")
DEFAULT_MANUAL_ACCEPTANCE_STATE_PATH = Path("state/product/formal_submission_package_manual_acceptance.json")
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
DELEGATED_SCHEMAS = {
    "pdf_export": "p6.formal_pdf_final_writeback.v1",
    "docx_export": "p6.formal_docx_export.v1",
    "package_manifest": "p6.formal_submission_package_manifest.v1",
    "manual_acceptance": "p6.formal_submission_package_manual_acceptance.v1",
}
DELEGATED_SUCCESS_STATUSES = {
    "pdf_export": {"final_pdf_written", "final_pdf_already_written"},
    "docx_export": {"docx_exported"},
    "package_manifest": {"formal_submission_package_ready"},
    "manual_acceptance": {
        "formal_submission_package_accepted",
        "pending_human_manual_acceptance",
        "formal_submission_package_needs_revision",
        "formal_submission_package_rejected",
    },
}
ROUTE_FLAGS = {
    "pdf_export": {
        "rendered_pdf": True,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
    },
    "docx_export": {
        "rendered_pdf": False,
        "rendered_docx": True,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
    },
    "package_manifest": {
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": True,
        "manual_acceptance_performed": False,
    },
    "manual_acceptance": {
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": True,
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_route_specific_artifact_verification(
    project_root: Path,
    route_specific_artifact_executor: dict[str, Any],
    delegated_report: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    executor_reasons = build_executor_blocking_reasons(route_specific_artifact_executor)
    contract_reasons = (
        build_executor_contract_blocking_reasons(route_specific_artifact_executor) if not executor_reasons else []
    )
    route_type = route_specific_artifact_executor.get("route_type", "") if not executor_reasons else ""
    delegated_reasons = (
        build_delegated_report_blocking_reasons(route_type, delegated_report)
        if not executor_reasons and not contract_reasons
        else []
    )
    artifact_records: list[dict[str, Any]] = []
    integrity_reasons: list[str] = []
    source_product_state_verified = False
    if not executor_reasons and not contract_reasons and not delegated_reasons:
        artifact_records, integrity_reasons, source_product_state_verified = build_artifact_verification_records(
            project_root,
            route_type,
            delegated_report,
        )

    blocking_reasons = executor_reasons + contract_reasons + delegated_reasons + integrity_reasons
    status = build_status(executor_reasons, contract_reasons, delegated_reasons, integrity_reasons)
    verified = status == "route_specific_artifact_verified_for_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_executor.get("topic", delegated_report.get("topic", "")),
        "source_paths": {
            "route_specific_artifact_executor": source_paths.get(
                "route_specific_artifact_executor",
                str(DEFAULT_EXECUTOR_PATH),
            ),
            "delegated_report": source_paths.get(
                "delegated_report",
                route_specific_artifact_executor.get("delegated_report_path", ""),
            ),
        },
        "status": status,
        "route_type": route_specific_artifact_executor.get("route_type", ""),
        "verified_route_type": route_type if verified else "",
        "delegated_status": delegated_report.get("status", route_specific_artifact_executor.get("delegated_status", "")),
        "route_specific_artifact_verified": verified,
        "source_product_state_verified": source_product_state_verified,
        "selected_route_executed": route_specific_artifact_executor.get("selected_route_executed") is True,
        "export_or_acceptance_executed": route_specific_artifact_executor.get("export_or_acceptance_executed") is True,
        "rendered_pdf": route_specific_artifact_executor.get("rendered_pdf") is True,
        "rendered_docx": route_specific_artifact_executor.get("rendered_docx") is True,
        "package_manifest_generated": route_specific_artifact_executor.get("package_manifest_generated") is True,
        "manual_acceptance_performed": route_specific_artifact_executor.get("manual_acceptance_performed") is True,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_executor": build_source_executor(route_specific_artifact_executor),
        "source_delegated_report": build_source_delegated_report(delegated_report),
        "artifact_verification_records": artifact_records if not blocking_reasons else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_executor_blocking_reasons(route_specific_artifact_executor: dict[str, Any]) -> list[str]:
    reasons = []
    if route_specific_artifact_executor.get("schema_version") != EXECUTOR_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_executor_missing_or_invalid_schema")
    if route_specific_artifact_executor.get("status") != "route_specific_artifact_executed":
        reasons.append("route_specific_artifact_executor_not_completed")
    if route_specific_artifact_executor.get("route_specific_artifact_executed") is not True:
        reasons.append("route_specific_artifact_not_executed")
    if route_specific_artifact_executor.get("selected_route_executed") is not True:
        reasons.append("selected_route_not_executed")
    if route_specific_artifact_executor.get("export_or_acceptance_executed") is not True:
        reasons.append("export_or_acceptance_not_executed")
    if route_specific_artifact_executor.get("blocking_reasons"):
        reasons.append("route_specific_artifact_executor_has_blocking_reasons")
    return dedupe(reasons)


def build_executor_contract_blocking_reasons(route_specific_artifact_executor: dict[str, Any]) -> list[str]:
    route_type = route_specific_artifact_executor.get("route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"route_type_unknown:{route_type}")
        return reasons
    if route_specific_artifact_executor.get("route_specific_command_executed") is not True:
        reasons.append("route_specific_command_not_executed")
    if route_specific_artifact_executor.get("delegated_returncode") != 0:
        reasons.append("delegated_returncode_not_zero")
    if not route_specific_artifact_executor.get("delegated_report_path"):
        reasons.append(f"delegated_report_path_missing:{route_type}")
    if route_specific_artifact_executor.get("delegated_status") not in DELEGATED_SUCCESS_STATUSES[route_type]:
        reasons.append(f"delegated_status_not_success:{route_type}")
    if route_specific_artifact_executor.get("can_write_product_state") is True and route_type != "manual_acceptance":
        reasons.append(f"executor_product_state_write_not_allowed:{route_type}")
    if route_specific_artifact_executor.get("can_write_product_state") is not True and route_type == "manual_acceptance":
        reasons.append("manual_acceptance_product_state_write_not_recorded")
    if not route_flags_match(route_specific_artifact_executor, route_type):
        reasons.append(f"executor_route_flag_mismatch:{route_type}")
    operation_route_type = (route_specific_artifact_executor.get("selected_route_operation") or {}).get("route_type", "")
    if operation_route_type and operation_route_type != route_type:
        reasons.append(f"selected_route_operation_mismatch:{route_type}")
    for flag, value in route_specific_artifact_executor.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"route_specific_artifact_executor_boundary_violation:{flag}")
    return dedupe(reasons)


def route_flags_match(route_specific_artifact_executor: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(route_specific_artifact_executor.get(flag) is expected_value for flag, expected_value in expected.items())


def build_delegated_report_blocking_reasons(route_type: str, delegated_report: dict[str, Any]) -> list[str]:
    reasons = []
    if delegated_report.get("schema_version") != DELEGATED_SCHEMAS[route_type]:
        reasons.append(f"delegated_report_schema_mismatch:{route_type}")
    if delegated_report.get("status") not in DELEGATED_SUCCESS_STATUSES[route_type]:
        reasons.append(f"delegated_report_status_not_success:{route_type}")
    if delegated_report.get("blocking_reasons"):
        reasons.append(f"delegated_report_has_blocking_reasons:{route_type}")
    return dedupe(reasons)


def build_artifact_verification_records(
    project_root: Path,
    route_type: str,
    delegated_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], bool]:
    if route_type == "pdf_export":
        return build_pdf_records(project_root, delegated_report)
    if route_type == "docx_export":
        return build_docx_records(project_root, delegated_report)
    if route_type == "package_manifest":
        return build_package_manifest_records(project_root, delegated_report)
    if route_type == "manual_acceptance":
        return build_manual_acceptance_records(project_root, delegated_report)
    return [], [f"route_type_unknown:{route_type}"], False


def build_pdf_records(project_root: Path, delegated_report: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], bool]:
    record, reasons = build_file_artifact_record(
        project_root,
        "paper_pdf",
        delegated_report.get("final_pdf", ""),
        delegated_report.get("final_pdf_bytes"),
        delegated_report.get("final_pdf_sha256", ""),
    )
    if delegated_report.get("final_pdf_exists") is not True:
        reasons.append("delegated_pdf_exists_flag_false:paper_pdf")
    return [record], reasons, False


def build_docx_records(project_root: Path, delegated_report: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], bool]:
    record, reasons = build_file_artifact_record(
        project_root,
        "paper_docx",
        delegated_report.get("docx", ""),
        delegated_report.get("docx_bytes"),
        delegated_report.get("docx_sha256", ""),
    )
    if delegated_report.get("docx_exists") is not True:
        reasons.append("delegated_docx_exists_flag_false:paper_docx")
    return [record], reasons, False


def build_package_manifest_records(
    project_root: Path,
    delegated_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], bool]:
    records = []
    reasons = []
    manifest_record, manifest_reasons = build_package_manifest_file_record(
        project_root,
        delegated_report.get("package_manifest", ""),
        delegated_report,
    )
    records.append(manifest_record)
    reasons.extend(manifest_reasons)
    if delegated_report.get("package_manifest_written") is not True:
        reasons.append("package_manifest_written_flag_false")
    artifacts = delegated_report.get("artifacts") or {}
    for artifact_id in ["paper_pdf", "paper_docx"]:
        artifact = artifacts.get(artifact_id) or {}
        record, artifact_reasons = build_file_artifact_record(
            project_root,
            artifact_id,
            artifact.get("path", ""),
            artifact.get("bytes"),
            artifact.get("sha256", ""),
        )
        records.append(record)
        reasons.extend(artifact_reasons)
    return records, dedupe(reasons), False


def build_manual_acceptance_records(
    project_root: Path,
    delegated_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], bool]:
    records = []
    reasons = []
    state_path = project_root / DEFAULT_MANUAL_ACCEPTANCE_STATE_PATH
    state_record, state_reasons, state_verified = build_manual_acceptance_state_record(
        project_root,
        state_path,
        delegated_report,
    )
    records.append(state_record)
    reasons.extend(state_reasons)
    artifacts = delegated_report.get("accepted_artifacts") or {}
    for artifact_id in ["paper_pdf", "paper_docx"]:
        artifact = artifacts.get(artifact_id) or {}
        record, artifact_reasons = build_file_artifact_record(
            project_root,
            artifact_id,
            artifact.get("path", ""),
            artifact.get("bytes"),
            artifact.get("sha256", ""),
        )
        records.append(record)
        reasons.extend(artifact_reasons)
        if artifact.get("hash_matches_summary") is not True:
            reasons.append(f"manual_acceptance_summary_hash_mismatch:{artifact_id}")
        if artifact.get("bytes_match_summary") is not True:
            reasons.append(f"manual_acceptance_summary_bytes_mismatch:{artifact_id}")
    return records, dedupe(reasons), state_verified and not reasons


def build_package_manifest_file_record(
    project_root: Path,
    manifest_path_value: str,
    delegated_report: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    path = resolve_project_path(project_root, manifest_path_value)
    rel = display_path(project_root, path, manifest_path_value)
    reasons = []
    exists = path.exists() if path else False
    if not rel.startswith("Submissions/formal_package/"):
        reasons.append("artifact_outside_formal_package:package_manifest")
    if not exists:
        reasons.append("artifact_missing:package_manifest")
        manifest_payload = {}
    else:
        manifest_payload = load_json_or_empty(path)
    if exists and manifest_payload.get("schema_version") != delegated_report.get("schema_version"):
        reasons.append("package_manifest_schema_mismatch")
    if exists and manifest_payload.get("status") != delegated_report.get("status"):
        reasons.append("package_manifest_status_mismatch")
    record = {
        "artifact_id": "package_manifest",
        "path": rel,
        "exists": exists,
        "bytes": path.stat().st_size if exists and path else None,
        "delegated_bytes": None,
        "sha256": sha256_file(path) if exists and path else "",
        "delegated_sha256": "",
        "verification_status": "verified" if not reasons else "blocked",
    }
    return record, reasons


def build_manual_acceptance_state_record(
    project_root: Path,
    state_path: Path,
    delegated_report: dict[str, Any],
) -> tuple[dict[str, Any], list[str], bool]:
    reasons = []
    exists = state_path.exists()
    state_payload = load_json_or_empty(state_path) if exists else {}
    if not exists:
        reasons.append("manual_acceptance_state_missing")
    for key in ["schema_version", "status", "decision", "accepted", "needs_revision"]:
        if exists and state_payload.get(key) != delegated_report.get(key):
            reasons.append(f"manual_acceptance_state_mismatch:{key}")
    record = {
        "artifact_id": "manual_acceptance_state",
        "path": str(DEFAULT_MANUAL_ACCEPTANCE_STATE_PATH),
        "exists": exists,
        "bytes": state_path.stat().st_size if exists else None,
        "delegated_bytes": None,
        "sha256": sha256_file(state_path) if exists else "",
        "delegated_sha256": "",
        "verification_status": "verified" if not reasons else "blocked",
    }
    return record, reasons, exists and not reasons


def build_file_artifact_record(
    project_root: Path,
    artifact_id: str,
    path_value: str,
    delegated_bytes: Any,
    delegated_sha256: str,
) -> tuple[dict[str, Any], list[str]]:
    reasons = []
    path = resolve_project_path(project_root, str(path_value or ""))
    rel = display_path(project_root, path, str(path_value or ""))
    if not rel.startswith("Submissions/formal_package/"):
        reasons.append(f"artifact_outside_formal_package:{artifact_id}")
    exists = path.exists() if path else False
    if not exists:
        reasons.append(f"artifact_missing:{artifact_id}")
    actual_bytes = path.stat().st_size if exists and path else None
    actual_sha256 = sha256_file(path) if exists and path else ""
    if delegated_bytes is None:
        reasons.append(f"artifact_delegated_bytes_missing:{artifact_id}")
    elif actual_bytes is not None and int(actual_bytes) != int(delegated_bytes):
        reasons.append(f"artifact_bytes_mismatch:{artifact_id}")
    if not delegated_sha256:
        reasons.append(f"artifact_delegated_sha256_missing:{artifact_id}")
    elif actual_sha256 and actual_sha256 != delegated_sha256:
        reasons.append(f"artifact_sha256_mismatch:{artifact_id}")
    return {
        "artifact_id": artifact_id,
        "path": rel,
        "exists": exists,
        "bytes": actual_bytes,
        "delegated_bytes": delegated_bytes,
        "sha256": actual_sha256,
        "delegated_sha256": delegated_sha256,
        "verification_status": "verified" if not reasons else "blocked",
    }, reasons


def build_status(
    executor_reasons: list[str],
    contract_reasons: list[str],
    delegated_reasons: list[str],
    integrity_reasons: list[str],
) -> str:
    if executor_reasons:
        return "blocked_by_route_specific_artifact_executor"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_contract"
    if delegated_reasons:
        return "blocked_by_delegated_artifact_report"
    if integrity_reasons:
        return "blocked_by_route_specific_artifact_integrity"
    return "route_specific_artifact_verified_for_review"


def build_source_executor(route_specific_artifact_executor: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_executor.get("schema_version", ""),
        "status": route_specific_artifact_executor.get("status", ""),
        "route_type": route_specific_artifact_executor.get("route_type", ""),
        "route_specific_artifact_executed": route_specific_artifact_executor.get("route_specific_artifact_executed")
        is True,
        "route_specific_command_executed": route_specific_artifact_executor.get("route_specific_command_executed")
        is True,
        "delegated_returncode": route_specific_artifact_executor.get("delegated_returncode"),
        "delegated_status": route_specific_artifact_executor.get("delegated_status", ""),
        "delegated_report_path": route_specific_artifact_executor.get("delegated_report_path", ""),
        "blocking_reasons": route_specific_artifact_executor.get("blocking_reasons", []),
    }


def build_source_delegated_report(delegated_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": delegated_report.get("schema_version", ""),
        "status": delegated_report.get("status", ""),
        "blocking_reasons": delegated_report.get("blocking_reasons", []),
    }


def build_boundary_flags() -> dict[str, bool]:
    return {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "generated_package_manifest": False,
        "performed_manual_acceptance": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "route_specific_artifact_verified_for_review":
        return {
            "id": "record_verified_route_completion",
            "label": "Record verified route completion",
            "description": f"The `{route_type}` route artifact is verified and can move to the next Auto Mode gate.",
        }
    if status == "blocked_by_route_specific_artifact_executor":
        return {
            "id": "resolve_route_specific_artifact_executor_blockers",
            "label": "Resolve P7-AB blockers",
            "description": "P7-AB must complete one route-specific artifact command before verification.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_contract":
        return {
            "id": "repair_route_specific_artifact_executor_contract",
            "label": "Repair P7-AB completion contract",
            "description": "P7-AB must record a clean completed route with matching flags and delegated status.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_delegated_artifact_report":
        return {
            "id": "repair_delegated_artifact_report",
            "label": "Repair delegated artifact report",
            "description": "The route-specific delegated report must have the expected schema and success status.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_route_specific_artifact_integrity",
        "label": "Repair route artifact integrity",
        "description": "The selected route artifact must exist and match delegated report fingerprints.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_route_specific_artifact_verification_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_VERIFICATION_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Package Route-Specific Artifact Verification",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 路线类型：`{report['route_type']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- delegated status：`{report['delegated_status']}`",
        f"- 已验证 route-specific artifact：{str(report['route_specific_artifact_verified']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["artifact_verification_records"]:
        lines.extend(["", "## Artifact Verification Records"])
        for record in report["artifact_verification_records"]:
            lines.append(
                f"- `{record['artifact_id']}`: `{record['path']}` / "
                f"bytes={record.get('bytes')} / sha256=`{record.get('sha256')}` / "
                f"status=`{record['verification_status']}`"
            )
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def display_path(project_root: Path, path: Path | None, fallback: str) -> str:
    if path is None:
        return fallback
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
