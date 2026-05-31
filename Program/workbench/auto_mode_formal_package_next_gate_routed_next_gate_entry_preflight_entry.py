from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "verified_route_next_gate_router_entry_result_review_ready"
ROUTER_SUCCESS_STATUS = "verified_route_next_gate_route_recorded"
PREFLIGHT_SUCCESS_STATUS = "ready_for_routed_next_gate_entry_review"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
)
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_next_gate_router.json")
DEFAULT_ROUTER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_next_gate_router.md")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json")
DEFAULT_PREFLIGHT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md")
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.md"
)
PREFLIGHT_COMMAND_PATH = "Program/auto_mode_formal_package_routed_next_gate_entry_preflight.py"
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
    project_root: Path,
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
        project_root,
        verified_route_next_gate_router_entry_result_review,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_enter_routed_next_gate_entry_preflight":
        return report, 0

    result = subprocess.run(
        report["routed_next_gate_entry_preflight_entry_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    preflight_report = load_json_or_empty(project_root / report["routed_next_gate_entry_preflight_report_path"])
    preflight_status = preflight_report.get("status", "")
    report["routed_next_gate_entry_preflight_entry_command_executed"] = True
    report["this_command_ran_routed_next_gate_entry_preflight"] = True
    report["routed_next_gate_entry_preflight_returncode"] = result.returncode
    report["routed_next_gate_entry_preflight_status"] = preflight_status
    report["routed_next_gate_entry_preflight_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": preflight_status,
        "report_path": report["routed_next_gate_entry_preflight_report_path"],
        "review_path": report["routed_next_gate_entry_preflight_review_path"],
        "routed_next_gate_entry_preflight_report_summary": build_preflight_report_summary(preflight_report),
    }
    if result.returncode == 0 and preflight_status == PREFLIGHT_SUCCESS_STATUS:
        mark_successful_preflight_entry(report, preflight_report)
        return report, 0

    report["status"] = "blocked_by_routed_next_gate_entry_preflight_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"routed_next_gate_entry_preflight_command_failed:{report['verified_route_type']}",
            f"routed_next_gate_entry_preflight_status:{preflight_status or 'missing'}",
        ]
    )
    report["can_request_routed_next_gate_entry"] = (
        preflight_report.get("can_request_routed_next_gate_entry") is True
    )
    report["next_gate_entry_plan"] = preflight_report.get("next_gate_entry_plan", [])
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
        report["routed_next_gate"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
    project_root: Path,
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        verified_route_next_gate_router_entry_result_review
    )
    contract_reasons = (
        build_preflight_input_record_contract_blocking_reasons(
            verified_route_next_gate_router_entry_result_review
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
    record = extract_preflight_input_record(verified_route_next_gate_router_entry_result_review)
    can_enter = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_enter else ""
    routed_next_gate = record.get("routed_next_gate", "") if can_enter else ""
    command = build_preflight_entry_command(project_root, record) if can_enter else []
    blocking_reasons = dedupe(result_review_reasons + contract_reasons + unavailable_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_next_gate_router_entry_result_review.get("topic", ""),
        "source_paths": {
            "verified_route_next_gate_router_entry_result_review": source_paths.get(
                "verified_route_next_gate_router_entry_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": verified_route_next_gate_router_entry_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_enter_routed_next_gate_entry_preflight": can_enter,
        "routed_next_gate_entry_preflight_entry_command": command,
        "routed_next_gate_entry_preflight_entry_command_executed": False,
        "this_command_ran_routed_next_gate_entry_preflight": False,
        "routed_next_gate_entry_preflight_report_path": str(DEFAULT_PREFLIGHT_PATH) if can_enter else "",
        "routed_next_gate_entry_preflight_review_path": str(DEFAULT_PREFLIGHT_REVIEW_PATH) if can_enter else "",
        "routed_next_gate_entry_preflight_returncode": None,
        "routed_next_gate_entry_preflight_status": "",
        "routed_next_gate_entry_preflight_result": {},
        "can_request_routed_next_gate_entry": False,
        "requires_explicit_next_gate_entry_command": False,
        "next_gate_entry_plan": [],
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
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
            verified_route_next_gate_router_entry_result_review
        ),
        "routed_next_gate_entry_preflight_input_record": record if can_enter else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, routed_next_gate),
    }


def build_result_review_blocking_reasons(
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    route_type = verified_route_next_gate_router_entry_result_review.get("verified_route_type", "unknown")
    if verified_route_next_gate_router_entry_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("verified_route_next_gate_router_entry_result_review_missing_or_invalid_schema")
    if verified_route_next_gate_router_entry_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("verified_route_next_gate_router_entry_result_review_not_ready")
    if (
        verified_route_next_gate_router_entry_result_review.get(
            "verified_route_next_gate_router_entry_result_reviewed"
        )
        is not True
    ):
        reasons.append("verified_route_next_gate_router_entry_result_not_reviewed")
    if (
        verified_route_next_gate_router_entry_result_review.get(
            "can_continue_to_routed_next_gate_entry_preflight"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_routed_next_gate_entry_preflight")
    if verified_route_next_gate_router_entry_result_review.get("verified_route_next_gate_router_status") != ROUTER_SUCCESS_STATUS:
        reasons.append("result_review_router_status_not_recorded")
    if verified_route_next_gate_router_entry_result_review.get("next_gate_route_recorded") is not True:
        reasons.append("result_review_next_gate_route_not_recorded")
    if verified_route_next_gate_router_entry_result_review.get("can_enter_routed_next_gate") is not True:
        reasons.append("result_review_cannot_enter_routed_next_gate")
    if not verified_route_next_gate_router_entry_result_review.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not verified_route_next_gate_router_entry_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if route_type not in VALID_ROUTE_TYPES and route_type != "unknown":
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if verified_route_next_gate_router_entry_result_review.get("route_completion_record_count", 0) <= 0:
        reasons.append("route_completion_record_count_missing")
    if not verified_route_next_gate_router_entry_result_review.get("next_gate_route"):
        reasons.append("next_gate_route_missing")
    if (
        verified_route_next_gate_router_entry_result_review.get("routed_next_gate_entry_preflight_executed")
        is True
    ):
        reasons.append("result_review_already_executed_preflight")
    if (
        verified_route_next_gate_router_entry_result_review.get(
            "this_command_ran_routed_next_gate_entry_preflight"
        )
        is True
    ):
        reasons.append("result_review_ran_preflight")
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
        if verified_route_next_gate_router_entry_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if verified_route_next_gate_router_entry_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in verified_route_next_gate_router_entry_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_preflight_input_record_contract_blocking_reasons(
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
) -> list[str]:
    records = verified_route_next_gate_router_entry_result_review.get(
        "routed_next_gate_entry_preflight_input_records",
        [],
    )
    if not records:
        return ["routed_next_gate_entry_preflight_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["routed_next_gate_entry_preflight_input_record_not_single"]

    record = records[0]
    route_type = verified_route_next_gate_router_entry_result_review.get("verified_route_type", "unknown")
    routed_next_gate = verified_route_next_gate_router_entry_result_review.get("routed_next_gate", "")
    route = verified_route_next_gate_router_entry_result_review.get("next_gate_route", {})
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"routed_next_gate_entry_preflight_route_type_unknown:{route_type}")
    if record.get("record_id") != f"routed_next_gate_entry_preflight_input::{routed_next_gate}::{route_type}":
        reasons.append(f"routed_next_gate_entry_preflight_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"routed_next_gate_entry_preflight_input_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"routed_next_gate_entry_preflight_input_record_gate_mismatch:{route_type}")
    if record.get("verified_route_next_gate_router_status") != ROUTER_SUCCESS_STATUS:
        reasons.append(f"verified_route_next_gate_router_status_mismatch:{route_type}")
    if record.get("verified_route_next_gate_router_report_path") != str(DEFAULT_ROUTER_PATH):
        reasons.append(f"verified_route_next_gate_router_report_path_mismatch:{route_type}")
    if record.get("verified_route_next_gate_router_review_path") != str(DEFAULT_ROUTER_REVIEW_PATH):
        reasons.append(f"verified_route_next_gate_router_review_path_mismatch:{route_type}")
    if record.get("next_gate_route_id") != route.get("route_id", ""):
        reasons.append(f"next_gate_route_id_mismatch:{route_type}")
    if record.get("next_gate_action") != route.get("next_gate_action", ""):
        reasons.append(f"next_gate_action_mismatch:{route_type}")
    if record.get("route_completion_record_count") != (
        verified_route_next_gate_router_entry_result_review.get("route_completion_record_count", 0)
    ):
        reasons.append(f"route_completion_record_count_mismatch:{route_type}")
    if record.get("review_status") != "verified_route_next_gate_router_entry_accepted_for_routed_next_gate_entry_preflight":
        reasons.append(f"routed_next_gate_entry_preflight_input_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_routed_next_gate_entry_preflight") is not True:
        reasons.append(f"routed_next_gate_entry_preflight_input_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    command_path = repo_root / PREFLIGHT_COMMAND_PATH
    if not command_path.exists() or command_path.is_dir():
        return [f"routed_next_gate_entry_preflight_command_file_missing:{PREFLIGHT_COMMAND_PATH}"]
    return []


def build_status(
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_verified_route_next_gate_router_entry_result_review"
    if contract_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_entry_contract"
    if unavailable_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_command_unavailable"
    return "ready_to_enter_routed_next_gate_entry_preflight"


def extract_preflight_input_record(
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    records = verified_route_next_gate_router_entry_result_review.get(
        "routed_next_gate_entry_preflight_input_records",
        [],
    )
    return records[0] if isinstance(records, list) and len(records) == 1 and isinstance(records[0], dict) else {}


def build_preflight_entry_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        PREFLIGHT_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--verified-route-next-gate-router",
        record.get("verified_route_next_gate_router_report_path", str(DEFAULT_ROUTER_PATH)),
        "--output-preflight",
        str(DEFAULT_PREFLIGHT_PATH),
        "--output-review",
        str(DEFAULT_PREFLIGHT_REVIEW_PATH),
    ]


def mark_successful_preflight_entry(report: dict[str, Any], preflight_report: dict[str, Any]) -> None:
    report["status"] = "next_gate_routed_next_gate_entry_preflight_entered"
    report["blocking_reasons"] = []
    report["verified_route_type"] = preflight_report.get("verified_route_type", report["verified_route_type"])
    report["routed_next_gate"] = preflight_report.get("routed_next_gate", report["routed_next_gate"])
    report["can_request_routed_next_gate_entry"] = (
        preflight_report.get("can_request_routed_next_gate_entry") is True
    )
    report["requires_explicit_next_gate_entry_command"] = (
        preflight_report.get("requires_explicit_next_gate_entry_command") is True
    )
    report["next_gate_entry_plan"] = preflight_report.get("next_gate_entry_plan", [])
    report["can_write_product_state"] = False
    report["next_action"] = build_next_action(
        report["status"],
        [],
        report["verified_route_type"],
        report["routed_next_gate"],
    )


def build_preflight_report_summary(preflight_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": preflight_report.get("schema_version", ""),
        "status": preflight_report.get("status", ""),
        "verified_route_type": preflight_report.get("verified_route_type", ""),
        "routed_next_gate": preflight_report.get("routed_next_gate", ""),
        "can_request_routed_next_gate_entry": preflight_report.get(
            "can_request_routed_next_gate_entry"
        )
        is True,
        "next_gate_entry_plan_count": len(preflight_report.get("next_gate_entry_plan", []) or []),
        "blocking_reasons": preflight_report.get("blocking_reasons", []),
    }


def build_source_result_review_summary(
    verified_route_next_gate_router_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": verified_route_next_gate_router_entry_result_review.get("schema_version", ""),
        "status": verified_route_next_gate_router_entry_result_review.get("status", ""),
        "verified_route_type": verified_route_next_gate_router_entry_result_review.get("verified_route_type", ""),
        "routed_next_gate": verified_route_next_gate_router_entry_result_review.get("routed_next_gate", ""),
        "verified_route_next_gate_router_entry_result_reviewed": verified_route_next_gate_router_entry_result_review.get(
            "verified_route_next_gate_router_entry_result_reviewed"
        )
        is True,
        "can_continue_to_routed_next_gate_entry_preflight": verified_route_next_gate_router_entry_result_review.get(
            "can_continue_to_routed_next_gate_entry_preflight"
        )
        is True,
        "preflight_input_record_count": len(
            verified_route_next_gate_router_entry_result_review.get(
                "routed_next_gate_entry_preflight_input_records",
                [],
            )
            or []
        ),
        "blocking_reasons": verified_route_next_gate_router_entry_result_review.get("blocking_reasons", []),
        "boundary_flags": verified_route_next_gate_router_entry_result_review.get("boundary_flags", {}),
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
        "ran_routed_next_gate_entry_preflight": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str, routed_next_gate: str) -> dict[str, Any]:
    if status == "next_gate_routed_next_gate_entry_preflight_entered":
        return {
            "id": "review_routed_next_gate_entry_preflight_result",
            "label": "Review routed next-gate entry preflight result",
            "description": f"The `{route_type}` completion has a routed next-gate preflight for `{routed_next_gate}`.",
        }
    if status == "ready_to_enter_routed_next_gate_entry_preflight":
        return {
            "id": "run_routed_next_gate_entry_preflight",
            "label": "Run routed next-gate entry preflight",
            "description": f"The `{route_type}` completion review can enter routed next-gate preflight.",
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_entry_contract":
        return {
            "id": "repair_routed_next_gate_entry_preflight_input_record",
            "label": "Repair routed next-gate entry preflight input record",
            "description": "P7-AY must provide exactly one accepted preflight input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_command_unavailable":
        return {
            "id": "restore_routed_next_gate_entry_preflight_command",
            "label": "Restore routed next-gate entry preflight command",
            "description": "The existing preflight CLI must be available before P7-AZ can run.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_failure":
        return {
            "id": "repair_routed_next_gate_entry_preflight_failure",
            "label": "Repair routed next-gate entry preflight failure",
            "description": "The preflight command ran, but no routed next-gate entry plan was recorded.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_next_gate_router_entry_result_review_blockers",
        "label": "Resolve P7-AY blockers",
        "description": "P7-AY must accept one routed next-gate router result before preflight entry can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_outputs(
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
        "# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        "- 可进入 routed next gate entry preflight："
        f"{str(report['can_enter_routed_next_gate_entry_preflight']).lower()}",
        "- preflight command 已执行："
        f"{str(report['routed_next_gate_entry_preflight_entry_command_executed']).lower()}",
        "- 本命令运行 routed next gate entry preflight："
        f"{str(report['this_command_ran_routed_next_gate_entry_preflight']).lower()}",
        f"- preflight status：`{report['routed_next_gate_entry_preflight_status']}`",
        f"- 可请求进入 routed next gate：{str(report['can_request_routed_next_gate_entry']).lower()}",
        f"- next gate entry plan 数：{len(report['next_gate_entry_plan'])}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["next_gate_entry_plan"]:
        lines.extend(["", "## Next Gate Entry Plan"])
        for item in report["next_gate_entry_plan"]:
            lines.append(f"- `{item.get('entry_id', '')}` -> `{item.get('next_command', '')}`")
            lines.append(f"- gate：`{item.get('gate_id', '')}`")
            lines.append(f"- action：`{item.get('next_gate_action', '')}`")
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
