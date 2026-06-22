from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Product.backend.variable_role_service import load_variable_role_draft_state, normalize_roles
from Program.workbench.parent_education_wage_variable_role_preflight import TOPIC_SLUG
from Program.workbench.parent_education_wage_variable_role_signoff import (
    DEFAULT_REVIEW_PATH,
    DEFAULT_SIGNOFF_PATH,
    has_parent_education_wage_p6_promoted_draft,
    is_parent_education_wage_p6_draft,
    parent_education_wage_p6_gate_applies,
    promote_parent_education_wage_variable_role_signoff,
    run_parent_education_wage_variable_role_signoff,
)


class VariableRoleFormalSaveRequiresP6DraftError(RuntimeError):
    pass


FORMAL_VARIABLE_ROLE_APPROVAL_PATH = Path("state/product/variable_role_formal_approvals.json")
APPROVAL_CONFIRMATION = "approve_formal_variable_roles_after_review"


def run_project_product_control_p6_variable_role_signoff(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    signoff, _, _ = run_parent_education_wage_variable_role_signoff(project_root)
    return attach_product_fields(project, project_root, project_id, signoff)


def get_project_product_control_p6_variable_role_signoff(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / DEFAULT_SIGNOFF_PATH
    if not path.exists():
        return {
            "status": "p6_variable_role_signoff_missing",
            "project": project_summary(project, project_root),
            "can_refresh": True,
            "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p6-variable-role-signoff",
            "ledger_path": DEFAULT_SIGNOFF_PATH.as_posix(),
            "review_path": DEFAULT_REVIEW_PATH.as_posix(),
            "next_action": "刷新 P6 人工签收包；GET 不会自动提升变量角色草稿。",
        }
    signoff = json.loads(path.read_text(encoding="utf-8"))
    return attach_product_fields(project, project_root, project_id, signoff)


def promote_project_product_control_p6_variable_role_signoff(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result = promote_parent_education_wage_variable_role_signoff(project_root, payload)
    return attach_product_fields(project, project_root, project_id, result)


def assert_project_product_control_p6_formal_save_ready(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    roles: dict[str, Any] | None = None,
) -> None:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    if not parent_education_wage_p6_gate_applies(project_root):
        return
    if not has_parent_education_wage_p6_promoted_draft(project_root):
        raise VariableRoleFormalSaveRequiresP6DraftError(
            "P6 human signoff must be promoted to an editable draft before saving formal variable roles."
        )
    latest_draft = latest_parent_education_wage_p6_draft(project_root)
    approval = load_parent_education_wage_formal_variable_role_approval(project_root)
    if not is_effective_parent_education_wage_formal_variable_role_approval(approval, latest_draft):
        raise VariableRoleFormalSaveRequiresP6DraftError(
            "P6 editable draft is not formal approval. Formal VariableRoleSet save requires a separate P8 approval."
        )
    approved_roles = normalize_roles(approval.get("source_draft_roles", {}))
    if roles is not None and normalize_roles(roles) != approved_roles:
        raise VariableRoleFormalSaveRequiresP6DraftError(
            "P8 approval only applies to the latest approved editable draft roles. Changed roles require a new P8 approval."
        )


def has_parent_education_wage_formal_variable_role_approval(project_root: Path) -> bool:
    latest_draft = latest_parent_education_wage_p6_draft(project_root)
    approval = load_parent_education_wage_formal_variable_role_approval(project_root)
    return is_effective_parent_education_wage_formal_variable_role_approval(approval, latest_draft)


def load_parent_education_wage_formal_variable_role_approval(project_root: Path) -> dict[str, Any] | None:
    path = project_root / FORMAL_VARIABLE_ROLE_APPROVAL_PATH
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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


def is_effective_parent_education_wage_formal_variable_role_approval(
    approval: dict[str, Any] | None,
    latest_draft: dict[str, Any] | None,
) -> bool:
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
    payload["can_refresh"] = True
    payload["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p6-variable-role-signoff"
    payload["promote_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p6-variable-role-signoff/promote"
    return payload
