from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_execute.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
)
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_workflow_continuation_execute.md")
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
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_workflow_continuation_execute(
    project_root: Path,
    next_gate_workflow_continuation_preflight: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_continuation_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
        project_root,
        next_gate_workflow_continuation_preflight,
        mode=mode,
        confirm_continuation_execute=confirm_continuation_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_next_gate_workflow_continuation":
        return (
            report,
            0 if report["status"] == "next_gate_workflow_continuation_execute_dry_run_ready" else 2,
        )

    result = subprocess.run(
        report["continuation_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    continuation_report = load_json_or_empty(project_root / report["continuation_report_path"])
    continuation_status = continuation_report.get("status", "")
    report["workflow_continuation_executed"] = True
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
        report["status"] = "next_gate_workflow_continuation_executed"
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

    report["status"] = "blocked_by_next_gate_workflow_continuation_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"next_gate_workflow_continuation_failed:{report['verified_route_type']}",
            f"continuation_status:{continuation_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_workflow_continuation_execute(
    project_root: Path,
    next_gate_workflow_continuation_preflight: dict[str, Any],
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
    preflight_reasons = build_preflight_blocking_reasons(next_gate_workflow_continuation_preflight)
    contract_reasons = (
        build_continuation_plan_contract_blocking_reasons(next_gate_workflow_continuation_preflight)
        if not preflight_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(next_gate_workflow_continuation_preflight, repo_root)
        if not preflight_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(
        mode,
        confirm_continuation_execute,
        reviewer,
        note,
    )
    status = build_status(mode, preflight_reasons, contract_reasons, unavailable_reasons, request_reasons)
    plan_item = extract_continuation_plan_item(next_gate_workflow_continuation_preflight)
    can_execute = not preflight_reasons and not contract_reasons and not unavailable_reasons
    route_type = plan_item.get("verified_route_type", "") if can_execute else ""
    routed_next_gate = plan_item.get("routed_next_gate", "") if can_execute else ""
    command = (
        build_continuation_command(project_root, plan_item)
        if status
        in {
            "next_gate_workflow_continuation_execute_dry_run_ready",
            "ready_to_execute_next_gate_workflow_continuation",
        }
        else []
    )
    blocking_reasons = dedupe(preflight_reasons + contract_reasons + unavailable_reasons + request_reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": next_gate_workflow_continuation_preflight.get("topic", ""),
        "source_paths": {
            "next_gate_workflow_continuation_preflight": source_paths.get(
                "next_gate_workflow_continuation_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "source_status": next_gate_workflow_continuation_preflight.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_continuation_execute": confirm_continuation_execute,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_next_gate_workflow_continuation_with_confirmation": can_execute,
        "requires_explicit_workflow_continuation_command": can_execute,
        "workflow_continuation_executed": False,
        "this_command_ran_continuation": False,
        "continuation_command": command,
        "continuation_report_path": plan_item.get("next_report_path", "") if can_execute else "",
        "continuation_review_path": plan_item.get("next_review_path", "") if can_execute else "",
        "continuation_returncode": None,
        "continuation_status": "",
        "continuation_result": {},
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight_summary(next_gate_workflow_continuation_preflight),
        "continuation_execute_request": build_continuation_execute_request(
            mode,
            confirm_continuation_execute,
            reviewer,
            note,
        ),
        "workflow_continuation_plan_item": plan_item if can_execute else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_preflight_blocking_reasons(
    next_gate_workflow_continuation_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    if next_gate_workflow_continuation_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("next_gate_workflow_continuation_preflight_missing_or_invalid_schema")
    if (
        next_gate_workflow_continuation_preflight.get("status")
        != "ready_for_next_gate_workflow_continuation_review"
    ):
        reasons.append("next_gate_workflow_continuation_preflight_not_ready")
    if next_gate_workflow_continuation_preflight.get("can_request_next_gate_workflow_continuation") is not True:
        reasons.append("next_gate_workflow_continuation_preflight_cannot_request_execution")
    if next_gate_workflow_continuation_preflight.get("requires_explicit_workflow_continuation_command") is not True:
        reasons.append("next_gate_workflow_continuation_preflight_missing_explicit_command_requirement")
    if next_gate_workflow_continuation_preflight.get("workflow_continuation_executed") is True:
        reasons.append("next_gate_workflow_continuation_preflight_already_executed")
    if next_gate_workflow_continuation_preflight.get("this_command_ran_continuation") is True:
        reasons.append("next_gate_workflow_continuation_preflight_ran_continuation")
    if next_gate_workflow_continuation_preflight.get("export_or_acceptance_executed") is True:
        reasons.append("next_gate_workflow_continuation_preflight_executed_export_or_acceptance")
    if next_gate_workflow_continuation_preflight.get("formal_writeback_executed") is True:
        reasons.append("next_gate_workflow_continuation_preflight_executed_formal_writeback")
    if next_gate_workflow_continuation_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("next_gate_workflow_continuation_preflight_wrote_formal_state")
    if next_gate_workflow_continuation_preflight.get("can_write_product_state") is True:
        reasons.append("next_gate_workflow_continuation_preflight_allows_product_state_write")
    if next_gate_workflow_continuation_preflight.get("blocking_reasons"):
        reasons.append("source_preflight_has_blocking_reasons")
    for flag, value in next_gate_workflow_continuation_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"next_gate_workflow_continuation_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_plan_contract_blocking_reasons(
    next_gate_workflow_continuation_preflight: dict[str, Any],
) -> list[str]:
    plan = next_gate_workflow_continuation_preflight.get("workflow_continuation_plan", [])
    if not plan:
        return ["workflow_continuation_plan_missing"]
    if not isinstance(plan, list) or len(plan) != 1:
        return ["workflow_continuation_plan_not_single"]

    item = plan[0]
    route_type = item.get("verified_route_type", "unknown")
    routed_next_gate = next_gate_workflow_continuation_preflight.get("routed_next_gate", "")
    contract = CONTINUATION_EXECUTE_CONTRACTS.get(routed_next_gate)
    reasons = []
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"workflow_continuation_route_type_not_allowed:{route_type}")
        if item.get("continuation_kind") != contract["continuation_kind"]:
            reasons.append(f"workflow_continuation_kind_mismatch:{route_type}")
        if item.get("next_command") != contract["next_command"]:
            reasons.append(f"workflow_continuation_next_command_mismatch:{route_type}")
        if item.get("command_path") != contract["command_path"]:
            reasons.append(f"workflow_continuation_command_path_mismatch:{route_type}")
        if item.get("source_report_path") != contract["source_report_path"]:
            reasons.append(f"workflow_continuation_source_report_path_mismatch:{route_type}")
        if item.get("next_report_path") != contract["next_report_path"]:
            reasons.append(f"workflow_continuation_next_report_path_mismatch:{route_type}")
        if item.get("next_review_path") != contract["next_review_path"]:
            reasons.append(f"workflow_continuation_next_review_path_mismatch:{route_type}")

    if route_type != next_gate_workflow_continuation_preflight.get("verified_route_type", ""):
        reasons.append(f"workflow_continuation_route_type_mismatch:{route_type}")
    if item.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"workflow_continuation_gate_mismatch:{routed_next_gate}")
    if item.get("continuation_id") != f"next_gate_workflow_continuation::{routed_next_gate}::{route_type}":
        reasons.append(f"workflow_continuation_id_mismatch:{route_type}")
    if not item.get("source_delegated_result_record_id"):
        reasons.append(f"workflow_continuation_source_record_missing:{route_type}")
    if item.get("continuation_status") != "pending_explicit_workflow_continuation_command":
        reasons.append(f"workflow_continuation_not_pending:{route_type}")
    if item.get("requires_explicit_workflow_continuation_command") is not True:
        reasons.append(f"workflow_continuation_missing_explicit_requirement:{route_type}")
    if item.get("will_run_continuation_by_this_command") is True:
        reasons.append(f"workflow_continuation_plan_marked_run_continuation:{route_type}")
    if item.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"workflow_continuation_plan_marked_export_or_acceptance:{route_type}")
    if item.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"workflow_continuation_plan_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(
    next_gate_workflow_continuation_preflight: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    item = extract_continuation_plan_item(next_gate_workflow_continuation_preflight)
    command_path = item.get("command_path", "")
    if command_path and not (repo_root / command_path).exists():
        return [f"workflow_continuation_command_file_missing:{command_path}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_continuation_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["next_gate_workflow_continuation_execute_mode_invalid"]
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
    preflight_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_next_gate_workflow_continuation_preflight"
    if contract_reasons:
        return "blocked_by_next_gate_workflow_continuation_execute_contract"
    if unavailable_reasons:
        return "blocked_by_next_gate_workflow_continuation_command_unavailable"
    if "next_gate_workflow_continuation_execute_mode_invalid" in request_reasons:
        return "blocked_by_next_gate_workflow_continuation_execute_mode"
    if mode == "dry-run":
        return "next_gate_workflow_continuation_execute_dry_run_ready"
    if "confirm_continuation_execute_required" in request_reasons:
        return "blocked_by_missing_next_gate_workflow_continuation_execute_confirmation"
    if request_reasons:
        return "blocked_by_next_gate_workflow_continuation_execute_metadata"
    return "ready_to_execute_next_gate_workflow_continuation"


def extract_continuation_plan_item(
    next_gate_workflow_continuation_preflight: dict[str, Any],
) -> dict[str, Any]:
    plan = next_gate_workflow_continuation_preflight.get("workflow_continuation_plan", [])
    if isinstance(plan, list) and len(plan) == 1:
        return plan[0]
    return {}


def build_continuation_command(project_root: Path, plan_item: dict[str, Any]) -> list[str]:
    return [
        "python3",
        plan_item.get("command_path", ""),
        "--project-root",
        str(project_root),
        "--export-acceptance-router",
        plan_item.get("source_report_path", ""),
        "--output-preflight",
        plan_item.get("next_report_path", ""),
        "--output-review",
        plan_item.get("next_review_path", ""),
    ]


def build_source_preflight_summary(
    next_gate_workflow_continuation_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": next_gate_workflow_continuation_preflight.get("schema_version", ""),
        "status": next_gate_workflow_continuation_preflight.get("status", ""),
        "verified_route_type": next_gate_workflow_continuation_preflight.get("verified_route_type", ""),
        "routed_next_gate": next_gate_workflow_continuation_preflight.get("routed_next_gate", ""),
        "can_request_next_gate_workflow_continuation": (
            next_gate_workflow_continuation_preflight.get("can_request_next_gate_workflow_continuation")
            is True
        ),
        "requires_explicit_workflow_continuation_command": (
            next_gate_workflow_continuation_preflight.get("requires_explicit_workflow_continuation_command")
            is True
        ),
        "workflow_continuation_executed": (
            next_gate_workflow_continuation_preflight.get("workflow_continuation_executed") is True
        ),
        "this_command_ran_continuation": (
            next_gate_workflow_continuation_preflight.get("this_command_ran_continuation") is True
        ),
        "export_or_acceptance_executed": (
            next_gate_workflow_continuation_preflight.get("export_or_acceptance_executed") is True
        ),
        "formal_writeback_executed": (
            next_gate_workflow_continuation_preflight.get("formal_writeback_executed") is True
        ),
        "this_command_wrote_formal_state": (
            next_gate_workflow_continuation_preflight.get("this_command_wrote_formal_state") is True
        ),
        "can_write_product_state": (
            next_gate_workflow_continuation_preflight.get("can_write_product_state") is True
        ),
        "workflow_continuation_plan_count": len(
            next_gate_workflow_continuation_preflight.get("workflow_continuation_plan", [])
        ),
        "source_blocking_reasons": next_gate_workflow_continuation_preflight.get("blocking_reasons", []),
        "boundary_flags": next_gate_workflow_continuation_preflight.get("boundary_flags", {}),
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
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "next_gate_workflow_continuation_execute_dry_run_ready":
        return {
            "id": "rerun_with_confirm_continuation_execute",
            "label": "Confirm workflow continuation execution",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to run the continuation preflight.",
        }
    if status == "ready_to_execute_next_gate_workflow_continuation":
        return {
            "id": "execute_next_gate_workflow_continuation",
            "label": "Execute next-gate workflow continuation",
            "description": "The continuation command is ready to run.",
        }
    if status == "next_gate_workflow_continuation_executed":
        return {
            "id": "review_selected_route_execution_preflight",
            "label": "Review selected route execution preflight",
            "description": f"The `{route_type}` continuation command ran; review its preflight output before route execution.",
        }
    if status == "blocked_by_missing_next_gate_workflow_continuation_execute_confirmation":
        return {
            "id": "rerun_with_confirm_continuation_execute",
            "label": "Rerun with explicit continuation confirmation",
            "description": "Execute mode requires --confirm-continuation-execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_execute_metadata":
        return {
            "id": "record_continuation_reviewer_and_note",
            "label": "Record continuation reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_command_unavailable":
        return {
            "id": "implement_or_restore_continuation_command",
            "label": "Implement continuation command",
            "description": "The planned continuation command file is missing, so it cannot be executed.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_failure":
        return {
            "id": "repair_continuation_command_inputs",
            "label": "Repair continuation command inputs",
            "description": "The continuation command ran but returned a failure.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_execute_contract":
        return {
            "id": "repair_workflow_continuation_plan",
            "label": "Repair workflow continuation plan",
            "description": "P7-AK must expose exactly one clean continuation plan before execution.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_workflow_continuation_preflight_blockers",
        "label": "Resolve P7-AK blockers",
        "description": "P7-AK must be ready before P7-AL can run the continuation command.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_workflow_continuation_execute_outputs(
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
        "# Auto Mode Formal Package Next Gate Workflow Continuation Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        "- 可确认执行 workflow continuation："
        f"{str(report['can_execute_next_gate_workflow_continuation_with_confirmation']).lower()}",
        f"- continuation command 数：{len(report['continuation_command'])}",
        f"- 已运行 continuation：{str(report['workflow_continuation_executed']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
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
