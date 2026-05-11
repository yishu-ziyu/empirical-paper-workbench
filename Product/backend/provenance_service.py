from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.artifact_service import find_artifact
from Product.backend.project_service import utc_now


def mock_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "mock",
        "service": service,
        "generated_at": utc_now(),
        "note": "Phase A provenance skeleton; not a verified execution lineage.",
    }


def get_artifact_provenance(product_root: Path, artifact_id: str) -> dict[str, Any]:
    if artifact_id == "mock_artifact_baseline":
        return {
            "_meta": mock_meta("provenance_service"),
            "artifact_id": artifact_id,
            "lineage": [
                {
                    "step": 1,
                    "type": "mock_source",
                    "description": "Phase A baseline artifact used for UI provenance rendering.",
                    "actor": "pipeline_artifacts",
                    "timestamp": utc_now(),
                },
                {
                    "step": 2,
                    "type": "governance_check",
                    "description": "Marked as mock so it cannot be treated as a formal research result.",
                    "actor": "pipeline_supervisor",
                    "timestamp": utc_now(),
                },
            ],
            "promotion_policy": {
                "allowed": False,
                "reason": "mock evidence cannot be promoted as a formal artifact.",
            },
        }

    artifact = find_artifact(product_root, artifact_id)
    if artifact is None:
        raise KeyError(artifact_id)
    return {
        "_meta": mock_meta("provenance_service"),
        "artifact_id": artifact_id,
        "lineage": [
            {
                "step": 1,
                "type": "workflow_artifact",
                "description": f"Artifact registered by workflow {artifact.get('workflow_id', 'unknown')}.",
                "actor": artifact.get("agent_name") or "unknown",
                "timestamp": artifact.get("created_at") or utc_now(),
            }
        ],
    }
