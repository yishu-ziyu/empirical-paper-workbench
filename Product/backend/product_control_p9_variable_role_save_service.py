from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_p8_variable_role_approval_service import (
    is_effective_formal_variable_role_approval,
    latest_parent_education_wage_p6_draft,
    load_formal_variable_role_approval,
)
from Product.backend.product_control_phase_service import project_summary
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import (
    ROLE_KEYS,
    load_saved_variable_role_set,
    normalize_roles,
    variable_role_state_path,
)
from Program.workbench.parent_education_wage_variable_role_preflight import TOPIC, TOPIC_SLUG


FORMAL_VARIABLE_ROLE_SAVE_CONFIRMATION = "save_formal_variable_roles_from_p8_approved_draft"


def get_project_product_control_p9_variable_role_formal_save(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    payload = build_parent_education_wage_formal_variable_role_save_packet(project_root)
    return attach_product_fields(project, project_root, project_id, payload)


def save_project_product_control_p9_variable_role_formal_save(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result = save_parent_education_wage_formal_variable_roles(project_root, payload)
    return attach_product_fields(project, project_root, project_id, result)


def build_parent_education_wage_formal_variable_role_save_packet(project_root: Path) -> dict[str, Any]:
    latest_draft = latest_parent_education_wage_p6_draft(project_root)
    approval = load_formal_variable_role_approval(project_root)
    base = {
        "schema_version": "p9.parent_education_wage_formal_variable_role_save.v1",
        "generated_at": utc_now(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "save_confirmation": FORMAL_VARIABLE_ROLE_SAVE_CONFIRMATION,
        "formal_variable_role_path": "state/product/variable_roles.json",
        "can_save_formal_variable_roles": False,
        "can_enter_design_spec_preflight": False,
        "can_write_design_spec": False,
        "can_write_run_plan": False,
        "can_create_run_id": False,
        "can_execute_model": False,
        "boundary_flags": {
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
            "source_contract": None,
            "missing_source_metadata_fields": [],
            "blocking_reasons": ["p7_editable_variable_role_draft_missing"],
            "product_control_signal": {
                "phase": "P9",
                "label": "正式变量表保存",
                "status": "blocked_missing_p7_variable_role_draft",
                "next_action": "complete_p7_editable_draft_promotion",
            },
        }
    if not is_effective_formal_variable_role_approval(approval, latest_draft):
        return {
            **base,
            "status": "blocked_missing_p8_formal_approval",
            "latest_draft": latest_draft,
            "approval": approval,
            "approved_roles": normalize_roles(latest_draft.get("roles", {})),
            "source_contract": normalize_source_contract(project_root, latest_draft),
            "missing_source_metadata_fields": [],
            "blocking_reasons": ["p8_formal_variable_role_approval_missing_or_stale"],
            "product_control_signal": {
                "phase": "P9",
                "label": "正式变量表保存",
                "status": "blocked_missing_p8_formal_approval",
                "next_action": "complete_p8_formal_variable_role_approval",
            },
        }

    approved_roles = normalize_roles(approval.get("source_draft_roles", {}))
    source_contract = normalize_source_contract(project_root, latest_draft)
    missing = missing_source_metadata_fields(project_root, latest_draft, approved_roles, source_contract)
    if missing:
        return {
            **base,
            "status": "blocked_missing_dataset_source_metadata",
            "latest_draft": latest_draft,
            "approval": approval,
            "approved_roles": approved_roles,
            "source_contract": source_contract,
            "missing_source_metadata_fields": missing,
            "blocking_reasons": ["dataset_or_field_source_metadata_incomplete"],
            "product_control_signal": {
                "phase": "P9",
                "label": "正式变量表保存",
                "status": "blocked_missing_dataset_source_metadata",
                "next_action": "complete_dataset_path_and_field_source_metadata_before_formal_save",
            },
        }

    saved_role_set = load_saved_variable_role_set(project_root)
    if saved_variable_role_set_matches_current_gate(saved_role_set, latest_draft, approved_roles, source_contract):
        return {
            **base,
            "status": "formal_variable_roles_saved",
            "can_save_formal_variable_roles": False,
            "can_enter_design_spec_preflight": True,
            "latest_draft": latest_draft,
            "approval": approval,
            "approved_roles": approved_roles,
            "source_contract": source_contract,
            "variable_role_set": saved_role_set,
            "missing_source_metadata_fields": [],
            "blocking_reasons": [],
            "product_control_signal": {
                "phase": "P9",
                "label": "正式变量表保存",
                "status": "formal_variable_roles_saved",
                "next_action": "enter_design_tree_pre_prd_without_model_execution",
            },
        }

    return {
        **base,
        "status": "formal_variable_role_save_ready",
        "can_save_formal_variable_roles": True,
        "latest_draft": latest_draft,
        "approval": approval,
        "approved_roles": approved_roles,
        "source_contract": source_contract,
        "missing_source_metadata_fields": [],
        "blocking_reasons": [],
        "product_control_signal": {
            "phase": "P9",
            "label": "正式变量表保存",
            "status": "formal_variable_role_save_ready",
            "next_action": "save_formal_variable_roles_from_p8_approved_draft",
        },
    }


def save_parent_education_wage_formal_variable_roles(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    packet = build_parent_education_wage_formal_variable_role_save_packet(project_root)
    missing = formal_save_missing_fields(payload)
    if missing:
        return {
            **packet,
            "status": "formal_variable_role_save_incomplete",
            "missing_save_fields": missing,
            "can_save_formal_variable_roles": False,
            "can_enter_design_spec_preflight": False,
        }
    if packet.get("status") != "formal_variable_role_save_ready":
        return {
            **packet,
            "can_save_formal_variable_roles": False,
            "can_enter_design_spec_preflight": False,
        }

    latest_draft = packet["latest_draft"]
    approved_roles = normalize_roles(packet["approved_roles"])
    source_contract = dict(packet["source_contract"])
    payload_roles = normalize_roles(payload.get("roles", {}))
    payload_dataset = str(payload.get("dataset_path", "")).strip()
    expected_dataset = str(source_contract.get("dataset_path", "")).strip()
    if (
        str(payload.get("source_draft_id", "")).strip() != str(latest_draft.get("id", "")).strip()
        or payload_dataset != expected_dataset
        or payload_roles != approved_roles
    ):
        return {
            **packet,
            "status": "formal_variable_role_save_payload_mismatch",
            "can_save_formal_variable_roles": False,
            "can_enter_design_spec_preflight": False,
            "payload_mismatch_reasons": payload_mismatch_reasons(payload, latest_draft, expected_dataset, approved_roles),
        }

    existing = load_saved_variable_role_set(project_root)
    version = int(existing.get("version", 0)) + 1 if existing else 1
    previous_events = existing.get("decision_events", []) if isinstance(existing, dict) else []
    timestamp = utc_now()
    approval = packet["approval"]
    event = {
        "actor": str(payload.get("reviewer", "")).strip(),
        "action": "save_formal_variable_roles_from_p8_approved_draft",
        "timestamp": timestamp,
        "note": str(payload.get("note", "")).strip(),
        "source_draft_id": latest_draft.get("id"),
    }
    source_contract["source_draft_id"] = latest_draft.get("id")
    role_set = {
        "id": "variable_role_set",
        "version": version,
        "status": "approved",
        "evidence_level": "local_file",
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "dataset_path": expected_dataset,
        "dataset_name": source_contract.get("dataset_name") or Path(expected_dataset).name,
        "updated_at": timestamp,
        "roles": approved_roles,
        "source_contract": source_contract,
        "operationalization": latest_draft.get("operationalization", {}),
        "p8_approval": {
            "source_draft_id": approval.get("source_draft_id"),
            "approved_at": approval.get("approved_at"),
            "reviewer": approval.get("reviewer"),
            "approval_path": "state/product/variable_role_formal_approvals.json",
        },
        "can_enter_design_spec_preflight": True,
        "can_create_run_id": False,
        "can_execute_model": False,
        "boundary_flags": {
            "modified_formal_variable_roles": True,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "created_run_id": False,
            "executed_regression": False,
        },
        "decision_events": [*previous_events, event],
    }
    path = variable_role_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(role_set, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        **packet,
        "status": "formal_variable_roles_saved",
        "can_save_formal_variable_roles": False,
        "can_enter_design_spec_preflight": True,
        "can_create_run_id": False,
        "can_execute_model": False,
        "variable_role_set": role_set,
        "boundary_flags": role_set["boundary_flags"],
        "product_control_signal": {
            "phase": "P9",
            "label": "正式变量表保存",
            "status": "formal_variable_roles_saved",
            "next_action": "enter_design_spec_preflight_without_model_execution",
        },
    }


def saved_variable_role_set_matches_current_gate(
    saved_role_set: dict[str, Any],
    latest_draft: dict[str, Any],
    approved_roles: dict[str, list[str]],
    source_contract: dict[str, Any],
) -> bool:
    if not isinstance(saved_role_set, dict) or saved_role_set.get("status") != "approved":
        return False
    saved_contract = saved_role_set.get("source_contract") if isinstance(saved_role_set.get("source_contract"), dict) else {}
    return (
        str(saved_contract.get("source_draft_id", "")).strip() == str(latest_draft.get("id", "")).strip()
        and str(saved_role_set.get("dataset_path", "")).strip() == str(source_contract.get("dataset_path", "")).strip()
        and normalize_roles(saved_role_set.get("roles", {})) == approved_roles
        and bool(saved_role_set.get("can_enter_design_spec_preflight"))
        and not bool(saved_role_set.get("can_create_run_id"))
        and not bool(saved_role_set.get("can_execute_model"))
    )


def normalize_source_contract(project_root: Path, draft: dict[str, Any]) -> dict[str, Any]:
    contract = draft.get("source_contract") if isinstance(draft.get("source_contract"), dict) else {}
    dataset_path = str(contract.get("dataset_path") or draft.get("dataset_path") or "").strip()
    return {
        **contract,
        "status": contract.get("status") or "incomplete",
        "dataset_path": dataset_path,
        "dataset_name": contract.get("dataset_name") or draft.get("dataset_name") or Path(dataset_path).name if dataset_path else "",
        "analysis_dataset_available": bool(contract.get("analysis_dataset_available")) or dataset_path_exists(project_root, dataset_path),
        "field_bindings": contract.get("field_bindings") if isinstance(contract.get("field_bindings"), dict) else {},
        "derived_variables": contract.get("derived_variables") if isinstance(contract.get("derived_variables"), dict) else {},
    }


def missing_source_metadata_fields(
    project_root: Path,
    draft: dict[str, Any],
    roles: dict[str, list[str]],
    source_contract: dict[str, Any],
) -> list[str]:
    missing: list[str] = []
    dataset_path = str(source_contract.get("dataset_path") or draft.get("dataset_path") or "").strip()
    if not dataset_path or not dataset_path_exists(project_root, dataset_path):
        missing.append("dataset_path")
    if source_contract.get("status") != "complete":
        missing.append("source_contract_status")
    bindings = source_contract.get("field_bindings", {})
    derived_variables = source_contract.get("derived_variables", {})
    for field in required_role_fields(roles):
        if field_has_source_metadata(field, bindings, derived_variables):
            continue
        missing.append(field)
    return list(dict.fromkeys(missing))


def required_role_fields(roles: dict[str, list[str]]) -> list[str]:
    fields: list[str] = []
    for key in ROLE_KEYS:
        value = roles.get(key, [])
        if isinstance(value, str):
            fields.append(value)
        elif isinstance(value, list):
            fields.extend(str(item) for item in value if str(item).strip())
    return list(dict.fromkeys(field.strip() for field in fields if field.strip()))


def field_has_source_metadata(field: str, bindings: dict[str, Any], derived_variables: dict[str, Any]) -> bool:
    binding = bindings.get(field)
    if binding_has_auditable_source_metadata(binding):
        return True
    derived = derived_variables.get(field)
    if not isinstance(derived, dict):
        return False
    if not str(derived.get("construction", "")).strip():
        return False
    source_fields = [str(item).strip() for item in derived.get("source_fields", []) if str(item).strip()]
    return bool(source_fields) and all(binding_has_auditable_source_metadata(bindings.get(source_field)) for source_field in source_fields)


def binding_has_auditable_source_metadata(binding: Any) -> bool:
    return (
        isinstance(binding, dict)
        and bool(str(binding.get("dataset_column") or binding.get("source_field") or "").strip())
        and bool(str(binding.get("source_path", "")).strip())
        and bool(str(binding.get("evidence_level", "")).strip())
    )


def dataset_path_exists(project_root: Path, dataset_path: str) -> bool:
    if not dataset_path:
        return False
    path = Path(dataset_path)
    candidate = path if path.is_absolute() else project_root / path
    try:
        candidate.resolve().relative_to(project_root.resolve())
    except ValueError:
        return False
    return candidate.exists() and candidate.is_file()


def formal_save_missing_fields(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if payload.get("decision") != "save_formal_variable_roles":
        missing.append("decision")
    if not str(payload.get("reviewer", "")).strip():
        missing.append("reviewer")
    if not str(payload.get("note", "")).strip():
        missing.append("note")
    if str(payload.get("confirmation", "")).strip() != FORMAL_VARIABLE_ROLE_SAVE_CONFIRMATION:
        missing.append("confirmation")
    if not str(payload.get("source_draft_id", "")).strip():
        missing.append("source_draft_id")
    if not str(payload.get("dataset_path", "")).strip():
        missing.append("dataset_path")
    if not normalize_roles(payload.get("roles", {})):
        missing.append("roles")
    return missing


def payload_mismatch_reasons(
    payload: dict[str, Any],
    latest_draft: dict[str, Any],
    expected_dataset: str,
    approved_roles: dict[str, list[str]],
) -> list[str]:
    reasons: list[str] = []
    if str(payload.get("source_draft_id", "")).strip() != str(latest_draft.get("id", "")).strip():
        reasons.append("source_draft_id")
    if str(payload.get("dataset_path", "")).strip() != expected_dataset:
        reasons.append("dataset_path")
    if normalize_roles(payload.get("roles", {})) != approved_roles:
        reasons.append("roles")
    return reasons


def attach_product_fields(project: dict[str, Any], project_root: Path, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    payload["project"] = project_summary(project, project_root)
    payload["save_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p9-variable-role-formal-save"
    return payload
