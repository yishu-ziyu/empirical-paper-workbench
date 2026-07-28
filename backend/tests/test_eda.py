"""Contract tests for POST /sessions/{id}/eda (T-03 red stage).

These tests pin the EDA sidebar contract from T-03:
- POST /sessions/{id}/eda accepts {action: "describe"|"corr"|"plot"|"scatter"|"regression"|"missing"}
- describe returns a table {columns, rows} with per-variable stats (mean/std/min/max/missing)
- corr returns a correlation matrix {variables, matrix}
- invalid action returns 400
- unknown session returns 404

Red stage: the endpoint does not exist yet, so every test fails on the
status-code assertion (404 from FastAPI's default not-found handler).

sample_csv (from conftest) schema:
    income,age,city
    100,30,Beijing
    200,25,Shanghai
    ,40,Guangzhou   <- missing income
    300,35,Beijing
    150,28,Shenzhen
age mean = (30+25+40+35+28)/5 = 31.6
income mean (present only) = (100+200+300+150)/4 = 187.5
income missing = 1
"""
from __future__ import annotations

# Importing the eda router triggers its self-registration on main.app (see
# routers/eda.py::_self_register). The integration phase will move this
# wiring into main.py explicitly; for T-03 the test imports the module so
# the endpoint is reachable without touching main.py.
import routers.eda  # noqa: F401


def test_eda_describe_returns_stats_table(client, uploaded_session):
    """POST /sessions/{id}/eda {action: "describe"} returns a stats table."""
    resp = client.post(
        f"/sessions/{uploaded_session}/eda",
        json={"action": "describe"},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "columns" in data, f"missing 'columns' in response: {data!r}"
    assert "rows" in data, f"missing 'rows' in response: {data!r}"
    assert isinstance(data["rows"], list) and len(data["rows"]) > 0

    # age row must carry the correct mean (31.6 for sample_csv)
    age_row = next((r for r in data["rows"] if r.get("variable") == "age"), None)
    assert age_row is not None, f"no 'age' row in describe output: {data['rows']!r}"
    assert "mean" in age_row, f"age row missing 'mean' key: {age_row!r}"
    assert abs(float(age_row["mean"]) - 31.6) < 0.01, (
        f"age mean expected 31.6, got {age_row['mean']!r}"
    )


def test_eda_describe_reports_missing_count(client, uploaded_session):
    """describe table reports missing count per variable (income has 1 missing)."""
    resp = client.post(
        f"/sessions/{uploaded_session}/eda",
        json={"action": "describe"},
    )
    assert resp.status_code == 200
    data = resp.json()
    income_row = next((r for r in data["rows"] if r.get("variable") == "income"), None)
    assert income_row is not None, f"no 'income' row: {data['rows']!r}"
    assert "missing" in income_row, f"income row missing 'missing' key: {income_row!r}"
    assert int(income_row["missing"]) == 1, (
        f"income missing expected 1, got {income_row['missing']!r}"
    )


def test_eda_corr_returns_correlation_matrix(client, uploaded_session):
    """POST /eda {action: "corr"} returns a Pearson correlation matrix."""
    resp = client.post(
        f"/sessions/{uploaded_session}/eda",
        json={"action": "corr"},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "matrix" in data, f"missing 'matrix' in corr response: {data!r}"
    assert "variables" in data, f"missing 'variables' in corr response: {data!r}"
    # numeric columns of sample_csv are income + age
    variables = data["variables"]
    assert "age" in variables, f"'age' not in corr variables: {variables!r}"
    matrix = data["matrix"]
    # diagonal must be 1.0
    n = len(variables)
    assert len(matrix) == n, f"matrix rows {len(matrix)} != variables {n}"
    for i in range(n):
        assert abs(float(matrix[i][i]) - 1.0) < 1e-6, (
            f"diagonal [{i}][{i}] expected 1.0, got {matrix[i][i]!r}"
        )


def test_eda_rejects_invalid_action(client, uploaded_session):
    """POST /eda {action: "invalid"} returns 400."""
    resp = client.post(
        f"/sessions/{uploaded_session}/eda",
        json={"action": "invalid"},
    )
    assert resp.status_code == 400, (
        f"expected 400 for invalid action, got {resp.status_code}"
    )


def test_eda_unknown_session_returns_404(client):
    """POST /sessions/{unknown}/eda returns 404."""
    resp = client.post(
        "/sessions/does-not-exist/eda",
        json={"action": "describe"},
    )
    assert resp.status_code == 404, (
        f"expected 404 for unknown session, got {resp.status_code}"
    )
