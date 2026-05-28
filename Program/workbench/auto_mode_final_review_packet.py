from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_SCHEMA_VERSION = "p7.auto_mode_final_review_packet.v1"
DECISION_SCHEMA_VERSION = "p7.auto_mode_final_review_decision.v1"
DEFAULT_ACCEPTANCE_CHAIN_PATH = Path("Results/json/auto_mode_acceptance_chain_method_stat_integrated.json")
DEFAULT_PACKAGE_MANIFEST_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/manifest.json")
DEFAULT_PACKET_PATH = Path("Results/json/auto_mode_final_review_packet.json")
DEFAULT_PACKET_REVIEW_PATH = Path("Reviews/auto_mode_final_review_packet.md")
DEFAULT_DECISION_PATH = Path("Results/json/auto_mode_final_review_decision.json")
DEFAULT_DECISION_REVIEW_PATH = Path("Reviews/auto_mode_final_review_decision.md")
VALID_DECISIONS = {"defer", "approve", "revise", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_final_review_packet(
    acceptance_chain: dict[str, Any],
    package_manifest: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    blocking_reasons = build_packet_blocking_reasons(acceptance_chain, package_manifest)
    component_statuses = acceptance_chain.get("component_statuses", [])
    method_readiness = acceptance_chain.get("method_readiness", {})
    statistical_readiness = acceptance_chain.get("statistical_readiness", {})
    package_artifacts = {
        "real_run_artifacts": package_manifest.get("real_run_artifacts", []),
        "draft_layer_artifacts": package_manifest.get("draft_layer_artifacts", []),
        "human_review_required": package_manifest.get("human_review_required", []),
        "rendered_artifact": package_manifest.get("rendered_artifact", ""),
        "file_count": len(package_manifest.get("files", [])),
        "missing_targets": package_manifest.get("missing_targets", []),
    }
    can_request_final_decision = not blocking_reasons
    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_human_final_review" if can_request_final_decision else "blocked_final_review_packet_inputs",
        "topic": package_manifest.get("topic", ""),
        "source_paths": {
            "acceptance_chain": source_paths.get("acceptance_chain", str(DEFAULT_ACCEPTANCE_CHAIN_PATH)),
            "package_manifest": source_paths.get("package_manifest", str(DEFAULT_PACKAGE_MANIFEST_PATH)),
        },
        "can_request_final_decision": can_request_final_decision,
        "blocking_reasons": blocking_reasons,
        "evidence_summary": {
            "acceptance_status": acceptance_chain.get("status", ""),
            "package_readiness": acceptance_chain.get("package_readiness", ""),
            "component_count": len(component_statuses),
            "method_recommended_check_count": method_readiness.get("recommended_check_count", 0),
            "method_proposal_source_count": method_readiness.get("proposal_source_count", 0),
            "method_reviewed_canonical_blocking_rule_count": method_readiness.get(
                "reviewed_canonical_blocking_rule_count", 0
            ),
            "statistical_normalized_result_count": statistical_readiness.get("normalized_result_count", 0),
            "statistical_contract_ready_result_count": statistical_readiness.get("contract_ready_result_count", 0),
            "package_status": package_manifest.get("status", ""),
            "package_file_count": len(package_manifest.get("files", [])),
        },
        "component_statuses": component_statuses,
        "method_readiness": method_readiness,
        "statistical_readiness": statistical_readiness,
        "package_artifacts": package_artifacts,
        "required_review_items": build_required_review_items(acceptance_chain, package_manifest),
        "next_actions": build_packet_next_actions(can_request_final_decision),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
        },
    }


def build_packet_blocking_reasons(
    acceptance_chain: dict[str, Any],
    package_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    if acceptance_chain.get("schema_version") != "p7.auto_mode_acceptance_chain.v1":
        reasons.append("acceptance_chain_missing_or_invalid_schema")
    if package_manifest.get("schema_version") != "p6.cgss_paper_package.v1":
        reasons.append("paper_package_manifest_missing_or_invalid_schema")
    if acceptance_chain.get("package_readiness") != "needs_human_final_review":
        reasons.append("acceptance_chain_not_ready_for_final_review")
    if acceptance_chain.get("missing_inputs"):
        reasons.append("acceptance_chain_has_missing_inputs")
    if acceptance_chain.get("repair_queue"):
        reasons.append("auto_mode_repair_queue_not_empty")
    if package_manifest.get("status") != "needs_human_paper_package_review":
        reasons.append("paper_package_not_ready_for_review")
    if package_manifest.get("missing_targets"):
        reasons.append("paper_package_manifest_has_missing_targets")
    return reasons


def build_required_review_items(
    acceptance_chain: dict[str, Any],
    package_manifest: dict[str, Any],
) -> list[str]:
    review_items = []
    for item in acceptance_chain.get("human_review_checklist", []):
        append_unique(review_items, item)
    for item in package_manifest.get("human_review_required", []):
        append_unique(review_items, item)
    for item in package_manifest.get("next_tasks", []):
        append_unique(review_items, item)
    return review_items


def build_packet_next_actions(can_request_final_decision: bool) -> list[str]:
    if can_request_final_decision:
        return ["human_defer_approve_revise_or_reject_final_packet"]
    return ["repair_auto_mode_acceptance_or_package_manifest_before_final_review"]


def append_unique(items: list[str], item: str) -> None:
    if item and item not in items:
        items.append(item)


def build_auto_mode_final_review_decision(
    packet: dict[str, Any],
    decision: str,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    normalized_decision = decision.strip().lower()
    if normalized_decision not in VALID_DECISIONS:
        normalized_decision = "defer"
    reviewer = reviewer.strip()
    note = note.strip()
    record = {
        "schema_version": DECISION_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": packet.get("topic", ""),
        "source_packet": {
            "schema_version": packet.get("schema_version", ""),
            "status": packet.get("status", ""),
            "can_request_final_decision": packet.get("can_request_final_decision") is True,
            "required_review_item_count": len(packet.get("required_review_items", [])),
        },
        "decision": normalized_decision,
        "reviewer": reviewer,
        "note": note,
        "approved": False,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "promotion": {"allowed": False},
        "blocking_reasons": [],
        "next_actions": [],
    }

    if packet.get("schema_version") != PACKET_SCHEMA_VERSION or not packet.get("can_request_final_decision"):
        record.update(
            {
                "status": "blocked_final_review_packet_not_ready",
                "route": "repair_final_review_packet",
                "blocking_reasons": packet.get("blocking_reasons", ["final_review_packet_not_ready"]),
                "next_actions": ["repair_auto_mode_final_review_packet"],
            }
        )
        return record

    if normalized_decision == "defer":
        record.update(
            {
                "status": "waiting_for_human_final_review_decision",
                "route": "wait_for_human_confirmation",
                "next_actions": ["human_approve_revise_reject_or_defer_final_packet"],
            }
        )
        return record

    metadata_reasons = missing_metadata_reasons(reviewer, note)
    if metadata_reasons:
        record.update(
            {
                "status": "blocked_missing_human_final_review_metadata",
                "route": "record_human_final_review_metadata",
                "blocking_reasons": metadata_reasons,
                "next_actions": ["record_reviewer_and_decision_note"],
            }
        )
        return record

    if normalized_decision == "approve":
        record.update(
            {
                "status": "approved_for_formal_promotion_preflight",
                "route": "formal_promotion_preflight",
                "approved": True,
                "promotion": {
                    "allowed": True,
                    "would_enable": ["formal_promotion_preflight"],
                    "required_next_gate": "formal_writeback_preflight_human_approval",
                },
                "next_actions": [
                    "run_formal_promotion_preflight",
                    "keep_formal_writeback_gated_until_separate_approval",
                ],
            }
        )
        return record

    if normalized_decision == "revise":
        record.update(
            {
                "status": "final_review_requires_auto_mode_repair",
                "route": "auto_mode_repair",
                "blocking_reasons": ["human_requested_final_packet_revision"],
                "next_actions": ["repair_auto_mode_packet_or_paper_package"],
            }
        )
        return record

    record.update(
        {
            "status": "final_review_rejected",
            "route": "stop_or_rebuild_package",
            "blocking_reasons": ["human_rejected_final_packet"],
            "next_actions": ["stop_or_rebuild_auto_mode_paper_package"],
        }
    )
    return record


def missing_metadata_reasons(reviewer: str, note: str) -> list[str]:
    reasons = []
    if not reviewer:
        reasons.append("reviewer_required")
    if not note:
        reasons.append("decision_note_required")
    return reasons


def write_auto_mode_final_review_outputs(
    project_root: Path,
    packet: dict[str, Any],
    decision_record: dict[str, Any],
    packet_path: Path = DEFAULT_PACKET_PATH,
    packet_review_path: Path = DEFAULT_PACKET_REVIEW_PATH,
    decision_path: Path = DEFAULT_DECISION_PATH,
    decision_review_path: Path = DEFAULT_DECISION_REVIEW_PATH,
) -> tuple[Path, Path, Path, Path]:
    absolute_packet = project_root / packet_path
    absolute_packet_review = project_root / packet_review_path
    absolute_decision = project_root / decision_path
    absolute_decision_review = project_root / decision_review_path
    absolute_packet.parent.mkdir(parents=True, exist_ok=True)
    absolute_packet_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_decision.parent.mkdir(parents=True, exist_ok=True)
    absolute_decision_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_packet.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_packet_review.write_text(render_packet_review(packet), encoding="utf-8")
    absolute_decision.write_text(json.dumps(decision_record, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_decision_review.write_text(render_decision_review(decision_record), encoding="utf-8")
    return absolute_packet, absolute_packet_review, absolute_decision, absolute_decision_review


def render_packet_review(packet: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Final Review Packet",
        "",
        f"- 题目：{packet.get('topic', '')}",
        f"- 状态：`{packet['status']}`",
        f"- 可请求终审决策：{str(packet['can_request_final_decision']).lower()}",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
        "",
        "## Evidence Summary",
    ]
    for key, value in packet["evidence_summary"].items():
        lines.append(f"- `{key}`: {value}")
    if packet["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in packet["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Component Statuses"])
    for item in packet["component_statuses"]:
        lines.append(f"- `{item.get('component', '')}`: {item.get('status', '')}")
    lines.extend(["", "## Required Review Items"])
    for item in packet["required_review_items"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Package Artifacts"])
    for key, value in packet["package_artifacts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Next Actions"])
    for action in packet["next_actions"]:
        lines.append(f"- `{action}`")
    return "\n".join(lines) + "\n"


def render_decision_review(record: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Final Review Decision",
        "",
        f"- 题目：{record.get('topic', '')}",
        f"- 状态：`{record['status']}`",
        f"- 决策：`{record['decision']}`",
        f"- 路由：`{record['route']}`",
        f"- 审阅人：{record.get('reviewer') or '未记录'}",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
        f"- Promotion allowed：{str(record.get('promotion', {}).get('allowed') is True).lower()}",
    ]
    if record.get("note"):
        lines.extend(["", "## Decision Note", record["note"]])
    if record.get("blocking_reasons"):
        lines.extend(["", "## Blocking Reasons"])
        for reason in record["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Actions"])
    for action in record["next_actions"]:
        lines.append(f"- `{action}`")
    return "\n".join(lines) + "\n"
