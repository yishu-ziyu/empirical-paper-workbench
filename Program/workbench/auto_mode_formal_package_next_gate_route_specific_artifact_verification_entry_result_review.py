from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_verified_route_completion_ledger import (
    build_auto_mode_formal_package_verified_route_completion_ledger,
)


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.v1"
ENTRY_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.v1"
VERIFICATION_SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_verification.v1"
ENTRY_READY_STATUS = "next_gate_route_specific_artifact_verification_entered"
VERIFICATION_SUCCESS_STATUS = "route_specific_artifact_verified_for_review"
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
)
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_verification.json")
DEFAULT_VERIFICATION_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_verification.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.md"
)
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


def build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review(
    project_root: Path,
    route_specific_artifact_verification_entry: dict[str, Any],
    route_specific_artifact_verification: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    entry_reasons = build_entry_blocking_reasons(route_specific_artifact_verification_entry)
    verification_has_valid_schema = (
        route_specific_artifact_verification.get("schema_version") == VERIFICATION_SCHEMA_VERSION
    )
    contract_reasons = (
        build_entry_result_contract_blocking_reasons(
            route_specific_artifact_verification_entry,
            route_specific_artifact_verification,
        )
        if not entry_reasons and verification_has_valid_schema
        else []
    )
    ledger_probe = (
        build_auto_mode_formal_package_verified_route_completion_ledger(route_specific_artifact_verification)
        if not entry_reasons and not contract_reasons
        else {}
    )
    verification_output_reasons = (
        list(ledger_probe.get("blocking_reasons", []))
        if ledger_probe and ledger_probe.get("status") != "verified_route_completion_ledger_recorded"
        else []
    )
    blocking_reasons = dedupe(entry_reasons + contract_reasons + verification_output_reasons)
    status = build_status(entry_reasons, contract_reasons, verification_output_reasons)
    ready = status == "route_specific_artifact_verification_entry_result_review_ready"
    route_type = route_specific_artifact_verification.get("verified_route_type", "") if ready else ""
    artifact_records = route_specific_artifact_verification.get("artifact_verification_records", []) if ready else []

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_verification_entry.get(
            "topic",
            route_specific_artifact_verification.get("topic", ""),
        ),
        "source_paths": {
            "route_specific_artifact_verification_entry": source_paths.get(
                "route_specific_artifact_verification_entry",
                str(DEFAULT_ENTRY_PATH),
            ),
            "route_specific_artifact_verification": source_paths.get(
                "route_specific_artifact_verification",
                str(DEFAULT_VERIFICATION_PATH),
            ),
        },
        "source_status": route_specific_artifact_verification_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "route_specific_artifact_verification_status": (
            route_specific_artifact_verification.get("status", "") if ready else ""
        ),
        "artifact_verification_entry_result_reviewed": ready,
        "can_continue_to_verified_route_completion_ledger": ready,
        "verified_route_completion_ledger_input_records": (
            build_verified_route_completion_ledger_input_records(route_specific_artifact_verification)
            if ready
            else []
        ),
        "route_specific_artifact_verified": (
            route_specific_artifact_verification.get("route_specific_artifact_verified") is True
            if ready
            else False
        ),
        "source_product_state_verified": (
            route_specific_artifact_verification.get("source_product_state_verified") is True
            if ready
            else False
        ),
        "selected_route_executed": (
            route_specific_artifact_verification.get("selected_route_executed") is True
            if ready
            else False
        ),
        "export_or_acceptance_executed": (
            route_specific_artifact_verification.get("export_or_acceptance_executed") is True
            if ready
            else False
        ),
        "rendered_pdf": route_specific_artifact_verification.get("rendered_pdf") is True if ready else False,
        "rendered_docx": route_specific_artifact_verification.get("rendered_docx") is True if ready else False,
        "package_manifest_generated": (
            route_specific_artifact_verification.get("package_manifest_generated") is True
            if ready
            else False
        ),
        "manual_acceptance_performed": (
            route_specific_artifact_verification.get("manual_acceptance_performed") is True
            if ready
            else False
        ),
        "artifact_verification_record_count": len(artifact_records),
        "artifact_verification_records": artifact_records,
        "delegated_status": route_specific_artifact_verification.get("delegated_status", "") if ready else "",
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_artifact_verification_entry": build_source_entry_summary(
            route_specific_artifact_verification_entry
        ),
        "source_artifact_verification": build_source_verification_summary(
            route_specific_artifact_verification
        ),
        "verified_route_completion_ledger_probe": build_ledger_probe_summary(ledger_probe),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_entry_blocking_reasons(route_specific_artifact_verification_entry: dict[str, Any]) -> list[str]:
    reasons = []
    route_type = route_specific_artifact_verification_entry.get("verified_route_type", "unknown")
    if route_specific_artifact_verification_entry.get("schema_version") != ENTRY_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_verification_entry_missing_or_invalid_schema")
    if route_specific_artifact_verification_entry.get("status") != ENTRY_READY_STATUS:
        reasons.append("route_specific_artifact_verification_entry_not_completed")
    if route_specific_artifact_verification_entry.get("can_enter_route_specific_artifact_verification") is not True:
        reasons.append("verification_entry_did_not_enter_route_specific_artifact_verification")
    if (
        route_specific_artifact_verification_entry.get(
            "route_specific_artifact_verification_entry_command_executed"
        )
        is not True
    ):
        reasons.append("artifact_verification_entry_command_not_executed")
    if (
        route_specific_artifact_verification_entry.get(
            "this_command_ran_route_specific_artifact_verification"
        )
        is not True
    ):
        reasons.append("entry_did_not_run_route_specific_artifact_verification")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verification_returncode") != 0:
        reasons.append("artifact_verification_entry_returncode_not_zero")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verified") is not True:
        reasons.append("artifact_verification_entry_verified_flag_false")
    for field in [
        "verified_route_type",
        "route_specific_artifact_verification_report_path",
        "route_specific_artifact_verification_review_path",
        "route_specific_artifact_verification_status",
    ]:
        if not route_specific_artifact_verification_entry.get(field):
            reasons.append(f"{field}_missing")
    for field in [
        "route_specific_command_executed",
        "route_specific_artifact_executed",
        "selected_route_executed",
        "export_or_acceptance_executed",
    ]:
        if route_specific_artifact_verification_entry.get(field) is not True:
            reasons.append(f"entry_{field}_missing")
    if route_type in VALID_ROUTE_TYPES and not route_flags_match(route_specific_artifact_verification_entry, route_type):
        reasons.append(f"entry_route_flag_mismatch:{route_type}")
    if route_specific_artifact_verification_entry.get("formal_writeback_executed") is True:
        reasons.append("entry_formal_writeback")
    if route_specific_artifact_verification_entry.get("this_command_wrote_formal_state") is True:
        reasons.append("entry_wrote_formal_state")
    if route_specific_artifact_verification_entry.get("can_write_product_state") is True:
        reasons.append("entry_product_state_write_not_allowed")
    if route_specific_artifact_verification_entry.get("blocking_reasons"):
        reasons.append("source_entry_has_blocking_reasons")
    for flag, value in route_specific_artifact_verification_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_entry_result_contract_blocking_reasons(
    route_specific_artifact_verification_entry: dict[str, Any],
    route_specific_artifact_verification: dict[str, Any],
) -> list[str]:
    route_type = route_specific_artifact_verification_entry.get("verified_route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"artifact_verification_route_type_unknown:{route_type}")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verification_report_path") != str(
        DEFAULT_VERIFICATION_PATH
    ):
        reasons.append(f"artifact_verification_report_path_mismatch:{route_type}")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verification_review_path") != str(
        DEFAULT_VERIFICATION_REVIEW_PATH
    ):
        reasons.append(f"artifact_verification_review_path_mismatch:{route_type}")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verification_returncode") != 0:
        reasons.append(f"artifact_verification_returncode_mismatch:{route_type}")
    if route_specific_artifact_verification_entry.get("route_specific_artifact_verification_status") != (
        VERIFICATION_SUCCESS_STATUS
    ):
        reasons.append(f"artifact_verification_status_mismatch:{route_type}")
    if route_specific_artifact_verification.get("verified_route_type") != route_type:
        reasons.append(f"artifact_verification_verified_route_type_mismatch:{route_type}")
    if route_specific_artifact_verification.get("route_type") not in {"", route_type}:
        reasons.append(f"artifact_verification_route_type_mismatch:{route_type}")
    if route_specific_artifact_verification_entry.get("delegated_status") != route_specific_artifact_verification.get(
        "delegated_status",
        "",
    ):
        reasons.append(f"artifact_verification_delegated_status_mismatch:{route_type}")
    for field in [
        "selected_route_executed",
        "export_or_acceptance_executed",
        "rendered_pdf",
        "rendered_docx",
        "package_manifest_generated",
        "manual_acceptance_performed",
    ]:
        if route_specific_artifact_verification_entry.get(field) is not route_specific_artifact_verification.get(field):
            reasons.append(f"artifact_verification_{field}_mismatch:{route_type}")

    result = route_specific_artifact_verification_entry.get("route_specific_artifact_verification_result", {})
    if result.get("report_path") != str(DEFAULT_VERIFICATION_PATH):
        reasons.append(f"artifact_verification_result_report_path_mismatch:{route_type}")
    if result.get("review_path") != str(DEFAULT_VERIFICATION_REVIEW_PATH):
        reasons.append(f"artifact_verification_result_review_path_mismatch:{route_type}")
    if result.get("returncode") != route_specific_artifact_verification_entry.get(
        "route_specific_artifact_verification_returncode"
    ):
        reasons.append(f"artifact_verification_result_returncode_mismatch:{route_type}")
    if result.get("status") != route_specific_artifact_verification_entry.get(
        "route_specific_artifact_verification_status"
    ):
        reasons.append(f"artifact_verification_result_status_mismatch:{route_type}")

    summary = result.get("route_specific_artifact_verification_report_summary", {})
    if summary:
        if summary.get("schema_version") != route_specific_artifact_verification.get("schema_version"):
            reasons.append(f"artifact_verification_summary_schema_mismatch:{route_type}")
        if summary.get("route_type") != route_specific_artifact_verification.get("route_type"):
            reasons.append(f"artifact_verification_summary_route_type_mismatch:{route_type}")
        if summary.get("verified_route_type") != route_specific_artifact_verification.get("verified_route_type"):
            reasons.append(f"artifact_verification_summary_verified_route_type_mismatch:{route_type}")
        if summary.get("delegated_status") != route_specific_artifact_verification.get("delegated_status"):
            reasons.append(f"artifact_verification_summary_delegated_status_mismatch:{route_type}")
    return dedupe(reasons)


def route_flags_match(payload: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(payload.get(flag) is expected_value for flag, expected_value in expected.items())


def build_status(
    entry_reasons: list[str],
    contract_reasons: list[str],
    verification_output_reasons: list[str],
) -> str:
    if entry_reasons:
        return "blocked_by_route_specific_artifact_verification_entry"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_verification_entry_result_contract"
    if verification_output_reasons:
        return "blocked_by_route_specific_artifact_verification_output"
    return "route_specific_artifact_verification_entry_result_review_ready"


def build_verified_route_completion_ledger_input_records(
    route_specific_artifact_verification: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = route_specific_artifact_verification.get("verified_route_type", "")
    artifact_records = route_specific_artifact_verification.get("artifact_verification_records", [])
    return [
        {
            "record_id": f"route_specific_artifact_verification_result::{route_type}",
            "verified_route_type": route_type,
            "route_specific_artifact_verification_status": route_specific_artifact_verification.get("status", ""),
            "route_specific_artifact_verification_report_path": str(DEFAULT_VERIFICATION_PATH),
            "route_specific_artifact_verification_review_path": str(DEFAULT_VERIFICATION_REVIEW_PATH),
            "delegated_status": route_specific_artifact_verification.get("delegated_status", ""),
            "artifact_verification_record_count": len(artifact_records),
            "artifact_ids": [record.get("artifact_id", "") for record in artifact_records],
            "review_status": "route_specific_artifact_verification_accepted_for_verified_route_completion_ledger",
            "can_continue_to_verified_route_completion_ledger": True,
        }
    ]


def build_source_entry_summary(route_specific_artifact_verification_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_verification_entry.get("schema_version", ""),
        "status": route_specific_artifact_verification_entry.get("status", ""),
        "verified_route_type": route_specific_artifact_verification_entry.get("verified_route_type", ""),
        "can_enter_route_specific_artifact_verification": route_specific_artifact_verification_entry.get(
            "can_enter_route_specific_artifact_verification"
        )
        is True,
        "route_specific_artifact_verification_entry_command_executed": route_specific_artifact_verification_entry.get(
            "route_specific_artifact_verification_entry_command_executed"
        )
        is True,
        "this_command_ran_route_specific_artifact_verification": route_specific_artifact_verification_entry.get(
            "this_command_ran_route_specific_artifact_verification"
        )
        is True,
        "route_specific_artifact_verification_status": route_specific_artifact_verification_entry.get(
            "route_specific_artifact_verification_status",
            "",
        ),
        "route_specific_artifact_verified": route_specific_artifact_verification_entry.get(
            "route_specific_artifact_verified"
        )
        is True,
        "verification_artifact_record_count": route_specific_artifact_verification_entry.get(
            "verification_artifact_record_count",
            0,
        ),
        "blocking_reasons": route_specific_artifact_verification_entry.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_verification_entry.get("boundary_flags", {}),
    }


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
        "artifact_verification_record_count": len(
            route_specific_artifact_verification.get("artifact_verification_records", []) or []
        ),
        "blocking_reasons": route_specific_artifact_verification.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_verification.get("boundary_flags", {}),
    }


def build_ledger_probe_summary(ledger_probe: dict[str, Any]) -> dict[str, Any]:
    if not ledger_probe:
        return {}
    return {
        "status": ledger_probe.get("status", ""),
        "route_completion_ledger_recorded": ledger_probe.get("route_completion_ledger_recorded") is True,
        "can_enter_next_auto_mode_gate": ledger_probe.get("can_enter_next_auto_mode_gate") is True,
        "blocking_reasons": ledger_probe.get("blocking_reasons", []),
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
        "entered_next_gate": False,
        "ran_next_gate_command": False,
        "wrote_formal_state": False,
        "executed_selected_route": False,
        "exported_or_accepted_formal_package": False,
        "verified_route_specific_artifact": False,
        "recorded_verified_route_completion_ledger": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "route_specific_artifact_verification_entry_result_review_ready":
        return {
            "id": "enter_verified_route_completion_ledger",
            "label": "Enter verified route completion ledger",
            "description": f"The `{route_type}` verification result is accepted for completion ledger entry.",
        }
    if status == "blocked_by_route_specific_artifact_verification_entry_result_contract":
        return {
            "id": "repair_artifact_verification_entry_result_contract",
            "label": "Repair artifact verification entry result contract",
            "description": "P7-AT and the artifact verification output must describe the same verification result.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_verification_output":
        return {
            "id": "repair_route_specific_artifact_verification_output",
            "label": "Repair route-specific artifact verification output",
            "description": "The verification output must satisfy the verified route completion ledger contract.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_route_specific_artifact_verification_entry_blockers",
        "label": "Resolve P7-AT blockers",
        "description": "P7-AT must complete route-specific artifact verification before result review can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_RESULT_REVIEW_PATH,
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Verification Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- artifact verification entry result 已审阅："
        f"{str(report['artifact_verification_entry_result_reviewed']).lower()}",
        "- 可进入 verified route completion ledger："
        f"{str(report['can_continue_to_verified_route_completion_ledger']).lower()}",
        "- verified route completion ledger input 数："
        f"{len(report['verified_route_completion_ledger_input_records'])}",
        f"- route-specific artifact verification status：`{report['route_specific_artifact_verification_status']}`",
        f"- 已验证 route-specific artifact：{str(report['route_specific_artifact_verified']).lower()}",
        f"- artifact verification record 数：{report['artifact_verification_record_count']}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["verified_route_completion_ledger_input_records"]:
        lines.extend(["", "## Verified Route Completion Ledger Inputs"])
        for record in report["verified_route_completion_ledger_input_records"]:
            lines.append(f"- `{record['record_id']}`: {record['review_status']}")
    if report["artifact_verification_records"]:
        lines.extend(["", "## Artifact Verification Records"])
        for record in report["artifact_verification_records"]:
            lines.append(
                f"- `{record['artifact_id']}`: `{record['path']}` / "
                f"status=`{record['verification_status']}`"
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
