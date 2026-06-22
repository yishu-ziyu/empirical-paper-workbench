from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def workflow_dashboard_state_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "product-control" / "workflow-dashboard-state.json"


def workflow_dashboard_html_path(repo_root: Path) -> Path:
    return repo_root / "docs" / "product-control" / "workflow-dashboard.html"


def load_workflow_dashboard_state(repo_root: Path) -> dict[str, Any]:
    state_path = workflow_dashboard_state_path(repo_root)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    return {
        **state,
        "state_source": str(state_path.relative_to(repo_root)),
        "state_source_mtime": state_path.stat().st_mtime,
    }
