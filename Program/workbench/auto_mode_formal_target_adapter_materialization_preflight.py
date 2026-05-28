from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_preflight.v1"
EXECUTION_REPORT_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_execution.v1"
EXECUTION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_execution_manifest.v1"
DEFAULT_EXECUTION_PATH = Path("Results/json/auto_mode_formal_target_adapter_execution.json")
DEFAULT_EXECUTION_MANIFEST_PATH = Path(
    "workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json"
)
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_target_adapter_materialization_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_materialization_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_materialization_preflight(
    target_adapter_execution: dict[str, Any],
    execution_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    execution_reasons = build_execution_report_blocking_reasons(target_adapter_execution)
    manifest_reasons = build_execution_manifest_blocking_reasons(execution_manifest) if not execution_reasons else []
    boundary_reasons = (
        build_manifest_boundary_blocking_reasons(execution_manifest)
        if not execution_reasons and not manifest_reasons
        else []
    )
    contract_reasons = (
        build_materialization_contract_blocking_reasons(execution_manifest)
        if not execution_reasons and not manifest_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = execution_reasons + manifest_reasons + boundary_reasons + contract_reasons
    status = build_status(execution_reasons, manifest_reasons, boundary_reasons, contract_reasons)
    materialization_plan = build_materialization_plan(execution_manifest) if not blocking_reasons else []
    ready = status == "ready_for_adapter_materialization_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": target_adapter_execution.get("topic") or execution_manifest.get("topic", ""),
        "source_paths": {
            "target_adapter_execution": source_paths.get("target_adapter_execution", str(DEFAULT_EXECUTION_PATH)),
            "execution_manifest": source_paths.get("execution_manifest", str(DEFAULT_EXECUTION_MANIFEST_PATH)),
        },
        "status": status,
        "can_request_adapter_materialization": ready,
        "requires_explicit_materialize_command": ready,
        "candidate_targets_materialized": False,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_execution": build_source_execution(target_adapter_execution),
        "source_execution_manifest": build_source_execution_manifest(execution_manifest),
        "materialization_plan": materialization_plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_execution_report_blocking_reasons(target_adapter_execution: dict[str, Any]) -> list[str]:
    reasons = []
    if target_adapter_execution.get("schema_version") != EXECUTION_REPORT_SCHEMA_VERSION:
        reasons.append("target_adapter_execution_missing_or_invalid_schema")
    if target_adapter_execution.get("status") != "target_adapter_execution_manifest_recorded":
        reasons.append("target_adapter_execution_not_manifest_recorded")
    if target_adapter_execution.get("execution_manifest_recorded") is not True:
        reasons.append("target_adapter_execution_manifest_not_recorded")
    if target_adapter_execution.get("formal_target_adapters_executed") is True:
        reasons.append("target_adapter_execution_already_executed_adapters")
    if target_adapter_execution.get("formal_writeback_executed") is True:
        reasons.append("target_adapter_execution_already_executed_formal_writeback")
    if target_adapter_execution.get("this_command_wrote_formal_state") is True:
        reasons.append("target_adapter_execution_already_wrote_formal_state")
    if target_adapter_execution.get("can_write_product_state") is True:
        reasons.append("target_adapter_execution_allows_product_state_write")
    if target_adapter_execution.get("execution_manifest_recorded") is True and not target_adapter_execution.get(
        "execution_manifest_path"
    ):
        reasons.append("target_adapter_execution_manifest_path_missing")
    for flag, value in target_adapter_execution.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"target_adapter_execution_boundary_violation:{flag}")
    return reasons


def build_execution_manifest_blocking_reasons(execution_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if execution_manifest.get("schema_version") != EXECUTION_MANIFEST_SCHEMA_VERSION:
        reasons.append("execution_manifest_missing_or_invalid_schema")
    if execution_manifest.get("formal_target_adapters_executed") is True:
        reasons.append("execution_manifest_already_executed_adapters")
    if execution_manifest.get("formal_writeback_executed") is True:
        reasons.append("execution_manifest_already_executed_formal_writeback")
    if execution_manifest.get("candidate_targets_created") is True:
        reasons.append("execution_manifest_candidate_targets_already_created")
    if not execution_manifest.get("adapter_execution_plan"):
        reasons.append("execution_manifest_adapter_execution_plan_missing")
    return reasons


def build_manifest_boundary_blocking_reasons(execution_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    for flag, value in execution_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"execution_manifest_boundary_violation:{flag}")
    return reasons


def build_materialization_contract_blocking_reasons(execution_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    for item in execution_manifest.get("adapter_execution_plan", []):
        group = item.get("writeback_target_group", "unknown")
        if item.get("execution_status") != "planned_not_executed":
            reasons.append(f"adapter_execution_status_not_planned:{group}")
        if item.get("requires_materialization_node") is not True:
            reasons.append(f"materialization_node_requirement_missing:{group}")
        if item.get("executed_by_this_command") is True:
            reasons.append(f"adapter_execution_already_executed:{group}")
        if not item.get("execution_id"):
            reasons.append(f"adapter_execution_id_missing:{group}")
        if not item.get("adapter_id"):
            reasons.append(f"adapter_id_missing:{group}")
        if not item.get("source_artifacts"):
            reasons.append(f"materialization_source_artifacts_missing:{group}")
        candidate_targets = item.get("candidate_targets", [])
        if not candidate_targets:
            reasons.append(f"materialization_candidate_targets_missing:{group}")
        for target in candidate_targets:
            if not target.get("path"):
                reasons.append(f"materialization_candidate_target_path_missing:{group}")
            if target.get("exists") is True:
                reasons.append(f"materialization_candidate_target_already_exists:{group}")
            if target.get("will_be_written_by_this_command") is True:
                reasons.append(f"materialization_candidate_target_already_marked_write:{group}")
    return dedupe(reasons)


def build_status(
    execution_reasons: list[str],
    manifest_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if execution_reasons:
        return "blocked_by_target_adapter_execution"
    if manifest_reasons:
        return "blocked_by_execution_manifest"
    if boundary_reasons:
        return "blocked_by_execution_manifest_boundary"
    if contract_reasons:
        return "blocked_by_materialization_contract"
    return "ready_for_adapter_materialization_review"


def build_source_execution(target_adapter_execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": target_adapter_execution.get("schema_version", ""),
        "status": target_adapter_execution.get("status", ""),
        "execution_manifest_recorded": target_adapter_execution.get("execution_manifest_recorded") is True,
        "execution_manifest_path": target_adapter_execution.get("execution_manifest_path", ""),
        "formal_target_adapters_executed": target_adapter_execution.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": target_adapter_execution.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": target_adapter_execution.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": target_adapter_execution.get("can_write_product_state") is True,
        "adapter_execution_plan_count": len(target_adapter_execution.get("adapter_execution_plan", [])),
        "blocking_reasons": target_adapter_execution.get("blocking_reasons", []),
    }


def build_source_execution_manifest(execution_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": execution_manifest.get("schema_version", ""),
        "manifest_path": execution_manifest.get("manifest_path", ""),
        "source_execution_report": execution_manifest.get("source_execution_report", ""),
        "reviewer": execution_manifest.get("reviewer", ""),
        "formal_target_adapters_executed": execution_manifest.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": execution_manifest.get("formal_writeback_executed") is True,
        "candidate_targets_created": execution_manifest.get("candidate_targets_created") is True,
        "adapter_execution_plan_count": len(execution_manifest.get("adapter_execution_plan", [])),
    }


def build_materialization_plan(execution_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for index, item in enumerate(execution_manifest.get("adapter_execution_plan", []), start=1):
        group = item.get("writeback_target_group", "")
        plan.append(
            {
                "materialization_id": f"materialization::{index:02d}::{group}",
                "execution_id": item.get("execution_id", ""),
                "operation_id": item.get("operation_id", ""),
                "category": item.get("category", ""),
                "writeback_target_group": group,
                "adapter_id": item.get("adapter_id", ""),
                "source_artifacts": item.get("source_artifacts", []),
                "candidate_targets": item.get("candidate_targets", []),
                "materialization_status": "planned_not_materialized",
                "requires_explicit_materialize_command": True,
                "will_materialize_by_this_command": False,
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
        "created_candidate_targets": False,
        "materialized_candidate_targets": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "ready_for_adapter_materialization_review":
        return {
            "id": "review_materialization_preflight_then_confirm_materialize",
            "label": "Review adapter materialization preflight",
            "description": "Preflight is ready; a later explicit materialize node can create candidate targets.",
        }
    if status == "blocked_by_execution_manifest":
        return {
            "id": "repair_or_record_execution_manifest",
            "label": "Repair or record execution manifest",
            "description": "A valid P7-O execution manifest is required before materialization preflight.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_execution_manifest_boundary":
        return {
            "id": "repair_execution_manifest_boundary",
            "label": "Repair execution manifest boundary violation",
            "description": "The execution manifest reports a boundary violation and cannot feed materialization.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_materialization_contract":
        return {
            "id": "repair_materialization_contract",
            "label": "Repair materialization contract",
            "description": "Adapter plan items must provide source artifacts, candidate targets, and materialization requirements.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "record_target_adapter_execution_manifest",
        "label": "Record target adapter execution manifest",
        "description": "P7-O must record an execution manifest before P7-P can inspect materialization readiness.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_materialization_preflight_outputs(
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
        "# Auto Mode Formal Target Adapter Materialization Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求 adapter materialization：{str(report['can_request_adapter_materialization']).lower()}",
        f"- 需要显式 materialize 命令：{str(report['requires_explicit_materialize_command']).lower()}",
        f"- 已 materialize candidate targets：{str(report['candidate_targets_materialized']).lower()}",
        f"- 已执行 target adapters：{str(report['formal_target_adapters_executed']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Materialization Plan"])
    if report["materialization_plan"]:
        for item in report["materialization_plan"]:
            lines.append(f"- `{item['materialization_id']}`: {item['materialization_status']}")
    else:
        lines.append("- 无；等待 target adapter execution manifest ready。")
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
