"""Contract tests for durable POST /upload admission.

These tests pin the upload contract from spec §12-§14:
- multipart/form-data file in (CSV / Stata .dta / Excel .xlsx by content sniffing)
- response: {session_id, dataset_meta: {columns, rows, dtypes, missing_count}}

The endpoint returns 202 only after the input, Session, Run, and first event
are durable; cleaning continues in the independent Runner.
"""
import asyncio
import logging
import os
import threading
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

COURSE_PANEL_CSV = (
    Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples" / "course-panel.csv"
)

import pandas as pd
import pytest
from sqlalchemy import select

from facade import facade
from models.research_session import ResearchSession
from run_repository import QueueFull, RunRepository
from upload_artifacts import reconcile_upload_artifacts, reconcile_upload_files


def _upload_headers(key: str | None = None) -> dict[str, str]:
    return {"Idempotency-Key": key or str(uuid.uuid4())}


@pytest.fixture(autouse=True)
def cleanup_sessions_created_by_upload_tests():
    async def ids() -> set[str]:
        repo = RunRepository()
        async with repo._factory() as db:
            return set(await db.scalars(select(ResearchSession.session_id)))

    before = asyncio.run(ids())
    yield
    for session_id in asyncio.run(ids()) - before:
        facade.delete_session(session_id)


def test_upload_returns_session_id_and_meta(client, sample_csv_path):
    """POST /upload returns session_id + dataset_meta (columns/rows/dtypes/missing_count)."""
    with open(sample_csv_path, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("sample.csv", f, "text/csv")},
            headers=_upload_headers(),
        )
    assert resp.status_code == 202, f"expected 202, got {resp.status_code}"
    data = resp.json()
    assert "session_id" in data and isinstance(data["session_id"], str)
    assert data["status"] == "PENDING"
    assert data["run_id"]
    assert data["events_url"] == f"/api/runs/{data['run_id']}/events"
    meta = data.get("dataset_meta")
    assert isinstance(meta, dict), f"dataset_meta not a dict: {meta!r}"
    for key in ("columns", "rows", "dtypes", "missing_count"):
        assert key in meta, f"dataset_meta missing key: {key}"


def test_upload_returns_before_graph_or_cleaning(client, tmp_path, monkeypatch):
    """The API admits durable work and never executes the upload graph."""
    from routers import sessions

    def should_not_run(*_args, **_kwargs):
        raise AssertionError("upload graph/cleaning must not run in the API process")

    monkeypatch.setattr(sessions.settings, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(sessions.settings, "S3_ENDPOINT_URL", None)
    monkeypatch.setattr(
        sessions.facade,
        "run_upload_pipeline",
        should_not_run,
    )
    response = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x,y\n1,2\n"), "text/csv")},
        headers=_upload_headers(),
    )
    assert response.status_code == 202, response.text
    facade.delete_session(response.json()["session_id"])


def test_upload_accepts_stata_dta(client):
    """A real Stata .dta file is parsed by content, not rejected by suffix."""
    df = pd.DataFrame({"gdp": [1.0, 2.0, 3.0], "treat": [0, 1, 1]})
    buf = BytesIO()
    df.to_stata(buf, write_index=False)
    buf.seek(0)
    resp = client.post(
        "/upload",
        files={"file": ("panel.dta", buf, "application/octet-stream")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202 for .dta, got {resp.status_code}"
    meta = resp.json()["dataset_meta"]
    assert meta["columns"] == ["gdp", "treat"]
    assert meta["rows"] == 3


def test_upload_accepts_dta_without_extension_hint(client):
    """Stata 117+ has a text header, so .dta content is detected even misnamed .csv."""
    df = pd.DataFrame({"x": [1.0, 2.0]})
    buf = BytesIO()
    df.to_stata(buf, write_index=False, version=117)
    buf.seek(0)
    resp = client.post(
        "/upload",
        files={"file": ("misnamed.csv", buf, "text/csv")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202, got {resp.status_code}"
    assert resp.json()["dataset_meta"]["columns"] == ["x"]


def test_upload_accepts_old_dta_via_suffix(client):
    """Old-format .dta (≤115) has no text header; the filename is the fallback hint."""
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    buf = BytesIO()
    df.to_stata(buf, write_index=False, version=114)
    buf.seek(0)
    resp = client.post(
        "/upload",
        files={"file": ("old.dta", buf, "application/octet-stream")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202, got {resp.status_code}"
    assert resp.json()["dataset_meta"]["columns"] == ["x"]


def test_upload_accepts_xlsx(client):
    """An Excel workbook is parsed by content (zip/PK header), first sheet."""
    df = pd.DataFrame({"city": ["a", "b"], "y": [1.5, 2.5]})
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    buf.seek(0)
    resp = client.post(
        "/upload",
        files={"file": ("data.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202 for .xlsx, got {resp.status_code}"
    meta = resp.json()["dataset_meta"]
    assert meta["columns"] == ["city", "y"]
    assert meta["rows"] == 2


def test_upload_accepts_gbk_csv(client):
    """CSVs exported by Chinese-market Excel are GBK-encoded and must parse."""
    content = "city,income\n北京,3000\n上海,5000\n".encode("gbk")
    resp = client.post(
        "/upload",
        files={"file": ("gbk.csv", BytesIO(content), "text/csv")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202 for GBK csv, got {resp.status_code}"
    assert resp.json()["dataset_meta"]["columns"] == ["city", "income"]


def test_upload_accepts_tabular_content_in_txt(client):
    """Content-first: a .txt file holding valid tabular data is accepted."""
    resp = client.post(
        "/upload",
        files={"file": ("notes.txt", BytesIO(b"x,y\n1,2\n"), "text/plain")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 202, f"expected 202, got {resp.status_code}"


def test_upload_rejects_binary_garbage(client):
    """POST /upload rejects files that are neither xlsx/dta nor decodable text."""
    resp = client.post(
        "/upload",
        files={"file": ("blob.bin", BytesIO(b"\xff\xfe\xff\xfe\xff\xfe"), "application/octet-stream")},
        headers=_upload_headers(),
    )
    assert resp.status_code == 400, (
        f"expected 400 for binary garbage, got {resp.status_code}"
    )


def test_upload_rejects_chunked_body_over_limit_without_retaining_artifacts(
    client,
    tmp_path,
    monkeypatch,
):
    """The in-process scan enforces the limit even without Content-Length."""
    from routers import sessions

    monkeypatch.setattr(sessions.settings, "MAX_UPLOAD_SIZE_MB", 1)
    monkeypatch.setattr(sessions.settings, "UPLOAD_DIR", tmp_path)
    boundary = "econpaper-bounded-upload"
    prefix = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="large.csv"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode()
    suffix = f"\r\n--{boundary}--\r\n".encode()
    body = prefix + b"x\n" + (b"1\n" * (600 * 1024)) + suffix

    response = client.post(
        "/upload",
        content=(body[offset : offset + 64 * 1024] for offset in range(0, len(body), 64 * 1024)),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Idempotency-Key": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 413
    assert list(tmp_path.rglob("*")) == []


def test_upload_openapi_requires_capability_and_documents_recovery_errors(client):
    spec = client.app.openapi()
    upload = spec["paths"]["/upload"]["post"]
    resolve = spec["paths"]["/upload/resolve"]["post"]

    upload_key = next(
        parameter
        for parameter in upload["parameters"]
        if parameter["name"] == "Idempotency-Key"
    )
    resolve_key = next(
        parameter
        for parameter in resolve["parameters"]
        if parameter["name"] == "Idempotency-Key"
    )
    assert upload_key["required"] is True
    assert resolve_key["required"] is True
    assert {"409", "429"}.issubset(upload["responses"])
    assert "Retry-After" in upload["responses"]["429"]["headers"]
    assert {"404", "503"}.issubset(resolve["responses"])


def test_debug_sql_logs_hide_anonymous_upload_capability(client, caplog, monkeypatch):
    from routers import sessions

    canary = "11111111-1111-4111-8111-111111111111"
    monkeypatch.setattr(sessions.settings, "DEBUG", True)
    caplog.set_level(logging.INFO, logger="sqlalchemy.engine.Engine")

    accepted = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x,y\n1,2\n"), "text/csv")},
        headers={"Idempotency-Key": canary},
    )
    assert accepted.status_code == 202
    resolved = client.post(
        "/upload/resolve",
        headers={"Idempotency-Key": canary},
    )
    assert resolved.status_code == 202

    engine_logs = "\n".join(
        record.getMessage()
        for record in caplog.records
        if record.name.startswith("sqlalchemy.engine")
    )
    assert canary not in engine_logs


def test_session_lookup_keeps_event_loop_responsive(monkeypatch):
    from routers import sessions

    release = threading.Event()
    started = threading.Event()

    def blocking_ownership(*_args):
        started.set()
        assert release.wait(timeout=1)

    monkeypatch.setattr(sessions, "require_session_ownership", blocking_ownership)
    monkeypatch.setattr(sessions.facade, "get_csv_path", lambda _session_id: None)
    monkeypatch.setattr(sessions.facade, "get_state", lambda _session_id: {})

    async def scenario():
        lookup = asyncio.create_task(sessions.get_session_info("session-1", None))
        assert await asyncio.to_thread(started.wait, 1)
        await asyncio.sleep(0)
        release.set()
        result = await asyncio.wait_for(lookup, timeout=1)
        assert result.session_id == "session-1"

    asyncio.run(scenario())


def test_s3_publication_is_removed_when_session_deletion_wins(monkeypatch):
    from routers import sessions

    session_id = facade.create_session()
    started = threading.Event()
    release = threading.Event()
    deleted: list[str] = []

    class BlockingS3:
        def upload_bytes(self, _data: bytes, _remote_path: str):
            started.set()
            assert release.wait(timeout=1)

        def delete(self, remote_path: str):
            deleted.append(remote_path)
            return True

    monkeypatch.setattr(sessions, "s3_fs", BlockingS3())
    worker = threading.Thread(
        target=sessions._sync_upload_to_s3,
        args=(session_id, b"x\n1\n"),
    )
    worker.start()
    assert started.wait(timeout=1)
    assert facade.delete_session(session_id) is True
    release.set()
    worker.join(timeout=1)

    assert not worker.is_alive()
    assert deleted == [f"{session_id}/data.csv"]
    assert facade.has_session(session_id) is False


def test_upload_course_panel_returns_202_without_checkpoint_db(client, monkeypatch):
    """POST /upload must return 202 when CHECKPOINT_DB_URL is unset (GS-E1).

    Compiling PostgresSaver at graph import used to make facade._graph None
    and this endpoint 503 with 'LangGraph graph not available'.
    """
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    from agent.graph import _reset_runtime

    _reset_runtime()
    assert COURSE_PANEL_CSV.is_file(), f"missing sample CSV: {COURSE_PANEL_CSV}"
    with open(COURSE_PANEL_CSV, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("course-panel.csv", f, "text/csv")},
            headers=_upload_headers(),
        )
    assert resp.status_code == 202, (
        f"expected 202 without Postgres, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    assert isinstance(data.get("session_id"), str) and data["session_id"]
    meta = data.get("dataset_meta")
    assert isinstance(meta, dict)
    for key in ("columns", "rows", "dtypes", "missing_count"):
        assert key in meta, f"dataset_meta missing key: {key}"


def test_upload_detects_missing_values(client, sample_csv_path):
    """dataset_meta.missing_count reflects the number of missing values in the CSV."""
    with open(sample_csv_path, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("sample.csv", f, "text/csv")},
            headers=_upload_headers(),
        )
    assert resp.status_code == 202, f"expected 202, got {resp.status_code}"
    meta = resp.json()["dataset_meta"]
    # sample_csv_path has exactly 1 missing value (income in row 3).
    assert meta["missing_count"] == 1, (
        f"expected 1 missing value, got {meta.get('missing_count')!r}"
    )


def test_upload_durable_acceptance_is_readable_before_202(client, tmp_path, monkeypatch):
    from models.research_session import ResearchSession

    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    response = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x,y\n1,2\n"), "text/csv")},
        headers=_upload_headers(),
    )
    assert response.status_code == 202, response.text
    accepted = response.json()

    async def inspect():
        repo = RunRepository()
        run = await repo.get(accepted["run_id"])
        events = await repo.events_after(accepted["run_id"], 0)
        async with repo._factory() as db:
            session = await db.get(ResearchSession, accepted["session_id"])
        return run, events, session

    run, events, session = asyncio.run(inspect())
    try:
        assert run is not None and run.kind == "upload_pipeline"
        assert run.status == "PENDING"
        assert session is not None
        assert session.state["upload_readiness"] == "PROCESSING"
        assert Path(session.csv_path).read_bytes() == b"x,y\n1,2\n"
        assert [(event.seq, event.event_type) for event in events] == [
            (1, "run.accepted")
        ]
    finally:
        facade.delete_session(accepted["session_id"])


@pytest.mark.parametrize(
    "key",
    [None, "not-a-uuid", str(uuid.uuid1()), str(uuid.uuid3(uuid.NAMESPACE_DNS, "x"))],
)
def test_upload_rejects_missing_or_non_v4_key_without_side_effects(
    client, tmp_path, monkeypatch, key
):
    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    headers = {} if key is None else _upload_headers(key)
    response = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
        headers=headers,
    )
    assert response.status_code == 422
    assert list(tmp_path.rglob("*.csv")) == []


def test_upload_retry_and_resolve_return_original_ids_without_duplicates(
    client, tmp_path, monkeypatch
):
    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    key = str(uuid.uuid4())

    def post():
        return client.post(
            "/upload",
            files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
            headers=_upload_headers(key),
        )

    first = post()
    second = post()
    resolved = client.post("/upload/resolve", headers=_upload_headers(key))
    assert first.status_code == second.status_code == resolved.status_code == 202
    assert {
        (item.json()["session_id"], item.json()["run_id"])
        for item in (first, second, resolved)
    } == {(first.json()["session_id"], first.json()["run_id"])}
    assert len(list(tmp_path.glob("*.csv"))) == 1
    assert list((tmp_path / ".staging").glob("*.csv")) == []
    facade.delete_session(first.json()["session_id"])


def test_upload_key_conflict_is_non_disclosing_and_cleans_loser(
    client, tmp_path, monkeypatch
):
    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    key = str(uuid.uuid4())
    first = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
        headers=_upload_headers(key),
    )
    conflict = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x\n2\n"), "text/csv")},
        headers=_upload_headers(key),
    )
    assert first.status_code == 202
    assert conflict.status_code == 409
    body = conflict.text
    assert first.json()["session_id"] not in body
    assert first.json()["run_id"] not in body
    assert len(list(tmp_path.glob("*.csv"))) == 1
    facade.delete_session(first.json()["session_id"])


@pytest.mark.parametrize("failure", [QueueFull("full"), RuntimeError("tx failed")])
def test_upload_admission_failure_cleans_promoted_file(
    client, tmp_path, monkeypatch, failure
):
    async def fail(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(RunRepository, "admit_upload", fail)
    if isinstance(failure, QueueFull):
        response = client.post(
            "/upload",
            files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
            headers=_upload_headers(),
        )
        assert response.status_code == 429
    else:
        response = client.post(
            "/upload",
            files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
            headers=_upload_headers(),
        )
        assert response.status_code == 500
        assert "tx failed" not in response.text
    assert list(tmp_path.rglob("*.csv")) == []


def test_reconciliation_removes_only_old_unreferenced_managed_uploads(tmp_path):
    old_orphan = tmp_path / f"{uuid.uuid4()}.csv"
    referenced = tmp_path / f"{uuid.uuid4()}.csv"
    fresh_orphan = tmp_path / f"{uuid.uuid4()}.csv"
    unrelated = tmp_path / "human-source.csv"
    staging = tmp_path / ".staging" / f"{uuid.uuid4()}.csv"
    staging.parent.mkdir()
    for path in (old_orphan, referenced, fresh_orphan, unrelated, staging):
        path.write_text("x\n1\n", encoding="utf-8")
    old = datetime.now(timezone.utc) - timedelta(hours=1)
    for path in (old_orphan, referenced, unrelated, staging):
        os.utime(path, (old.timestamp(), old.timestamp()))

    removed = reconcile_upload_files(
        {referenced.resolve()},
        upload_dir=tmp_path,
        now=datetime.now(timezone.utc),
        grace_seconds=900,
    )

    assert set(removed) == {old_orphan, staging}
    assert not old_orphan.exists() and not staging.exists()
    assert referenced.exists() and fresh_orphan.exists() and unrelated.exists()


def test_reconciliation_refuses_symlink_and_path_escape(tmp_path):
    outside = tmp_path.parent / f"{uuid.uuid4()}.csv"
    outside.write_text("private\n", encoding="utf-8")
    link = tmp_path / f"{uuid.uuid4()}.csv"
    link.symlink_to(outside)
    old = datetime.now(timezone.utc) - timedelta(hours=1)
    os.utime(outside, (old.timestamp(), old.timestamp()))
    try:
        assert reconcile_upload_files(
            set(),
            upload_dir=tmp_path,
            now=datetime.now(timezone.utc),
            grace_seconds=0,
        ) == []
        assert outside.read_text(encoding="utf-8") == "private\n"
        assert link.is_symlink()
    finally:
        link.unlink(missing_ok=True)
        outside.unlink(missing_ok=True)


def test_reconciliation_uses_primary_session_references(tmp_path, monkeypatch):
    referenced_id = str(uuid.uuid4())
    orphan_id = str(uuid.uuid4())
    referenced = tmp_path / f"{referenced_id}.csv"
    orphan = tmp_path / f"{orphan_id}.csv"
    referenced.write_text("x\n1\n", encoding="utf-8")
    orphan.write_text("x\n2\n", encoding="utf-8")
    old = datetime.now(timezone.utc) - timedelta(hours=1)
    for path in (referenced, orphan):
        os.utime(path, (old.timestamp(), old.timestamp()))
    facade.seed_state(
        referenced_id,
        {"csv_path": str(referenced), "uploaded_datasets": [{"path": str(referenced)}]},
    )
    monkeypatch.setattr("upload_artifacts.settings.UPLOAD_DIR", tmp_path)
    try:
        removed = asyncio.run(
            reconcile_upload_artifacts(
                upload_dir=tmp_path,
                now=datetime.now(timezone.utc),
                grace_seconds=900,
            )
        )
        assert removed == [orphan]
        assert referenced.exists()
        assert not orphan.exists()
    finally:
        facade.drop_session(referenced_id)


def test_s3_failure_is_a_stable_visible_local_degradation(
    client, tmp_path, monkeypatch
):
    def fail_remote(*_args, **_kwargs):
        raise RuntimeError("secret-token at s3://private-bucket")

    monkeypatch.setattr("routers.sessions.settings.UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        "routers.sessions.settings.S3_ENDPOINT_URL", "http://unavailable.invalid"
    )
    monkeypatch.setattr("routers.sessions.s3_fs.upload_bytes", fail_remote)
    response = client.post(
        "/upload",
        files={"file": ("sample.csv", BytesIO(b"x\n1\n"), "text/csv")},
        headers=_upload_headers(),
    )
    assert response.status_code == 202, response.text
    degradations = facade.get_degradations(response.json()["session_id"])
    assert any(
        item.get("node") == "upload"
        and item.get("reason") == "remote_storage_unavailable"
        and item.get("fallback") == "local_fs"
        and item.get("visible") is True
        for item in degradations
    )
    assert "secret-token" not in response.text
    assert "private-bucket" not in response.text
