from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_final_pdf_export import (
    FINAL_HTML_PATH,
    FINAL_PDF_PATH,
    REPORT_PATH,
    REVIEW_PATH,
    get_parent_education_wage_final_pdf_export,
    run_parent_education_wage_final_pdf_export,
)


def run_project_product_control_final_pdf(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    report = run_parent_education_wage_final_pdf_export(project_root)
    return attach_product_fields(project, project_root, project_id, report)


def get_project_product_control_final_pdf(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    report = get_parent_education_wage_final_pdf_export(project_root)
    return attach_product_fields(project, project_root, project_id, report)


def attach_product_fields(
    project: dict[str, Any],
    project_root: Path,
    project_id: str,
    report: dict[str, Any],
) -> dict[str, Any]:
    return {
        **report,
        "project": project_summary(project, project_root),
        "can_refresh": True,
        "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/final-pdf",
        "generate_endpoint": f"/api/v1/projects/{project_id}/product-control/final-pdf",
        "artifact_paths": {
            "report": REPORT_PATH.as_posix(),
            "review": REVIEW_PATH.as_posix(),
            "html": FINAL_HTML_PATH.as_posix(),
            "pdf": FINAL_PDF_PATH.as_posix(),
        },
    }
