from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_p13_p16_demo_closure import (
    P13_JSON_PATH,
    P13_REVIEW_PATH,
    P14_JSON_PATH,
    P14_REVIEW_PATH,
    P15_ISSUE_LIST_PATH,
    P15_JSON_PATH,
    P15_REVIEW_PATH,
    P16_JSON_PATH,
    P16_REVIEW_PATH,
    get_parent_education_wage_p13_p16_demo_closure,
    run_parent_education_wage_p13_p16_demo_closure,
)


def run_project_product_control_p13_p16_demo_closure(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    closure, _ = run_parent_education_wage_p13_p16_demo_closure(project_root)
    return attach_product_fields(project, project_root, project_id, closure)


def get_project_product_control_p13_p16_demo_closure(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    closure = get_parent_education_wage_p13_p16_demo_closure(project_root)
    return attach_product_fields(project, project_root, project_id, closure)


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    closure: dict[str, Any],
) -> dict[str, Any]:
    return {
        **closure,
        "project": project_summary(project, project_root),
        "can_refresh": True,
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p13-p16-demo-closure",
        "artifact_paths": {
            "p13_json": P13_JSON_PATH.as_posix(),
            "p13_review": P13_REVIEW_PATH.as_posix(),
            "p14_json": P14_JSON_PATH.as_posix(),
            "p14_review": P14_REVIEW_PATH.as_posix(),
            "p15_json": P15_JSON_PATH.as_posix(),
            "p15_review": P15_REVIEW_PATH.as_posix(),
            "p15_issue_list": P15_ISSUE_LIST_PATH.as_posix(),
            "p16_json": P16_JSON_PATH.as_posix(),
            "p16_review": P16_REVIEW_PATH.as_posix(),
        },
    }
