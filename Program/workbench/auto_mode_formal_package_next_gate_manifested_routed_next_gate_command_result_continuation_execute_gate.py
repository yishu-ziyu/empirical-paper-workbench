from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.v1"
)
GATE_ENTRY_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.v1"
)
GATE_ENTRY_READY_STATUS = "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry"
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.json"
)
DEFAULT_EXECUTE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate.md"
)
VALID_MODES = {"dry-run", "execute"}

CONTINUATION_EXECUTE_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "continuation_kind": "selected_route_execution_preflight",
        "next_command": "auto_mode_formal_package_selected_route_execution_preflight",
        "command_path": "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
        "source_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        "next_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
        "next_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
        "continuation_status": "pending_explicit_continuation_command",
        "requires_explicit_continuation_command": True,
        "completion_terminal": False,
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "continuation_kind": "delivery_completion_terminal_record",
        "next_command": "none",
        "command_path": "",
        "source_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "next_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "next_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
        "continuation_status": "terminal_delivery_completion_ready_for_product_review",
        "requires_explicit_continuation_command": False,
        "completion_terminal": True,
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
    project_root: Path,
    continuation_gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_continuation_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
        project_root,
        continuation_gate_entry,
        mode=mode,
        confirm_continuation_execute=confirm_continuation_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_manifested_routed_next_gate_result_continuation":
        return (
            report,
            0
            if report["status"]
            == "manifested_routed_next_gate_result_continuation_execute_dry_run_ready"
            else 2,
        )
    if report["completion_terminal"]:
        report["status"] = "manifested_routed_next_gate_terminal_continuation_recorded"
        report["terminal_continuation_recorded"] = True
        report["this_command_recorded_terminal_continuation"] = True
        report["continuation_status"] = "terminal_delivery_completion_ready_for_product_review"
        report["blocking_reasons"] = []
        report["next_action"] = build_next_action(
            report["status"],
            [],
            report["verified_route_type"],
        )
        return report, 0

    result = subprocess.run(
        report["continuation_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    continuation_report = load_json_or_empty(project_root / report["continuation_report_path"])
    continuation_status = continuation_report.get("status", "")
    report["continuation_executed"] = True
    report["this_command_ran_continuation"] = True
    report["continuation_returncode"] = result.returncode
    report["continuation_status"] = continuation_status
    report["continuation_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": continuation_status,
        "report_path": report["continuation_report_path"],
        "review_path": report["continuation_review_path"],
        "continuation_report_summary": build_continuation_report_summary(continuation_report),
    }
    if result.returncode == 0:
        report["status"] = "manifested_routed_next_gate_result_continuation_executed"
        report["blocking_reasons"] = []
        report["selected_route_executed"] = continuation_report.get("selected_route_executed") is True
        report["export_or_acceptance_executed"] = (
            continuation_report.get("export_or_acceptance_executed") is True
        )
        report["next_action"] = build_next_action(
            report["status"],
            [],
            report["verified_route_type"],
        )
        return report, 0

    report["status"] = "blocked_by_manifested_routed_next_gate_result_continuation_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"manifested_routed_next_gate_result_continuation_failed:{report['verified_route_type']}",
            f"continuation_status:{continuation_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
    project_root: Path,
    continuation_gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_continuation_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    gate_reasons = build_gate_entry_blocking_reasons(continuation_gate_entry)
    contract_reasons = (
        build_continuation_record_contract_blocking_reasons(continuation_gate_entry)
        if not gate_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(continuation_gate_entry, repo_root)
        if not gate_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(
        mode,
        confirm_continuation_execute,
        reviewer,
        note,
    )
    status = build_status(mode, gate_reasons, contract_reasons, unavailable_reasons, request_reasons)
    record = extract_continuation_record(continuation_gate_entry)
    can_execute = not gate_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_execute else ""
    routed_next_gate = record.get("routed_next_gate", "") if can_execute else ""
    completion_terminal = record.get("completion_terminal") is True if can_execute else False
    command = (
        build_continuation_command(project_root, record)
        if can_execute and not completion_terminal
        else []
    )
    blocking_reasons = dedupe(gate_reasons + contract_reasons + unavailable_reasons + request_reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": continuation_gate_entry.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_command_result_continuation_gate_entry": (
                source_paths.get(
                    "manifested_routed_next_gate_command_result_continuation_gate_entry",
                    str(DEFAULT_GATE_ENTRY_PATH),
                )
            ),
        },
        "source_status": continuation_gate_entry.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_continuation_execute": confirm_continuation_execute,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_manifested_routed_next_gate_result_continuation_with_confirmation": can_execute,
        "requires_explicit_continuation_command": (
            record.get("requires_explicit_continuation_command") is True if can_execute else False
        ),
        "completion_terminal": completion_terminal,
        "terminal_continuation_recorded": False,
        "this_command_recorded_terminal_continuation": False,
        "continuation_executed": False,
        "this_command_ran_continuation": False,
        "continuation_command": (
            command
            if status
            in {
                "manifested_routed_next_gate_result_continuation_execute_dry_run_ready",
                "ready_to_execute_manifested_routed_next_gate_result_continuation",
            }
            else []
        ),
        "continuation_report_path": record.get("next_report_path", "") if can_execute else "",
        "continuation_review_path": record.get("next_review_path", "") if can_execute else "",
        "continuation_returncode": None,
        "continuation_status": "",
        "continuation_result": {},
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_continuation_gate_entry": build_source_gate_entry_summary(continuation_gate_entry),
        "continuation_execute_request": build_continuation_execute_request(
            mode,
            confirm_continuation_execute,
            reviewer,
            note,
        ),
        "continuation_input_record": record if can_execute else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_gate_entry_blocking_reasons(continuation_gate_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if continuation_gate_entry.get("schema_version") != GATE_ENTRY_SCHEMA_VERSION:
        reasons.append("manifested_routed_next_gate_result_continuation_gate_entry_missing_or_invalid_schema")
    if continuation_gate_entry.get("status") != GATE_ENTRY_READY_STATUS:
        reasons.append("manifested_routed_next_gate_result_continuation_gate_entry_not_ready")
    if continuation_gate_entry.get("command_result_continuation_gate_entry_recorded") is not True:
        reasons.append("manifested_routed_next_gate_result_continuation_gate_entry_not_recorded")
    if continuation_gate_entry.get("can_request_manifested_routed_next_gate_result_continuation") is not True:
        reasons.append("manifested_routed_next_gate_result_continuation_gate_entry_cannot_request")
    if not continuation_gate_entry.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not continuation_gate_entry.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if continuation_gate_entry.get("continuation_executed") is True:
        reasons.append("manifested_routed_next_gate_result_continuation_already_executed")
    if continuation_gate_entry.get("this_command_ran_continuation") is True:
        reasons.append("continuation_gate_entry_ran_continuation")
    if continuation_gate_entry.get("export_or_acceptance_executed") is True:
        reasons.append("continuation_gate_entry_executed_export_or_acceptance")
    if continuation_gate_entry.get("formal_writeback_executed") is True:
        reasons.append("continuation_gate_entry_executed_formal_writeback")
    if continuation_gate_entry.get("this_command_wrote_formal_state") is True:
        reasons.append("continuation_gate_entry_wrote_formal_state")
    if continuation_gate_entry.get("can_write_product_state") is True:
        reasons.append("continuation_gate_entry_allows_product_state_write")
    if continuation_gate_entry.get("blocking_reasons"):
        reasons.append("source_continuation_gate_entry_has_blocking_reasons")
    for flag, value in continuation_gate_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"continuation_gate_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_record_contract_blocking_reasons(
    continuation_gate_entry: dict[str, Any],
) -> list[str]:
    records = continuation_gate_entry.get("continuation_input_records", [])
    if not records:
        return ["continuation_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["continuation_input_record_not_single"]

    record = records[0]
    route_type = record.get("verified_route_type", "unknown")
    routed_next_gate = continuation_gate_entry.get("routed_next_gate", "")
    contract = CONTINUATION_EXECUTE_CONTRACTS.get(routed_next_gate)
    reasons = []
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"continuation_route_type_not_allowed:{route_type}")
        for field in [
            "continuation_kind",
            "next_command",
            "command_path",
            "source_report_path",
            "next_report_path",
            "next_review_path",
            "continuation_status",
            "requires_explicit_continuation_command",
            "completion_terminal",
        ]:
            if record.get(field) != contract[field]:
                reasons.append(f"continuation_{field}_mismatch:{route_type}")

    if route_type != continuation_gate_entry.get("verified_route_type", ""):
        reasons.append(f"continuation_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"continuation_gate_mismatch:{routed_next_gate}")
    if (
        record.get("record_id")
        != f"manifested_routed_next_gate_command_result_continuation::{routed_next_gate}::{route_type}"
    ):
        reasons.append(f"continuation_record_id_mismatch:{route_type}")
    if not record.get("source_delegated_result_record_id"):
        reasons.append(f"continuation_source_record_missing:{route_type}")
    if record.get("will_run_continuation_by_this_command") is True:
        reasons.append(f"continuation_input_marked_run_continuation:{route_type}")
    if record.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"continuation_input_marked_export_or_acceptance:{route_type}")
    if record.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"continuation_input_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(
    continuation_gate_entry: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    record = extract_continuation_record(continuation_gate_entry)
    if record.get("completion_terminal") is True:
        return []
    command_path = record.get("command_path", "")
    if command_path and not (repo_root / command_path).exists():
        return [f"continuation_command_file_missing:{command_path}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_continuation_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["manifested_routed_next_gate_result_continuation_execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_continuation_execute:
        reasons.append("confirm_continuation_execute_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("continuation_execute_note_required")
    return reasons


def build_status(
    mode: str,
    gate_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if gate_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_gate_entry"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_contract"
    if unavailable_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_command_unavailable"
    if "manifested_routed_next_gate_result_continuation_execute_mode_invalid" in request_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_mode"
    if mode == "dry-run":
        return "manifested_routed_next_gate_result_continuation_execute_dry_run_ready"
    if "confirm_continuation_execute_required" in request_reasons:
        return "blocked_by_missing_manifested_routed_next_gate_result_continuation_execute_confirmation"
    if request_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_metadata"
    return "ready_to_execute_manifested_routed_next_gate_result_continuation"


def extract_continuation_record(continuation_gate_entry: dict[str, Any]) -> dict[str, Any]:
    records = continuation_gate_entry.get("continuation_input_records", [])
    if isinstance(records, list) and len(records) == 1:
        return records[0]
    return {}


def build_continuation_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        record.get("command_path", ""),
        "--project-root",
        str(project_root),
        "--export-acceptance-router",
        record.get("source_report_path", ""),
        "--output-preflight",
        record.get("next_report_path", ""),
        "--output-review",
        record.get("next_review_path", ""),
    ]


def build_source_gate_entry_summary(continuation_gate_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": continuation_gate_entry.get("schema_version", ""),
        "status": continuation_gate_entry.get("status", ""),
        "verified_route_type": continuation_gate_entry.get("verified_route_type", ""),
        "routed_next_gate": continuation_gate_entry.get("routed_next_gate", ""),
        "command_result_continuation_gate_entry_recorded": (
            continuation_gate_entry.get("command_result_continuation_gate_entry_recorded") is True
        ),
        "can_request_manifested_routed_next_gate_result_continuation": (
            continuation_gate_entry.get("can_request_manifested_routed_next_gate_result_continuation")
            is True
        ),
        "requires_explicit_continuation_command": (
            continuation_gate_entry.get("requires_explicit_continuation_command") is True
        ),
        "continuation_input_records_count": len(
            continuation_gate_entry.get("continuation_input_records", []) or []
        ),
        "source_blocking_reasons": continuation_gate_entry.get("blocking_reasons", []),
        "boundary_flags": continuation_gate_entry.get("boundary_flags", {}),
    }


def build_continuation_execute_request(
    mode: str,
    confirm_continuation_execute: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_continuation_execute": confirm_continuation_execute,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_continuation_report_summary(continuation_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": continuation_report.get("schema_version", ""),
        "status": continuation_report.get("status", ""),
        "can_request_selected_route_execution": (
            continuation_report.get("can_request_selected_route_execution") is True
        ),
        "selected_route_execution_plan_count": len(
            continuation_report.get("selected_route_execution_plan", []) or []
        ),
        "blocking_reasons": continuation_report.get("blocking_reasons", []),
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
        "executed_manifested_routed_next_gate_result_continuation": False,
        "recorded_terminal_continuation": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "manifested_routed_next_gate_result_continuation_execute_dry_run_ready":
        return {
            "id": "rerun_with_confirm_continuation_execute",
            "label": "Confirm manifested routed continuation execution",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note.",
        }
    if status == "ready_to_execute_manifested_routed_next_gate_result_continuation":
        return {
            "id": "execute_manifested_routed_next_gate_result_continuation",
            "label": "Execute manifested routed result continuation",
            "description": "The continuation request is ready to execute.",
        }
    if status == "manifested_routed_next_gate_result_continuation_executed":
        return {
            "id": "review_manifested_routed_continuation_result",
            "label": "Review manifested routed continuation result",
            "description": f"The `{route_type}` continuation command ran; review its output before continuing.",
        }
    if status == "manifested_routed_next_gate_terminal_continuation_recorded":
        return {
            "id": "review_terminal_delivery_completion",
            "label": "Review terminal delivery completion",
            "description": "Terminal continuation is recorded; product state writeback remains separate.",
        }
    if status == "blocked_by_missing_manifested_routed_next_gate_result_continuation_execute_confirmation":
        return {
            "id": "rerun_with_confirm_continuation_execute",
            "label": "Rerun with explicit continuation confirmation",
            "description": "Execute mode requires --confirm-continuation-execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_metadata":
        return {
            "id": "record_continuation_reviewer_and_note",
            "label": "Record continuation reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_command_unavailable":
        return {
            "id": "restore_continuation_command",
            "label": "Restore continuation command",
            "description": "The planned continuation command file is missing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_contract":
        return {
            "id": "repair_manifested_routed_continuation_record",
            "label": "Repair continuation input record",
            "description": "P7-BF must expose one clean continuation input record before P7-BG can execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_failure":
        return {
            "id": "repair_manifested_routed_continuation_execution",
            "label": "Repair continuation execution",
            "description": "The continuation command ran but returned a failure.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_routed_continuation_gate_entry_blockers",
        "label": "Resolve P7-BF blockers",
        "description": "P7-BF must be ready before P7-BG can execute continuation.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Gate",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        "- 可确认执行 manifested routed continuation："
        f"{str(report['can_execute_manifested_routed_next_gate_result_continuation_with_confirmation']).lower()}",
        "- 需要显式 continuation command："
        f"{str(report['requires_explicit_continuation_command']).lower()}",
        f"- continuation command 数：{len(report['continuation_command'])}",
        f"- 已运行 continuation：{str(report['continuation_executed']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
        f"- terminal continuation 已记录：{str(report['terminal_continuation_recorded']).lower()}",
        f"- 本命令记录 terminal continuation：{str(report['this_command_recorded_terminal_continuation']).lower()}",
        f"- continuation returncode：{report['continuation_returncode']}",
        f"- continuation status：`{report['continuation_status']}`",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["continuation_command"]:
        lines.extend(["", "## Continuation Command"])
        lines.append(f"- `{' '.join(report['continuation_command'])}`")
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
