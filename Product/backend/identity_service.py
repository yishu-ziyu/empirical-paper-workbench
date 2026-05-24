from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.governance_schema import Identity
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id_or_transient


IDENTITY_STATE_PATH = Path("state/product/identity.json")


DEFAULT_AGENTS: list[dict[str, str]] = [
    {"role": "supervisor", "display_name": "Supervisor", "role_type": "orchestrator"},
    {"role": "literature_agent", "display_name": "文献 Agent", "role_type": "researcher"},
    {"role": "data_agent", "display_name": "数据 Agent", "role_type": "researcher"},
    {"role": "identification_agent", "display_name": "识别策略 Agent", "role_type": "researcher"},
    {"role": "modeling_agent", "display_name": "建模 Agent", "role_type": "researcher"},
    {"role": "robustness_agent", "display_name": "稳健性 Agent", "role_type": "researcher"},
    {"role": "writing_agent", "display_name": "写作 Agent", "role_type": "writer"},
    {"role": "reviewer_agent", "display_name": "审阅 Agent", "role_type": "reviewer"},
    {"role": "export_agent", "display_name": "导出 Agent", "role_type": "writer"},
]


def identity_state_path(project_root: Path) -> Path:
    return project_root / IDENTITY_STATE_PATH


def load_saved_identity(project_root: Path) -> dict[str, Any] | None:
    path = identity_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_identity() -> dict[str, Any]:
    return {
        "id": "identity_registry",
        "version": 0,
        "status": "empty",
        "evidence_level": "local_file",
        "updated_at": utc_now(),
        "identities": [],
        "default_agents": DEFAULT_AGENTS,
        "next_action": {
            "id": "init_identities",
            "label": "初始化 Agent 身份",
        },
    }


def _capability_profile_for_role(role: str) -> str:
    return f"cap_profile_{role}"


def _build_default_identity(index: int, spec: dict[str, str], project_id: str) -> Identity:
    timestamp = utc_now()
    return Identity(
        id=f"agent_{spec['role']}_{index:02d}",
        kind="agent",
        display_name=spec["display_name"],
        role=spec["role"],
        role_type=spec["role_type"],
        created_by=f"user_owner_{project_id}",
        status="active",
        capability_profile_id=_capability_profile_for_role(spec["role"]),
        created_at=timestamp,
        updated_at=timestamp,
    )


def create_default_identities(project_id: str) -> dict[str, Any]:
    timestamp = utc_now()
    identities = [
        _build_default_identity(index, spec, project_id)
        for index, spec in enumerate(DEFAULT_AGENTS, start=1)
    ]
    return {
        "id": "identity_registry",
        "version": 1,
        "status": "active",
        "evidence_level": "local_file",
        "updated_at": timestamp,
        "identities": [identity.to_dict() for identity in identities],
        "default_agents": DEFAULT_AGENTS,
        "next_action": {
            "id": "manage_identities",
            "label": "管理 Agent 身份",
        },
    }


def get_project_identity(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    identity = load_saved_identity(project_root)
    if not identity:
        identity = build_empty_identity()
    return {
        "_meta": {
            "evidence_level": identity.get("evidence_level", "local_file"),
            "service": "identity_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "identity": identity,
    }


def init_project_identities(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    existing = load_saved_identity(project_root)
    if existing and existing.get("version", 0) > 0:
        return {
            "_meta": {
                "evidence_level": "local_file",
                "service": "identity_service",
                "generated_at": utc_now(),
            },
            "project": {
                "id": project["id"],
                "slug": project["slug"],
                "title": project["title"],
            },
            "identity": existing,
            "note": "Identity registry already initialized.",
        }
    identity = create_default_identities(project_id)
    path = identity_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "identity_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "identity": identity,
    }


def _update_agent_status(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    agent_id: str,
    new_status: str,
) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    identity = load_saved_identity(project_root)
    if not identity:
        raise IdentityServiceError("identity_not_found", "Identity registry not initialized.")
    identities = identity.get("identities", [])
    for agent in identities:
        if agent.get("id") == agent_id:
            agent["status"] = new_status
            agent["updated_at"] = utc_now()
            identity["identities"] = identities
            identity["updated_at"] = utc_now()
            path = identity_state_path(project_root)
            path.write_text(json.dumps(identity, ensure_ascii=False, indent=2), encoding="utf-8")
            return {
                "_meta": {
                    "evidence_level": "local_file",
                    "service": "identity_service",
                    "generated_at": utc_now(),
                },
                "project": {
                    "id": project["id"],
                    "slug": project["slug"],
                    "title": project["title"],
                },
                "identity": identity,
            }
    raise IdentityServiceError("agent_not_found", f"Agent {agent_id} not found.")


def activate_agent(product_root: Path, repo_root: Path, project_id: str, agent_id: str) -> dict[str, Any]:
    return _update_agent_status(product_root, repo_root, project_id, agent_id, "active")


def deactivate_agent(product_root: Path, repo_root: Path, project_id: str, agent_id: str) -> dict[str, Any]:
    return _update_agent_status(product_root, repo_root, project_id, agent_id, "inactive")


class IdentityServiceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
