from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_variable_role_preflight import (
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    run_parent_education_wage_variable_role_preflight,
)


def run_project_product_control_p5_variable_role_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    preflight, _, _ = run_parent_education_wage_variable_role_preflight(project_root)
    preflight["project"] = project_summary(project, project_root)
    preflight["can_refresh"] = True
    preflight["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p5-variable-role-preflight"
    return preflight


def get_project_product_control_p5_variable_role_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / DEFAULT_PREFLIGHT_PATH
    if not path.exists():
        return {
            "status": "p5_variable_role_preflight_missing",
            "project": project_summary(project, project_root),
            "can_refresh": True,
            "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p5-variable-role-preflight",
            "ledger_path": DEFAULT_PREFLIGHT_PATH.as_posix(),
            "review_path": DEFAULT_REVIEW_PATH.as_posix(),
            "next_action": "显式刷新 P5 VariableRoleSet 草案预检；GET 不会自动写正式变量角色。",
        }
    preflight = json.loads(path.read_text(encoding="utf-8"))
    preflight["project"] = project_summary(project, project_root)
    preflight["can_refresh"] = True
    preflight["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p5-variable-role-preflight"
    return preflight
