from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_delivery_package import (
    MANIFEST_PATH,
    README_PATH,
    ZIP_PATH,
    get_parent_education_wage_delivery_package,
    run_parent_education_wage_delivery_package,
)


def run_project_product_control_delivery_package(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    manifest, _ = run_parent_education_wage_delivery_package(project_root)
    return attach_product_fields(project, project_root, project_id, manifest)


def get_project_product_control_delivery_package(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    manifest = get_parent_education_wage_delivery_package(project_root)
    return attach_product_fields(project, project_root, project_id, manifest)


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        **manifest,
        "project": project_summary(project, project_root),
        "can_refresh": True,
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/delivery-package",
        "generate_endpoint": f"/api/v1/projects/{project_id}/product-control/delivery-package",
        "artifact_paths": {
            "manifest": MANIFEST_PATH.as_posix(),
            "readme": README_PATH.as_posix(),
            "zip": ZIP_PATH.as_posix(),
        },
    }

