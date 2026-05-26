from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.results_draft_service import project_root_for


FORMAL_SUBMISSION_PACKAGE_SUMMARY_PATH = "state/product/formal_submission_package_summary.json"


class FormalSubmissionPackageSummaryRequiredError(FileNotFoundError):
    pass


def get_project_formal_submission_package_summary(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    path = project_root / FORMAL_SUBMISSION_PACKAGE_SUMMARY_PATH
    if not path.exists():
        raise FormalSubmissionPackageSummaryRequiredError(FORMAL_SUBMISSION_PACKAGE_SUMMARY_PATH)

    summary = json.loads(path.read_text(encoding="utf-8"))
    response = dict(summary)
    response["_meta"] = {
        "evidence_level": "local_file",
        "service": "formal_submission_package_service",
        "mode": "read_only",
        "generated_at": utc_now(),
    }
    response["project_id"] = project_id
    response["summary_path"] = FORMAL_SUBMISSION_PACKAGE_SUMMARY_PATH
    return response
