from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_p6_variable_role_signoff_service import FORMAL_VARIABLE_ROLE_APPROVAL_PATH
from Product.backend.product_control_phase_service import project_summary
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import load_variable_role_draft_state, normalize_roles
from Program.workbench.parent_education_wage_variable_role_preflight import TOPIC, TOPIC_SLUG
from Program.workbench.parent_education_wage_variable_role_signoff import (
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_SIGNOFF_PATH,
    is_parent_education_wage_p6_draft,
    parent_education_wage_p6_gate_applies,
)


APPROVAL_CONFIRMATION = "approve_formal_variable_roles_after_review"


def get_project_product_control_p8_variable_role_approval(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    payload = build_parent_education_wage_formal_variable_role_approval_packet(project_root)
    return attach_product_fields(project, project_root, project_id, payload)


def approve_project_product_control_p8_variable_role_approval(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result = approve_parent_education_wage_formal_variable_roles(project_root, payload)
    return attach_product_fields(project, project_root, project_id, result)


def build_parent_education_wage_formal_variable_role_approval_packet(project_root: Path) -> dict[str, Any]:
    latest_draft = latest_parent_education_wage_p6_draft(project_root)
    approval = load_formal_variable_role_approval(project_root)
    base = {
        "schema_version": "p8.parent_education_wage_formal_variable_role_approval.v1",
        "generated_at": utc_now(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "approval_path": FORMAL_VARIABLE_ROLE_APPROVAL_PATH.as_posix(),
        "required_confirmations": [APPROVAL_CONFIRMATION],
        "can_write_formal_variable_roles": False,
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
    if not parent_education_wage_p6_gate_applies(project_root) or not latest_draft:
        return {
            **base,
            "status": "blocked_missing_p7_variable_role_draft",
            "can_approve_formal_variable_roles": False,
            "latest_draft": None,
            "approval": approval,
            "blocking_reasons": ["p7_editable_variable_role_draft_missing"],
            "product_control_signal": {
                "phase": "P8",
                "label": "正式变量角色审批",
                "status": "blocked_missing_p7_variable_role_draft",
                "next_action": "complete_p7_editable_draft_promotion",
            },
        }
    if is_effective_formal_variable_role_approval(approval, latest_draft):
        return {
            **base,
            "status": "formal_variable_role_approval_recorded",
            "can_approve_formal_variable_roles": False,
            "can_write_formal_variable_roles": True,
            "latest_draft": latest_draft,
            "approval": approval,
            "blocking_reasons": [],
            "product_control_signal": {
                "phase": "P8",
                "label": "正式变量角色审批",
                "status": "formal_variable_role_approval_recorded",
                "next_action": "save_formal_variable_roles_only",
            },
        }
    return {
        **base,
        "status": "formal_variable_role_approval_required",
        "can_approve_formal_variable_roles": True,
        "latest_draft": latest_draft,
        "approval": approval,
        "blocking_reasons": [],
        "product_control_signal": {
            "phase": "P8",
            "label": "正式变量角色审批",
            "status": "formal_variable_role_approval_required",
            "next_action": "collect_p8_formal_variable_role_approval",
        },
    }


def approve_parent_education_wage_formal_variable_roles(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    packet = build_parent_education_wage_formal_variable_role_approval_packet(project_root)
    latest_draft = packet.get("latest_draft")
    if packet["status"] == "blocked_missing_p7_variable_role_draft" or not latest_draft:
        return {
            **packet,
            "status": "blocked_missing_p7_variable_role_draft",
            "can_approve_formal_variable_roles": False,
            "can_write_formal_variable_roles": False,
        }
    missing = approval_missing_fields(payload)
    if missing:
        return {
            **packet,
            "status": "formal_variable_role_approval_incomplete",
            "missing_approval_fields": missing,
            "can_write_formal_variable_roles": False,
        }
    timestamp = utc_now()
    approval = {
        "schema_version": "p8.parent_education_wage_formal_variable_role_approval.v1",
        "status": "approved",
        "approval_scope": "formal_variable_roles",
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "source_draft_id": latest_draft.get("id"),
        "source_draft_roles": normalize_roles(latest_draft.get("roles", {})),
        "source_signoff_path": DEFAULT_SIGNOFF_PATH.as_posix(),
        "source_preflight_path": DEFAULT_PREFLIGHT_PATH.as_posix(),
        "reviewer": str(payload.get("reviewer", "")).strip(),
        "note": str(payload.get("note", "")).strip(),
        "confirmation": str(payload.get("confirmation", "")).strip(),
        "approved_at": timestamp,
        "can_write_formal_variable_roles": True,
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
    path = project_root / FORMAL_VARIABLE_ROLE_APPROVAL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(approval, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        **packet,
        "status": "formal_variable_role_approval_recorded",
        "approval": approval,
        "can_approve_formal_variable_roles": False,
        "can_write_formal_variable_roles": True,
        "boundary_flags": {**packet["boundary_flags"], "modified_formal_variable_role_approval": True},
        "product_control_signal": {
            "phase": "P8",
            "label": "正式变量角色审批",
            "status": "formal_variable_role_approval_recorded",
            "next_action": "save_formal_variable_roles_only",
        },
    }


def latest_parent_education_wage_p6_draft(project_root: Path) -> dict[str, Any] | None:
    state = load_variable_role_draft_state(project_root)
    latest_id = state.get("latest_draft_id")
    drafts = state.get("drafts", {})
    if isinstance(drafts, dict) and latest_id:
        draft = drafts.get(latest_id)
        if is_parent_education_wage_p6_draft(draft):
            return draft
    pending = state.get("pending_variable_roles_draft")
    if is_parent_education_wage_p6_draft(pending):
        return pending
    if isinstance(drafts, dict):
        for draft in reversed(list(drafts.values())):
            if is_parent_education_wage_p6_draft(draft):
                return draft
    return None


def approval_missing_fields(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if payload.get("decision") != "approve_formal_variable_roles":
        missing.append("decision")
    if not str(payload.get("reviewer", "")).strip():
        missing.append("reviewer")
    if not str(payload.get("note", "")).strip():
        missing.append("note")
    if str(payload.get("confirmation", "")).strip() != APPROVAL_CONFIRMATION:
        missing.append("confirmation")
    return missing


def load_formal_variable_role_approval(project_root: Path) -> dict[str, Any] | None:
    path = project_root / FORMAL_VARIABLE_ROLE_APPROVAL_PATH
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def is_effective_formal_variable_role_approval(approval: dict[str, Any] | None, latest_draft: dict[str, Any] | None) -> bool:
    draft_id = latest_draft.get("id") if isinstance(latest_draft, dict) else None
    return (
        isinstance(approval, dict)
        and isinstance(latest_draft, dict)
        and approval.get("status") == "approved"
        and approval.get("approval_scope") == "formal_variable_roles"
        and approval.get("topic_slug") == TOPIC_SLUG
        and approval.get("source_draft_id") == draft_id
        and normalize_roles(approval.get("source_draft_roles", {})) == normalize_roles(latest_draft.get("roles", {}))
        and approval.get("confirmation") == APPROVAL_CONFIRMATION
    )


def attach_product_fields(project: dict[str, Any], project_root: Path, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    payload["project"] = project_summary(project, project_root)
    payload["approval_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p8-variable-role-approval"
    return payload
