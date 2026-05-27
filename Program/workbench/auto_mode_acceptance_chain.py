from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_acceptance_chain.v1"
DEFAULT_DATASET_INDEX_PATH = Path("Results/json/dataset_motherlode_index.json")
DEFAULT_LITERATURE_SEED_PATH = Path("Results/json/literature_discovery_seed.json")
DEFAULT_LEVEL3_GATE_PATH = Path("Results/json/level3_manuscript_quality_gate.json")
DEFAULT_REPORT_PATH = Path("Results/json/auto_mode_acceptance_chain.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_acceptance_chain.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_acceptance_chain(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    missing_inputs = missing_required_inputs(dataset_index, literature_seed, level3_gate)
    component_statuses = build_component_statuses(dataset_index, literature_seed, level3_gate, source_paths)
    artifact_layers = build_artifact_layers(level3_gate)
    boundary_flags = {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_product_state": False,
    }
    if missing_inputs:
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "blocked_missing_acceptance_inputs",
            "package_readiness": "blocked",
            "missing_inputs": missing_inputs,
            "component_statuses": component_statuses,
            "artifact_layers": artifact_layers,
            "repair_queue": [],
            "human_review_checklist": [],
            "boundary_flags": boundary_flags,
        }

    repair_queue = build_repair_queue(level3_gate)
    if repair_queue:
        status = "needs_auto_mode_repair"
        package_readiness = "needs_auto_mode_repair"
    elif level3_gate.get("ready_for_level3_review"):
        status = "needs_human_final_review"
        package_readiness = "needs_human_final_review"
    else:
        status = "needs_auto_mode_repair"
        package_readiness = "needs_auto_mode_repair"

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "package_readiness": package_readiness,
        "missing_inputs": [],
        "component_statuses": component_statuses,
        "artifact_layers": artifact_layers,
        "repair_queue": repair_queue,
        "human_review_checklist": build_human_review_checklist(dataset_index, literature_seed, level3_gate),
        "boundary_flags": boundary_flags,
    }


def missing_required_inputs(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
) -> list[str]:
    missing = []
    if dataset_index.get("schema_version") != "p7.dataset_motherlode_index.v1":
        missing.append("dataset_motherlode_index")
    if literature_seed.get("schema_version") != "p7.literature_discovery_seed.v1":
        missing.append("literature_discovery_seed")
    if level3_gate.get("schema_version") != "p7.level3_manuscript_quality_gate.v1":
        missing.append("level3_manuscript_quality_gate")
    return missing


def build_component_statuses(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
    source_paths: dict[str, str],
) -> list[dict[str, str]]:
    return [
        {
            "component": "dataset_motherlode_index",
            "schema_version": dataset_index.get("schema_version", ""),
            "status": dataset_index.get("status", "missing"),
            "path": source_paths.get("dataset_index", str(DEFAULT_DATASET_INDEX_PATH)),
        },
        {
            "component": "literature_discovery_seed",
            "schema_version": literature_seed.get("schema_version", ""),
            "status": literature_seed.get("status", "missing"),
            "path": source_paths.get("literature_seed", str(DEFAULT_LITERATURE_SEED_PATH)),
        },
        {
            "component": "level3_manuscript_quality_gate",
            "schema_version": level3_gate.get("schema_version", ""),
            "status": level3_gate.get("status", "missing"),
            "path": source_paths.get("level3_gate", str(DEFAULT_LEVEL3_GATE_PATH)),
        },
    ]


def build_artifact_layers(level3_gate: dict[str, Any]) -> dict[str, list[str]]:
    artifact_check = level3_gate.get("artifact_check", {})
    return {
        "real_run_artifacts": artifact_check.get("real_run_artifacts", []),
        "draft_layer_artifacts": artifact_check.get("draft_layer_artifacts", []),
        "human_review_required": artifact_check.get("human_review_required", []),
    }


def build_repair_queue(level3_gate: dict[str, Any]) -> list[dict[str, str]]:
    if level3_gate.get("ready_for_level3_review"):
        return []
    queue = []
    for task in level3_gate.get("required_followup_tasks", []):
        queue.append(
            {
                "task_id": task,
                "source_component": "level3_manuscript_quality_gate",
                "owner_agent": route_task_owner(task),
                "required_before": "needs_human_final_review",
            }
        )
    if not queue:
        queue.append(
            {
                "task_id": "repair_level3_quality_gate",
                "source_component": "level3_manuscript_quality_gate",
                "owner_agent": "SupervisorAgent",
                "required_before": "needs_human_final_review",
            }
        )
    return queue


def route_task_owner(task_id: str) -> str:
    if "reference" in task_id or "citation" in task_id:
        return "LiteratureAgent"
    if "section" in task_id or "paper" in task_id:
        return "ManuscriptAgent"
    if "artifact" in task_id or "manifest" in task_id:
        return "SupervisorAgent"
    return "SupervisorAgent"


def build_human_review_checklist(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
) -> list[str]:
    checklist = []
    if dataset_index.get("status"):
        checklist.append("review_dataset_motherlode_candidates")
    if literature_seed.get("status"):
        checklist.append("review_literature_discovery_seed")
    if level3_gate.get("status"):
        checklist.append("review_level3_quality_gate")
    checklist.append("decide_formal_promotion_or_auto_mode_repair")
    return checklist


def write_report(project_root: Path, report: dict[str, Any], report_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Acceptance Chain",
        "",
        f"- 状态：{report['status']}",
        f"- Package readiness：{report['package_readiness']}",
        "- 正式论文写回：否",
        "- 正式 bibliography 写回：否",
        "- 正式 product state 写回：否",
        "",
        "## 组件状态",
    ]
    for item in report["component_statuses"]:
        lines.append(f"- `{item['component']}`: {item['status']} ({item['path']})")
    if report["missing_inputs"]:
        lines.extend(["", "## 缺失输入"])
        for item in report["missing_inputs"]:
            lines.append(f"- `{item}`")
    lines.extend(["", "## Repair Queue"])
    if report["repair_queue"]:
        for item in report["repair_queue"]:
            lines.append(f"- `{item['task_id']}` -> {item['owner_agent']}")
    else:
        lines.append("- 无自动修复阻断；等待人工 final review。")
    lines.extend(["", "## 人工审阅清单"])
    for item in report["human_review_checklist"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## 产物信任层"])
    for key, title in [
        ("real_run_artifacts", "真实运行产物"),
        ("draft_layer_artifacts", "草稿层产物"),
        ("human_review_required", "需要人工审阅"),
    ]:
        lines.append(f"- {title}: {', '.join(report['artifact_layers'][key]) or '无'}")
    return "\n".join(lines) + "\n"
