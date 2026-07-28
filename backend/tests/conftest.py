"""Shared fixtures for econpaper backend tests.

sys.path setup + mock_llm 已上移至根 conftest.py（ADR-0003 Stage C）。
本文件只保留 backend 专用 fixture：client (FastAPI TestClient)、
sample_csv_path、uploaded_session。
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """FastAPI TestClient wired to the backend app.

    Uses the context-manager form so the ASGI lifespan (and the portal
    backing WebSocket test sessions) is active for the duration of each
    test that depends on this fixture.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_csv_path(tmp_path):
    """Write a 5-row CSV to tmp_path.

    Schema: 2 numeric columns (income, age) + 1 categorical column (city).
    Contains exactly 1 missing value (income in row 3) so tests can assert
    dataset_meta.missing_count == 1.
    """
    csv = tmp_path / "sample.csv"
    content = (
        "income,age,city\n"
        "100,30,Beijing\n"
        "200,25,Shanghai\n"
        ",40,Guangzhou\n"  # missing income → 1 missing value
        "300,35,Beijing\n"
        "150,28,Shenzhen\n"
    )
    csv.write_text(content, encoding="utf-8")
    return csv


@pytest.fixture
def uploaded_session(client, sample_csv_path):
    """Upload the sample CSV and return the resulting session_id.

    Red stage: ``POST /upload`` does not exist yet, so the request returns
    a non-200. To keep dependent tests (export / ws) failing on their own
    assertions rather than erroring at fixture setup, this fixture returns
    a sentinel session_id when the endpoint is missing. Once ``/upload``
    is implemented, it returns the real session_id from the response.
    """
    with open(sample_csv_path, "rb") as f:
        resp = client.post(
            "/upload",
            files={"file": ("sample.csv", f, "text/csv")},
        )
    if resp.status_code == 200:
        return resp.json()["session_id"]
    return "red-stage-dummy-session-id"
