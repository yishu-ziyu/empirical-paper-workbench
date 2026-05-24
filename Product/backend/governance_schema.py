from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Identity:
    id: str
    kind: str  # "agent" | "user"
    display_name: str
    role: str
    role_type: str
    created_by: str
    status: str  # "active" | "inactive"
    capability_profile_id: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PermissionPolicy:
    id: str
    subject_id: str
    subject_kind: str  # "agent" | "user"
    project_id: str
    allow: list[str] = field(default_factory=list)
    deny: list[str] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Capability:
    id: str
    namespace: str
    name: str
    category: str
    description: str
    risk_level: str  # "low" | "medium" | "high"
    cost_model: str  # "local_cpu_time" | "llm_tokens" | "external_api"
    allowed_roles: list[str] = field(default_factory=list)
    adapter_path: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    status: str = "executable"  # "advisory" | "template" | "role_prompt" | "checklist" | "executable"
    assumptions: list[str] = field(default_factory=list)
    pre_conditions: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CostEvent:
    event_id: str
    project_id: str
    workflow_id: str
    task_id: str
    actor_id: str
    capability_id: str
    event_type: str
    started_at: str
    finished_at: str = ""
    wall_seconds: float = 0.0
    provider: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_usd: float = 0.0
    status: str = "pending"  # "pending" | "succeeded" | "failed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
