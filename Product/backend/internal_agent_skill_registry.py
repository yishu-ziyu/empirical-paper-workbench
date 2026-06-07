from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


INTERNAL_AGENT_SKILL_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "internal_skills" / "agent_skill_registry.json"
)
INTERNAL_AGENT_SKILL_PROPOSAL_PATH = "Program/methodology/proposals/internal-agent-skills/"


def _load_registry(registry_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not registry_path.exists():
        return None, "registry_not_found"
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "registry_unreadable"
    if not isinstance(payload, dict) or not isinstance(payload.get("skills"), list):
        return None, "registry_invalid"
    return payload, None


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return normalized or "unknown"


def _default_registry_path(registry_path: Path | None = None) -> Path:
    return (registry_path or INTERNAL_AGENT_SKILL_REGISTRY_PATH).expanduser()


def build_internal_agent_skill_policy() -> dict[str, Any]:
    return {
        "source": "internal_agent_skill_registry",
        "proposal_path": INTERNAL_AGENT_SKILL_PROPOSAL_PATH,
        "auto_mode": {
            "can_generate_patch_proposal": True,
            "can_write_canonical": False,
            "proposal_status": "needs_human_review",
        },
        "hard_constraints": [
            "internal_draft_requires_human_review_before_canonical",
            "formal_write_targets_must_be_empty_until_review",
            "external_sources_and_licenses_must_stay_visible",
            "high_risk_method_gate_blocks_default_run_plan_until_review",
        ],
    }


def get_internal_agent_skill_source_info(registry_path: Path | None = None) -> dict[str, Any]:
    target_path = _default_registry_path(registry_path)
    registry, reason = _load_registry(target_path)
    base = {
        "available": registry is not None,
        "path": str(target_path),
        "canonical_policy": {
            "mode": "internal_draft_until_human_review",
            "auto_write_canonical": False,
            "proposal_path": INTERNAL_AGENT_SKILL_PROPOSAL_PATH,
        },
    }
    if registry is None:
        return {
            **base,
            "reason": reason,
            "schema_version": "unknown",
            "skill_count": 0,
            "lifecycle_counts": {},
        }

    lifecycle_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    source_names: set[str] = set()
    licenses: set[str] = set()
    for skill in registry.get("skills", []):
        if not isinstance(skill, dict):
            continue
        lifecycle = str(skill.get("lifecycle") or "unknown")
        lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1
        metadata = skill.get("metadata") if isinstance(skill.get("metadata"), dict) else {}
        domain = str(metadata.get("domain") or "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        provenance = skill.get("provenance") if isinstance(skill.get("provenance"), dict) else {}
        for source in provenance.get("external_sources", []):
            if isinstance(source, dict):
                if source.get("name"):
                    source_names.add(str(source["name"]))
                if source.get("license"):
                    licenses.add(str(source["license"]))

    return {
        **base,
        "schema_version": registry.get("schema_version", "unknown"),
        "status": registry.get("status", "unknown"),
        "skill_count": len([skill for skill in registry.get("skills", []) if isinstance(skill, dict)]),
        "lifecycle_counts": lifecycle_counts,
        "domain_counts": domain_counts,
        "external_source_names": sorted(source_names),
        "licenses": sorted(licenses),
    }


def index_internal_agent_skill_capabilities(registry_path: Path | None = None) -> list[dict[str, Any]]:
    target_path = _default_registry_path(registry_path)
    registry, _reason = _load_registry(target_path)
    if registry is None:
        return []

    capabilities: list[dict[str, Any]] = []
    for skill in registry.get("skills", []):
        if not isinstance(skill, dict):
            continue
        skill_id = str(skill.get("id") or "unknown")
        metadata = skill.get("metadata") if isinstance(skill.get("metadata"), dict) else {}
        applies_when = skill.get("applies_when") if isinstance(skill.get("applies_when"), dict) else {}
        inputs = skill.get("inputs") if isinstance(skill.get("inputs"), dict) else {}
        outputs = skill.get("outputs") if isinstance(skill.get("outputs"), dict) else {}
        quality_gates = (
            skill.get("quality_gates") if isinstance(skill.get("quality_gates"), dict) else {}
        )
        human_confirmation = (
            skill.get("human_confirmation") if isinstance(skill.get("human_confirmation"), dict) else {}
        )
        benchmark = skill.get("benchmark") if isinstance(skill.get("benchmark"), dict) else {}
        provenance = skill.get("provenance") if isinstance(skill.get("provenance"), dict) else {}

        required_inputs = list(inputs.get("required") or [])
        optional_inputs = list(inputs.get("optional") or [])
        artifacts = list(outputs.get("artifacts") or [])
        formal_write_targets = list(outputs.get("formal_write_targets") or [])
        allowed_agents = list(metadata.get("allowed_agents") or ["Supervisor"])
        domain = str(metadata.get("domain") or "methodology")
        status = "template" if domain in {"full_pipeline", "writing"} else "checklist"

        capabilities.append(
            {
                "id": f"cap_internal_skill_{_slug(skill_id)}",
                "namespace": "internal_agent_skill",
                "name": str(metadata.get("name") or skill_id),
                "category": f"{domain}_skill",
                "description": _describe_skill(skill, metadata, applies_when),
                "risk_level": str(metadata.get("risk_level") or "medium"),
                "cost_model": "llm_tokens_and_external_sources",
                "allowed_roles": allowed_agents,
                "adapter_path": f"internal://{skill_id}",
                "input_schema": {
                    "type": "object",
                    "required": required_inputs,
                    "properties": {
                        key: {"type": "string"}
                        for key in [*required_inputs, *optional_inputs]
                    },
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "artifacts": {
                            "type": "array",
                            "items": artifacts,
                        },
                        "state_patch_proposal": {
                            "type": "array",
                            "items": list(outputs.get("state_patch_proposal") or []),
                        },
                    },
                },
                "status": status,
                "internal_skill": {
                    "id": skill_id,
                    "lifecycle": str(skill.get("lifecycle") or "internal_draft"),
                    "domain": domain,
                    "stage": str(applies_when.get("stage") or ""),
                    "required_state": list(applies_when.get("required_state") or []),
                    "blockers": list(applies_when.get("blockers") or []),
                    "owner_agent": str(metadata.get("owner_agent") or "Supervisor"),
                    "allowed_agents": allowed_agents,
                    "source_policy": str(metadata.get("source_policy") or ""),
                    "evidence_level": str(metadata.get("evidence_level") or "local_file"),
                    "formal_write_targets": formal_write_targets,
                    "quality_gates": quality_gates,
                    "human_confirmation": human_confirmation,
                    "benchmark": benchmark,
                    "external_sources": list(provenance.get("external_sources") or []),
                    "transformation_log": list(provenance.get("transformation_log") or []),
                },
                "canonical_policy": build_internal_agent_skill_policy(),
            }
        )
    return capabilities


def _describe_skill(
    skill: dict[str, Any],
    metadata: dict[str, Any],
    applies_when: dict[str, Any],
) -> str:
    skill_id = str(skill.get("id") or "unknown")
    name = str(metadata.get("name") or skill_id)
    domain = str(metadata.get("domain") or "methodology")
    stage = str(applies_when.get("stage") or "unknown_stage")
    owner = str(metadata.get("owner_agent") or "Supervisor")
    return f"{name}: {owner} 在 {stage} 阶段调用的 {domain} 内部 Agent Skill。"
