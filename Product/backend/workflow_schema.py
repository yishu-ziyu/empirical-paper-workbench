from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WorkflowTask:
    id: str
    workflow_id: str
    agent_name: str
    role: str
    dimension: str
    dimension_number: int
    status: str = "queued"
    progress: float = 0.0
    summary: str = ""
    research_scope: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    started_at: str | None = None
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Workflow:
    id: str
    project_id: str
    title: str
    status: str = "queued"
    phase: str = "queued"
    progress: float = 0.0
    agent_count: int = 0
    execution_provider: str = "local_codex"
    provider_status: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowArtifact:
    id: str
    workflow_id: str
    task_id: str | None
    kind: str
    path: str
    title: str
    created_by: str
    status: str = "draft"
    created_at: str = ""
    evidence_level: str = "mock"
    promotion_status: str = "not_promoted"
    promoted_to: str | None = None
    promoted_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
