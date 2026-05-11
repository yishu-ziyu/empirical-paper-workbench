from __future__ import annotations

from pathlib import Path
from typing import Any


def run_statspai_paper(paper_config: dict[str, Any], dataset_path: Path) -> dict[str, Any]:
    import pandas as pd
    import statspai as sp

    df = pd.read_csv(dataset_path)
    variables = paper_config["data"]["key_variables"]

    kwargs: dict[str, Any] = {
        "y": variables["outcome"][0] if variables["outcome"] else None,
        "treatment": variables["treatment"][0] if variables["treatment"] else None,
        "covariates": variables["controls"] or None,
        "fmt": "markdown",
    }
    if variables["instruments"]:
        kwargs["instrument"] = variables["instruments"][0]

    draft = sp.paper(
        df,
        paper_config["research"]["question"],
        **{key: value for key, value in kwargs.items() if value is not None},
    )

    result_payload = None
    if getattr(draft.workflow, "result", None) is not None:
        result_payload = draft.workflow.result.to_dict()

    return {
        "draft": draft,
        "draft_dict": draft.to_dict(),
        "workflow_design": getattr(draft.workflow, "design", None),
        "workflow_verdict": getattr(getattr(draft.workflow, "diagnostics", None), "verdict", None),
        "robustness_findings": getattr(draft.workflow, "robustness_findings", None),
        "result_payload": result_payload,
    }
