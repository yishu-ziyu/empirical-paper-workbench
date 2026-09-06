"""Evidence 读模型端点（C2）：main-estimate + 溯源链，一个只读组合面。

北极星「数字先于正文」的读侧：把结论数字（β/SE/p/N）、研究设定、识别
验真、稳健性状态和完整来源链（run → dataset → trace/artifacts）投影成
一个端点。全部数据组合自既有存储——facade state（SessionStore）+
run_store 工件 + RunRepository durable 队列——不建第二存储。

estimate 缺失时返回 ``available=false`` + ``blockers``，不报 500：失败也
要显式，而不是让前端靠猜。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends

from agent.engine.readiness import robustness_ran
from auth import get_optional_user, require_session_ownership
from facade import facade
from run_repository import RunRepository
from routers.run_execution import public_instrument_fields, _public_value
from schemas.responses import (
    EvidenceIdentificationResponse,
    EvidenceProvenanceResponse,
    EvidenceResponse,
    EvidenceRobustnessResponse,
    SnapshotDatasetResponse,
)

import run_store

router = APIRouter()

_TRACE_TAIL_LIMIT = 20


def _dataset_from_entry(entry: dict) -> Optional[SnapshotDatasetResponse]:
    """Dataset metadata from session storage (metadata_json + csv_path)."""
    meta = {
        key: value
        for key, value in entry.items()
        if key not in {"state", "csv_path", "user_id", "charls_config"}
    }
    columns = [str(item) for item in meta.get("columns") or []]
    rows = meta.get("rows") if isinstance(meta.get("rows"), int) else None
    name = meta.get("name") if isinstance(meta.get("name"), str) else None
    if name is None:
        csv_path = entry.get("csv_path")
        if csv_path:
            leaf = Path(str(csv_path)).name
            session_id = (entry.get("state") or {}).get("session_id")
            if leaf != f"{session_id}.csv":
                name = leaf
    return SnapshotDatasetResponse(name=name, rows=rows, columns=columns)


def _evidence_blockers(state: dict) -> list[str]:
    """Why the main estimate is not (yet) usable, in next-step terms.

    ``no_estimate``  — the payload never landed on state;
    ``estimate_failed`` — the node ran but reported status=error;
    ``no_identification`` / ``no_robustness`` — surrounding gates missing.
    """
    blockers: list[str] = []
    estimate = state.get("estimate")
    if not (isinstance(estimate, dict) and estimate.get("produced_by") == "estimate"):
        blockers.append("no_estimate")
    elif estimate.get("status") == "error":
        blockers.append("estimate_failed")
    if not state.get("identification_diag"):
        blockers.append("no_identification")
    if not robustness_ran(state):
        blockers.append("no_robustness")
    return blockers


def _identification(state: dict) -> EvidenceIdentificationResponse:
    diag = state.get("identification_diag") or {}
    report = diag.get("report") if isinstance(diag, dict) else None
    return EvidenceIdentificationResponse(
        star_rating=state.get("star_rating"),
        failed=bool(state.get("identification_failed")),
        report=report if isinstance(report, str) else None,
    )


def _robustness(fields: dict, state: dict) -> EvidenceRobustnessResponse:
    return EvidenceRobustnessResponse(
        status=fields.get("robustness_status"),
        ran=bool(state.get("robustness_results")),
    )


def _provenance(session_id: str) -> EvidenceProvenanceResponse:
    """Combine run_store artifacts with session storage into a source chain."""
    dataset: Optional[SnapshotDatasetResponse] = None
    try:
        dataset = _dataset_from_entry(facade.get_session_entry(session_id))
    except Exception:
        dataset = None

    trace_events = [
        event
        for event in (
            _public_value(item)
            for item in run_store.tail_events(session_id, limit=_TRACE_TAIL_LIMIT)
        )
        if isinstance(event, dict)
    ]
    manifest = _public_value(run_store.read_manifest(session_id))
    artifacts = [
        {"path": item.get("path"), "bytes": item.get("bytes")}
        for item in run_store.list_files(session_id)
        if isinstance(item, dict) and item.get("path")
    ]
    return EvidenceProvenanceResponse(
        dataset=dataset,
        trace_events=trace_events,
        manifest=manifest if isinstance(manifest, dict) else None,
        artifacts=artifacts,
    )


async def _attach_latest_run(
    session_id: str, provenance: EvidenceProvenanceResponse
) -> None:
    """Fill run identity from the durable queue (latest prewrite run)."""
    try:
        run = await RunRepository().latest_run(session_id, kind="prewrite")
    except Exception:
        return
    if run is None:
        return
    provenance.run_id = run.run_id
    provenance.run_status = run.status
    provenance.run_events_url = f"/api/runs/{run.run_id}/events"


@router.get("/sessions/{session_id}/evidence", response_model=EvidenceResponse)
async def get_evidence(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> EvidenceResponse:
    """Project the main-estimate read model plus its full provenance chain."""
    require_session_ownership(session_id, current_user)
    try:
        state = facade.get_state(session_id)
    except Exception:
        state = {}
    if not isinstance(state, dict):
        state = {}

    fields = public_instrument_fields(state)
    estimate = fields.get("estimate")
    available = bool(
        isinstance(estimate, dict)
        and estimate.get("produced_by") == "estimate"
        and estimate.get("status") != "error"
    )
    results = state.get("results")
    provenance = _provenance(session_id)
    await _attach_latest_run(session_id, provenance)

    return EvidenceResponse(
        session_id=session_id,
        available=available,
        blockers=_evidence_blockers(state),
        estimate=estimate if isinstance(estimate, dict) else None,
        results=results if isinstance(results, str) else None,
        claim=fields.get("claim"),
        specification=fields.get("research_direction"),
        identification=_identification(state),
        robustness=_robustness(fields, state),
        provenance=provenance,
    )
