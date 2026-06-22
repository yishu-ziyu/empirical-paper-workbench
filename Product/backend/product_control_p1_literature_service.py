from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id
from Program.workbench.parent_education_wage_literature_evidence_ledger import (
    DEFAULT_LEDGER_PATH,
    DEFAULT_REVIEW_PATH,
    build_parent_education_wage_literature_evidence_ledger,
    write_parent_education_wage_literature_evidence_ledger,
)


def run_project_product_control_p1_literature_ledger(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    ledger = build_parent_education_wage_literature_evidence_ledger(project_root)
    write_parent_education_wage_literature_evidence_ledger(project_root, ledger)
    ledger["project"] = project_summary(project, project_root)
    ledger["can_refresh"] = True
    ledger["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p1-literature-ledger"
    return ledger


def get_project_product_control_p1_literature_ledger(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / DEFAULT_LEDGER_PATH
    if not path.exists():
        return {
            "status": "p1a_literature_ledger_missing",
            "project": project_summary(project, project_root),
            "can_refresh": True,
            "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p1-literature-ledger",
            "ledger_path": DEFAULT_LEDGER_PATH.as_posix(),
            "review_path": DEFAULT_REVIEW_PATH.as_posix(),
            "next_action": "显式刷新 P1-A 文献证据账本；GET 不会自动生成或写入产物。",
        }
    ledger = json.loads(path.read_text(encoding="utf-8"))
    ledger["project"] = project_summary(project, project_root)
    ledger["can_refresh"] = True
    ledger["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p1-literature-ledger"
    return ledger
