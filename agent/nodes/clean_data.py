"""clean_data node -- 8-step orchestrator (ADR-0002).

Iterates the 8 cleaning steps declared as ``CleaningStep`` implementations,
unifies try/except so a single step failure does not block the pipeline, and
aggregates per-step reports into ``cleaning_report.steps``.

HITL is handled at the *graph* layer, not here: this node reads config from
state instead of calling LangGraph ``interrupt()``. Each step is wrapped in
try/except; a failure is recorded as ``status="failed"`` + ``report.error``
and the pipeline continues with the unchanged datasets.

Signature is unchanged from T-02: ``clean_data(state) -> dict``.
"""
from datetime import datetime
from pathlib import Path

from cleaning.audit import AuditStep
from cleaning.balance import BalanceStep
from cleaning.filter import FilterStep
from cleaning.merge import MergeStep
from cleaning.missing import MissingStep
from cleaning.outliers import OutliersStep
from cleaning.profiling import ProfilingStep
from cleaning.step import CleaningStep, StepReport
from cleaning.transform import TransformStep
from protocols import CleanDataOutput
from state import EconPaperState

STEPS: list[CleaningStep] = [
    ProfilingStep(),
    MergeStep(),
    MissingStep(),
    OutliersStep(),
    TransformStep(),
    FilterStep(),
    BalanceStep(),
    AuditStep(),
]


def _step_config(
    state: dict,
    step_name: str,
    order: int,
    workspace: str,
    prev_reports: list,
) -> dict:
    """Build the per-step config dict from state."""
    base = {"workspace": workspace, "order": order}
    if step_name == "missing":
        base["strategy"] = state.get("missing_strategy")
    elif step_name == "outliers":
        base["cuts"] = state.get("outliers_cuts", (5, 95))
    elif step_name == "transform":
        base.update(state.get("transform_config", {}))
    elif step_name == "filter":
        base["conditions"] = state.get("filter_conditions", [])
    elif step_name == "balance":
        base["panel_id"] = state.get("panel_id")
        base["time_col"] = state.get("time_col")
    elif step_name == "audit":
        base["steps"] = prev_reports
    return base


def clean_data(state: EconPaperState) -> CleanDataOutput:
    """Run the 8 cleaning steps in order, aggregating ``cleaning_report.steps``."""
    datasets = state.get("uploaded_datasets", [])
    workspace = state.get("workspace", "/tmp/econpaper_workspace")
    Path(workspace).mkdir(parents=True, exist_ok=True)

    reports: list[StepReport] = []
    for order, step in enumerate(STEPS):
        started_at = datetime.now().isoformat()
        try:
            config = _step_config(state, step.name, order, workspace, reports)
            datasets, report = step.run(datasets, config)
            status = "success"
        except Exception as e:
            report = {"error": str(e)}
            status = "failed"
        duration = (
            datetime.now() - datetime.fromisoformat(started_at)
        ).total_seconds()
        reports.append(
            {
                "name": step.name,
                "status": status,
                "started_at": started_at,
                "duration": duration,
                "report": report,
            }
        )

    return {
        "uploaded_datasets": datasets,
        "cleaned_datasets": datasets,
        "cleaning_report": {"steps": reports},
    }
