from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


INTERNAL_AGENT_SKILL_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "internal_skills" / "agent_skill_registry.json"
)
INTERNAL_AGENT_SKILL_PROPOSAL_PATH = "Program/methodology/proposals/internal-agent-skills/"


SKILL_TRIGGER_KEYWORDS: dict[str, list[str]] = {
    "recursive_research_search": [
        "递归",
        "文献",
        "检索",
        "引用",
        "citation",
        "cnki",
        "zotero",
        "literature",
        "search",
        "数据线索",
        "变量证据",
    ],
    "did_staggered_identification_gate": [
        "did",
        "双重差分",
        "diff-in-diff",
        "事件研究",
        "event study",
        "staggered",
        "交错",
        "政策冲击",
        "treatment timing",
        "平行趋势",
    ],
    "weak_iv_diagnostic_gate": [
        "iv",
        "工具变量",
        "instrument",
        "2sls",
        "weak iv",
        "弱工具",
        "first stage",
        "第一阶段",
        "内生",
    ],
    "aer_abstract_submission_preflight": [
        "aer",
        "aej",
        "投稿",
        "submission",
        "abstract",
        "摘要",
        "table",
        "figure",
        "预检",
        "期刊",
    ],
    "replication_package_gate": [
        "复现",
        "可复现",
        "repro",
        "replication",
        "package",
        "export",
        "导出",
        "artifact",
        "产物",
        "readme",
        "一键",
    ],
}


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


def normalize_agent_role_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


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


def recommend_internal_agent_skills_for_plan_context(
    context: dict[str, Any],
    registry_path: Path | None = None,
) -> list[dict[str, Any]]:
    return build_internal_agent_skill_recommendation_bundle(
        context,
        registry_path,
    )["recommended_internal_skills"]


def build_internal_agent_skill_recommendation_bundle(
    context: dict[str, Any],
    registry_path: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    capabilities = index_internal_agent_skill_capabilities(registry_path)
    if not capabilities:
        return {
            "recommended_internal_skills": [],
            "unmatched_internal_skill_judgments": normalize_llm_internal_skill_judgments(context),
        }

    dispatch_items = [
        item for item in _as_list(context.get("subagent_dispatch")) if isinstance(item, dict)
    ]
    capability_skill_ids = {
        str((capability.get("internal_skill") or {}).get("id") or "")
        for capability in capabilities
        if isinstance(capability.get("internal_skill"), dict)
    }
    llm_judgments: dict[str, dict[str, Any]] = {}
    unmatched_llm_judgments: list[dict[str, Any]] = []
    for judgment in normalize_llm_internal_skill_judgments(context):
        skill_id = str(judgment.get("skill_id") or "")
        if skill_id in capability_skill_ids:
            llm_judgments[skill_id] = judgment
        else:
            unmatched_llm_judgments.append(
                {
                    **judgment,
                    "status": "ignored_unknown_skill",
                    "reason_code": "skill_not_in_internal_registry",
                }
            )

    context_for_rule_match = {
        key: value
        for key, value in context.items()
        if key
        not in {
            "internal_skill_judgments",
            "skill_judgments",
            "recommended_internal_skills",
            "llm_internal_skill_judgments",
        }
    }
    full_text = _context_text(context_for_rule_match)
    recommendations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for capability in capabilities:
        skill = capability.get("internal_skill") if isinstance(capability.get("internal_skill"), dict) else {}
        skill_id = str(skill.get("id") or capability.get("id") or "")
        matched_keywords = [
            keyword
            for keyword in SKILL_TRIGGER_KEYWORDS.get(skill_id, [])
            if keyword.lower() in full_text
        ]
        dispatch_targets = _matching_dispatch_targets(skill, dispatch_items)
        llm_judgment = llm_judgments.get(skill_id)
        if not matched_keywords and not dispatch_targets and not llm_judgment:
            continue
        if skill_id in seen:
            continue
        seen.add(skill_id)
        matched_reason = _matched_reason(skill, matched_keywords, dispatch_targets)
        selection_source = _selection_source(matched_keywords, dispatch_targets, llm_judgment)
        recommendations.append(
            {
                "id": capability.get("id"),
                "skill_id": skill_id,
                "name": capability.get("name"),
                "owner_agent": skill.get("owner_agent"),
                "allowed_agents": list(skill.get("allowed_agents") or []),
                "stage": skill.get("stage", ""),
                "risk_level": capability.get("risk_level", "medium"),
                "status": capability.get("status", "checklist"),
                "adapter_path": capability.get("adapter_path", ""),
                "matched_keywords": matched_keywords,
                "matched_reason": matched_reason,
                "selection_source": selection_source,
                "semantic_selection_reason": (llm_judgment or {}).get("reason") or matched_reason,
                "llm_semantic_judgment": llm_judgment or {},
                "dispatch_targets": dispatch_targets,
                "required_state": list(skill.get("required_state") or []),
                "blockers": list(skill.get("blockers") or []),
                "quality_gates": skill.get("quality_gates") or {},
                "human_confirmation": skill.get("human_confirmation") or {},
                "benchmark": skill.get("benchmark") or {},
                "formal_write_targets": list(skill.get("formal_write_targets") or []),
                "source_policy": skill.get("source_policy", ""),
                "canonical_policy": capability.get("canonical_policy") or build_internal_agent_skill_policy(),
            }
        )
    return {
        "recommended_internal_skills": recommendations,
        "unmatched_internal_skill_judgments": unmatched_llm_judgments,
    }


def normalize_llm_internal_skill_judgments(context: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items: list[Any] = []
    for key in (
        "internal_skill_judgments",
        "skill_judgments",
        "recommended_internal_skills",
        "llm_internal_skill_judgments",
    ):
        raw_items.extend(_as_list(context.get(key)))

    judgments: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        skill_id = _normalize_skill_id(item.get("skill_id") or item.get("internal_skill_id") or item.get("id"))
        if not skill_id or skill_id in seen:
            continue
        seen.add(skill_id)
        judgment = {
            "skill_id": skill_id,
            "reason": str(
                item.get("reason")
                or item.get("why_this_skill")
                or item.get("rationale")
                or item.get("semantic_selection_reason")
                or item.get("matched_reason")
                or ""
            ),
            "evidence_fit": str(item.get("evidence_fit") or ""),
            "agent_fit": str(item.get("agent_fit") or ""),
            "risk_note": str(item.get("risk_note") or ""),
            "human_review_note": str(item.get("human_review_note") or ""),
            "confidence": item.get("confidence") or "",
        }
        judgments.append({key: value for key, value in judgment.items() if value != ""})
    return judgments


def compact_internal_agent_skills_for_prompt() -> dict[str, Any]:
    return {
        "policy": build_internal_agent_skill_policy(),
        "skills": [
            {
                "id": cap.get("id"),
                "skill_id": (cap.get("internal_skill") or {}).get("id")
                if isinstance(cap.get("internal_skill"), dict)
                else "",
                "name": cap.get("name"),
                "owner_agent": (cap.get("internal_skill") or {}).get("owner_agent")
                if isinstance(cap.get("internal_skill"), dict)
                else "",
                "allowed_agents": cap.get("allowed_roles", []),
                "stage": (cap.get("internal_skill") or {}).get("stage")
                if isinstance(cap.get("internal_skill"), dict)
                else "",
                "risk_level": cap.get("risk_level"),
                "status": cap.get("status"),
            }
            for cap in index_internal_agent_skill_capabilities()
        ],
    }


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


def _matching_dispatch_targets(
    skill: dict[str, Any],
    dispatch_items: list[dict[str, Any]],
) -> list[str]:
    owner_agent = normalize_agent_role_name(skill.get("owner_agent"))
    targets: list[str] = []
    for item in dispatch_items:
        role = normalize_agent_role_name(item.get("role") or item.get("owner_agent"))
        owner = normalize_agent_role_name(item.get("agent_id"))
        if owner_agent and (role == owner_agent or owner == owner_agent):
            targets.append(str(item.get("agent_id") or item.get("role") or ""))
    return [target for target in targets if target]


def _matched_reason(
    skill: dict[str, Any],
    matched_keywords: list[str],
    dispatch_targets: list[str],
) -> str:
    if matched_keywords and dispatch_targets:
        return f"命中关键词 {', '.join(matched_keywords[:5])}，且可绑定 {skill.get('owner_agent')} 分工。"
    if matched_keywords:
        return f"命中关键词 {', '.join(matched_keywords[:5])}。"
    return f"存在可绑定 {skill.get('owner_agent')} 分工。"


def _selection_source(
    matched_keywords: list[str],
    dispatch_targets: list[str],
    llm_judgment: dict[str, Any] | None,
) -> str:
    if llm_judgment and (matched_keywords or dispatch_targets):
        return "registry_and_llm_semantic_judgment"
    if llm_judgment:
        return "llm_semantic_judgment"
    return "registry_rule_match"


def _normalize_skill_id(value: Any) -> str:
    skill_id = str(value or "").strip()
    if skill_id.startswith("cap_internal_skill_"):
        return skill_id.removeprefix("cap_internal_skill_")
    return skill_id


def _context_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        return " ".join(_context_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_context_text(item) for item in value)
    if value is None:
        return ""
    return str(value).lower()


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]
