from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "route_specific_artifact_verification_entry_result_review_ready"
VERIFICATION_SUCCESS_STATUS = "route_specific_artifact_verified_for_review"
LEDGER_SUCCESS_STATUS = "verified_route_completion_ledger_recorded"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_result_review.json"
)
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_verification.json")
DEFAULT_VERIFICATION_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_verification.md")
DEFAULT_LEDGER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_completion_ledger.json")
DEFAULT_LEDGER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_completion_ledger.md")
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.md")
LEDGER_COMMAND_PATH = "Program/auto_mode_formal_package_verified_route_completion_ledger.py"
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


def run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
    project_root: Path,
    route_specific_artifact_verification_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
        project_root,
        route_specific_artifact_verification_entry_result_review,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_enter_verified_route_completion_ledger":
        return report, 0

    result = subprocess.run(
        report["verified_route_completion_ledger_entry_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    ledger_report = load_json_or_empty(project_root / report["verified_route_completion_ledger_report_path"])
    ledger_status = ledger_report.get("status", "")
    report["verified_route_completion_ledger_entry_command_executed"] = True
    report["this_command_ran_verified_route_completion_ledger"] = True
    report["verified_route_completion_ledger_returncode"] = result.returncode
    report["verified_route_completion_ledger_status"] = ledger_status
    report["verified_route_completion_ledger_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": ledger_status,
        "report_path": report["verified_route_completion_ledger_report_path"],
        "review_path": report["verified_route_completion_ledger_review_path"],
        "verified_route_completion_ledger_report_summary": build_ledger_report_summary(ledger_report),
    }
    if result.returncode == 0 and ledger_status == LEDGER_SUCCESS_STATUS:
        mark_successful_ledger_entry(report, ledger_report)
        return report, 0

    report["status"] = "blocked_by_verified_route_completion_ledger_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"verified_route_completion_ledger_command_failed:{report['verified_route_type']}",
            f"verified_route_completion_ledger_status:{ledger_status or 'missing'}",
        ]
    )
    report["route_completion_ledger_recorded"] = ledger_report.get("route_completion_ledger_recorded") is True
    report["can_enter_next_auto_mode_gate"] = ledger_report.get("can_enter_next_auto_mode_gate") is True
    report["route_completion_record_count"] = len(ledger_report.get("route_completion_records", []))
    report["route_completion_records"] = ledger_report.get("route_completion_records", [])
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
    project_root: Path,
    route_specific_artifact_verification_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        route_specific_artifact_verification_entry_result_review
    )
    contract_reasons = (
        build_ledger_input_record_contract_blocking_reasons(
            route_specific_artifact_verification_entry_result_review
        )
        if not result_review_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(repo_root)
        if not result_review_reasons and not contract_reasons
        else []
    )
    status = build_status(result_review_reasons, contract_reasons, unavailable_reasons)
    record = extract_ledger_input_record(route_specific_artifact_verification_entry_result_review)
    can_enter = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_enter else ""
    command = build_completion_ledger_entry_command(project_root=project_root, record=record) if can_enter else []
    blocking_reasons = dedupe(result_review_reasons + contract_reasons + unavailable_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_verification_entry_result_review.get("topic", ""),
        "source_paths": {
            "route_specific_artifact_verification_entry_result_review": source_paths.get(
                "route_specific_artifact_verification_entry_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": route_specific_artifact_verification_entry_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "can_enter_verified_route_completion_ledger": can_enter,
        "verified_route_completion_ledger_entry_command": command,
        "verified_route_completion_ledger_entry_command_executed": False,
        "this_command_ran_verified_route_completion_ledger": False,
        "verified_route_completion_ledger_report_path": str(DEFAULT_LEDGER_PATH) if can_enter else "",
        "verified_route_completion_ledger_review_path": str(DEFAULT_LEDGER_REVIEW_PATH) if can_enter else "",
        "verified_route_completion_ledger_returncode": None,
        "verified_route_completion_ledger_status": "",
        "verified_route_completion_ledger_result": {},
        "route_completion_ledger_recorded": False,
        "can_enter_next_auto_mode_gate": False,
        "route_completion_record_count": 0,
        "route_completion_records": [],
        "route_specific_artifact_verified": (
            route_specific_artifact_verification_entry_result_review.get("route_specific_artifact_verified")
            is True
            if can_enter
            else False
        ),
        "artifact_verification_record_count": (
            route_specific_artifact_verification_entry_result_review.get("artifact_verification_record_count", 0)
            if can_enter
            else 0
        ),
        "delegated_status": (
            route_specific_artifact_verification_entry_result_review.get("delegated_status", "")
            if can_enter
            else ""
        ),
        "selected_route_executed": (
            route_specific_artifact_verification_entry_result_review.get("selected_route_executed") is True
            if can_enter
            else False
        ),
        "export_or_acceptance_executed": (
            route_specific_artifact_verification_entry_result_review.get("export_or_acceptance_executed") is True
            if can_enter
            else False
        ),
        "rendered_pdf": (
            route_specific_artifact_verification_entry_result_review.get("rendered_pdf") is True
            if can_enter
            else False
        ),
        "rendered_docx": (
            route_specific_artifact_verification_entry_result_review.get("rendered_docx") is True
            if can_enter
            else False
        ),
        "package_manifest_generated": (
            route_specific_artifact_verification_entry_result_review.get("package_manifest_generated") is True
            if can_enter
            else False
        ),
        "manual_acceptance_performed": (
            route_specific_artifact_verification_entry_result_review.get("manual_acceptance_performed") is True
            if can_enter
            else False
        ),
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_result_review": build_source_result_review_summary(
            route_specific_artifact_verification_entry_result_review
        ),
        "verified_route_completion_ledger_input_record": record if can_enter else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_result_review_blocking_reasons(
    route_specific_artifact_verification_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    route_type = route_specific_artifact_verification_entry_result_review.get("verified_route_type", "unknown")
    if route_specific_artifact_verification_entry_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_verification_entry_result_review_missing_or_invalid_schema")
    if route_specific_artifact_verification_entry_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("route_specific_artifact_verification_entry_result_review_not_ready")
    if (
        route_specific_artifact_verification_entry_result_review.get(
            "artifact_verification_entry_result_reviewed"
        )
        is not True
    ):
        reasons.append("artifact_verification_entry_result_not_reviewed")
    if (
        route_specific_artifact_verification_entry_result_review.get(
            "can_continue_to_verified_route_completion_ledger"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_verified_route_completion_ledger")
    if (
        route_specific_artifact_verification_entry_result_review.get(
            "route_specific_artifact_verification_status"
        )
        != VERIFICATION_SUCCESS_STATUS
    ):
        reasons.append("result_review_artifact_verification_status_not_verified")
    if route_specific_artifact_verification_entry_result_review.get("route_specific_artifact_verified") is not True:
        reasons.append("result_review_route_specific_artifact_verified_missing")
    if not route_specific_artifact_verification_entry_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if route_specific_artifact_verification_entry_result_review.get("artifact_verification_record_count", 0) <= 0:
        reasons.append("artifact_verification_record_count_missing")
    for field in ["selected_route_executed", "export_or_acceptance_executed"]:
        if route_specific_artifact_verification_entry_result_review.get(field) is not True:
            reasons.append(f"result_review_{field}_missing")
    if route_type in VALID_ROUTE_TYPES and not route_flags_match(
        route_specific_artifact_verification_entry_result_review,
        route_type,
    ):
        reasons.append(f"result_review_route_flag_mismatch:{route_type}")
    for field in ["formal_writeback_executed", "this_command_wrote_formal_state", "can_write_product_state"]:
        if route_specific_artifact_verification_entry_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if route_specific_artifact_verification_entry_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in route_specific_artifact_verification_entry_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_ledger_input_record_contract_blocking_reasons(
    route_specific_artifact_verification_entry_result_review: dict[str, Any],
) -> list[str]:
    records = route_specific_artifact_verification_entry_result_review.get(
        "verified_route_completion_ledger_input_records",
        [],
    )
    if not records:
        return ["verified_route_completion_ledger_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["verified_route_completion_ledger_input_record_not_single"]

    record = records[0]
    route_type = route_specific_artifact_verification_entry_result_review.get("verified_route_type", "unknown")
    expected_artifact_ids = [
        artifact.get("artifact_id", "")
        for artifact in route_specific_artifact_verification_entry_result_review.get(
            "artifact_verification_records",
            [],
        )
    ]
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"verified_route_completion_ledger_route_type_unknown:{route_type}")
    if record.get("record_id") != f"route_specific_artifact_verification_result::{route_type}":
        reasons.append(f"verified_route_completion_ledger_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"verified_route_completion_ledger_input_record_route_type_mismatch:{route_type}")
    if record.get("route_specific_artifact_verification_status") != VERIFICATION_SUCCESS_STATUS:
        reasons.append(f"route_specific_artifact_verification_status_mismatch:{route_type}")
    if record.get("route_specific_artifact_verification_report_path") != str(DEFAULT_VERIFICATION_PATH):
        reasons.append(f"route_specific_artifact_verification_report_path_mismatch:{route_type}")
    if record.get("route_specific_artifact_verification_review_path") != str(DEFAULT_VERIFICATION_REVIEW_PATH):
        reasons.append(f"route_specific_artifact_verification_review_path_mismatch:{route_type}")
    if record.get("delegated_status") != route_specific_artifact_verification_entry_result_review.get(
        "delegated_status",
        "",
    ):
        reasons.append(f"delegated_status_mismatch:{route_type}")
    if record.get("artifact_verification_record_count") != len(expected_artifact_ids):
        reasons.append(f"artifact_verification_record_count_mismatch:{route_type}")
    if record.get("artifact_ids") != expected_artifact_ids:
        reasons.append(f"artifact_ids_mismatch:{route_type}")
    if record.get("review_status") != "route_specific_artifact_verification_accepted_for_verified_route_completion_ledger":
        reasons.append(f"verified_route_completion_ledger_input_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_verified_route_completion_ledger") is not True:
        reasons.append(f"verified_route_completion_ledger_input_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    command_path = repo_root / LEDGER_COMMAND_PATH
    if not command_path.exists() or command_path.is_dir():
        return [f"verified_route_completion_ledger_command_file_missing:{LEDGER_COMMAND_PATH}"]
    return []


def build_status(
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_route_specific_artifact_verification_entry_result_review"
    if contract_reasons:
        return "blocked_by_verified_route_completion_ledger_entry_contract"
    if unavailable_reasons:
        return "blocked_by_verified_route_completion_ledger_command_unavailable"
    return "ready_to_enter_verified_route_completion_ledger"


def extract_ledger_input_record(route_specific_artifact_verification_entry_result_review: dict[str, Any]) -> dict[str, Any]:
    records = route_specific_artifact_verification_entry_result_review.get(
        "verified_route_completion_ledger_input_records",
        [],
    )
    return records[0] if isinstance(records, list) and len(records) == 1 and isinstance(records[0], dict) else {}


def build_completion_ledger_entry_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        LEDGER_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--route-specific-artifact-verification",
        record.get("route_specific_artifact_verification_report_path", str(DEFAULT_VERIFICATION_PATH)),
        "--output-ledger",
        str(DEFAULT_LEDGER_PATH),
        "--output-review",
        str(DEFAULT_LEDGER_REVIEW_PATH),
    ]


def mark_successful_ledger_entry(report: dict[str, Any], ledger_report: dict[str, Any]) -> None:
    report["status"] = "next_gate_verified_route_completion_ledger_entered"
    report["blocking_reasons"] = []
    report["verified_route_type"] = ledger_report.get("verified_route_type", report["verified_route_type"])
    report["route_completion_ledger_recorded"] = True
    report["can_enter_next_auto_mode_gate"] = ledger_report.get("can_enter_next_auto_mode_gate") is True
    report["route_completion_record_count"] = len(ledger_report.get("route_completion_records", []))
    report["route_completion_records"] = ledger_report.get("route_completion_records", [])
    report["can_write_product_state"] = False
    report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])


def build_ledger_report_summary(ledger_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": ledger_report.get("schema_version", ""),
        "status": ledger_report.get("status", ""),
        "verified_route_type": ledger_report.get("verified_route_type", ""),
        "route_completion_ledger_recorded": ledger_report.get("route_completion_ledger_recorded") is True,
        "can_enter_next_auto_mode_gate": ledger_report.get("can_enter_next_auto_mode_gate") is True,
        "route_completion_record_count": len(ledger_report.get("route_completion_records", [])),
        "blocking_reasons": ledger_report.get("blocking_reasons", []),
    }


def build_source_result_review_summary(
    route_specific_artifact_verification_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_verification_entry_result_review.get("schema_version", ""),
        "status": route_specific_artifact_verification_entry_result_review.get("status", ""),
        "verified_route_type": route_specific_artifact_verification_entry_result_review.get("verified_route_type", ""),
        "artifact_verification_entry_result_reviewed": route_specific_artifact_verification_entry_result_review.get(
            "artifact_verification_entry_result_reviewed"
        )
        is True,
        "can_continue_to_verified_route_completion_ledger": route_specific_artifact_verification_entry_result_review.get(
            "can_continue_to_verified_route_completion_ledger"
        )
        is True,
        "ledger_input_record_count": len(
            route_specific_artifact_verification_entry_result_review.get(
                "verified_route_completion_ledger_input_records",
                [],
            )
            or []
        ),
        "blocking_reasons": route_specific_artifact_verification_entry_result_review.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_verification_entry_result_review.get("boundary_flags", {}),
    }


def route_flags_match(payload: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(payload.get(flag) is expected_value for flag, expected_value in expected.items())


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
    if status == "next_gate_verified_route_completion_ledger_entered":
        return {
            "id": "route_verified_completion_to_next_auto_mode_gate",
            "label": "Route verified completion to next Auto Mode gate",
            "description": f"The `{route_type}` route completion ledger is recorded and can be routed onward.",
        }
    if status == "ready_to_enter_verified_route_completion_ledger":
        return {
            "id": "run_verified_route_completion_ledger",
            "label": "Run verified route completion ledger",
            "description": f"The `{route_type}` verification result can be recorded by the existing ledger.",
        }
    if status == "blocked_by_verified_route_completion_ledger_entry_contract":
        return {
            "id": "repair_verified_route_completion_ledger_input_record",
            "label": "Repair verified route completion ledger input record",
            "description": "P7-AU must provide exactly one accepted ledger input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_completion_ledger_command_unavailable":
        return {
            "id": "restore_verified_route_completion_ledger_command",
            "label": "Restore verified route completion ledger command",
            "description": "The existing completion ledger CLI must be available before P7-AV can run.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_completion_ledger_failure":
        return {
            "id": "repair_verified_route_completion_ledger_failure",
            "label": "Repair verified route completion ledger failure",
            "description": "The ledger command ran, but the route completion was not recorded.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verification_entry_result_review_blockers",
        "label": "Resolve P7-AU blockers",
        "description": "P7-AU must accept one verification result before ledger entry can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_ENTRY_PATH,
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
        "# Auto Mode Formal Package Next Gate Verified Route Completion Ledger Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- 可进入 verified route completion ledger："
        f"{str(report['can_enter_verified_route_completion_ledger']).lower()}",
        "- ledger command 已执行："
        f"{str(report['verified_route_completion_ledger_entry_command_executed']).lower()}",
        "- 本命令运行 verified route completion ledger："
        f"{str(report['this_command_ran_verified_route_completion_ledger']).lower()}",
        f"- ledger status：`{report['verified_route_completion_ledger_status']}`",
        f"- route completion ledger recorded：{str(report['route_completion_ledger_recorded']).lower()}",
        f"- 可进入下一 Auto Mode gate：{str(report['can_enter_next_auto_mode_gate']).lower()}",
        f"- route completion record 数：{report['route_completion_record_count']}",
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
    if report["route_completion_records"]:
        lines.extend(["", "## Route Completion Records"])
        for record in report["route_completion_records"]:
            lines.append(
                f"- `{record['completion_id']}`: route=`{record['route_type']}`, "
                f"artifacts={record['artifact_count']}, "
                f"next_gate={str(record['can_enter_next_auto_mode_gate']).lower()}"
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
