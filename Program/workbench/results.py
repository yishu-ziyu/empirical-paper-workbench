from __future__ import annotations

from pathlib import Path
from typing import Any


def artifact_record(path: Path, project_root: Path, kind: str, description: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "path": str(path.relative_to(project_root)),
        "description": description,
        "exists": path.exists(),
    }


def build_results_index(
    project_slug: str,
    mode: str,
    stage: str,
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "project_slug": project_slug,
        "mode": mode,
        "current_stage": stage,
        "artifacts": artifacts,
    }

