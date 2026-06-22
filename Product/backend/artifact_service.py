from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from Product.backend.registry import get_project_by_id
from Product.backend.workflow_service import (
    artifacts_path,
    load_artifacts,
    load_workflow,
    project_root_for,
    utc_now,
    workflow_state_root,
    write_json,
)


PROMOTE_TARGETS = {
    "manuscripts": "Manuscripts/generated/agent-cluster",
    "results": "Results/agent-cluster",
    "submissions": "Submissions/agent-cluster",
}


def find_artifact(product_root: Path, artifact_id: str) -> dict[str, Any]:
    for artifact_file in workflow_state_root(product_root).glob("*/artifacts.json"):
        artifacts = load_artifacts(product_root, artifact_file.parent.name)
        for artifact in artifacts:
            if artifact["id"] == artifact_id:
                return artifact
    raise KeyError(artifact_id)


def get_artifact(product_root: Path, repo_root: Path, artifact_id: str) -> dict[str, Any]:
    artifact = find_artifact(product_root, artifact_id)
    workflow = load_workflow(product_root, artifact["workflow_id"])
    project = get_project_by_id(product_root, repo_root, workflow["project_id"])
    content = None
    source = project_root_for(project) / artifact["path"]
    if source.exists():
        content = source.read_text(encoding="utf-8")
    return {"artifact": artifact, "content": content}


def promote_artifact(product_root: Path, repo_root: Path, artifact_id: str, target: str) -> dict[str, Any]:
    if target not in PROMOTE_TARGETS:
        raise ValueError(target)
    artifact = find_artifact(product_root, artifact_id)
    if artifact.get("promotion_status") == "not_promotable" or artifact.get("evidence_level") in {
        "mock",
        "pipeline_contract",
    }:
        raise PermissionError("This artifact is not backed by executable paper outputs and cannot be promoted.")

    workflow = load_workflow(product_root, artifact["workflow_id"])
    project = get_project_by_id(product_root, repo_root, workflow["project_id"])
    project_root = project_root_for(project)
    source = project_root / artifact["path"]
    if not source.exists():
        raise FileNotFoundError(source)

    destination = project_root / PROMOTE_TARGETS[target] / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    artifacts = load_artifacts(product_root, artifact["workflow_id"])
    for item in artifacts:
        if item["id"] == artifact_id:
            item.update(
                {
                    "status": "promoted",
                    "promotion_status": "promoted",
                    "promoted_to": str(destination.relative_to(project_root)),
                    "promoted_at": utc_now(),
                }
            )
            artifact = item
            break
    write_json(artifacts_path(product_root, workflow["id"]), artifacts)
    return {"artifact": artifact}
