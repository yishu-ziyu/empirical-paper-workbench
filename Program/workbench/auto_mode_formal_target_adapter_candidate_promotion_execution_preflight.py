from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.v1"
APPROVAL_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_approval.v1"
DEFAULT_APPROVAL_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json")
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
    candidate_promotion_approval: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    approval_reasons = build_approval_blocking_reasons(candidate_promotion_approval)
    boundary_reasons = build_boundary_blocking_reasons(candidate_promotion_approval) if not approval_reasons else []
    plan_reasons = (
        build_approved_plan_blocking_reasons(candidate_promotion_approval)
        if not approval_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = approval_reasons + boundary_reasons + plan_reasons
    status = build_status(approval_reasons, boundary_reasons, plan_reasons)
    ready = status == "ready_for_verified_candidate_promotion_execution_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": candidate_promotion_approval.get("topic", ""),
        "source_paths": {
            "candidate_promotion_approval": source_paths.get(
                "candidate_promotion_approval",
                str(DEFAULT_APPROVAL_PATH),
            ),
        },
        "status": status,
        "can_request_verified_candidate_promotion_execution": ready,
        "requires_explicit_promotion_execute_command": ready,
        "candidate_targets_promoted": False,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_approval": build_source_approval(candidate_promotion_approval),
        "promotion_execution_plan": build_promotion_execution_plan(candidate_promotion_approval) if ready else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_approval_blocking_reasons(candidate_promotion_approval: dict[str, Any]) -> list[str]:
    reasons = []
    if candidate_promotion_approval.get("schema_version") != APPROVAL_SCHEMA_VERSION:
        reasons.append("candidate_promotion_approval_missing_or_invalid_schema")
    if candidate_promotion_approval.get("status") != "approved_for_verified_candidate_promotion_execution_preflight":
        reasons.append("candidate_promotion_approval_not_effective")
    if candidate_promotion_approval.get("approved") is not True:
        reasons.append("candidate_promotion_not_approved")
    if candidate_promotion_approval.get("verified_candidate_promotion_allowed") is not True:
        reasons.append("verified_candidate_promotion_not_allowed")
    if candidate_promotion_approval.get("can_enter_verified_candidate_promotion_execution_preflight") is not True:
        reasons.append("candidate_promotion_approval_cannot_enter_execution_preflight")
    if candidate_promotion_approval.get("candidate_targets_promoted") is True:
        reasons.append("candidate_promotion_approval_already_promoted_candidates")
    if candidate_promotion_approval.get("formal_target_adapters_executed") is True:
        reasons.append("candidate_promotion_approval_already_executed_target_adapters")
    if candidate_promotion_approval.get("formal_writeback_executed") is True:
        reasons.append("candidate_promotion_approval_already_executed_formal_writeback")
    if candidate_promotion_approval.get("this_command_wrote_formal_state") is True:
        reasons.append("candidate_promotion_approval_already_wrote_formal_state")
    if candidate_promotion_approval.get("can_write_product_state") is True:
        reasons.append("candidate_promotion_approval_allows_product_state_write")
    if candidate_promotion_approval.get("blocking_reasons"):
        reasons.append("candidate_promotion_approval_has_blocking_reasons")

    approval = candidate_promotion_approval.get("approval", {})
    if approval.get("decision") != "approve":
        reasons.append("candidate_promotion_approval_decision_not_approve")
    if approval.get("metadata_complete") is not True:
        reasons.append("candidate_promotion_approval_metadata_incomplete")
    return dedupe(reasons)


def build_boundary_blocking_reasons(candidate_promotion_approval: dict[str, Any]) -> list[str]:
    reasons = []
    for flag, value in candidate_promotion_approval.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"candidate_promotion_approval_boundary_violation:{flag}")
    return reasons


def build_approved_plan_blocking_reasons(candidate_promotion_approval: dict[str, Any]) -> list[str]:
    approved_plan = candidate_promotion_approval.get("approved_promotion_plan", [])
    if not approved_plan:
        return ["approved_promotion_plan_missing"]

    reasons = []
    seen_candidates: set[str] = set()
    seen_formal_targets: set[str] = set()
    for item in approved_plan:
        group = item.get("writeback_target_group", "unknown")
        candidate_path = item.get("candidate_path", "")
        formal_target_path = item.get("formal_target_path", "")
        if item.get("approval_status") != "approved_for_verified_candidate_promotion_execution_preflight":
            reasons.append(f"approved_promotion_item_not_ready:{group}")
        if item.get("requires_explicit_promotion_execute_command") is not True:
            reasons.append(f"approved_promotion_item_missing_execute_requirement:{group}")
        if item.get("promoted_by_this_command") is True:
            reasons.append(f"approved_promotion_item_already_promoted:{group}")
        if item.get("this_command_wrote_formal_state") is True:
            reasons.append(f"approved_promotion_item_already_wrote_formal_state:{group}")
        if not item.get("promotion_id"):
            reasons.append(f"promotion_id_missing:{group}")
        if not item.get("writeback_target_group"):
            reasons.append("writeback_target_group_missing")
        if not candidate_path:
            reasons.append(f"candidate_path_missing:{group}")
        elif not candidate_path.startswith("Submissions/auto_mode/"):
            reasons.append(f"candidate_path_outside_auto_mode_submission:{group}")
        if not formal_target_path:
            reasons.append(f"formal_target_path_missing:{group}")
        elif not formal_target_path.startswith("Submissions/formal_package/"):
            reasons.append(f"formal_target_path_outside_formal_package:{group}")
        if candidate_path and formal_target_path and candidate_path == formal_target_path:
            reasons.append(f"candidate_and_formal_target_same_path:{group}")
        if candidate_path in seen_candidates:
            reasons.append(f"duplicate_candidate_path:{group}")
        if formal_target_path in seen_formal_targets:
            reasons.append(f"duplicate_formal_target_path:{group}")
        if candidate_path:
            seen_candidates.add(candidate_path)
        if formal_target_path:
            seen_formal_targets.add(formal_target_path)
        if item.get("candidate_bytes") is None:
            reasons.append(f"candidate_bytes_missing:{group}")
        if not is_sha256(item.get("candidate_sha256", "")):
            reasons.append(f"candidate_sha256_missing_or_invalid:{group}")
    return dedupe(reasons)


def build_status(
    approval_reasons: list[str],
    boundary_reasons: list[str],
    plan_reasons: list[str],
) -> str:
    if approval_reasons:
        return "blocked_by_candidate_promotion_approval"
    if boundary_reasons:
        return "blocked_by_candidate_promotion_approval_boundary"
    if plan_reasons:
        return "blocked_by_approved_promotion_plan"
    return "ready_for_verified_candidate_promotion_execution_review"


def build_source_approval(candidate_promotion_approval: dict[str, Any]) -> dict[str, Any]:
    approval = candidate_promotion_approval.get("approval", {})
    return {
        "schema_version": candidate_promotion_approval.get("schema_version", ""),
        "status": candidate_promotion_approval.get("status", ""),
        "approved": candidate_promotion_approval.get("approved") is True,
        "verified_candidate_promotion_allowed": candidate_promotion_approval.get(
            "verified_candidate_promotion_allowed"
        )
        is True,
        "can_enter_verified_candidate_promotion_execution_preflight": candidate_promotion_approval.get(
            "can_enter_verified_candidate_promotion_execution_preflight"
        )
        is True,
        "candidate_targets_promoted": candidate_promotion_approval.get("candidate_targets_promoted") is True,
        "formal_writeback_executed": candidate_promotion_approval.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": candidate_promotion_approval.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": candidate_promotion_approval.get("can_write_product_state") is True,
        "approved_promotion_plan_count": len(candidate_promotion_approval.get("approved_promotion_plan", [])),
        "blocking_reasons": candidate_promotion_approval.get("blocking_reasons", []),
        "decision": approval.get("decision", ""),
        "reviewer": approval.get("reviewer", ""),
        "metadata_complete": approval.get("metadata_complete") is True,
    }


def build_promotion_execution_plan(candidate_promotion_approval: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for index, item in enumerate(candidate_promotion_approval.get("approved_promotion_plan", []), start=1):
        group = item.get("writeback_target_group", "")
        plan.append(
            {
                "execution_id": f"verified_candidate_promotion_execution::{index:02d}::{group}",
                "promotion_id": item.get("promotion_id", ""),
                "operation_id": item.get("operation_id", ""),
                "writeback_target_group": group,
                "candidate_path": item.get("candidate_path", ""),
                "candidate_bytes": item.get("candidate_bytes"),
                "candidate_sha256": item.get("candidate_sha256", ""),
                "formal_target_path": item.get("formal_target_path", ""),
                "execution_status": "pending_explicit_promotion_execute_command",
                "requires_explicit_promotion_execute_command": True,
                "promoted_by_this_command": False,
                "this_command_wrote_formal_state": False,
            }
        )
    return plan


def build_boundary_flags() -> dict[str, bool]:
    return {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "executed_target_adapters": False,
        "wrote_formal_state": False,
        "created_or_repaired_candidate_targets": False,
        "promoted_candidate_targets": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "ready_for_verified_candidate_promotion_execution_review":
        return {
            "id": "run_explicit_verified_candidate_promotion_execute_gate",
            "label": "Run explicit verified candidate promotion execute gate",
            "description": "The promotion execution preflight is ready; a separate execute node must perform target writes.",
        }
    if status == "blocked_by_candidate_promotion_approval_boundary":
        return {
            "id": "repair_candidate_promotion_approval_boundary",
            "label": "Repair candidate promotion approval boundary violation",
            "description": "The approval ledger reports a boundary violation and cannot feed execution.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_approved_promotion_plan":
        return {
            "id": "repair_approved_promotion_plan",
            "label": "Repair approved promotion plan",
            "description": "Approved candidate promotion items need candidate paths, formal targets, bytes, and SHA256.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "obtain_effective_candidate_promotion_approval",
        "label": "Obtain effective candidate promotion approval",
        "description": "The execution preflight cannot proceed until P7-T approval is effective.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_PREFLIGHT_PATH,
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
        "# Auto Mode Formal Target Adapter Candidate Promotion Execution Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求 candidate promotion execute：{str(report['can_request_verified_candidate_promotion_execution']).lower()}",
        f"- 需要显式 promotion execute 命令：{str(report['requires_explicit_promotion_execute_command']).lower()}",
        f"- 已提升 candidate targets：{str(report['candidate_targets_promoted']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Promotion Execution Plan"])
    if report["promotion_execution_plan"]:
        for item in report["promotion_execution_plan"]:
            lines.append(f"- `{item['execution_id']}`: {item['execution_status']}")
    else:
        lines.append("- 无；等待生效审批或修复 approved promotion plan。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def is_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)


def dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
