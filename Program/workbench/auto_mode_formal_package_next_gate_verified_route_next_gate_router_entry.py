from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "verified_route_completion_ledger_entry_result_review_ready"
LEDGER_SUCCESS_STATUS = "verified_route_completion_ledger_recorded"
ROUTER_SUCCESS_STATUS = "verified_route_next_gate_route_recorded"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.json"
)
DEFAULT_LEDGER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_completion_ledger.json")
DEFAULT_LEDGER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_completion_ledger.md")
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_next_gate_router.json")
DEFAULT_ROUTER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_next_gate_router.md")
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.md"
)
ROUTER_COMMAND_PATH = "Program/auto_mode_formal_package_verified_route_next_gate_router.py"
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry(
    project_root: Path,
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry(
        project_root,
        verified_route_completion_ledger_entry_result_review,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_enter_verified_route_next_gate_router":
        return report, 0

    result = subprocess.run(
        report["verified_route_next_gate_router_entry_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    router_report = load_json_or_empty(project_root / report["verified_route_next_gate_router_report_path"])
    router_status = router_report.get("status", "")
    report["verified_route_next_gate_router_entry_command_executed"] = True
    report["this_command_ran_verified_route_next_gate_router"] = True
    report["verified_route_next_gate_router_returncode"] = result.returncode
    report["verified_route_next_gate_router_status"] = router_status
    report["verified_route_next_gate_router_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": router_status,
        "report_path": report["verified_route_next_gate_router_report_path"],
        "review_path": report["verified_route_next_gate_router_review_path"],
        "verified_route_next_gate_router_report_summary": build_router_report_summary(router_report),
    }
    if result.returncode == 0 and router_status == ROUTER_SUCCESS_STATUS:
        mark_successful_router_entry(report, router_report)
        return report, 0

    report["status"] = "blocked_by_verified_route_next_gate_router_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"verified_route_next_gate_router_command_failed:{report['verified_route_type']}",
            f"verified_route_next_gate_router_status:{router_status or 'missing'}",
        ]
    )
    report["next_gate_route_recorded"] = router_report.get("next_gate_route_recorded") is True
    report["can_enter_routed_next_gate"] = router_report.get("can_enter_routed_next_gate") is True
    report["routed_next_gate"] = router_report.get("routed_next_gate", "")
    report["next_gate_route"] = router_report.get("next_gate_route", {})
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
        report["routed_next_gate"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry(
    project_root: Path,
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        verified_route_completion_ledger_entry_result_review
    )
    contract_reasons = (
        build_router_input_record_contract_blocking_reasons(
            verified_route_completion_ledger_entry_result_review
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
    record = extract_router_input_record(verified_route_completion_ledger_entry_result_review)
    can_enter = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_enter else ""
    command = build_router_entry_command(project_root, record) if can_enter else []
    blocking_reasons = dedupe(result_review_reasons + contract_reasons + unavailable_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_completion_ledger_entry_result_review.get("topic", ""),
        "source_paths": {
            "verified_route_completion_ledger_entry_result_review": source_paths.get(
                "verified_route_completion_ledger_entry_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": verified_route_completion_ledger_entry_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "can_enter_verified_route_next_gate_router": can_enter,
        "verified_route_next_gate_router_entry_command": command,
        "verified_route_next_gate_router_entry_command_executed": False,
        "this_command_ran_verified_route_next_gate_router": False,
        "verified_route_next_gate_router_report_path": str(DEFAULT_ROUTER_PATH) if can_enter else "",
        "verified_route_next_gate_router_review_path": str(DEFAULT_ROUTER_REVIEW_PATH) if can_enter else "",
        "verified_route_next_gate_router_returncode": None,
        "verified_route_next_gate_router_status": "",
        "verified_route_next_gate_router_result": {},
        "next_gate_route_recorded": False,
        "can_enter_routed_next_gate": False,
        "routed_next_gate": "",
        "next_gate_route": {},
        "route_completion_ledger_recorded": (
            verified_route_completion_ledger_entry_result_review.get("route_completion_ledger_recorded") is True
            if can_enter
            else False
        ),
        "can_enter_next_auto_mode_gate": (
            verified_route_completion_ledger_entry_result_review.get("can_enter_next_auto_mode_gate") is True
            if can_enter
            else False
        ),
        "route_completion_record_count": (
            verified_route_completion_ledger_entry_result_review.get("route_completion_record_count", 0)
            if can_enter
            else 0
        ),
        "route_completion_records": (
            verified_route_completion_ledger_entry_result_review.get("route_completion_records", [])
            if can_enter
            else []
        ),
        "entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_result_review": build_source_result_review_summary(
            verified_route_completion_ledger_entry_result_review
        ),
        "verified_route_next_gate_router_input_record": record if can_enter else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, ""),
    }


def build_result_review_blocking_reasons(
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    route_type = verified_route_completion_ledger_entry_result_review.get("verified_route_type", "unknown")
    if verified_route_completion_ledger_entry_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("verified_route_completion_ledger_entry_result_review_missing_or_invalid_schema")
    if verified_route_completion_ledger_entry_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("verified_route_completion_ledger_entry_result_review_not_ready")
    if (
        verified_route_completion_ledger_entry_result_review.get(
            "verified_route_completion_ledger_entry_result_reviewed"
        )
        is not True
    ):
        reasons.append("verified_route_completion_ledger_entry_result_not_reviewed")
    if (
        verified_route_completion_ledger_entry_result_review.get(
            "can_continue_to_verified_route_next_gate_router"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_verified_route_next_gate_router")
    if (
        verified_route_completion_ledger_entry_result_review.get(
            "verified_route_completion_ledger_status"
        )
        != LEDGER_SUCCESS_STATUS
    ):
        reasons.append("result_review_ledger_status_not_recorded")
    if verified_route_completion_ledger_entry_result_review.get("route_completion_ledger_recorded") is not True:
        reasons.append("result_review_route_completion_ledger_not_recorded")
    if verified_route_completion_ledger_entry_result_review.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append("result_review_cannot_enter_next_auto_mode_gate")
    if not verified_route_completion_ledger_entry_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if verified_route_completion_ledger_entry_result_review.get("route_completion_record_count", 0) <= 0:
        reasons.append("route_completion_record_count_missing")
    if route_type not in VALID_ROUTE_TYPES and route_type != "unknown":
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if verified_route_completion_ledger_entry_result_review.get("verified_route_next_gate_router_executed") is True:
        reasons.append("result_review_already_executed_router")
    if verified_route_completion_ledger_entry_result_review.get("this_command_ran_verified_route_next_gate_router") is True:
        reasons.append("result_review_ran_router")
    for field in [
        "entered_next_gate",
        "export_or_acceptance_executed",
        "rendered_pdf",
        "rendered_docx",
        "package_manifest_generated",
        "manual_acceptance_performed",
        "formal_writeback_executed",
        "this_command_wrote_formal_state",
        "can_write_product_state",
    ]:
        if verified_route_completion_ledger_entry_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if verified_route_completion_ledger_entry_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in verified_route_completion_ledger_entry_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_router_input_record_contract_blocking_reasons(
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
) -> list[str]:
    records = verified_route_completion_ledger_entry_result_review.get(
        "verified_route_next_gate_router_input_records",
        [],
    )
    if not records:
        return ["verified_route_next_gate_router_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["verified_route_next_gate_router_input_record_not_single"]

    record = records[0]
    route_type = verified_route_completion_ledger_entry_result_review.get("verified_route_type", "unknown")
    completion_ids = [
        completion.get("completion_id", "")
        for completion in verified_route_completion_ledger_entry_result_review.get("route_completion_records", [])
    ]
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"verified_route_next_gate_router_route_type_unknown:{route_type}")
    if record.get("record_id") != f"verified_route_next_gate_router_input::{route_type}":
        reasons.append(f"verified_route_next_gate_router_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"verified_route_next_gate_router_input_record_route_type_mismatch:{route_type}")
    if record.get("verified_route_completion_ledger_status") != LEDGER_SUCCESS_STATUS:
        reasons.append(f"verified_route_completion_ledger_status_mismatch:{route_type}")
    if record.get("verified_route_completion_ledger_report_path") != str(DEFAULT_LEDGER_PATH):
        reasons.append(f"verified_route_completion_ledger_report_path_mismatch:{route_type}")
    if record.get("verified_route_completion_ledger_review_path") != str(DEFAULT_LEDGER_REVIEW_PATH):
        reasons.append(f"verified_route_completion_ledger_review_path_mismatch:{route_type}")
    if record.get("route_completion_record_count") != len(completion_ids):
        reasons.append(f"route_completion_record_count_mismatch:{route_type}")
    if record.get("route_completion_ids") != completion_ids:
        reasons.append(f"route_completion_ids_mismatch:{route_type}")
    if record.get("review_status") != "verified_route_completion_ledger_entry_accepted_for_next_gate_router":
        reasons.append(f"verified_route_next_gate_router_input_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_verified_route_next_gate_router") is not True:
        reasons.append(f"verified_route_next_gate_router_input_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    command_path = repo_root / ROUTER_COMMAND_PATH
    if not command_path.exists() or command_path.is_dir():
        return [f"verified_route_next_gate_router_command_file_missing:{ROUTER_COMMAND_PATH}"]
    return []


def build_status(
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_verified_route_completion_ledger_entry_result_review"
    if contract_reasons:
        return "blocked_by_verified_route_next_gate_router_entry_contract"
    if unavailable_reasons:
        return "blocked_by_verified_route_next_gate_router_command_unavailable"
    return "ready_to_enter_verified_route_next_gate_router"


def extract_router_input_record(
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    records = verified_route_completion_ledger_entry_result_review.get(
        "verified_route_next_gate_router_input_records",
        [],
    )
    return records[0] if isinstance(records, list) and len(records) == 1 and isinstance(records[0], dict) else {}


def build_router_entry_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        ROUTER_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--verified-route-completion-ledger",
        record.get("verified_route_completion_ledger_report_path", str(DEFAULT_LEDGER_PATH)),
        "--output-router",
        str(DEFAULT_ROUTER_PATH),
        "--output-review",
        str(DEFAULT_ROUTER_REVIEW_PATH),
    ]


def mark_successful_router_entry(report: dict[str, Any], router_report: dict[str, Any]) -> None:
    report["status"] = "next_gate_verified_route_next_gate_router_entered"
    report["blocking_reasons"] = []
    report["verified_route_type"] = router_report.get("verified_route_type", report["verified_route_type"])
    report["next_gate_route_recorded"] = router_report.get("next_gate_route_recorded") is True
    report["can_enter_routed_next_gate"] = router_report.get("can_enter_routed_next_gate") is True
    report["routed_next_gate"] = router_report.get("routed_next_gate", "")
    report["next_gate_route"] = router_report.get("next_gate_route", {})
    report["route_completion_records"] = router_report.get("route_completion_records", [])
    report["route_completion_record_count"] = len(router_report.get("route_completion_records", []))
    report["can_write_product_state"] = False
    report["next_action"] = build_next_action(
        report["status"],
        [],
        report["verified_route_type"],
        report["routed_next_gate"],
    )


def build_router_report_summary(router_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": router_report.get("schema_version", ""),
        "status": router_report.get("status", ""),
        "verified_route_type": router_report.get("verified_route_type", ""),
        "next_gate_route_recorded": router_report.get("next_gate_route_recorded") is True,
        "can_enter_routed_next_gate": router_report.get("can_enter_routed_next_gate") is True,
        "routed_next_gate": router_report.get("routed_next_gate", ""),
        "blocking_reasons": router_report.get("blocking_reasons", []),
    }


def build_source_result_review_summary(
    verified_route_completion_ledger_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": verified_route_completion_ledger_entry_result_review.get("schema_version", ""),
        "status": verified_route_completion_ledger_entry_result_review.get("status", ""),
        "verified_route_type": verified_route_completion_ledger_entry_result_review.get("verified_route_type", ""),
        "verified_route_completion_ledger_entry_result_reviewed": verified_route_completion_ledger_entry_result_review.get(
            "verified_route_completion_ledger_entry_result_reviewed"
        )
        is True,
        "can_continue_to_verified_route_next_gate_router": verified_route_completion_ledger_entry_result_review.get(
            "can_continue_to_verified_route_next_gate_router"
        )
        is True,
        "router_input_record_count": len(
            verified_route_completion_ledger_entry_result_review.get(
                "verified_route_next_gate_router_input_records",
                [],
            )
            or []
        ),
        "blocking_reasons": verified_route_completion_ledger_entry_result_review.get("blocking_reasons", []),
        "boundary_flags": verified_route_completion_ledger_entry_result_review.get("boundary_flags", {}),
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
        "recorded_verified_route_next_gate_router": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str, routed_next_gate: str) -> dict[str, Any]:
    if status == "next_gate_verified_route_next_gate_router_entered":
        return {
            "id": "run_routed_next_auto_mode_gate",
            "label": "Run routed next Auto Mode gate",
            "description": f"The `{route_type}` completion has been routed to `{routed_next_gate}`.",
        }
    if status == "ready_to_enter_verified_route_next_gate_router":
        return {
            "id": "run_verified_route_next_gate_router",
            "label": "Run verified route next-gate router",
            "description": f"The `{route_type}` completion review can be routed by the existing router.",
        }
    if status == "blocked_by_verified_route_next_gate_router_entry_contract":
        return {
            "id": "repair_verified_route_next_gate_router_input_record",
            "label": "Repair verified route next-gate router input record",
            "description": "P7-AW must provide exactly one accepted router input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_next_gate_router_command_unavailable":
        return {
            "id": "restore_verified_route_next_gate_router_command",
            "label": "Restore verified route next-gate router command",
            "description": "The existing router CLI must be available before P7-AX can run.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_next_gate_router_failure":
        return {
            "id": "repair_verified_route_next_gate_router_failure",
            "label": "Repair verified route next-gate router failure",
            "description": "The router command ran, but no next-gate route was recorded.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_completion_ledger_entry_result_review_blockers",
        "label": "Resolve P7-AW blockers",
        "description": "P7-AW must accept one completion ledger result before router entry can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_outputs(
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
        "# Auto Mode Formal Package Next Gate Verified Route Next-Gate Router Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- 可进入 verified route next-gate router："
        f"{str(report['can_enter_verified_route_next_gate_router']).lower()}",
        "- router command 已执行："
        f"{str(report['verified_route_next_gate_router_entry_command_executed']).lower()}",
        "- 本命令运行 verified route next-gate router："
        f"{str(report['this_command_ran_verified_route_next_gate_router']).lower()}",
        f"- router status：`{report['verified_route_next_gate_router_status']}`",
        f"- next gate route recorded：{str(report['next_gate_route_recorded']).lower()}",
        f"- 可进入 routed next gate：{str(report['can_enter_routed_next_gate']).lower()}",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- route completion record 数：{report['route_completion_record_count']}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["next_gate_route"]:
        route = report["next_gate_route"]
        lines.extend(["", "## Next Gate Route"])
        lines.append(
            f"- `{route.get('route_id', '')}`: gate=`{route.get('gate_id', '')}`, "
            f"action=`{route.get('next_gate_action', '')}`"
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
