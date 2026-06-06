from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id_or_transient
from Product.backend.auto_empirical_research_skills import (
    get_aers_source_info,
    index_aers_capabilities,
)
from Product.backend.reproducibility_skill_contract import build_reproducibility_product_capability
from Product.backend.statspai_adapter import get_statspai_info, index_statspai_capabilities


CAPABILITY_STATE_PATH = Path("state/product/capabilities.json")


def capability_state_path(project_root: Path) -> Path:
    return project_root / CAPABILITY_STATE_PATH


def load_saved_capabilities(project_root: Path) -> dict[str, Any] | None:
    path = capability_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_capabilities() -> dict[str, Any]:
    return {
        "id": "capability_registry",
        "version": 0,
        "status": "empty",
        "evidence_level": "local_file",
        "updated_at": utc_now(),
        "sources": {},
        "capabilities": [],
        "classification": {
            "advisory": [],
            "template": [],
            "role_prompt": [],
            "checklist": [],
            "executable": [],
        },
        "next_action": {
            "id": "reindex_capabilities",
            "label": "索引能力目录",
        },
    }


def _classify_capabilities(capabilities: list[dict[str, Any]]) -> dict[str, list[str]]:
    classification: dict[str, list[str]] = {
        "advisory": [],
        "template": [],
        "role_prompt": [],
        "checklist": [],
        "executable": [],
    }
    for cap in capabilities:
        status = cap.get("status", "advisory")
        if status in classification:
            classification[status].append(cap["id"])
    return classification


def reindex_capabilities(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    timestamp = utc_now()

    statspai_info = get_statspai_info()
    statspai_caps = index_statspai_capabilities()
    aers_info = get_aers_source_info()
    aers_caps = index_aers_capabilities()

    # Built-in capabilities (product actions)
    builtin_caps: list[dict[str, Any]] = [
        {
            "id": "cap_export_docx",
            "namespace": "product",
            "name": "export_docx",
            "category": "export",
            "description": "Export manuscript to Word/DOCX format",
            "risk_level": "low",
            "cost_model": "local_cpu_time",
            "allowed_roles": ["export_agent", "supervisor"],
            "adapter_path": "Product.backend.artifact_service.export_docx",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {"type": "object", "properties": {}},
            "status": "executable",
        },
        {
            "id": "cap_build_evidence",
            "namespace": "product",
            "name": "build_evidence",
            "category": "observability",
            "description": "Build evidence inventory from project files",
            "risk_level": "low",
            "cost_model": "local_cpu_time",
            "allowed_roles": ["supervisor", "data_agent"],
            "adapter_path": "Product.backend.evidence.build_evidence_inventory",
            "input_schema": {"type": "object", "properties": {}},
            "output_schema": {"type": "object", "properties": {}},
            "status": "executable",
        },
        build_reproducibility_product_capability(),
    ]

    all_capabilities = builtin_caps + statspai_caps + aers_caps
    classification = _classify_capabilities(all_capabilities)

    registry = {
        "id": "capability_registry",
        "version": 1,
        "status": "active",
        "evidence_level": "local_file",
        "updated_at": timestamp,
        "sources": {
            "statspai": {
                "path": str(statspai_info.get("path", "")),
                "version": str(statspai_info.get("version", "unknown")),
                "indexed_at": timestamp,
                "available": statspai_info.get("available", False),
                "function_count": len(statspai_caps),
            },
            "auto_empirical_research_skills": {
                "path": str(aers_info.get("path", "")),
                "source_url": aers_info.get("source_url", ""),
                "license": aers_info.get("license", "unknown"),
                "indexed_at": timestamp,
                "available": aers_info.get("available", False),
                "function_count": len(aers_caps),
                "summary": aers_info.get("summary", {}),
                "canonical_policy": aers_info.get("canonical_policy", {}),
            },
            "product": {
                "version": "1.0.0",
                "indexed_at": timestamp,
                "available": True,
                "function_count": len(builtin_caps),
            },
        },
        "capabilities": all_capabilities,
        "classification": classification,
        "next_action": {
            "id": "browse_capabilities",
            "label": "浏览能力目录",
        },
    }

    path = capability_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "capability_registry",
            "generated_at": timestamp,
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "capability": registry,
    }


def get_project_capabilities(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    capabilities = load_saved_capabilities(project_root)
    if not capabilities:
        capabilities = build_empty_capabilities()
    return {
        "_meta": {
            "evidence_level": capabilities.get("evidence_level", "local_file"),
            "service": "capability_registry",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "capability": capabilities,
    }


def find_capability_by_id(capabilities: list[dict[str, Any]], cap_id: str) -> dict[str, Any] | None:
    for cap in capabilities:
        if cap.get("id") == cap_id:
            return cap
    return None


def filter_capabilities(
    capabilities: list[dict[str, Any]],
    category: str | None = None,
    status: str | None = None,
    allowed_role: str | None = None,
) -> list[dict[str, Any]]:
    result = capabilities
    if category:
        result = [cap for cap in result if cap.get("category") == category]
    if status:
        result = [cap for cap in result if cap.get("status") == status]
    if allowed_role:
        result = [cap for cap in result if allowed_role in cap.get("allowed_roles", [])]
    return result


class CapabilityRegistryError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
