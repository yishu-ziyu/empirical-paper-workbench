from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_p18_data_repair_apply import (
    P18_JSON_PATH,
    P18_REVIEW_PATH,
    get_parent_education_wage_p18_data_repair_apply,
    run_parent_education_wage_p18_data_repair_apply,
)


def run_project_product_control_p18_data_repair_apply(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result, _, _ = run_parent_education_wage_p18_data_repair_apply(project_root, payload)
    return attach_product_fields(project, project_root, project_id, result)


def get_project_product_control_p18_data_repair_apply(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    result = get_parent_education_wage_p18_data_repair_apply(project_root)
    return attach_product_fields(project, project_root, project_id, result)


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        **result,
        "project": project_summary(project, project_root),
        "can_refresh": True,
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p18-data-repair-apply",
        "apply_endpoint": f"/api/v1/projects/{project_id}/product-control/p18-data-repair-apply",
        "ledger_path": P18_JSON_PATH.as_posix(),
        "review_path": P18_REVIEW_PATH.as_posix(),
    }

