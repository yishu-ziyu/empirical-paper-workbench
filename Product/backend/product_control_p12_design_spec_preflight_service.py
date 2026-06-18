from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_design_spec_preflight import (
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    build_parent_education_wage_design_spec_preflight,
    run_parent_education_wage_design_spec_preflight,
)


def run_project_product_control_p12_design_spec_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    preflight, _, _ = run_parent_education_wage_design_spec_preflight(project_root)
    return attach_product_fields(project, project_root, project_id, preflight)


def get_project_product_control_p12_design_spec_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / DEFAULT_PREFLIGHT_PATH
    if path.exists():
        preflight = json.loads(path.read_text(encoding="utf-8"))
    else:
        preflight = build_parent_education_wage_design_spec_preflight(project_root)
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
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p12-design-spec-preflight",
        "ledger_path": DEFAULT_PREFLIGHT_PATH.as_posix(),
        "review_path": DEFAULT_REVIEW_PATH.as_posix(),
    }
