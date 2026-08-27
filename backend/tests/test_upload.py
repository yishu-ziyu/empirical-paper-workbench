"""Contract tests for POST /upload (T-02 red stage).

These tests pin the upload contract from spec §12-§14:
- multipart/form-data CSV file in
- response: {session_id, dataset_meta: {columns, rows, dtypes, missing_count}}

In the red stage the endpoint does not exist, so every test fails on the
status-code assertion (404 from FastAPI's default not-found handler).
"""
from io import BytesIO
from pathlib import Path

COURSE_PANEL_CSV = (
    Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples" / "course-panel.csv"
)


def test_upload_returns_session_id_and_meta(client, sample_csv_path):
    """POST /upload returns session_id + dataset_meta (columns/rows/dtypes/missing_count)."""
    with open(sample_csv_path, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("sample.csv", f, "text/csv")},
        )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
    data = resp.json()
    assert "session_id" in data and isinstance(data["session_id"], str)
    meta = data.get("dataset_meta")
    assert isinstance(meta, dict), f"dataset_meta not a dict: {meta!r}"
    for key in ("columns", "rows", "dtypes", "missing_count"):
        assert key in meta, f"dataset_meta missing key: {key}"


def test_upload_rejects_non_csv(client):
    """POST /upload rejects non-CSV files with HTTP 400."""
    resp = client.post(
        "/upload",
        files={"file": ("notes.txt", BytesIO(b"hello world"), "text/plain")},
    )
    assert resp.status_code == 400, (
        f"expected 400 for non-csv upload, got {resp.status_code}"
    )


def test_upload_course_panel_returns_200_without_checkpoint_db(client, monkeypatch):
    """POST /upload must return 200 when CHECKPOINT_DB_URL is unset (GS-E1).

    Compiling PostgresSaver at graph import used to make facade._graph None
    and this endpoint 503 with 'LangGraph graph not available'.
    """
    monkeypatch.delenv("CHECKPOINT_DB_URL", raising=False)
    from graph import _reset_runtime

    _reset_runtime()
    assert COURSE_PANEL_CSV.is_file(), f"missing sample CSV: {COURSE_PANEL_CSV}"
    with open(COURSE_PANEL_CSV, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("course-panel.csv", f, "text/csv")},
        )
    assert resp.status_code == 200, (
        f"expected 200 without Postgres, got {resp.status_code}: {resp.text}"
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
        )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
    meta = resp.json()["dataset_meta"]
    # sample_csv_path has exactly 1 missing value (income in row 3).
    assert meta["missing_count"] == 1, (
        f"expected 1 missing value, got {meta.get('missing_count')!r}"
    )
