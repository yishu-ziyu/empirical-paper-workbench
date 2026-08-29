"""Contract tests for POST /upload (T-02 red stage).

These tests pin the upload contract from spec §12-§14:
- multipart/form-data file in (CSV / Stata .dta / Excel .xlsx by content sniffing)
- response: {session_id, dataset_meta: {columns, rows, dtypes, missing_count}}

In the red stage the endpoint does not exist, so every test fails on the
status-code assertion (404 from FastAPI's default not-found handler).
"""
from io import BytesIO
from pathlib import Path

COURSE_PANEL_CSV = (
    Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples" / "course-panel.csv"
)

import pandas as pd


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


def test_upload_accepts_stata_dta(client):
    """A real Stata .dta file is parsed by content, not rejected by suffix."""
    df = pd.DataFrame({"gdp": [1.0, 2.0, 3.0], "treat": [0, 1, 1]})
    buf = BytesIO()
    df.to_stata(buf, write_index=False)
    buf.seek(0)
    resp = client.post(
        "/upload",
        files={"file": ("panel.dta", buf, "application/octet-stream")},
    )
    assert resp.status_code == 200, f"expected 200 for .dta, got {resp.status_code}"
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
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
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
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
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
    )
    assert resp.status_code == 200, f"expected 200 for .xlsx, got {resp.status_code}"
    meta = resp.json()["dataset_meta"]
    assert meta["columns"] == ["city", "y"]
    assert meta["rows"] == 2


def test_upload_accepts_gbk_csv(client):
    """CSVs exported by Chinese-market Excel are GBK-encoded and must parse."""
    content = "city,income\n北京,3000\n上海,5000\n".encode("gbk")
    resp = client.post(
        "/upload",
        files={"file": ("gbk.csv", BytesIO(content), "text/csv")},
    )
    assert resp.status_code == 200, f"expected 200 for GBK csv, got {resp.status_code}"
    assert resp.json()["dataset_meta"]["columns"] == ["city", "income"]


def test_upload_accepts_tabular_content_in_txt(client):
    """Content-first: a .txt file holding valid tabular data is accepted."""
    resp = client.post(
        "/upload",
        files={"file": ("notes.txt", BytesIO(b"x,y\n1,2\n"), "text/plain")},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}"


def test_upload_rejects_binary_garbage(client):
    """POST /upload rejects files that are neither xlsx/dta nor decodable text."""
    resp = client.post(
        "/upload",
        files={"file": ("blob.bin", BytesIO(b"\xff\xfe\xff\xfe\xff\xfe"), "application/octet-stream")},
    )
    assert resp.status_code == 400, (
        f"expected 400 for binary garbage, got {resp.status_code}"
    )


def test_upload_course_panel_returns_200_without_checkpoint_db(client, monkeypatch):
    """POST /upload must return 200 when CHECKPOINT_DB_URL is unset (GS-E1).

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
