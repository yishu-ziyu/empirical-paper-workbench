from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_routed_next_gate_command_execute.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_routed_next_gate_command_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
)
DEFAULT_EXECUTE_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_execute.md")
VALID_MODES = {"dry-run", "execute"}

NEXT_GATE_COMMAND_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "allowed_actions": {"continue_formal_package_export_acceptance_cycle"},
        "next_command": "auto_mode_formal_package_export_acceptance_router",
        "command_path": "Program/auto_mode_formal_package_export_acceptance_router.py",
        "command_kind": "continue_export_acceptance_cycle",
        "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "allowed_actions": {"finalize_formal_package_delivery_review"},
        "next_command": "auto_mode_formal_package_delivery_completion_gate",
        "command_path": "Program/auto_mode_formal_package_delivery_completion_gate.py",
        "command_kind": "delivery_completion",
        "delegated_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
    project_root: Path,
    manifested_routed_next_gate_command_preflight: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_command_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
        project_root,
        manifested_routed_next_gate_command_preflight,
        mode=mode,
        confirm_command_execute=confirm_command_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_manifested_next_gate_command":
        return report, 0 if report["status"] == "manifested_next_gate_command_execute_dry_run_ready" else 2

    result = subprocess.run(
        report["delegated_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    delegated_report = load_json_or_empty(project_root / report["delegated_report_path"])
    delegated_status = delegated_report.get("status", "")
    report["next_gate_command_executed"] = True
    report["this_command_ran_next_gate_command"] = True
    report["next_gate_entered"] = True
    report["this_command_entered_next_gate"] = True
    report["delegated_returncode"] = result.returncode
    report["delegated_status"] = delegated_status
    report["delegated_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": delegated_status,
        "report_path": report["delegated_report_path"],
        "review_path": report["delegated_review_path"],
    }
    if result.returncode == 0:
        report["status"] = "manifested_next_gate_command_executed"
        report["blocking_reasons"] = []
        report["delegated_result"]["delegated_report_summary"] = build_delegated_report_summary(delegated_report)
        report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])
        return report, 0

    report["status"] = "blocked_by_manifested_next_gate_command_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"manifested_next_gate_command_failed:{report['verified_route_type']}",
            f"delegated_status:{delegated_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
    project_root: Path,
    manifested_routed_next_gate_command_preflight: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_command_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(manifested_routed_next_gate_command_preflight)
    contract_reasons = (
        build_command_plan_contract_blocking_reasons(manifested_routed_next_gate_command_preflight)
        if not preflight_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(manifested_routed_next_gate_command_preflight, repo_root)
        if not preflight_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(mode, confirm_command_execute, reviewer, note)
    status = build_status(mode, preflight_reasons, contract_reasons, unavailable_reasons, request_reasons)
    command_plan = extract_command_plan(manifested_routed_next_gate_command_preflight) if not contract_reasons else {}
    route_type = command_plan.get("verified_route_type", "") if not preflight_reasons and not contract_reasons else ""
    routed_next_gate = command_plan.get("gate_id", "") if not preflight_reasons and not contract_reasons else ""
    delegated_paths = build_delegated_paths(routed_next_gate)
    can_execute = not preflight_reasons and not contract_reasons and not unavailable_reasons
    delegated_command = (
        build_delegated_command(project_root, command_plan)
        if status in {"manifested_next_gate_command_execute_dry_run_ready", "ready_to_execute_manifested_next_gate_command"}
        else []
    )
    blocking_reasons = dedupe(preflight_reasons + contract_reasons + unavailable_reasons + request_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_routed_next_gate_command_preflight.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_command_preflight": source_paths.get(
                "manifested_routed_next_gate_command_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "source_status": manifested_routed_next_gate_command_preflight.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_command_execute": confirm_command_execute,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_manifested_next_gate_command_with_confirmation": can_execute,
        "requires_explicit_next_gate_command_execute": can_execute,
        "next_gate_command_executed": False,
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "delegated_command": delegated_command,
        "delegated_report_path": delegated_paths["report"],
        "delegated_review_path": delegated_paths["review"],
        "delegated_returncode": None,
        "delegated_status": "",
        "delegated_result": {},
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight_summary(manifested_routed_next_gate_command_preflight),
        "command_execute_request": build_command_execute_request(
            mode,
            confirm_command_execute,
            reviewer,
            note,
        ),
        "command_plan_item": command_plan if can_execute else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_preflight_blocking_reasons(
    manifested_routed_next_gate_command_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    if manifested_routed_next_gate_command_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("manifested_routed_next_gate_command_preflight_missing_or_invalid_schema")
    if (
        manifested_routed_next_gate_command_preflight.get("status")
        != "ready_for_manifested_routed_next_gate_command_review"
    ):
        reasons.append("manifested_routed_next_gate_command_preflight_not_ready")
    if manifested_routed_next_gate_command_preflight.get("can_request_manifested_next_gate_command_execution") is not True:
        reasons.append("manifested_routed_next_gate_command_preflight_cannot_request_execution")
    if manifested_routed_next_gate_command_preflight.get("requires_explicit_next_gate_command_execute") is not True:
        reasons.append("manifested_routed_next_gate_command_preflight_missing_explicit_command_requirement")
    if manifested_routed_next_gate_command_preflight.get("next_gate_command_executed") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_already_executed_command")
    if manifested_routed_next_gate_command_preflight.get("this_command_ran_next_gate_command") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_ran_command")
    if manifested_routed_next_gate_command_preflight.get("next_gate_entered") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_already_entered_next_gate")
    if manifested_routed_next_gate_command_preflight.get("export_or_acceptance_executed") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_executed_export_or_acceptance")
    if manifested_routed_next_gate_command_preflight.get("formal_writeback_executed") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_executed_formal_writeback")
    if manifested_routed_next_gate_command_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_wrote_formal_state")
    if manifested_routed_next_gate_command_preflight.get("can_write_product_state") is True:
        reasons.append("manifested_routed_next_gate_command_preflight_allows_product_state_write")
    if manifested_routed_next_gate_command_preflight.get("blocking_reasons"):
        reasons.append("source_preflight_has_blocking_reasons")
    for flag, value in manifested_routed_next_gate_command_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"manifested_routed_next_gate_command_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_command_plan_contract_blocking_reasons(
    manifested_routed_next_gate_command_preflight: dict[str, Any],
) -> list[str]:
    plan = manifested_routed_next_gate_command_preflight.get("next_gate_command_call_plan", [])
    if not plan:
        return ["next_gate_command_call_plan_missing"]
    if not isinstance(plan, list) or len(plan) != 1:
        return ["next_gate_command_call_plan_not_single"]

    item = plan[0]
    route_type = item.get("verified_route_type", "unknown")
    gate_id = item.get("gate_id", "")
    contract = NEXT_GATE_COMMAND_CONTRACTS.get(gate_id)
    reasons = []
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{gate_id}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"next_gate_command_route_type_not_allowed:{route_type}")
        if item.get("next_gate_action") not in contract["allowed_actions"]:
            reasons.append(f"next_gate_command_action_not_allowed:{gate_id}")
        next_command = item.get("next_command", "")
        if not next_command:
            reasons.append(f"next_gate_command_missing:{route_type}")
        elif next_command != contract["next_command"]:
            reasons.append(f"next_gate_command_mismatch:{route_type}")
        if item.get("command_path") != contract["command_path"]:
            reasons.append(f"next_gate_command_path_mismatch:{route_type}")
        if item.get("command_kind") != contract["command_kind"]:
            reasons.append(f"next_gate_command_kind_mismatch:{route_type}")

    if route_type != manifested_routed_next_gate_command_preflight.get("verified_route_type", ""):
        reasons.append(f"next_gate_command_route_type_mismatch:{route_type}")
    if gate_id != manifested_routed_next_gate_command_preflight.get("routed_next_gate", ""):
        reasons.append(f"next_gate_command_gate_mismatch:{gate_id}")
    if item.get("command_plan_id") != f"manifested_routed_next_gate_command::{gate_id}::{route_type}":
        reasons.append(f"next_gate_command_plan_id_mismatch:{route_type}")
    if not item.get("source_operation_id"):
        reasons.append(f"next_gate_command_source_operation_missing:{route_type}")
    if not item.get("source_entry_id"):
        reasons.append(f"next_gate_command_source_entry_missing:{route_type}")
    if item.get("command_status") != "pending_explicit_next_gate_command_execute":
        reasons.append(f"next_gate_command_not_pending:{route_type}")
    if item.get("requires_explicit_next_gate_command_execute") is not True:
        reasons.append(f"next_gate_command_missing_explicit_requirement:{route_type}")
    if item.get("will_run_next_gate_command_by_this_command") is True:
        reasons.append(f"next_gate_command_plan_marked_run_command:{route_type}")
    if item.get("will_enter_next_gate_by_this_command") is True:
        reasons.append(f"next_gate_command_plan_marked_enter_next_gate:{route_type}")
    if item.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"next_gate_command_plan_marked_export_or_acceptance:{route_type}")
    if item.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"next_gate_command_plan_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(
    manifested_routed_next_gate_command_preflight: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    item = extract_command_plan(manifested_routed_next_gate_command_preflight)
    command_path = item.get("command_path", "")
    if command_path and not (repo_root / command_path).exists():
        return [f"next_gate_command_file_missing:{command_path}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_command_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["manifested_next_gate_command_execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_command_execute:
        reasons.append("confirm_command_execute_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("command_execute_note_required")
    return reasons


def build_status(
    mode: str,
    preflight_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_manifested_routed_next_gate_command_preflight"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_contract"
    if unavailable_reasons:
        return "blocked_by_manifested_next_gate_command_unavailable"
    if "manifested_next_gate_command_execute_mode_invalid" in request_reasons:
        return "blocked_by_manifested_next_gate_command_execute_mode"
    if mode == "dry-run":
        return "manifested_next_gate_command_execute_dry_run_ready"
    if "confirm_command_execute_required" in request_reasons:
        return "blocked_by_missing_manifested_next_gate_command_execute_confirmation"
    if request_reasons:
        return "blocked_by_manifested_next_gate_command_execute_metadata"
    return "ready_to_execute_manifested_next_gate_command"


def extract_command_plan(manifested_routed_next_gate_command_preflight: dict[str, Any]) -> dict[str, Any]:
    plan = manifested_routed_next_gate_command_preflight.get("next_gate_command_call_plan", [])
    if isinstance(plan, list) and len(plan) == 1:
        return plan[0]
    return {}


def build_delegated_command(project_root: Path, command_plan: dict[str, Any]) -> list[str]:
    command_path = command_plan.get("command_path", "")
    args = list(command_plan.get("command_args", []))
    normalized_args = []
    skip_next = False
    for index, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg == "--project-root" and index + 1 < len(args):
            normalized_args.extend(["--project-root", str(project_root)])
            skip_next = True
            continue
        normalized_args.append(str(arg))
    if "--project-root" not in normalized_args:
        normalized_args.extend(["--project-root", str(project_root)])
    return ["python3", command_path] + normalized_args


def build_delegated_paths(routed_next_gate: str) -> dict[str, str]:
    contract = NEXT_GATE_COMMAND_CONTRACTS.get(routed_next_gate, {})
    return {
        "report": contract.get("delegated_report_path", ""),
        "review": contract.get("delegated_review_path", ""),
    }


def build_source_preflight_summary(
    manifested_routed_next_gate_command_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": manifested_routed_next_gate_command_preflight.get("schema_version", ""),
        "status": manifested_routed_next_gate_command_preflight.get("status", ""),
        "verified_route_type": manifested_routed_next_gate_command_preflight.get("verified_route_type", ""),
        "routed_next_gate": manifested_routed_next_gate_command_preflight.get("routed_next_gate", ""),
        "can_request_manifested_next_gate_command_execution": (
            manifested_routed_next_gate_command_preflight.get(
                "can_request_manifested_next_gate_command_execution"
            )
            is True
        ),
        "requires_explicit_next_gate_command_execute": (
            manifested_routed_next_gate_command_preflight.get("requires_explicit_next_gate_command_execute")
            is True
        ),
        "next_gate_command_executed": (
            manifested_routed_next_gate_command_preflight.get("next_gate_command_executed") is True
        ),
        "this_command_ran_next_gate_command": (
            manifested_routed_next_gate_command_preflight.get("this_command_ran_next_gate_command") is True
        ),
        "next_gate_entered": manifested_routed_next_gate_command_preflight.get("next_gate_entered") is True,
        "export_or_acceptance_executed": (
            manifested_routed_next_gate_command_preflight.get("export_or_acceptance_executed") is True
        ),
        "formal_writeback_executed": (
            manifested_routed_next_gate_command_preflight.get("formal_writeback_executed") is True
        ),
        "this_command_wrote_formal_state": (
            manifested_routed_next_gate_command_preflight.get("this_command_wrote_formal_state") is True
        ),
        "can_write_product_state": (
            manifested_routed_next_gate_command_preflight.get("can_write_product_state") is True
        ),
        "command_plan_count": len(
            manifested_routed_next_gate_command_preflight.get("next_gate_command_call_plan", [])
        ),
        "source_blocking_reasons": manifested_routed_next_gate_command_preflight.get("blocking_reasons", []),
        "boundary_flags": manifested_routed_next_gate_command_preflight.get("boundary_flags", {}),
    }


def build_command_execute_request(
    mode: str,
    confirm_command_execute: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_command_execute": confirm_command_execute,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_delegated_report_summary(delegated_report: dict[str, Any]) -> dict[str, Any]:
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
        "entered_next_gate": False,
        "ran_next_gate_command": False,
        "wrote_formal_state": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "manifested_next_gate_command_execute_dry_run_ready":
        return {
            "id": "rerun_with_confirm_command_execute",
            "label": "Confirm manifested next-gate command execution",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to run the delegated next-gate command.",
        }
    if status == "ready_to_execute_manifested_next_gate_command":
        return {
            "id": "execute_manifested_next_gate_command",
            "label": "Execute manifested next-gate command",
            "description": "The delegated next-gate command is ready to run.",
        }
    if status == "manifested_next_gate_command_executed":
        return {
            "id": "review_delegated_next_gate_result",
            "label": "Review delegated next-gate result",
            "description": f"The `{route_type}` next-gate command ran; review the delegated output before continuing.",
        }
    if status == "blocked_by_missing_manifested_next_gate_command_execute_confirmation":
        return {
            "id": "rerun_with_confirm_command_execute",
            "label": "Rerun with explicit command execution confirmation",
            "description": "Execute mode requires --confirm-command-execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_next_gate_command_execute_metadata":
        return {
            "id": "record_command_execute_reviewer_and_note",
            "label": "Record command execution reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_next_gate_command_unavailable":
        return {
            "id": "implement_or_restore_delegated_next_gate_command",
            "label": "Implement delegated next-gate command",
            "description": "The planned next-gate command file is missing, so it cannot be executed.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_next_gate_command_failure":
        return {
            "id": "repair_delegated_next_gate_command_inputs",
            "label": "Repair delegated next-gate command inputs",
            "description": "The delegated next-gate command ran but returned a failure.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_contract":
        return {
            "id": "repair_manifested_next_gate_command_plan",
            "label": "Repair manifested next-gate command plan",
            "description": "P7-AH must expose exactly one clean command plan before execution.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_routed_next_gate_command_preflight_blockers",
        "label": "Resolve P7-AH blockers",
        "description": "P7-AH must be ready before P7-AI can run a delegated next-gate command.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs(
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
        "# Auto Mode Formal Package Manifested Routed Next Gate Command Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        "- 可确认执行下一关命令："
        f"{str(report['can_execute_manifested_next_gate_command_with_confirmation']).lower()}",
        f"- delegated command 数：{len(report['delegated_command'])}",
        f"- 已运行下一关命令：{str(report['next_gate_command_executed']).lower()}",
        f"- 本命令运行下一关命令：{str(report['this_command_ran_next_gate_command']).lower()}",
        f"- delegated returncode：{report['delegated_returncode']}",
        f"- delegated status：`{report['delegated_status']}`",
        f"- 已进入下一关：{str(report['next_gate_entered']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["delegated_command"]:
        lines.extend(["", "## Delegated Command"])
        lines.append(f"- `{' '.join(report['delegated_command'])}`")
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
