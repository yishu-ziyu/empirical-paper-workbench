from __future__ import annotations

from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.workflow_service import RESEARCH_DIMENSIONS


PIPELINE_ROLES = [
    ("pipeline_overview", "Overview", "研究总览协调"),
    ("pipeline_data", "Data", "数据与变量治理"),
    ("pipeline_design", "Design", "研究设计编排"),
    ("pipeline_execution", "Execution", "实证执行调度"),
    ("pipeline_manuscript", "Manuscript", "论文草稿生产"),
    ("pipeline_artifacts", "Artifacts", "产物与复现管理"),
    ("pipeline_supervisor", "Supervisor", "监督、权限与成本治理"),
]


def mock_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "mock",
        "service": service,
        "generated_at": utc_now(),
        "note": "Phase A role registry skeleton; not a live agent execution state.",
    }


def pipeline_agents() -> list[dict[str, Any]]:
    return [
        {
            "id": role_id,
            "name": name,
            "role": role,
            "role_type": "pipeline",
            "status": "available",
        }
        for role_id, name, role in PIPELINE_ROLES
    ]


def dimension_agents() -> list[dict[str, Any]]:
    return [
        {
            "id": f"dimension_{index:02d}",
            "name": dimension["agent_name"],
            "role": dimension["role"],
            "role_type": "dimension",
            "status": "available",
            "dimension": dimension["dimension"],
            "scope": dimension["scope"],
        }
        for index, dimension in enumerate(RESEARCH_DIMENSIONS, start=1)
    ]


def all_agents() -> list[dict[str, Any]]:
    return pipeline_agents() + dimension_agents()


def list_agents() -> dict[str, Any]:
    return {
        "_meta": mock_meta("agent_registry_service"),
        "items": all_agents(),
        "role_types": ["pipeline", "dimension"],
    }


def get_agent_details(agent_id: str) -> dict[str, Any]:
    agents = {agent["id"]: agent for agent in all_agents()}
    if agent_id not in agents:
        raise KeyError(agent_id)
    agent = agents[agent_id]
    return {
        "_meta": mock_meta("agent_registry_service"),
        "agent": agent,
        "identity": {
            "id": agent["id"],
            "name": agent["name"],
            "role": agent["role"],
            "role_type": agent["role_type"],
            "provider": "local_codex",
        },
        "permissions": [
            {"scope": "read_project_context", "level": "allowed"},
            {"scope": "write_artifacts", "level": "requires_approval"},
            {"scope": "external_network", "level": "disabled_in_phase_a"},
        ],
        "capabilities": [
            {"id": "summarize_state", "name": "汇总项目状态", "status": "registered"},
            {"id": "trace_artifacts", "name": "追踪产物归属", "status": "registered"},
            {"id": "request_hitl", "name": "发起人工确认", "status": "planned"},
        ],
        "cost": {
            "provider": "local_codex",
            "estimated_tokens": 0,
            "estimated_cost_usd": 0,
            "evidence_level": "mock",
        },
        "artifacts": [],
        "audit_log": [
            {
                "timestamp": utc_now(),
                "actor": "system",
                "action": "phase_a_registry_loaded",
                "description": "Agent details are served from the Phase A static registry.",
            }
        ],
    }
