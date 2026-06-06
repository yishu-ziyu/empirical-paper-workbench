from __future__ import annotations

import json
import os
import re
import tomllib
from pathlib import Path
from typing import Any


AERS_SOURCE_URL = "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills"
AERS_LICENSE = "CC-BY-SA-4.0"
AERS_DEFAULT_PATH = Path(
    os.environ.get(
        "AERS_SKILLS_PATH",
        "/Users/mahaoxuan/Desktop/经济学论文/Auto-Empirical-Research-Skills",
    )
)
AERS_PROPOSAL_PATH = "Program/methodology/proposals/auto-empirical-research-skills/"


def _catalog_path(source_path: Path) -> Path:
    return source_path / "catalog" / "skills.json"


def _load_catalog(source_path: Path) -> dict[str, Any] | None:
    catalog_path = _catalog_path(source_path)
    if not catalog_path.exists():
        return None
    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _load_toml(path: Path) -> dict[str, Any] | None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return normalized or "unknown"


def _status_for_collection(collection: dict[str, Any]) -> str:
    collection_id = str(collection.get("id", "")).lower()
    primary = collection.get("primary_skill") or {}
    name = str(primary.get("name", "")).lower()
    description = str(primary.get("description", "")).lower()
    text = " ".join([collection_id, name, description])
    if "full-empirical-analysis" in collection_id:
        return "template"
    if "aer" in text or "replication" in text or "robustness" in text:
        return "checklist"
    if "agent" in text or "reviewer" in text or "supervisor" in text:
        return "role_prompt"
    return "advisory"


def _category_for_collection(collection: dict[str, Any]) -> str:
    collection_id = str(collection.get("id", "")).lower()
    primary = collection.get("primary_skill") or {}
    text = " ".join(
        [
            collection_id,
            str(primary.get("name", "")).lower(),
            str(primary.get("description", "")).lower(),
        ]
    )
    if "full-empirical-analysis" in collection_id or "pipeline" in text:
        return "full_empirical_pipeline"
    if "aer" in text:
        return "journal_standard"
    if "stata" in text:
        return "stata_methodology"
    if "statspai" in text:
        return "statspai_methodology"
    if "paper" in text or "manuscript" in text or "writing" in text:
        return "manuscript_methodology"
    return "methodology_skill"


def _risk_for_status(status: str) -> str:
    if status == "checklist":
        return "medium"
    if status in {"template", "role_prompt"}:
        return "medium"
    return "low"


def _risk_for_severity(severity: str) -> str:
    if severity.lower() in {"critical", "high"}:
        return "high"
    if severity.lower() in {"medium", "moderate"}:
        return "medium"
    return "low"


def _quality_gate_summary(source_path: Path) -> dict[str, int]:
    eval_count = len(list((source_path / "eval-harness" / "scenarios").glob("*.toml")))
    benchmark_count = len(list((source_path / "benchmark" / "tasks").glob("*.toml")))
    return {
        "eval_scenarios": eval_count,
        "benchmark_tasks": benchmark_count,
        "total": eval_count + benchmark_count,
    }


def build_aers_methodology_policy() -> dict[str, Any]:
    return {
        "source": "auto_empirical_research_skills",
        "proposal_path": AERS_PROPOSAL_PATH,
        "auto_mode": {
            "can_generate_patch_proposal": True,
            "can_write_canonical": False,
            "proposal_status": "needs_human_review",
        },
        "hard_constraints": [
            "canonical_rules_require_manual_review",
            "external_skill_content_must_keep_attribution",
            "skills_are_not_executable_without_a_local_adapter",
        ],
    }


def get_aers_source_info(source_path: Path | None = None) -> dict[str, Any]:
    target_path = (source_path or AERS_DEFAULT_PATH).expanduser()
    catalog = _load_catalog(target_path)
    base = {
        "available": bool(catalog),
        "path": str(target_path),
        "source_url": AERS_SOURCE_URL,
        "license": AERS_LICENSE,
        "license_obligations": [
            "Attribution",
            "ShareAlike",
            "Link to license",
            "Indicate changes",
        ],
        "canonical_policy": {
            "mode": "proposal_only_until_human_review",
            "auto_write_canonical": False,
            "proposal_path": AERS_PROPOSAL_PATH,
        },
    }
    if catalog is None:
        return {
            **base,
            "reason": "catalog_not_found",
            "summary": {
                "skill_files": 0,
                "top_level_collections": 0,
                "quality_gates": _quality_gate_summary(target_path),
            },
        }
    summary = dict(catalog.get("summary", {}))
    summary["quality_gates"] = _quality_gate_summary(target_path)
    return {
        **base,
        "schema_version": catalog.get("schema_version", "unknown"),
        "summary": summary,
    }


def index_aers_capabilities(source_path: Path | None = None) -> list[dict[str, Any]]:
    target_path = (source_path or AERS_DEFAULT_PATH).expanduser()
    catalog = _load_catalog(target_path)
    if catalog is None:
        return []

    capabilities: list[dict[str, Any]] = []
    for collection in catalog.get("collections", []):
        if not isinstance(collection, dict):
            continue
        primary = collection.get("primary_skill") or {}
        if not isinstance(primary, dict):
            primary = {}
        collection_id = str(collection.get("id") or primary.get("name") or "unknown")
        skill_path = str(primary.get("path") or collection.get("path") or "")
        status = _status_for_collection(collection)
        capabilities.append(
            {
                "id": f"cap_aers_{_slug(collection_id)}",
                "namespace": "external_skill",
                "name": str(primary.get("name") or collection_id),
                "category": _category_for_collection(collection),
                "description": str(primary.get("description") or ""),
                "risk_level": _risk_for_status(status),
                "cost_model": "llm_tokens_and_local_files",
                "allowed_roles": [
                    "supervisor",
                    "methodology_agent",
                    "reviewer_agent",
                    "manuscript_agent",
                    "execution_agent",
                ],
                "adapter_path": f"external://{skill_path}" if skill_path else "external://",
                "input_schema": {"type": "object", "properties": {}},
                "output_schema": {"type": "object", "properties": {}},
                "status": status,
                "external_source": {
                    "name": "Auto-Empirical Research Skills",
                    "path": str(target_path),
                    "collection_id": collection_id,
                    "collection_path": str(collection.get("path", "")),
                    "skill_path": skill_path,
                    "source_url": collection.get("source_url") or AERS_SOURCE_URL,
                    "license": collection.get("license") or f"{AERS_LICENSE} (repository default)",
                    "commercial_use": collection.get("commercial_use", "share-alike"),
                    "source_confidence": collection.get("source_confidence", "unknown"),
                    "skill_count": collection.get("skill_count", 0),
                },
                "canonical_policy": build_aers_methodology_policy(),
            }
        )
    return capabilities


def index_aers_quality_gates(source_path: Path | None = None) -> list[dict[str, Any]]:
    target_path = (source_path or AERS_DEFAULT_PATH).expanduser()
    if not _catalog_path(target_path).exists():
        return []

    capabilities: list[dict[str, Any]] = []
    scenario_dir = target_path / "eval-harness" / "scenarios"
    for scenario_path in sorted(scenario_dir.glob("*.toml")):
        scenario = _load_toml(scenario_path)
        if scenario is None:
            continue
        scenario_id = str(scenario.get("id") or scenario_path.stem)
        title = str(scenario.get("title") or scenario_id)
        severity = str(scenario.get("severity") or "medium")
        rubric = scenario.get("rubric") if isinstance(scenario.get("rubric"), list) else []
        manual_count = sum(1 for item in rubric if isinstance(item, dict) and item.get("check") == "manual")
        machine_count = sum(1 for item in rubric if isinstance(item, dict) and item.get("check") != "manual")
        required_count = sum(1 for item in rubric if isinstance(item, dict) and item.get("required") is True)
        relative_path = scenario_path.relative_to(target_path)
        capabilities.append(
            {
                "id": f"cap_aers_eval_{_slug(scenario_id)}",
                "namespace": "external_skill",
                "name": title,
                "category": "evaluation_gate",
                "description": str(scenario.get("prompt") or title).strip()[:280],
                "risk_level": _risk_for_severity(severity),
                "cost_model": "llm_review_and_local_checks",
                "allowed_roles": [
                    "supervisor",
                    "methodology_agent",
                    "reviewer_agent",
                    "execution_agent",
                ],
                "adapter_path": f"external://{relative_path.as_posix()}",
                "input_schema": {"type": "object", "properties": {}},
                "output_schema": {"type": "object", "properties": {}},
                "status": "checklist",
                "external_source": {
                    "name": "Auto-Empirical Research Skills",
                    "path": str(target_path),
                    "source_file": relative_path.as_posix(),
                    "source_url": AERS_SOURCE_URL,
                    "license": AERS_LICENSE,
                    "source_confidence": "high",
                },
                "canonical_policy": build_aers_methodology_policy(),
                "quality_gate": {
                    "gate_type": "eval_scenario",
                    "scenario_id": scenario_id,
                    "skill": scenario.get("skill", ""),
                    "category": scenario.get("category", ""),
                    "severity": severity,
                    "rubric_count": len(rubric),
                    "required_rubric_count": required_count,
                    "machine_checkable_count": machine_count,
                    "manual_count": manual_count,
                    "source_file": relative_path.as_posix(),
                },
            }
        )

    benchmark_dir = target_path / "benchmark" / "tasks"
    for task_path in sorted(benchmark_dir.glob("*.toml")):
        task = _load_toml(task_path)
        if task is None:
            continue
        task_id = str(task.get("id") or task_path.stem)
        title = str(task.get("title") or task_id)
        gold = task.get("gold") if isinstance(task.get("gold"), list) else []
        required_count = sum(1 for item in gold if isinstance(item, dict) and item.get("required") is True)
        relative_path = task_path.relative_to(target_path)
        capabilities.append(
            {
                "id": f"cap_aers_benchmark_{_slug(task_id)}",
                "namespace": "external_skill",
                "name": title,
                "category": "empirical_benchmark",
                "description": str(task.get("description") or title).strip()[:280],
                "risk_level": "medium",
                "cost_model": "local_python_and_fixture_data",
                "allowed_roles": [
                    "supervisor",
                    "methodology_agent",
                    "execution_agent",
                    "reviewer_agent",
                ],
                "adapter_path": f"external://{relative_path.as_posix()}",
                "input_schema": {"type": "object", "properties": {}},
                "output_schema": {"type": "object", "properties": {}},
                "status": "checklist",
                "external_source": {
                    "name": "Auto-Empirical Research Skills",
                    "path": str(target_path),
                    "source_file": relative_path.as_posix(),
                    "source_url": AERS_SOURCE_URL,
                    "license": AERS_LICENSE,
                    "source_confidence": "high",
                },
                "canonical_policy": build_aers_methodology_policy(),
                "quality_gate": {
                    "gate_type": "benchmark_task",
                    "task_id": task_id,
                    "data": task.get("data", ""),
                    "reference_candidate": task.get("reference_candidate", ""),
                    "gold_count": len(gold),
                    "required_gold_count": required_count,
                    "checks": [
                        item.get("check")
                        for item in gold
                        if isinstance(item, dict) and item.get("check")
                    ],
                    "source_file": relative_path.as_posix(),
                },
            }
        )

    return capabilities
