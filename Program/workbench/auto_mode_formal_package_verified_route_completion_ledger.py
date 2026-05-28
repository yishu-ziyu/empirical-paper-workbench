from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_completion_ledger.v1"
VERIFICATION_SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_verification.v1"
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_verification.json")
DEFAULT_LEDGER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_completion_ledger.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_completion_ledger.md")
VERIFIED_STATUS = "route_specific_artifact_verified_for_review"
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
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


def build_auto_mode_formal_package_verified_route_completion_ledger(
    route_specific_artifact_verification: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    verification_reasons = build_verification_blocking_reasons(route_specific_artifact_verification)
    contract_reasons = []
    boundary_reasons = []
    if not verification_reasons:
        contract_reasons = build_completion_contract_blocking_reasons(route_specific_artifact_verification)
    if not verification_reasons and not contract_reasons:
        boundary_reasons = build_boundary_blocking_reasons(route_specific_artifact_verification)

    blocking_reasons = dedupe(verification_reasons + contract_reasons + boundary_reasons)
    status = build_status(verification_reasons, contract_reasons, boundary_reasons)
    ledger_recorded = status == "verified_route_completion_ledger_recorded"
    route_type = route_specific_artifact_verification.get("verified_route_type", "")
    records = build_route_completion_records(route_specific_artifact_verification) if ledger_recorded else []
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_verification.get("topic", ""),
        "source_paths": {
            "route_specific_artifact_verification": source_paths.get(
                "route_specific_artifact_verification",
                str(DEFAULT_VERIFICATION_PATH),
            ),
        },
        "status": status,
        "route_completion_ledger_recorded": ledger_recorded,
        "can_enter_next_auto_mode_gate": ledger_recorded,
        "route_type": route_specific_artifact_verification.get("route_type", ""),
        "verified_route_type": route_type if ledger_recorded else "",
        "delegated_status": route_specific_artifact_verification.get("delegated_status", ""),
        "route_specific_artifact_verified": route_specific_artifact_verification.get("route_specific_artifact_verified")
        is True,
        "source_product_state_verified": route_specific_artifact_verification.get("source_product_state_verified")
        is True,
        "selected_route_executed": route_specific_artifact_verification.get("selected_route_executed") is True,
        "export_or_acceptance_executed": route_specific_artifact_verification.get("export_or_acceptance_executed")
        is True,
        "rendered_pdf": route_specific_artifact_verification.get("rendered_pdf") is True,
        "rendered_docx": route_specific_artifact_verification.get("rendered_docx") is True,
        "package_manifest_generated": route_specific_artifact_verification.get("package_manifest_generated") is True,
        "manual_acceptance_performed": route_specific_artifact_verification.get("manual_acceptance_performed") is True,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "artifact_verification_records_count": len(
            route_specific_artifact_verification.get("artifact_verification_records", []) or []
        ),
        "blocking_reasons": blocking_reasons,
        "source_verification": build_source_verification_summary(route_specific_artifact_verification),
        "route_completion_records": records,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_verification_blocking_reasons(route_specific_artifact_verification: dict[str, Any]) -> list[str]:
    reasons = []
    if route_specific_artifact_verification.get("schema_version") != VERIFICATION_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_verification_missing_or_invalid_schema")
    verified_status = route_specific_artifact_verification.get("status") == VERIFIED_STATUS
    if not verified_status:
        reasons.append("route_specific_artifact_verification_not_verified")
        if route_specific_artifact_verification.get("blocking_reasons"):
            reasons.append("source_verification_has_blocking_reasons")
    if route_specific_artifact_verification.get("route_specific_artifact_verified") is not True:
        reasons.append("route_specific_artifact_verified_flag_false")
    return dedupe(reasons)


def build_completion_contract_blocking_reasons(route_specific_artifact_verification: dict[str, Any]) -> list[str]:
    route_type = route_specific_artifact_verification.get("verified_route_type", "")
    source_route_type = route_specific_artifact_verification.get("route_type", "")
    reasons = []
    if route_specific_artifact_verification.get("blocking_reasons"):
        reasons.append("source_verification_has_blocking_reasons")
    if not route_type:
        reasons.append("verified_route_type_missing")
    elif route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if route_type and source_route_type and route_type != source_route_type:
        reasons.append(f"verified_route_type_mismatch:{route_type}")
    if route_specific_artifact_verification.get("selected_route_executed") is not True:
        reasons.append("selected_route_not_executed")
    if route_specific_artifact_verification.get("export_or_acceptance_executed") is not True:
        reasons.append("export_or_acceptance_not_executed")
    if route_type in VALID_ROUTE_TYPES and not route_flags_match(route_specific_artifact_verification, route_type):
        reasons.append(f"verified_route_flag_mismatch:{route_type}")
    if route_type == "manual_acceptance" and route_specific_artifact_verification.get("source_product_state_verified") is not True:
        reasons.append("manual_acceptance_source_product_state_not_verified")
    if route_type in {"pdf_export", "docx_export", "package_manifest"}:
        if route_specific_artifact_verification.get("source_product_state_verified") is True:
            reasons.append(f"non_manual_source_product_state_should_be_false:{route_type}")
    records = route_specific_artifact_verification.get("artifact_verification_records", []) or []
    if not records:
        reasons.append("artifact_verification_records_missing")
    for record in records:
        artifact_id = record.get("artifact_id", "unknown")
        if record.get("verification_status") != "verified":
            reasons.append(f"artifact_verification_record_not_verified:{artifact_id}")
        if record.get("exists") is not True:
            reasons.append(f"artifact_not_existing:{artifact_id}")
        if not record.get("path"):
            reasons.append(f"artifact_path_missing:{artifact_id}")
        if record.get("bytes") is None:
            reasons.append(f"artifact_bytes_missing:{artifact_id}")
        if not record.get("sha256"):
            reasons.append(f"artifact_sha256_missing:{artifact_id}")
    return dedupe(reasons)


def route_flags_match(route_specific_artifact_verification: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(
        route_specific_artifact_verification.get(flag) is expected_value
        for flag, expected_value in expected.items()
    )


def build_boundary_blocking_reasons(route_specific_artifact_verification: dict[str, Any]) -> list[str]:
    reasons = []
    if route_specific_artifact_verification.get("formal_writeback_executed") is True:
        reasons.append("source_verification_formal_writeback_executed")
    if route_specific_artifact_verification.get("this_command_wrote_formal_state") is True:
        reasons.append("source_verification_wrote_formal_state")
    if route_specific_artifact_verification.get("can_write_product_state") is True:
        reasons.append("source_verification_allows_product_state_write")
    for flag, value in route_specific_artifact_verification.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"source_verification_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    verification_reasons: list[str],
    contract_reasons: list[str],
    boundary_reasons: list[str],
) -> str:
    if verification_reasons:
        return "blocked_by_route_specific_artifact_verification"
    if contract_reasons:
        return "blocked_by_verified_route_completion_contract"
    if boundary_reasons:
        return "blocked_by_verified_route_completion_boundary"
    return "verified_route_completion_ledger_recorded"


def build_source_verification_summary(route_specific_artifact_verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_verification.get("schema_version", ""),
        "status": route_specific_artifact_verification.get("status", ""),
        "route_type": route_specific_artifact_verification.get("route_type", ""),
        "verified_route_type": route_specific_artifact_verification.get("verified_route_type", ""),
        "delegated_status": route_specific_artifact_verification.get("delegated_status", ""),
        "route_specific_artifact_verified": route_specific_artifact_verification.get(
            "route_specific_artifact_verified"
        )
        is True,
        "source_product_state_verified": route_specific_artifact_verification.get(
            "source_product_state_verified"
        )
        is True,
        "selected_route_executed": route_specific_artifact_verification.get("selected_route_executed") is True,
        "export_or_acceptance_executed": route_specific_artifact_verification.get(
            "export_or_acceptance_executed"
        )
        is True,
        "artifact_verification_records_count": len(
            route_specific_artifact_verification.get("artifact_verification_records", []) or []
        ),
        "formal_writeback_executed": route_specific_artifact_verification.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": route_specific_artifact_verification.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": route_specific_artifact_verification.get("can_write_product_state") is True,
        "blocking_reasons": route_specific_artifact_verification.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_verification.get("boundary_flags", {}),
    }


def build_route_completion_records(route_specific_artifact_verification: dict[str, Any]) -> list[dict[str, Any]]:
    route_type = route_specific_artifact_verification.get("verified_route_type", "")
    artifacts = [
        build_verified_artifact(record)
        for record in route_specific_artifact_verification.get("artifact_verification_records", [])
    ]
    return [
        {
            "completion_id": f"verified_route_completion::{route_type}",
            "completion_status": "verified_route_completion_recorded",
            "route_type": route_type,
            "delegated_status": route_specific_artifact_verification.get("delegated_status", ""),
            "source_verification_status": route_specific_artifact_verification.get("status", ""),
            "source_product_state_verified": route_specific_artifact_verification.get(
                "source_product_state_verified"
            )
            is True,
            "artifact_count": len(artifacts),
            "artifact_ids": [artifact["artifact_id"] for artifact in artifacts],
            "verified_artifacts": artifacts,
            "can_enter_next_auto_mode_gate": True,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
        }
    ]


def build_verified_artifact(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": record.get("artifact_id", ""),
        "path": record.get("path", ""),
        "exists": record.get("exists") is True,
        "bytes": record.get("bytes"),
        "delegated_bytes": record.get("delegated_bytes"),
        "sha256": record.get("sha256", ""),
        "delegated_sha256": record.get("delegated_sha256", ""),
        "verification_status": record.get("verification_status", ""),
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
    if status == "verified_route_completion_ledger_recorded":
        return {
            "id": "run_next_auto_mode_gate_for_verified_route",
            "label": "Run next Auto Mode gate",
            "description": f"The `{route_type}` route completion ledger is recorded and ready for the next gate.",
        }
    if status == "blocked_by_route_specific_artifact_verification":
        return {
            "id": "resolve_route_specific_artifact_verification_blockers",
            "label": "Resolve P7-AC blockers",
            "description": "P7-AC must verify one route-specific artifact before completion can be recorded.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_completion_contract":
        return {
            "id": "repair_verified_route_completion_contract",
            "label": "Repair verified route completion contract",
            "description": "The verified route report must be internally consistent before ledger recording.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_boundary_violation",
        "label": "Resolve verified route boundary violation",
        "description": "The completion ledger is read-only and cannot consume a source report with state-write flags.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_verified_route_completion_ledger_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_LEDGER_PATH,
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
        "# Auto Mode Formal Package Verified Route Completion Ledger",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- route completion ledger recorded：{str(report['route_completion_ledger_recorded']).lower()}",
        f"- 可进入下一 Auto Mode gate：{str(report['can_enter_next_auto_mode_gate']).lower()}",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- delegated status：`{report['delegated_status']}`",
        f"- artifact verification records：{report['artifact_verification_records_count']}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["route_completion_records"]:
        lines.extend(["", "## Route Completion Records"])
        for record in report["route_completion_records"]:
            lines.append(
                f"- `{record['completion_id']}`: route=`{record['route_type']}`, "
                f"artifacts={record['artifact_count']}, next_gate={str(record['can_enter_next_auto_mode_gate']).lower()}"
            )
            for artifact in record["verified_artifacts"]:
                lines.append(
                    f"  - `{artifact['artifact_id']}`: `{artifact['path']}` / "
                    f"bytes={artifact.get('bytes')} / sha256=`{artifact.get('sha256')}` / "
                    f"status=`{artifact['verification_status']}`"
                )
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


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
