from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id_or_transient


PERMISSION_STATE_PATH = Path("state/product/permissions.json")

ACTION_CATALOG: list[str] = [
    "project.read",
    "project.write",
    "source.register",
    "source.inspect",
    "source.promote",
    "workflow.create",
    "workflow.run",
    "workflow.cancel",
    "agent.spawn",
    "agent.assign",
    "artifact.read",
    "artifact.write",
    "artifact.promote",
    "method.execute",
    "export.docx",
]

DEFAULT_POLICIES: list[dict[str, Any]] = [
    {
        "role": "supervisor",
        "allow": ["project.read", "project.write", "workflow.create", "workflow.run", "workflow.cancel", "agent.spawn", "agent.assign", "artifact.read", "artifact.write", "artifact.promote", "method.execute", "export.docx"],
        "deny": [],
    },
    {
        "role": "literature_agent",
        "allow": ["project.read", "source.inspect", "artifact.read", "artifact.write"],
        "deny": ["source.promote", "method.execute", "export.docx", "agent.spawn"],
    },
    {
        "role": "data_agent",
        "allow": ["project.read", "source.register", "source.inspect", "artifact.read", "artifact.write", "method.execute"],
        "deny": ["source.promote", "export.docx", "agent.spawn"],
    },
    {
        "role": "identification_agent",
        "allow": ["project.read", "source.inspect", "artifact.read", "artifact.write", "method.execute"],
        "deny": ["source.promote", "export.docx", "agent.spawn"],
    },
    {
        "role": "modeling_agent",
        "allow": ["project.read", "artifact.read", "artifact.write", "method.execute"],
        "deny": ["source.promote", "export.docx", "agent.spawn"],
    },
    {
        "role": "robustness_agent",
        "allow": ["project.read", "artifact.read", "artifact.write", "method.execute"],
        "deny": ["source.promote", "export.docx", "agent.spawn"],
    },
    {
        "role": "writing_agent",
        "allow": ["project.read", "artifact.read", "artifact.write"],
        "deny": ["source.promote", "method.execute", "export.docx", "agent.spawn"],
    },
    {
        "role": "reviewer_agent",
        "allow": ["project.read", "artifact.read", "artifact.write"],
        "deny": ["source.promote", "method.execute", "export.docx", "agent.spawn"],
    },
    {
        "role": "export_agent",
        "allow": ["project.read", "artifact.read", "export.docx"],
        "deny": ["source.promote", "method.execute", "agent.spawn"],
    },
]


def permission_state_path(project_root: Path) -> Path:
    return project_root / PERMISSION_STATE_PATH


def load_saved_permissions(project_root: Path) -> dict[str, Any] | None:
    path = permission_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_permissions() -> dict[str, Any]:
    return {
        "id": "permission_registry",
        "version": 0,
        "status": "empty",
        "evidence_level": "local_file",
        "updated_at": utc_now(),
        "policies": [],
        "action_catalog": ACTION_CATALOG,
        "next_action": {
            "id": "init_permissions",
            "label": "初始化权限策略",
        },
    }


def create_default_permissions(project_id: str) -> dict[str, Any]:
    timestamp = utc_now()
    policies = [
        {
            "id": f"policy_{spec['role']}_{project_id}",
            "subject_id": f"agent_{spec['role']}_01",
            "subject_kind": "agent",
            "project_id": project_id,
            "allow": spec["allow"],
            "deny": spec["deny"],
            "created_at": timestamp,
        }
        for spec in DEFAULT_POLICIES
    ]
    return {
        "id": "permission_registry",
        "version": 1,
        "status": "active",
        "evidence_level": "local_file",
        "updated_at": timestamp,
        "policies": policies,
        "action_catalog": ACTION_CATALOG,
        "next_action": {
            "id": "manage_permissions",
            "label": "管理权限策略",
        },
    }


def get_project_permissions(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    permissions = load_saved_permissions(project_root)
    if not permissions:
        permissions = build_empty_permissions()
    return {
        "_meta": {
            "evidence_level": permissions.get("evidence_level", "local_file"),
            "service": "permission_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "permissions": permissions,
    }


def init_project_permissions(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    existing = load_saved_permissions(project_root)
    if existing and existing.get("version", 0) > 0:
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "permission_service",
                "generated_at": utc_now(),
            },
            "project": {
                "id": project["id"],
                "slug": project["slug"],
                "title": project["title"],
            },
            "permissions": existing,
            "note": "Permission registry already initialized.",
        }
    permissions = create_default_permissions(project_id)
    path = permission_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(permissions, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "permission_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "permissions": permissions,
    }


def check_permission(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    subject_id: str,
    action: str,
) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    permissions = load_saved_permissions(project_root)
    if not permissions:
        return {
            "allowed": False,
            "reason": "permission_registry_not_initialized",
            "subject_id": subject_id,
            "action": action,
        }
    policies = permissions.get("policies", [])
    for policy in policies:
        if policy.get("subject_id") == subject_id and policy.get("project_id") == project_id:
            if action in policy.get("deny", []):
                return {
                    "allowed": False,
                    "reason": "explicitly_denied",
                    "policy_id": policy.get("id"),
                    "subject_id": subject_id,
                    "action": action,
                }
            if action in policy.get("allow", []):
                return {
                    "allowed": True,
                    "reason": "explicitly_allowed",
                    "policy_id": policy.get("id"),
                    "subject_id": subject_id,
                    "action": action,
                }
    return {
        "allowed": False,
        "reason": "no_matching_policy",
        "subject_id": subject_id,
        "action": action,
    }


def update_policy(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    subject_id: str,
    allow: list[str],
    deny: list[str],
) -> dict[str, Any]:
    """Update a single policy's allow/deny lists."""
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    permissions = load_saved_permissions(project_root)
    if not permissions:
        raise PermissionServiceError("not_initialized", "Permission registry not initialized.")

    policies = permissions.get("policies", [])
    policy = None
    for p in policies:
        if p.get("subject_id") == subject_id and p.get("project_id") == project_id:
            policy = p
            break

    if policy is None:
        raise PermissionServiceError("policy_not_found", f"Policy for {subject_id} not found.")

    # Validate actions against catalog
    invalid_allow = [a for a in allow if a not in ACTION_CATALOG]
    invalid_deny = [a for a in deny if a not in ACTION_CATALOG]
    if invalid_allow or invalid_deny:
        raise PermissionServiceError(
            "invalid_action",
            f"Invalid actions: {invalid_allow + invalid_deny}. Must be in catalog.",
        )

    policy["allow"] = list(allow)
    policy["deny"] = list(deny)
    policy["updated_at"] = utc_now()
    permissions["updated_at"] = utc_now()

    path = permission_state_path(project_root)
    path.write_text(json.dumps(permissions, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "updated",
        "policy_id": policy.get("id"),
        "subject_id": subject_id,
        "allow": allow,
        "deny": deny,
    }


def save_project_permissions(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    policies: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replace all policies in the permission registry."""
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    permissions = load_saved_permissions(project_root)
    if not permissions:
        raise PermissionServiceError("not_initialized", "Permission registry not initialized.")

    # Validate all policies
    for p in policies:
        sid = p.get("subject_id", "")
        if not sid:
            raise PermissionServiceError("missing_subject_id", "Each policy must have a subject_id.")
        invalid_allow = [a for a in p.get("allow", []) if a not in ACTION_CATALOG]
        invalid_deny = [a for a in p.get("deny", []) if a not in ACTION_CATALOG]
        if invalid_allow or invalid_deny:
            raise PermissionServiceError(
                "invalid_action",
                f"Invalid actions in policy {sid}: {invalid_allow + invalid_deny}",
            )

    # Rebuild policies preserving IDs and metadata
    existing_map = {ep.get("subject_id"): ep for ep in permissions.get("policies", [])}
    new_policies = []
    for p in policies:
        sid = p["subject_id"]
        existing = existing_map.get(sid, {})
        new_policies.append({
            "id": existing.get("id") or f"policy_{sid.replace('agent_', '').replace('_01', '')}_{project_id}",
            "subject_id": sid,
            "subject_kind": existing.get("subject_kind", "agent"),
            "project_id": project_id,
            "allow": list(p.get("allow", [])),
            "deny": list(p.get("deny", [])),
            "created_at": existing.get("created_at", utc_now()),
            "updated_at": utc_now(),
        })

    permissions["policies"] = new_policies
    permissions["updated_at"] = utc_now()

    path = permission_state_path(project_root)
    path.write_text(json.dumps(permissions, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "saved",
        "policies_count": len(new_policies),
        "updated_at": permissions["updated_at"],
    }


class PermissionServiceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
