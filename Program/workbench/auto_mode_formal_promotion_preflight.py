from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_promotion_preflight.v1"
DEFAULT_DECISION_PATH = Path("Results/json/auto_mode_final_review_decision.json")
DEFAULT_PACKET_PATH = Path("Results/json/auto_mode_final_review_packet.json")
DEFAULT_PACKAGE_MANIFEST_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/manifest.json")
DEFAULT_REPORT_PATH = Path("Results/json/auto_mode_formal_promotion_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_promotion_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_promotion_preflight(
    final_review_decision: dict[str, Any],
    final_review_packet: dict[str, Any],
    package_manifest: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    blocking_reasons = build_blocking_reasons(final_review_decision, final_review_packet, package_manifest)
    status = build_status(blocking_reasons)
    ready = not blocking_reasons
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": final_review_packet.get("topic") or package_manifest.get("topic", ""),
        "source_paths": {
            "final_review_decision": source_paths.get("final_review_decision", str(DEFAULT_DECISION_PATH)),
            "final_review_packet": source_paths.get("final_review_packet", str(DEFAULT_PACKET_PATH)),
            "package_manifest": source_paths.get("package_manifest", str(DEFAULT_PACKAGE_MANIFEST_PATH)),
        },
        "status": status,
        "can_request_formal_writeback_approval": ready,
        "requires_separate_formal_writeback_approval": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_decision": build_source_decision(final_review_decision),
        "source_packet": build_source_packet(final_review_packet),
        "package_summary": build_package_summary(package_manifest),
        "promotion_scope": build_promotion_scope(package_manifest) if ready else [],
        "approval_contract": build_approval_contract(ready),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(ready, blocking_reasons),
    }


def build_blocking_reasons(
    final_review_decision: dict[str, Any],
    final_review_packet: dict[str, Any],
    package_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    if final_review_decision.get("schema_version") != "p7.auto_mode_final_review_decision.v1":
        reasons.append("final_review_decision_missing_or_invalid_schema")
    if final_review_decision.get("status") != "approved_for_formal_promotion_preflight":
        reasons.append("final_review_decision_not_approved_for_preflight")
    if final_review_decision.get("decision") != "approve":
        reasons.append("final_review_decision_not_approve")
    if final_review_decision.get("route") != "formal_promotion_preflight":
        reasons.append("final_review_route_not_formal_promotion_preflight")
    if final_review_decision.get("approved") is not True:
        reasons.append("final_review_decision_not_approved")
    if final_review_decision.get("promotion", {}).get("allowed") is not True:
        reasons.append("final_review_promotion_not_allowed")
    if final_review_decision.get("formal_writeback_allowed") is True:
        reasons.append("final_review_decision_already_allows_formal_writeback")
    if final_review_decision.get("can_write_product_state") is True:
        reasons.append("final_review_decision_allows_product_state_write")
    reasons.extend(missing_human_metadata_reasons(final_review_decision))

    if final_review_packet.get("schema_version") != "p7.auto_mode_final_review_packet.v1":
        reasons.append("final_review_packet_missing_or_invalid_schema")
    if final_review_packet.get("status") != "awaiting_human_final_review":
        reasons.append("final_review_packet_not_awaiting_review")
    if final_review_packet.get("can_request_final_decision") is not True:
        reasons.append("final_review_packet_cannot_request_decision")

    if package_manifest.get("schema_version") != "p6.cgss_paper_package.v1":
        reasons.append("paper_package_manifest_missing_or_invalid_schema")
    if package_manifest.get("status") != "needs_human_paper_package_review":
        reasons.append("paper_package_not_ready_for_review")
    if package_manifest.get("missing_targets"):
        reasons.append("paper_package_manifest_has_missing_targets")
    return reasons


def missing_human_metadata_reasons(final_review_decision: dict[str, Any]) -> list[str]:
    if final_review_decision.get("approved") is not True:
        return []
    reasons = []
    if not str(final_review_decision.get("reviewer", "")).strip():
        reasons.append("reviewer_required")
    if not str(final_review_decision.get("note", "")).strip():
        reasons.append("decision_note_required")
    return reasons


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "ready_for_formal_writeback_approval"
    if any(reason.startswith("paper_package") for reason in blocking_reasons):
        return "blocked_by_package_manifest"
    return "blocked_by_final_review_decision"


def build_source_decision(final_review_decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": final_review_decision.get("schema_version", ""),
        "status": final_review_decision.get("status", ""),
        "decision": final_review_decision.get("decision", ""),
        "route": final_review_decision.get("route", ""),
        "approved": final_review_decision.get("approved") is True,
        "reviewer": final_review_decision.get("reviewer", ""),
        "promotion_allowed": final_review_decision.get("promotion", {}).get("allowed") is True,
    }


def build_source_packet(final_review_packet: dict[str, Any]) -> dict[str, Any]:
    evidence = final_review_packet.get("evidence_summary", {})
    return {
        "schema_version": final_review_packet.get("schema_version", ""),
        "status": final_review_packet.get("status", ""),
        "can_request_final_decision": final_review_packet.get("can_request_final_decision") is True,
        "component_count": evidence.get("component_count", 0),
        "method_recommended_check_count": evidence.get("method_recommended_check_count", 0),
        "statistical_contract_ready_result_count": evidence.get("statistical_contract_ready_result_count", 0),
        "required_review_item_count": len(final_review_packet.get("required_review_items", [])),
    }


def build_package_summary(package_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": package_manifest.get("schema_version", ""),
        "status": package_manifest.get("status", ""),
        "package_dir": package_manifest.get("package_dir", ""),
        "file_count": len(package_manifest.get("files", [])),
        "missing_targets": package_manifest.get("missing_targets", []),
    }


def build_promotion_scope(package_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    files = package_manifest.get("files", [])
    return [
        build_scope_item(
            "manuscript",
            "Manuscript draft and rendered paper",
            files,
            {"paper.md", "paper.pdf"},
            ["formal_manuscript_sources", "formal_pdf_candidate_preflight"],
        ),
        build_scope_item(
            "bibliography",
            "Candidate bibliography and literature packet",
            files,
            {"literature_review_packet.json", "paper.md"},
            ["verified_bibliography_preflight", "citation_binding_review"],
        ),
        build_scope_item(
            "method_review",
            "Method gate and Method KB review evidence",
            files,
            {"method_gate.md", "reviewer_report.md"},
            ["method_gate_human_approval"],
        ),
        build_scope_item(
            "statistical_results",
            "Results evidence and statistical contract",
            files,
            {"results_evidence_package.json"},
            ["statistical_results_formalization_preflight"],
        ),
        build_scope_item(
            "reproducibility",
            "Reproducibility README and package manifest",
            files,
            {"reproducibility_readme.md", "manifest.json"},
            ["reproducibility_preflight"],
        ),
        build_scope_item(
            "package_artifacts",
            "Package-level review outputs",
            files,
            {"paper.pdf", "revision_task_queue.md", "reviewer_report.md"},
            ["submission_package_preflight"],
        ),
    ]


def build_scope_item(
    category: str,
    label: str,
    files: list[dict[str, Any]],
    targets: set[str],
    next_gates: list[str],
) -> dict[str, Any]:
    evidence_refs = [
        {"target": item.get("target", ""), "kind": item.get("kind", "")}
        for item in files
        if item.get("target") in targets
    ]
    return {
        "category": category,
        "label": label,
        "evidence_refs": evidence_refs,
        "approval_status": "pending_formal_writeback_approval",
        "requires_human_confirmation": True,
        "can_write_formal_state": False,
        "next_gates": next_gates,
    }


def build_approval_contract(ready: bool) -> dict[str, Any]:
    return {
        "ready_for_formal_writeback_approval": ready,
        "required_next_decision": "human_approve_auto_mode_formal_writeback",
        "approval_record_path": "Results/json/auto_mode_formal_writeback_approval.json",
        "approval_review_path": "Reviews/auto_mode_formal_writeback_approval.md",
        "writeback_policy": "P7-J only permits a later approval request; it does not write formal research state.",
    }


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
    }


def build_next_action(ready: bool, blocking_reasons: list[str]) -> dict[str, Any]:
    if ready:
        return {
            "id": "record_auto_mode_formal_writeback_approval",
            "label": "Record separate formal writeback approval",
            "description": "Human approval of the final review packet is present; a separate writeback approval gate is still required.",
        }
    return {
        "id": "obtain_human_final_review_approval",
        "label": "Wait for human final review approval",
        "description": "The package cannot request formal writeback approval until the final review decision is approve.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_promotion_preflight_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_REPORT_PATH,
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
        "# Auto Mode Formal Promotion Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求正式写回审批：{str(report['can_request_formal_writeback_approval']).lower()}",
        f"- 需要单独正式写回审批：{str(report['requires_separate_formal_writeback_approval']).lower()}",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
        "- 渲染 PDF/DOCX：否",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Promotion Scope"])
    if report["promotion_scope"]:
        for item in report["promotion_scope"]:
            lines.append(f"- `{item['category']}`: {item['approval_status']}")
    else:
        lines.append("- 无；等待前置人工批准。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"
