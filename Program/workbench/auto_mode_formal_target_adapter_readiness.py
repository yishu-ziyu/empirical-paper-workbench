from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_readiness.v1"
APPLY_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_writeback_apply_manifest.v1"
PACKAGE_MANIFEST_SCHEMA_VERSION = "p6.cgss_paper_package.v1"
DEFAULT_APPLY_MANIFEST_PATH = Path("workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json")
DEFAULT_PACKAGE_MANIFEST_PATH = Path("workspace/paper_packages/cgss_social_capital_happiness/manifest.json")
DEFAULT_REPORT_PATH = Path("Results/json/auto_mode_formal_target_adapter_readiness.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_readiness.md")
DEFAULT_TARGET_ROOT = Path("Submissions/auto_mode")


TARGET_GROUP_CONTRACTS = {
    "formal_manuscript_sources": {
        "adapter_id": "formal_manuscript_sources_adapter",
        "label": "Formal manuscript sources",
        "source_targets": ["paper.md"],
        "candidate_targets": ["manuscript/paper.md"],
    },
    "formal_bibliography_sources": {
        "adapter_id": "formal_bibliography_sources_adapter",
        "label": "Formal bibliography sources",
        "source_targets": ["literature_review_packet.json"],
        "candidate_targets": ["bibliography/literature_review_packet.json"],
    },
    "method_review_records": {
        "adapter_id": "method_review_records_adapter",
        "label": "Method review records",
        "source_targets": ["method_gate.md", "reviewer_report.md", "revision_task_queue.md"],
        "candidate_targets": ["reviews/method_gate.md", "reviews/reviewer_report.md", "reviews/revision_task_queue.md"],
    },
    "statistical_result_records": {
        "adapter_id": "statistical_result_records_adapter",
        "label": "Statistical result records",
        "source_targets": ["results_evidence_package.json"],
        "candidate_targets": ["evidence/results_evidence_package.json"],
    },
    "reproducibility_records": {
        "adapter_id": "reproducibility_records_adapter",
        "label": "Reproducibility records",
        "source_targets": ["reproducibility_readme.md"],
        "candidate_targets": ["reproducibility/reproducibility_readme.md"],
    },
    "formal_package_records": {
        "adapter_id": "formal_package_records_adapter",
        "label": "Formal package records",
        "source_targets": ["manifest.json", "paper.pdf"],
        "candidate_targets": ["manifest.json", "paper.pdf"],
    },
}
REQUIRED_TARGET_GROUPS = tuple(TARGET_GROUP_CONTRACTS.keys())


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_readiness(
    project_root: Path,
    apply_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
    *,
    target_root: Path = DEFAULT_TARGET_ROOT,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    apply_reasons = build_apply_manifest_blocking_reasons(apply_manifest)
    boundary_reasons = build_boundary_blocking_reasons(apply_manifest)
    package_reasons = build_package_manifest_blocking_reasons(project_root, package_manifest)
    mapping_reasons = build_mapping_blocking_reasons(project_root, apply_manifest, package_manifest)
    blocking_reasons = boundary_reasons + apply_reasons + package_reasons + mapping_reasons
    status = build_status(boundary_reasons, apply_reasons, package_reasons, mapping_reasons)
    ready = status == "ready_for_formal_target_adapter_review"
    adapter_mappings = (
        build_adapter_mappings(project_root, apply_manifest, package_manifest, target_root)
        if ready
        else []
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": apply_manifest.get("topic") or package_manifest.get("topic", ""),
        "source_paths": {
            "apply_manifest": source_paths.get("apply_manifest", str(DEFAULT_APPLY_MANIFEST_PATH)),
            "package_manifest": source_paths.get("package_manifest", str(DEFAULT_PACKAGE_MANIFEST_PATH)),
        },
        "status": status,
        "can_request_target_adapter_execution": ready,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_apply_manifest": build_source_apply_manifest(apply_manifest),
        "source_package_manifest": build_source_package_manifest(project_root, package_manifest),
        "required_target_groups": list(REQUIRED_TARGET_GROUPS),
        "adapter_mappings": adapter_mappings,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_apply_manifest_blocking_reasons(apply_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if apply_manifest.get("schema_version") != APPLY_MANIFEST_SCHEMA_VERSION:
        reasons.append("apply_manifest_missing_or_invalid_schema")
    if apply_manifest.get("formal_writeback_executed") is True:
        reasons.append("apply_manifest_already_executed_formal_writeback")
    if apply_manifest.get("formal_target_adapters_executed") is True:
        reasons.append("apply_manifest_already_executed_target_adapters")
    if not apply_manifest.get("operations"):
        reasons.append("apply_manifest_operations_missing")
    return reasons


def build_boundary_blocking_reasons(apply_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    for flag, value in apply_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"apply_manifest_boundary_violation:{flag}")
    return reasons


def build_package_manifest_blocking_reasons(project_root: Path, package_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if package_manifest.get("schema_version") != PACKAGE_MANIFEST_SCHEMA_VERSION:
        reasons.append("package_manifest_missing_or_invalid_schema")
    package_dir = package_manifest.get("package_dir", "")
    if not package_dir:
        reasons.append("package_manifest_package_dir_missing")
    if package_dir and not (project_root / package_dir).exists():
        reasons.append("package_dir_missing")
    return reasons


def build_mapping_blocking_reasons(
    project_root: Path,
    apply_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
) -> list[str]:
    if apply_manifest.get("schema_version") != APPLY_MANIFEST_SCHEMA_VERSION:
        return []
    reasons = []
    groups = [operation.get("writeback_target_group", "") for operation in apply_manifest.get("operations", [])]
    for group in groups:
        if group not in TARGET_GROUP_CONTRACTS:
            reasons.append(f"unknown_writeback_target_group:{group}")
    for group in REQUIRED_TARGET_GROUPS:
        if group not in groups:
            reasons.append(f"writeback_target_group_missing:{group}")
    package_files = package_files_by_target(package_manifest)
    package_dir = package_manifest.get("package_dir", "")
    for group in groups:
        contract = TARGET_GROUP_CONTRACTS.get(group)
        if not contract:
            continue
        for target in contract["source_targets"]:
            if target not in package_files:
                reasons.append(f"package_artifact_not_declared:{target}")
                continue
            source_path = project_root / package_dir / target
            if not source_path.exists():
                reasons.append(f"package_artifact_missing:{target}")
    return dedupe(reasons)


def build_status(
    boundary_reasons: list[str],
    apply_reasons: list[str],
    package_reasons: list[str],
    mapping_reasons: list[str],
) -> str:
    if boundary_reasons:
        return "blocked_by_apply_manifest_boundary"
    if apply_reasons:
        return "blocked_by_apply_manifest"
    if package_reasons:
        return "blocked_by_package_manifest"
    if any(reason.startswith("package_artifact_") for reason in mapping_reasons):
        return "blocked_by_package_artifacts"
    if mapping_reasons:
        return "blocked_by_target_adapter_mapping"
    return "ready_for_formal_target_adapter_review"


def build_source_apply_manifest(apply_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": apply_manifest.get("schema_version", ""),
        "manifest_path": apply_manifest.get("manifest_path", ""),
        "source_execute_report": apply_manifest.get("source_execute_report", ""),
        "reviewer": apply_manifest.get("reviewer", ""),
        "operations_count": len(apply_manifest.get("operations", [])),
        "formal_writeback_executed": apply_manifest.get("formal_writeback_executed") is True,
        "formal_target_adapters_executed": apply_manifest.get("formal_target_adapters_executed") is True,
    }


def build_source_package_manifest(project_root: Path, package_manifest: dict[str, Any]) -> dict[str, Any]:
    package_dir = package_manifest.get("package_dir", "")
    return {
        "schema_version": package_manifest.get("schema_version", ""),
        "status": package_manifest.get("status", ""),
        "package_dir": package_dir,
        "package_dir_exists": bool(package_dir and (project_root / package_dir).exists()),
        "files_count": len(package_manifest.get("files", [])),
        "missing_targets": package_manifest.get("missing_targets", []),
        "draft_layer_only": package_manifest.get("draft_layer_only") is True,
        "formal_writeback_allowed": package_manifest.get("formal_writeback_allowed") is True,
    }


def build_adapter_mappings(
    project_root: Path,
    apply_manifest: dict[str, Any],
    package_manifest: dict[str, Any],
    target_root: Path,
) -> list[dict[str, Any]]:
    package_id = build_package_id(package_manifest)
    mappings = []
    for operation in apply_manifest.get("operations", []):
        group = operation.get("writeback_target_group", "")
        contract = TARGET_GROUP_CONTRACTS[group]
        mappings.append(
            {
                "operation_id": operation.get("operation_id", ""),
                "category": operation.get("category", ""),
                "writeback_target_group": group,
                "adapter_id": contract["adapter_id"],
                "adapter_label": contract["label"],
                "source_artifacts": build_source_artifacts(project_root, package_manifest, contract["source_targets"]),
                "candidate_targets": build_candidate_targets(project_root, target_root, package_id, contract["candidate_targets"]),
                "mapping_status": "ready_for_target_adapter",
                "requires_target_adapter_execution": True,
                "executed_by_this_command": False,
            }
        )
    return mappings


def build_source_artifacts(
    project_root: Path,
    package_manifest: dict[str, Any],
    source_targets: list[str],
) -> list[dict[str, Any]]:
    package_dir = package_manifest.get("package_dir", "")
    package_files = package_files_by_target(package_manifest)
    artifacts = []
    for target in source_targets:
        file_record = package_files.get(target, {})
        path = project_root / package_dir / target
        exists = path.exists()
        artifacts.append(
            {
                "target": target,
                "kind": file_record.get("kind", ""),
                "path": f"{package_dir}/{target}" if package_dir else target,
                "exists": exists,
                "bytes": path.stat().st_size if exists else None,
            }
        )
    return artifacts


def build_candidate_targets(
    project_root: Path,
    target_root: Path,
    package_id: str,
    candidate_targets: list[str],
) -> list[dict[str, Any]]:
    targets = []
    for relative_target in candidate_targets:
        path = target_root / package_id / relative_target
        targets.append(
            {
                "path": path.as_posix(),
                "exists": (project_root / path).exists(),
                "will_be_written_by_this_command": False,
            }
        )
    return targets


def build_package_id(package_manifest: dict[str, Any]) -> str:
    package_dir = package_manifest.get("package_dir", "")
    if package_dir:
        return Path(package_dir).name
    return "unknown_package"


def package_files_by_target(package_manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("target", ""): item
        for item in package_manifest.get("files", [])
        if item.get("target")
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
        "executed_target_adapters": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "ready_for_formal_target_adapter_review":
        return {
            "id": "review_target_adapter_mapping",
            "label": "Review target adapter mapping",
            "description": "Target adapter mapping is ready for review; a later node must execute any adapter writes.",
        }
    if status == "blocked_by_apply_manifest_boundary":
        return {
            "id": "repair_apply_manifest_boundary",
            "label": "Repair apply manifest boundary violation",
            "description": "The apply manifest reports a boundary violation and cannot feed target adapters.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_apply_manifest":
        return {
            "id": "record_formal_writeback_apply_manifest",
            "label": "Record formal writeback apply manifest",
            "description": "Run P7-M apply only after upstream approvals are ready.",
            "blocking_reasons": blocking_reasons,
        }
    if status in {"blocked_by_package_manifest", "blocked_by_package_artifacts"}:
        return {
            "id": "repair_package_manifest_inputs",
            "label": "Repair package manifest inputs",
            "description": "The package manifest and source artifacts must be complete before target mapping can be reviewed.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_target_adapter_contract",
        "label": "Repair target adapter contract",
        "description": "Unknown or missing target groups need explicit adapter contracts before execution.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_readiness_outputs(
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
        "# Auto Mode Formal Target Adapter Readiness",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求 target adapter 执行：{str(report['can_request_target_adapter_execution']).lower()}",
        f"- 已执行 target adapters：{str(report['formal_target_adapters_executed']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Adapter Mappings"])
    if report["adapter_mappings"]:
        for mapping in report["adapter_mappings"]:
            lines.append(
                f"- `{mapping['writeback_target_group']}` -> `{mapping['adapter_id']}`: {mapping['mapping_status']}"
            )
    else:
        lines.append("- 无；等待 apply manifest 和 package artifact ready。")
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
