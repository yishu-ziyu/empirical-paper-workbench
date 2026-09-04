"""Shared fixtures for econpaper backend tests.

sys.path setup + mock_llm 已上移至根 conftest.py（ADR-0003 Stage C）。
本文件只保留 backend 专用 fixture：client (FastAPI TestClient)、
sample_csv_path、uploaded_session、s3_enabled。
"""
import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    """Create the shared test schema through the production bootstrap path."""
    if os.getenv("TEST_POSTGRES_DATABASE_URL"):
        # PostgreSQL async connections are bound to their event loop. The
        # dedicated PostgreSQL acceptance owns one loop for bootstrap + test.
        return
    from database import create_tables

    asyncio.run(create_tables())


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


@pytest.fixture(scope="session")
def s3_enabled() -> bool:
    """Check if S3/MinIO is available for integration tests."""
    return bool(os.getenv("S3_ENDPOINT_URL"))


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
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
    if resp.status_code == 202:
        from runner import process_one_run

        accepted = resp.json()
        if asyncio.run(
            process_one_run(
                owner="uploaded-session-fixture",
                run_id=accepted["run_id"],
            )
        ):
            return accepted["session_id"]
    return "red-stage-dummy-session-id"
