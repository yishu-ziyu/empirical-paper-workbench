from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_p8_variable_role_approval_service import (
    is_effective_formal_variable_role_approval,
    latest_parent_education_wage_p6_draft,
    load_formal_variable_role_approval,
)
from Product.backend.product_control_p9_variable_role_save_service import (
    binding_has_auditable_source_metadata,
    build_parent_education_wage_formal_variable_role_save_packet,
    dataset_path_exists,
    field_has_source_metadata,
    missing_source_metadata_fields,
    normalize_source_contract,
    required_role_fields,
)
from Product.backend.product_control_phase_service import project_summary
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import (
    load_variable_role_draft_state,
    normalize_roles,
    write_variable_role_draft_state,
)
from Program.workbench.parent_education_wage_variable_role_preflight import TOPIC, TOPIC_SLUG


SOURCE_METADATA_CONFIRMATION = "save_source_metadata_contract_for_p9_formal_save"
CANONICAL_PARENT_EDUCATION_WAGE_SOURCE_FIELDS = [
    "ln_wage",
    "parent_education",
    "age",
    "female",
    "urban",
    "edu_last",
    "experience",
    "father_education",
    "mother_education",
]


def get_project_product_control_p11_source_metadata_contract(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    payload = build_parent_education_wage_source_metadata_contract_packet(project_root)
    return attach_product_fields(project, project_root, project_id, payload)


def save_project_product_control_p11_source_metadata_contract(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result = save_parent_education_wage_source_metadata_contract(project_root, payload)
    return attach_product_fields(project, project_root, project_id, result)


def build_parent_education_wage_source_metadata_contract_packet(project_root: Path) -> dict[str, Any]:
    latest_draft = latest_parent_education_wage_p6_draft(project_root)
    approval = load_formal_variable_role_approval(project_root)
    base = {
        "schema_version": "p11.parent_education_wage_source_metadata_contract.v1",
        "generated_at": utc_now(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "save_confirmation": SOURCE_METADATA_CONFIRMATION,
        "can_save_formal_variable_roles": False,
        "can_return_to_p9_formal_save": False,
        "can_enter_design_spec_preflight": False,
        "can_write_design_spec": False,
        "can_write_run_plan": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "boundary_flags": {
            "modified_variable_roles_draft": False,
            "modified_formal_variable_roles": False,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "created_run_id": False,
            "executed_regression": False,
        },
    }
    if not latest_draft:
        return {
            **base,
            "status": "blocked_missing_p7_variable_role_draft",
            "latest_draft": None,
            "approval": approval,
            "required_source_fields": [],
            "missing_source_metadata_fields": [],
            "source_contract": None,
            "product_control_signal": {
                "phase": "P11",
                "label": "Source Metadata",
                "status": "blocked_missing_p7_variable_role_draft",
                "next_action": "complete_p7_editable_draft_promotion",
            },
        }
    if not is_effective_formal_variable_role_approval(approval, latest_draft):
        roles = normalize_roles(latest_draft.get("roles", {}))
        source_contract = normalize_source_contract(project_root, latest_draft)
        return {
            **base,
            "status": "blocked_missing_p8_formal_approval",
            "latest_draft": latest_draft,
            "approval": approval,
            "approved_roles": roles,
            "required_source_fields": required_source_contract_fields(roles, latest_draft),
            "missing_source_metadata_fields": [],
            "source_contract": source_contract,
            "source_contract_review_kit": build_source_contract_review_kit(
                project_root,
                latest_draft,
                roles,
                source_contract,
                [],
            ),
            "product_control_signal": {
                "phase": "P11",
                "label": "Source Metadata",
                "status": "blocked_missing_p8_formal_approval",
                "next_action": "complete_p8_formal_variable_role_approval",
            },
        }

    roles = normalize_roles(approval.get("source_draft_roles", {}))
    source_contract = normalize_source_contract(project_root, latest_draft)
    missing = missing_source_metadata_fields_for_p11(project_root, latest_draft, roles, source_contract)
    status = "source_metadata_contract_required" if missing else "source_metadata_contract_ready_for_p9_save"
    return {
        **base,
        "status": status,
        "latest_draft": latest_draft,
        "approval": approval,
        "approved_roles": roles,
        "required_source_fields": required_source_contract_fields(roles, latest_draft),
        "missing_source_metadata_fields": missing,
        "source_contract": source_contract,
        "field_bindings": source_contract.get("field_bindings", {}),
        "derived_variables": source_contract.get("derived_variables", {}),
        "suggested_field_bindings": suggested_field_bindings(required_source_contract_fields(roles, latest_draft), source_contract),
        "source_contract_review_kit": build_source_contract_review_kit(
            project_root,
            latest_draft,
            roles,
            source_contract,
            missing,
        ),
        "can_return_to_p9_formal_save": not missing,
        "product_control_signal": {
            "phase": "P11",
            "label": "Source Metadata",
            "status": status,
            "next_action": "complete_dataset_path_and_field_source_metadata"
            if missing
            else "return_to_p9_formal_variable_role_save",
        },
    }


def save_parent_education_wage_source_metadata_contract(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    packet = build_parent_education_wage_source_metadata_contract_packet(project_root)
    if packet.get("status") not in {"source_metadata_contract_required", "source_metadata_contract_ready_for_p9_save"}:
        return packet
    missing_payload = source_metadata_payload_missing_fields(payload)
    latest_draft = dict(packet["latest_draft"])
    roles = normalize_roles(packet.get("approved_roles", latest_draft.get("roles", {})))
    candidate_contract = normalize_payload_source_contract(project_root, latest_draft, roles, payload)
    missing_source = missing_source_metadata_fields_for_p11(project_root, latest_draft, roles, candidate_contract)
    if missing_payload or missing_source:
        return {
            **packet,
            "status": "source_metadata_contract_incomplete",
            "missing_source_metadata_fields": list(dict.fromkeys([*missing_payload, *missing_source])),
            "source_contract": {**candidate_contract, "status": "incomplete"},
            "can_return_to_p9_formal_save": False,
            "can_save_formal_variable_roles": False,
            "can_enter_design_spec_preflight": False,
            "product_control_signal": {
                "phase": "P11",
                "label": "Source Metadata",
                "status": "source_metadata_contract_incomplete",
                "next_action": "complete_dataset_path_and_field_source_metadata",
            },
        }

    completed_contract = {
        **candidate_contract,
        "status": "complete",
        "analysis_dataset_available": True,
        "source_draft_id": latest_draft.get("id"),
        "updated_at": utc_now(),
        "review": {
            "reviewer": str(payload.get("reviewer", "")).strip(),
            "note": str(payload.get("note", "")).strip(),
            "confirmation": str(payload.get("confirmation", "")).strip(),
        },
    }
    updated_draft = {
        **latest_draft,
        "dataset_path": completed_contract["dataset_path"],
        "dataset_name": completed_contract["dataset_name"],
        "source_contract": completed_contract,
        "updated_at": completed_contract["updated_at"],
        "decision_events": [
            *latest_draft.get("decision_events", []),
            {
                "actor": completed_contract["review"]["reviewer"],
                "action": "save_source_metadata_contract_for_p9_formal_save",
                "timestamp": completed_contract["updated_at"],
                "note": completed_contract["review"]["note"],
            },
        ],
    }
    write_latest_draft(project_root, updated_draft)
    refreshed_p9 = build_parent_education_wage_formal_variable_role_save_packet(project_root)
    return {
        **build_parent_education_wage_source_metadata_contract_packet(project_root),
        "status": "source_metadata_contract_ready_for_p9_save",
        "source_contract": completed_contract,
        "field_bindings": completed_contract["field_bindings"],
        "derived_variables": completed_contract["derived_variables"],
        "missing_source_metadata_fields": [],
        "can_return_to_p9_formal_save": refreshed_p9.get("status") == "formal_variable_role_save_ready",
        "can_save_formal_variable_roles": False,
        "can_enter_design_spec_preflight": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "boundary_flags": {
            "modified_variable_roles_draft": True,
            "modified_formal_variable_roles": False,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "created_run_id": False,
            "executed_regression": False,
        },
        "p9_status_after_update": refreshed_p9.get("status"),
        "product_control_signal": {
            "phase": "P11",
            "label": "Source Metadata",
            "status": "source_metadata_contract_ready_for_p9_save",
            "next_action": "return_to_p9_formal_variable_role_save",
        },
    }


def source_metadata_payload_missing_fields(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if payload.get("decision") != "save_source_metadata_contract":
        missing.append("decision")
    if not str(payload.get("reviewer", "")).strip():
        missing.append("reviewer")
    if not str(payload.get("note", "")).strip():
        missing.append("note")
    if str(payload.get("confirmation", "")).strip() != SOURCE_METADATA_CONFIRMATION:
        missing.append("confirmation")
    if not str(payload.get("dataset_path", "")).strip():
        missing.append("dataset_path")
    return missing


def normalize_payload_source_contract(
    project_root: Path,
    latest_draft: dict[str, Any],
    roles: dict[str, list[str]],
    payload: dict[str, Any],
) -> dict[str, Any]:
    dataset_path = str(payload.get("dataset_path", "")).strip()
    dataset_name = Path(dataset_path).name if dataset_path else ""
    field_bindings = normalize_field_bindings(payload.get("field_bindings", {}))
    derived_variables = normalize_derived_variables(payload.get("derived_variables", {}))
    status = "complete"
    if not dataset_path_exists(project_root, dataset_path):
        status = "incomplete"
    for field in required_source_contract_fields(roles, latest_draft):
        if field in required_role_fields(roles):
            if field == "parent_education" and field in derived_variables:
                continue
            if not binding_has_auditable_source_metadata(field_bindings.get(field)):
                status = "incomplete"
        elif not binding_has_auditable_source_metadata(field_bindings.get(field)):
            status = "incomplete"
    if "parent_education" in required_role_fields(roles):
        parent = derived_variables.get("parent_education", {})
        source_fields = parent.get("source_fields", []) if isinstance(parent, dict) else []
        if not parent.get("construction") or not source_fields:
            status = "incomplete"
    return {
        "status": status,
        "dataset_path": dataset_path,
        "dataset_name": dataset_name,
        "analysis_dataset_available": dataset_path_exists(project_root, dataset_path),
        "source_draft_id": latest_draft.get("id"),
        "field_bindings": field_bindings,
        "derived_variables": derived_variables,
    }


def normalize_field_bindings(value: Any) -> dict[str, dict[str, str]]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, dict[str, str]] = {}
    for field, binding in value.items():
        if not isinstance(binding, dict):
            continue
        key = str(field).strip()
        if not key:
            continue
        normalized[key] = {
            "dataset_column": str(binding.get("dataset_column") or binding.get("source_field") or key).strip(),
            "source_field": str(binding.get("source_field") or binding.get("dataset_column") or key).strip(),
            "source_path": str(binding.get("source_path", "")).strip(),
            "evidence_level": str(binding.get("evidence_level", "")).strip(),
        }
    return normalized


def normalize_derived_variables(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for variable, spec in value.items():
        if not isinstance(spec, dict):
            continue
        key = str(variable).strip()
        if not key:
            continue
        source_fields = [str(item).strip() for item in spec.get("source_fields", []) if str(item).strip()]
        normalized[key] = {
            "source_fields": source_fields,
            "construction": str(spec.get("construction", "")).strip(),
        }
    return normalized


def required_source_contract_fields(roles: dict[str, list[str]], draft: dict[str, Any]) -> list[str]:
    fields = required_role_fields(roles)
    if "parent_education" in fields:
        operationalization = draft.get("operationalization", {})
        parent = operationalization.get("parent_education", {}) if isinstance(operationalization, dict) else {}
        source_fields = parent.get("source_fields", ["father_education", "mother_education"]) if isinstance(parent, dict) else []
        fields.extend(str(item).strip() for item in source_fields if str(item).strip())
    fields.extend(CANONICAL_PARENT_EDUCATION_WAGE_SOURCE_FIELDS)
    return list(dict.fromkeys(fields))


def missing_source_metadata_fields_for_p11(
    project_root: Path,
    draft: dict[str, Any],
    roles: dict[str, list[str]],
    source_contract: dict[str, Any],
) -> list[str]:
    missing = missing_source_metadata_fields(project_root, draft, roles, source_contract)
    bindings = source_contract.get("field_bindings", {})
    derived_variables = source_contract.get("derived_variables", {})
    for field in required_source_contract_fields(roles, draft):
        if field == "parent_education" and field_has_source_metadata(field, bindings, derived_variables):
            continue
        if field_has_source_metadata(field, bindings, derived_variables):
            continue
        missing.append(field)
    return list(dict.fromkeys(missing))


def suggested_field_bindings(fields: list[str], source_contract: dict[str, Any]) -> dict[str, dict[str, str]]:
    existing = source_contract.get("field_bindings", {}) if isinstance(source_contract.get("field_bindings"), dict) else {}
    return {
        field: existing.get(field, {
            "dataset_column": field,
            "source_field": field,
            "source_path": source_contract.get("dataset_path", ""),
            "evidence_level": "local_file",
        })
        for field in fields
    }


def build_source_contract_review_kit(
    project_root: Path,
    draft: dict[str, Any],
    roles: dict[str, list[str]],
    source_contract: dict[str, Any],
    missing: list[str],
) -> dict[str, Any]:
    required_fields = required_source_contract_fields(roles, draft)
    p5_preflight = load_json(project_root / "Results/json/parent_education_wage_p5_variable_role_preflight.json")
    source_by_field = preferred_sources_by_field(p5_preflight)
    dataset_path_candidates = dataset_path_candidates_for_review(project_root, draft, source_contract)
    recommended_dataset_path = source_contract.get("dataset_path") or first_existing_dataset_path(project_root, dataset_path_candidates)
    field_review_items = [
        build_field_review_item(field, source_by_field.get(field), source_contract, missing)
        for field in required_fields
    ]
    return {
        "schema_version": "p11a.parent_education_wage_source_contract_review_kit.v1",
        "status": "needs_human_source_contract_review" if missing else "source_contract_review_ready_for_p9",
        "can_save_without_human_review": False,
        "can_write_formal_variable_roles": False,
        "can_enter_design_spec_preflight": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "recommended_dataset_path": recommended_dataset_path,
        "dataset_path_candidates": dataset_path_candidates,
        "required_source_fields": required_fields,
        "field_review_items": field_review_items,
        "recommended_parent_education_construction": parent_education_construction_default(p5_preflight, draft),
        "missing_source_metadata_fields": missing,
        "save_requirements": [
            "dataset_path",
            "field_bindings with source_path and evidence_level",
            "derived_variables.parent_education construction and source_fields",
            "reviewer",
            "note",
            SOURCE_METADATA_CONFIRMATION,
        ],
        "boundary": "review kit only; no formal VariableRoleSet, no DesignSpec, no RunPlan, no run id, no model execution",
    }


def build_field_review_item(
    field: str,
    preferred_source: dict[str, Any] | None,
    source_contract: dict[str, Any],
    missing: list[str],
) -> dict[str, Any]:
    bindings = source_contract.get("field_bindings", {})
    derived_variables = source_contract.get("derived_variables", {})
    confirmed = field_has_source_metadata(field, bindings, derived_variables)
    if confirmed:
        review_status = "source_metadata_already_recorded"
    elif preferred_source:
        review_status = "needs_human_confirmation"
    else:
        review_status = "missing_recommended_source"
    return {
        "field": field,
        "review_status": review_status,
        "is_missing": field in missing,
        "recommended_source": normalize_preferred_source(preferred_source),
        "current_binding": bindings.get(field),
        "current_derived_variable": derived_variables.get(field),
    }


def preferred_sources_by_field(preflight: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for item in preflight.get("role_bindings", []) if isinstance(preflight, dict) else []:
        if not isinstance(item, dict):
            continue
        field = str(item.get("dataset_column", "")).strip()
        preferred = item.get("preferred_candidate")
        if field and isinstance(preferred, dict):
            sources[field] = preferred
    return sources


def normalize_preferred_source(source: dict[str, Any] | None) -> dict[str, Any] | None:
    if not source:
        return None
    return {
        "name": str(source.get("name", "")).strip(),
        "label": str(source.get("label", "")).strip(),
        "source_path": str(source.get("source_path", "")).strip(),
        "source_root": str(source.get("source_root", "")).strip(),
        "source_type": str(source.get("source_type", "")).strip(),
        "evidence_level": str(source.get("evidence_level", "")).strip(),
        "match_reason": str(source.get("match_reason", "")).strip(),
    }


def dataset_path_candidates_for_review(
    project_root: Path,
    draft: dict[str, Any],
    source_contract: dict[str, Any],
) -> list[str]:
    candidates = [
        source_contract.get("dataset_path", ""),
        draft.get("dataset_path", ""),
        draft.get("source_dataset", {}).get("binding", {}).get("path", "")
        if isinstance(draft.get("source_dataset"), dict)
        else "",
        "Data/Final/cfps_robot_reallocation.csv",
        "Data/Raw/cfps2010famecon_202008.dta",
    ]
    data_root = project_root / "Data"
    if data_root.exists():
        for path in sorted(data_root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".csv", ".dta", ".parquet", ".xlsx"}:
                candidates.append(str(path.relative_to(project_root)))
    return [item for item in dict.fromkeys(str(candidate).strip() for candidate in candidates) if item]


def first_existing_dataset_path(project_root: Path, candidates: list[str]) -> str:
    for candidate in candidates:
        if dataset_path_exists(project_root, candidate):
            return candidate
    return candidates[0] if candidates else ""


def parent_education_construction_default(preflight: dict[str, Any], draft: dict[str, Any]) -> str:
    draft_roles = preflight.get("draft_variable_roles", {}) if isinstance(preflight, dict) else {}
    treatment = draft_roles.get("treatment", {}) if isinstance(draft_roles, dict) else {}
    construction = treatment.get("construction", {}) if isinstance(treatment, dict) else {}
    recommended = construction.get("recommended_default") if isinstance(construction, dict) else None
    if recommended:
        return str(recommended)
    operationalization = draft.get("operationalization", {})
    parent = operationalization.get("parent_education", {}) if isinstance(operationalization, dict) else {}
    if isinstance(parent, dict) and parent.get("construction"):
        return str(parent["construction"])
    return "max(father_education, mother_education)"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_latest_draft(project_root: Path, draft: dict[str, Any]) -> None:
    state = load_variable_role_draft_state(project_root)
    draft_id = str(draft.get("id", "")).strip()
    state.setdefault("drafts", {})[draft_id] = draft
    state["latest_draft_id"] = draft_id
    state["pending_variable_roles_draft"] = draft
    state["updated_at"] = draft.get("updated_at") or utc_now()
    write_variable_role_draft_state(project_root, state)


def attach_product_fields(project: dict[str, Any], project_root: Path, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    payload["project"] = project_summary(project, project_root)
    payload["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p11-source-metadata-contract"
    payload["save_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p11-source-metadata-contract"
    return payload
