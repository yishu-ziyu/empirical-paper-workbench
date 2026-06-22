from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_p17_data_repair_preflight import (
    P17_JSON_PATH,
    P17_REVIEW_PATH,
    get_parent_education_wage_p17_data_repair_preflight,
    run_parent_education_wage_p17_data_repair_preflight,
)


def run_project_product_control_p17_data_repair_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    preflight, _, _ = run_parent_education_wage_p17_data_repair_preflight(project_root)
    return attach_product_fields(project, project_root, project_id, preflight)


def get_project_product_control_p17_data_repair_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    preflight = get_parent_education_wage_p17_data_repair_preflight(project_root)
    return attach_product_fields(project, project_root, project_id, preflight)


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        **preflight,
        "project": project_summary(project, project_root),
        "can_refresh": True,
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p17-data-repair-preflight",
        "ledger_path": P17_JSON_PATH.as_posix(),
        "review_path": P17_REVIEW_PATH.as_posix(),
    }
