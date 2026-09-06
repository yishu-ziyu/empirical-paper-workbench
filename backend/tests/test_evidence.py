"""C1/C2/C5: Project Snapshot + Evidence read model + explicit failure paths.

- C1 ``GET /sessions/{id}`` 是唯一研究状态读模型：dataset 元信息（后端持有）、
  active_run（RunRepository）、degradations 摘要，instrument 字段一个不少。
- C2 ``GET /sessions/{id}/evidence`` 投影 main-estimate + specification +
  identification + robustness + provenance（run_store + RunRepository 组合）；
  estimate 缺失 → available=false + blockers，不报 500。
- C5 estimate 失败显式化：status=error 时 evidence 报 estimate_failed，
  results 章 409 write_blocked（readiness 门不被弱化）。
"""

from __future__ import annotations

import asyncio
import uuid

from conftest import make_state, make_six_chapter_outline, make_write_ready_state
from facade import facade
from run_repository import RunRepository


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def _snapshot(client, sid: str) -> dict:
    resp = client.get(f"/sessions/{sid}")
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# C1 Project Snapshot
# ---------------------------------------------------------------------------


def test_snapshot_keeps_instrument_fields(client):
    sid = _unique("snap-instrument")
    facade.seed_state(
        sid,
        make_write_ready_state(
            write_blockers=["no_literature"],
            outline=make_six_chapter_outline(),
        ),
    )
    data = _snapshot(client, sid)
    assert data["exists"] is True
    for key in (
        "claim",
        "star_rating",
        "identification_failed",
        "identification_report",
        "results",
        "estimate",
        "cleaning_report",
        "literature_source",
        "write_blockers",
        "robustness_status",
        "outline",
        "body_chapters",
        "research_direction",
    ):
        assert key in data, f"snapshot lost instrument field {key}"
    assert data["estimate"]["coef"] == 0.1234
    assert data["research_direction"]["dv"] == "income"


def test_snapshot_exposes_dataset_name_rows_columns_from_backend(client, uploaded_session):
    """上传后 dataset 元信息只在后端：name/rows/columns 全部来自 session 存储。"""
    sid = uploaded_session
    data = _snapshot(client, sid)
    dataset = data["dataset"]
    assert dataset is not None
    assert dataset["name"] == "sample.csv"
    assert dataset["rows"] == 5
    assert dataset["columns"] == ["income", "age", "city"]


def test_snapshot_exposes_active_run_from_run_repository(client):
    sid = _unique("snap-active-run")
    facade.seed_state(sid, make_state())
    assert _snapshot(client, sid)["active_run"] is None

    run = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}},
            idempotency_key=f"{sid}-key",
        )
    )
    try:
        active = _snapshot(client, sid)["active_run"]
        assert active is not None
        assert active["run_id"] == run.run_id
        assert active["kind"] == "prewrite"
        assert active["status"] in {"PENDING", "RUNNING", "RECONCILING"}
    finally:
        asyncio.run(RunRepository().purge_session(sid))


def test_snapshot_exposes_visible_degradations(client):
    sid = _unique("snap-degradations")
    facade.seed_state(sid, make_state())
    facade.record_degradation(
        sid, "review_chapter", "review_llm_unavailable", "mock_review", visible=True
    )
    data = _snapshot(client, sid)
    rows = [item for item in data["degradations"] if item.get("node") == "review_chapter"]
    assert rows, data["degradations"]
    assert rows[0]["reason"] == "review_llm_unavailable"
    assert rows[0]["visible"] is True


# ---------------------------------------------------------------------------
# C2 Evidence read model
# ---------------------------------------------------------------------------


def test_evidence_projects_main_estimate_and_provenance(client):
    sid = _unique("ev-full")
    facade.seed_state(sid, make_write_ready_state())

    run = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}},
            idempotency_key=f"{sid}-key",
        )
    )
    try:
        resp = client.get(f"/sessions/{sid}/evidence")
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["available"] is True
        assert data["blockers"] == []

        est = data["estimate"]
        assert est["status"] == "ok"
        assert est["produced_by"] == "estimate"
        assert est["coef"] == 0.1234
        assert est["se"] == 0.0456
        assert est["p"] == 0.0078
        assert est["n"] == 5
        assert est["estimator"] == "statspai.feols"
        assert est["method"] == "ols"
        assert est["formula"] == "income ~ age"
        assert "age" in est["treatment_row"]

        assert data["specification"]["dv"] == "income"
        assert data["specification"]["iv"] == "age"

        assert data["identification"]["failed"] is False
        assert data["identification"]["report"]
        assert data["robustness"]["ran"] is True

        provenance = data["provenance"]
        assert provenance["run_id"] == run.run_id
        assert provenance["run_status"] in {"PENDING", "RUNNING", "RECONCILING"}
        assert provenance["run_events_url"] == f"/api/runs/{run.run_id}/events"
        assert isinstance(provenance["trace_events"], list)
        assert isinstance(provenance["artifacts"], list)
        assert "manifest" in provenance
    finally:
        asyncio.run(RunRepository().purge_session(sid))


def test_evidence_without_estimate_is_available_false_not_500(client):
    sid = _unique("ev-empty")
    facade.seed_state(sid, make_state())
    resp = client.get(f"/sessions/{sid}/evidence")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["available"] is False
    assert "no_estimate" in data["blockers"]
    assert data["estimate"] is None


def test_evidence_provenance_carries_dataset_from_upload(client, uploaded_session):
    resp = client.get(f"/sessions/{uploaded_session}/evidence")
    assert resp.status_code == 200, resp.text
    dataset = resp.json()["provenance"]["dataset"]
    assert dataset is not None
    assert dataset["name"] == "sample.csv"
    assert dataset["columns"] == ["income", "age", "city"]


# ---------------------------------------------------------------------------
# C5 explicit failure paths
# ---------------------------------------------------------------------------


def test_evidence_marks_failed_estimate_explicitly(client):
    sid = _unique("ev-failed")
    facade.seed_state(
        sid,
        make_write_ready_state(
            estimate={
                "status": "error",
                "produced_by": "estimate",
                "treatment_row": "",
                "method": "iv",
            },
            results="估计失败：缺工具变量。",
        ),
    )
    resp = client.get(f"/sessions/{sid}/evidence")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["available"] is False
    assert "estimate_failed" in data["blockers"]
    assert data["estimate"]["status"] == "error"
    assert "coef" not in data["estimate"] or data["estimate"]["coef"] is None


def test_results_chapter_stays_409_when_estimate_failed(client):
    """C5：估计失败的 session 请求 results 章 → 409 write_blocked。"""
    sid = _unique("ev-failed-write")
    facade.seed_state(
        sid,
        make_write_ready_state(
            estimate={
                "status": "error",
                "produced_by": "estimate",
                "treatment_row": "",
                "method": "iv",
            },
            results="估计失败：缺工具变量。",
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={
            "chapter": {"type": "results", "title": "结果"},
            "render_kwargs": {"results": "FABRICATED"},
        },
    )
    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["write_blocked"] is True
    assert "no_results" in detail["write_blockers"]
