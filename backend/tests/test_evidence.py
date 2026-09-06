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
import hashlib
import uuid

from conftest import make_state, make_six_chapter_outline, make_write_ready_state
from facade import facade
from run_repository import RunRepository

import run_store


async def _succeed_run(run_id: str, result: dict | None = None) -> None:
    repo = RunRepository()
    owner = f"test-{run_id[:8]}"
    claimed = await repo.claim(run_id, owner)
    assert claimed is not None
    await repo.complete(
        run_id,
        owner=owner,
        lease_epoch=claimed.lease_epoch,
        result=result or {},
    )


def _ready_estimate(**extra) -> dict:
    estimate = dict(make_write_ready_state()["estimate"])
    estimate.update(extra)
    return estimate


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def _snapshot(client, sid: str) -> dict:
    resp = client.get(f"/sessions/{sid}")
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# C1 Project Snapshot
# ---------------------------------------------------------------------------


def test_stamp_estimate_producer_only_when_this_run_replaced_estimate():
    from runner import _stamp_estimate_producer

    estimate = {"produced_by": "estimate", "coef": 1}
    unchanged = _stamp_estimate_producer(
        {"estimate": estimate}, "run-new", {"estimate": estimate}
    )
    assert "source_run_id" not in unchanged["estimate"]
    replaced = _stamp_estimate_producer(
        {"estimate": {"produced_by": "estimate", "coef": 2}},
        "run-new",
        {"estimate": estimate},
    )
    assert replaced["estimate"]["source_run_id"] == "run-new"


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
    run = None
    facade.seed_state(sid, make_write_ready_state())
    run = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}},
            idempotency_key=f"{sid}-key",
        )
    )
    facade.seed_state(
        sid,
        make_write_ready_state(estimate=_ready_estimate(source_run_id=run.run_id)),
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
        assert provenance["code"] == []
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


def test_evidence_without_analysis_dataset_does_not_use_upload_metadata(
    client, uploaded_session
):
    """Upload metadata is not the estimate's analysis input."""
    resp = client.get(f"/sessions/{uploaded_session}/evidence")
    assert resp.status_code == 200, resp.text
    assert resp.json()["provenance"]["dataset"] is None


def test_evidence_run_id_follows_older_producer_after_newer_prewrite(client):
    sid = _unique("ev-old-producer")
    facade.seed_state(sid, make_write_ready_state())
    older = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-old",
        )
    )
    asyncio.run(_succeed_run(older.run_id))
    newer = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-new",
        )
    )
    asyncio.run(_succeed_run(newer.run_id, {"claim": "association"}))
    facade.seed_state(
        sid,
        make_write_ready_state(estimate=_ready_estimate(source_run_id=older.run_id)),
    )
    try:
        data = client.get(f"/sessions/{sid}/evidence").json()
        assert data["provenance"]["run_id"] == older.run_id
        assert data["provenance"]["run_id"] != newer.run_id
    finally:
        asyncio.run(RunRepository().purge_session(sid))


def test_evidence_run_id_stays_on_specified_producer_after_later_run(client):
    sid = _unique("ev-specified-producer")
    facade.seed_state(sid, make_write_ready_state())
    bound = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-bound",
        )
    )
    asyncio.run(_succeed_run(bound.run_id))
    later = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-later",
        )
    )
    asyncio.run(_succeed_run(later.run_id, {"literature_source": "mock"}))
    facade.seed_state(
        sid,
        make_write_ready_state(estimate=_ready_estimate(source_run_id=bound.run_id)),
    )
    try:
        data = client.get(f"/sessions/{sid}/evidence").json()
        assert data["provenance"]["run_id"] == bound.run_id
    finally:
        asyncio.run(RunRepository().purge_session(sid))


def test_evidence_dataset_points_at_cleaned_not_raw(client, tmp_path):
    sid = _unique("ev-cleaned-ds")
    raw_path = tmp_path / "raw-upload.csv"
    cleaned_path = tmp_path / "cleaned-analysis.csv"
    raw_path.write_text("income,age\n1,20\n2,21\n", encoding="utf-8")
    cleaned_path.write_text("income,age,treat\n1,20,0\n2,21,1\n3,22,1\n", encoding="utf-8")
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    cleaned_hash = hashlib.sha256(cleaned_path.read_bytes()).hexdigest()
    assert raw_hash != cleaned_hash
    facade.seed_state(
        sid,
        make_write_ready_state(
            csv_path=str(cleaned_path),
            uploaded_datasets=[
                {
                    "name": "raw-upload.csv",
                    "path": str(raw_path),
                    "rows": 2,
                    "columns": ["income", "age"],
                }
            ],
            cleaned_datasets=[
                {
                    "name": "cleaned-analysis.csv",
                    "path": str(cleaned_path),
                    "rows": 3,
                    "columns": ["income", "age", "treat"],
                }
            ],
            estimate=_ready_estimate(
                analysis_dataset={
                    "name": "cleaned-analysis.csv",
                    "path": str(cleaned_path),
                    "hash": cleaned_hash,
                    "role": "cleaned",
                    "rows": 3,
                    "columns": ["income", "age", "treat"],
                }
            ),
        ),
    )
    data = client.get(f"/sessions/{sid}/evidence").json()
    dataset = data["provenance"]["dataset"]
    assert dataset is not None
    assert dataset["path"] == str(cleaned_path)
    assert dataset["hash"] == cleaned_hash
    assert dataset["role"] == "cleaned"
    assert dataset["name"] == "cleaned-analysis.csv"
    assert dataset["path"] != str(raw_path)
    assert dataset["hash"] != raw_hash


def test_evidence_code_artifacts_only_for_producer_run(client):
    sid = _unique("ev-code")
    facade.seed_state(sid, make_write_ready_state())
    producer = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-prod",
        )
    )
    asyncio.run(_succeed_run(producer.run_id))
    other = asyncio.run(
        RunRepository().enqueue(
            session_id=sid,
            kind="prewrite",
            payload={"research_direction": {"method": "OLS"}, "initial_state": {}},
            idempotency_key=f"{sid}-other",
        )
    )
    asyncio.run(_succeed_run(other.run_id))
    run_store.persist_code_translations(
        sid,
        producer.run_id,
        [
            {
                "lang": "py",
                "code": "import pandas as pd\ndf = pd.read_csv('data.csv')\nmodel = smf.ols('y ~ x', data=df).fit()\n",
                "filename": "analysis.py",
            }
        ],
    )
    run_store.persist_code_translations(
        sid,
        other.run_id,
        [
            {
                "lang": "stata",
                "code": 'import delimited "other.csv", clear\nregress y x\n',
                "filename": "analysis.do",
            }
        ],
    )
    facade.seed_state(
        sid,
        make_write_ready_state(estimate=_ready_estimate(source_run_id=producer.run_id)),
    )
    try:
        data = client.get(f"/sessions/{sid}/evidence").json()
        code = data["provenance"]["code"]
        assert code
        assert all(item["run_id"] == producer.run_id for item in code)
        assert any(item["path"].endswith("analysis.py") for item in code)
        assert all("analysis.do" not in item["path"] for item in code)
    finally:
        asyncio.run(RunRepository().purge_session(sid))


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
