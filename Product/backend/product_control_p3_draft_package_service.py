from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_draft_package import (
    DEFAULT_AUDIT_REPORT_PATH,
    DEFAULT_DOCX_PATH,
    DEFAULT_ISSUE_LIST_PATH,
    DEFAULT_MARKDOWN_PATH,
    DEFAULT_PACKAGE_PATH,
    run_parent_education_wage_draft_package,
)


def run_project_product_control_p3_draft_package(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    package, _ = run_parent_education_wage_draft_package(project_root)
    package["project"] = project_summary(project, project_root)
    package["can_refresh"] = True
    package["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p3-draft-package"
    return package


def get_project_product_control_p3_draft_package(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / DEFAULT_PACKAGE_PATH
    if not path.exists():
        return {
            "status": "p3_draft_package_missing",
            "project": project_summary(project, project_root),
            "can_refresh": True,
            "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p3-draft-package",
            "outputs": {
                "json": DEFAULT_PACKAGE_PATH.as_posix(),
                "markdown": DEFAULT_MARKDOWN_PATH.as_posix(),
                "docx": DEFAULT_DOCX_PATH.as_posix(),
                "issue_list": DEFAULT_ISSUE_LIST_PATH.as_posix(),
                "audit_report": DEFAULT_AUDIT_REPORT_PATH.as_posix(),
            },
            "next_action": "显式刷新 P3 DraftPackage；GET 不会自动生成或写入论文初稿。",
        }
    package = json.loads(path.read_text(encoding="utf-8"))
    package["project"] = project_summary(project, project_root)
    package["can_refresh"] = True
    package["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p3-draft-package"
    return package
