from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_acceptance_chain.v1"
DEFAULT_DATASET_INDEX_PATH = Path("Results/json/dataset_motherlode_index.json")
DEFAULT_LITERATURE_SEED_PATH = Path("Results/json/literature_discovery_seed.json")
DEFAULT_LEVEL3_GATE_PATH = Path("Results/json/level3_manuscript_quality_gate.json")
DEFAULT_METHOD_KB_PATH = Path("Results/json/method_knowledge_base.json")
DEFAULT_STATISTICAL_CONTRACT_PATH = Path("Results/json/statistical_adapter_contract.json")
DEFAULT_REPORT_PATH = Path("Results/json/auto_mode_acceptance_chain.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_acceptance_chain.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_acceptance_chain(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
    source_paths: dict[str, str] | None = None,
    method_knowledge_base: dict[str, Any] | None = None,
    statistical_adapter_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    method_knowledge_base = method_knowledge_base or {}
    statistical_adapter_contract = statistical_adapter_contract or {}
    missing_inputs = missing_required_inputs(
        dataset_index,
        literature_seed,
        level3_gate,
        method_knowledge_base,
        statistical_adapter_contract,
    )
    component_statuses = build_component_statuses(
        dataset_index,
        literature_seed,
        level3_gate,
        method_knowledge_base,
        statistical_adapter_contract,
        source_paths,
    )
    artifact_layers = build_artifact_layers(level3_gate, source_paths)
    method_readiness = build_method_readiness(method_knowledge_base)
    statistical_readiness = build_statistical_readiness(statistical_adapter_contract)
    boundary_flags = {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "modified_canonical_method_rules": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
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
            "method_readiness": method_readiness,
            "statistical_readiness": statistical_readiness,
            "repair_queue": build_missing_input_repair_queue(missing_inputs),
            "human_review_checklist": [],
            "boundary_flags": boundary_flags,
        }

    repair_queue = (
        build_repair_queue(level3_gate)
        + build_method_repair_queue(method_readiness)
        + build_statistical_repair_queue(statistical_readiness)
    )
    if repair_queue:
        status = "needs_auto_mode_repair"
        package_readiness = "needs_auto_mode_repair"
    elif (
        level3_gate.get("ready_for_level3_review")
        and method_readiness["ready_for_human_review"]
        and statistical_readiness["ready_for_human_review"]
    ):
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
        "method_readiness": method_readiness,
        "statistical_readiness": statistical_readiness,
        "repair_queue": repair_queue,
        "human_review_checklist": build_human_review_checklist(
            dataset_index,
            literature_seed,
            level3_gate,
            method_knowledge_base,
            statistical_adapter_contract,
        ),
        "boundary_flags": boundary_flags,
    }


def missing_required_inputs(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
    method_knowledge_base: dict[str, Any],
    statistical_adapter_contract: dict[str, Any],
) -> list[str]:
    missing = []
    if dataset_index.get("schema_version") != "p7.dataset_motherlode_index.v1":
        missing.append("dataset_motherlode_index")
    if literature_seed.get("schema_version") != "p7.literature_discovery_seed.v1":
        missing.append("literature_discovery_seed")
    if level3_gate.get("schema_version") != "p7.level3_manuscript_quality_gate.v1":
        missing.append("level3_manuscript_quality_gate")
    if method_knowledge_base.get("schema_version") != "p7.method_knowledge_base.v1":
        missing.append("method_knowledge_base")
    if statistical_adapter_contract.get("schema_version") != "p7.statistical_adapter_contract.v1":
        missing.append("statistical_adapter_contract")
    return missing


def build_component_statuses(
    dataset_index: dict[str, Any],
    literature_seed: dict[str, Any],
    level3_gate: dict[str, Any],
    method_knowledge_base: dict[str, Any],
    statistical_adapter_contract: dict[str, Any],
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
        {
            "component": "method_knowledge_base",
            "schema_version": method_knowledge_base.get("schema_version", ""),
            "status": method_knowledge_base.get("status", "missing"),
            "path": source_paths.get("method_knowledge_base", str(DEFAULT_METHOD_KB_PATH)),
        },
        {
            "component": "statistical_adapter_contract",
            "schema_version": statistical_adapter_contract.get("schema_version", ""),
            "status": statistical_adapter_contract.get("status", "missing"),
            "path": source_paths.get("statistical_adapter_contract", str(DEFAULT_STATISTICAL_CONTRACT_PATH)),
        },
    ]


def build_artifact_layers(level3_gate: dict[str, Any], source_paths: dict[str, str]) -> dict[str, list[str]]:
    artifact_check = level3_gate.get("artifact_check", {})
    return {
        "real_run_artifacts": append_unique(
            artifact_check.get("real_run_artifacts", []),
            Path(source_paths.get("statistical_adapter_contract", str(DEFAULT_STATISTICAL_CONTRACT_PATH))).name,
        ),
        "draft_layer_artifacts": append_unique(
            artifact_check.get("draft_layer_artifacts", []),
            Path(source_paths.get("method_knowledge_base", str(DEFAULT_METHOD_KB_PATH))).name,
        ),
        "human_review_required": append_unique(
            artifact_check.get("human_review_required", []),
            "method_knowledge_base.md",
            "statistical_adapter_contract.md",
        ),
    }


def append_unique(items: list[str], *extra_items: str) -> list[str]:
    merged = list(items)
    for item in extra_items:
        if item and item not in merged:
            merged.append(item)
    return merged


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


def build_missing_input_repair_queue(missing_inputs: list[str]) -> list[dict[str, str]]:
    routes = {
        "dataset_motherlode_index": ("build_dataset_motherlode_index", "DataAgent"),
        "literature_discovery_seed": ("build_literature_discovery_seed", "LiteratureAgent"),
        "level3_manuscript_quality_gate": ("repair_level3_quality_gate", "SupervisorAgent"),
        "method_knowledge_base": ("build_method_knowledge_base", "MethodAgent"),
        "statistical_adapter_contract": ("build_statistical_adapter_contract", "ExecutionAgent"),
    }
    queue = []
    for missing in missing_inputs:
        task_id, owner_agent = routes.get(missing, (f"build_{missing}", "SupervisorAgent"))
        queue.append(
            {
                "task_id": task_id,
                "source_component": missing,
                "owner_agent": owner_agent,
                "required_before": "needs_human_final_review",
            }
        )
    return queue


def build_method_repair_queue(method_readiness: dict[str, Any]) -> list[dict[str, str]]:
    if method_readiness["ready_for_human_review"]:
        return []
    task_id = "repair_method_knowledge_base_policy" if method_readiness["proposal_rules_can_block"] else "build_method_knowledge_base"
    return [
        {
            "task_id": task_id,
            "source_component": "method_knowledge_base",
            "owner_agent": "MethodAgent",
            "required_before": "needs_human_final_review",
        }
    ]


def build_statistical_repair_queue(statistical_readiness: dict[str, Any]) -> list[dict[str, str]]:
    if statistical_readiness["ready_for_human_review"]:
        return []
    task_id = (
        "repair_statistical_adapter_contract"
        if statistical_readiness["schema_version"] == "p7.statistical_adapter_contract.v1"
        else "build_statistical_adapter_contract"
    )
    return [
        {
            "task_id": task_id,
            "source_component": "statistical_adapter_contract",
            "owner_agent": "ExecutionAgent",
            "required_before": "needs_human_final_review",
        }
    ]


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
    method_knowledge_base: dict[str, Any],
    statistical_adapter_contract: dict[str, Any],
) -> list[str]:
    checklist = []
    if dataset_index.get("status"):
        checklist.append("review_dataset_motherlode_candidates")
    if literature_seed.get("status"):
        checklist.append("review_literature_discovery_seed")
    if level3_gate.get("status"):
        checklist.append("review_level3_quality_gate")
    if method_knowledge_base.get("status"):
        checklist.append("review_method_knowledge_base")
    if statistical_adapter_contract.get("status"):
        checklist.append("review_statistical_adapter_contract")
    checklist.append("decide_formal_promotion_or_auto_mode_repair")
    return checklist


def build_method_readiness(method_knowledge_base: dict[str, Any]) -> dict[str, Any]:
    policy = method_knowledge_base.get("formal_export_policy", {})
    source_summary = method_knowledge_base.get("source_summary", {})
    proposal_rules_can_block = bool(policy.get("proposal_rules_can_block"))
    ready_for_human_review = (
        method_knowledge_base.get("schema_version") == "p7.method_knowledge_base.v1"
        and method_knowledge_base.get("status") == "needs_human_method_kb_review"
        and not proposal_rules_can_block
    )
    return {
        "schema_version": method_knowledge_base.get("schema_version", ""),
        "status": method_knowledge_base.get("status", "missing"),
        "recommended_check_count": len(method_knowledge_base.get("recommended_checks", [])),
        "proposal_source_count": source_summary.get("proposal_source_count", 0),
        "canonical_rule_count": source_summary.get("canonical_rule_count", 0),
        "reviewed_canonical_blocking_rule_count": policy.get(
            "reviewed_canonical_blocking_rule_count",
            source_summary.get("reviewed_canonical_blocking_rule_count", 0),
        ),
        "proposal_rules_can_block": proposal_rules_can_block,
        "ready_for_human_review": ready_for_human_review,
    }


def build_statistical_readiness(statistical_adapter_contract: dict[str, Any]) -> dict[str, Any]:
    capability_matrix = statistical_adapter_contract.get("capability_matrix", {})
    normalized_results = statistical_adapter_contract.get("normalized_results", [])
    contract_ready_result_count = sum(
        int(item.get("contract_ready_count", 0))
        for item in capability_matrix.values()
        if isinstance(item, dict)
    )
    if not capability_matrix:
        contract_ready_result_count = sum(
            1 for item in normalized_results if item.get("status") == "contract_ready"
        )
    observed_methods = sorted(
        method_id
        for method_id, item in capability_matrix.items()
        if isinstance(item, dict) and item.get("result_count", 0) > 0
    )
    if not observed_methods:
        observed_methods = sorted(
            {item.get("method_id") for item in normalized_results if item.get("method_id")}
        )
    ready_for_human_review = (
        statistical_adapter_contract.get("schema_version") == "p7.statistical_adapter_contract.v1"
        and statistical_adapter_contract.get("status") == "needs_human_statistical_adapter_review"
        and contract_ready_result_count > 0
    )
    return {
        "schema_version": statistical_adapter_contract.get("schema_version", ""),
        "status": statistical_adapter_contract.get("status", "missing"),
        "normalized_result_count": len(normalized_results),
        "contract_ready_result_count": contract_ready_result_count,
        "observed_methods": observed_methods,
        "ready_for_human_review": ready_for_human_review,
    }


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
    lines.extend(
        [
            "",
            "## Method Knowledge Base",
            f"- 状态：{report['method_readiness']['status']}",
            f"- 推荐检查数：{report['method_readiness']['recommended_check_count']}",
            f"- Proposal rules can block：{report['method_readiness']['proposal_rules_can_block']}",
            f"- Reviewed canonical blocking rules：{report['method_readiness']['reviewed_canonical_blocking_rule_count']}",
            "",
            "## Statistical Adapter Contract",
            f"- 状态：{report['statistical_readiness']['status']}",
            f"- Normalized results：{report['statistical_readiness']['normalized_result_count']}",
            f"- Contract-ready results：{report['statistical_readiness']['contract_ready_result_count']}",
            f"- Observed methods：{', '.join(report['statistical_readiness']['observed_methods']) or '无'}",
        ]
    )
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
