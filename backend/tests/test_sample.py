"""T-05 backend sample router contract tests.

Seams: the three POST endpoints self-registered by ``routers.sample``:
- POST /sessions/{id}/transform  -- sub-step 5
- POST /sessions/{id}/filter      -- sub-step 6
- POST /sessions/{id}/balance     -- sub-step 7

Each test uploads a small CSV, then exercises the endpoint and checks the
response shape. The session store is the in-module ``_sessions`` dict from
``routers.sessions``.
"""
import io

# Importing the sample router triggers its self-registration on main.app
# (see routers/sample.py::_self_register). Matches the eda.py pattern.
import routers.sample  # noqa: F401


def _upload_csv(client):
    """Upload a small panel CSV and return the session_id."""
    csv_bytes = (
        b"id,year,income,age,city,treated,post\n"
        b"1,2018,100,30,Beijing,1,0\n"
        b"1,2020,150,32,Beijing,1,1\n"
        b"2,2018,200,45,Shanghai,0,0\n"
        b"2,2020,250,47,Shanghai,0,1\n"
        b"3,2018,300,60,Guangzhou,1,0\n"
        b"3,2020,350,62,Guangzhou,1,1\n"
    )
    resp = client.post(
        "/upload",
        files={"file": ("panel.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


# --------------------------------------------------------------------------- #
# Sub-step 5: transform
# --------------------------------------------------------------------------- #

def test_transform_log_endpoint(client):
    """POST /transform with type=log_transform creates an income_log column."""
    session_id = _upload_csv(client)

    resp = client.post(
        f"/sessions/{session_id}/transform",
        json={"type": "log_transform", "column": "income"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "constructed_vars" in data
    assert "income_log" in data["constructed_vars"]


# --------------------------------------------------------------------------- #
# Sub-step 6: filter
# --------------------------------------------------------------------------- #

def test_filter_endpoint(client):
    """POST /filter with age>=40 returns before/after counts."""
    session_id = _upload_csv(client)

    resp = client.post(
        f"/sessions/{session_id}/filter",
        json={"conditions": [{"col": "age", "op": ">=", "val": 40}]},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["n_before"] == 6
    assert data["n_after"] == 4  # rows with age 45,47,60,62


# --------------------------------------------------------------------------- #
# Sub-step 7: balance
# --------------------------------------------------------------------------- #

def test_balance_endpoint(client):
    """POST /balance returns balanced / n_periods / attrition_rate."""
    session_id = _upload_csv(client)

    resp = client.post(
        f"/sessions/{session_id}/balance",
        json={"panel_id": "id", "time_col": "year"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["balanced"] == 3
    assert data["n_periods"] == 2
    assert data["attrition_rate"] == 0.0


# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #

def test_balance_missing_params(client):
    """POST /balance without panel_id returns 400."""
    session_id = _upload_csv(client)

    resp = client.post(
        f"/sessions/{session_id}/balance",
        json={"panel_id": "", "time_col": ""},
    )
    assert resp.status_code == 400
