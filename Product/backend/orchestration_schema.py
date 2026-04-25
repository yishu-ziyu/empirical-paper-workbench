from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HandoffPacket:
    run_id: str
    agent: str
    stage: str
    inputs: list[str]
    outputs: list[str]
    claims: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    next_agent: str | None = None
    status: str = "completed"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewPacket:
    run_id: str
    reviewer: str
    target_agent: str
    target_artifact: str
    decision: str
    revision_requests: list[str]
    strengths: list[str]
    risks: list[str] = field(default_factory=list)
    status: str = "completed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OrchestrationManifest:
    run_id: str
    project_id: str
    project_root: str
    run_root: str
    mode: str
    supervisor: dict[str, Any]
    agents: list[dict[str, Any]] = field(default_factory=list)
    review_loop: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    status: str = "completed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
