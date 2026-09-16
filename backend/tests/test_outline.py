"""Contract tests for T-06: HITL outline endpoints (backend layer).

Agent 节点测试（set_direction / generate_outline）已迁移至
agent/tests/test_generate_outline.py（ADR-0003 Stage C 命名约定）。

本文件只保留 backend endpoint 契约：
- POST /sessions/{id}/direction 接受 {question, dv, iv, controls, method, template}
- POST /sessions/{id}/resume 接受调整后的 outline
"""
import asyncio
import pytest
import uuid

from facade import facade
from runner import process_one_run


def _confirm_and_finish(client, session_id: str) -> dict:
    accepted = client.post(
        f"/sessions/{session_id}/prewrite/confirm",
        json={
            "action": "continue_estimate",
            "table1Confirmed": True,
            "specConfirmed": True,
        },
        headers={"Idempotency-Key": f"confirm-{session_id}"},
    )
    assert accepted.status_code == 202, accepted.text
    run_id = accepted.json()["run_id"]
    assert asyncio.run(
        process_one_run(
            owner="outline-confirm-test",
            run_id=run_id,
        )
    ) is True
    terminal = client.get(f"/runs/{run_id}")
    assert terminal.status_code == 200, terminal.text
    assert terminal.json()["status"] == "SUCCEEDED", terminal.text
    return terminal.json()["result"]


def _post_and_finish(
    client,
    session_id: str,
    payload: dict,
) -> dict:
    accepted = client.post(
        f"/sessions/{session_id}/direction",
        json=payload,
        headers={"Idempotency-Key": f"test-{session_id}"},
    )
    assert accepted.status_code == 202, accepted.text
    run_id = accepted.json()["run_id"]
    assert asyncio.run(
        process_one_run(
            owner="outline-test",
            run_id=run_id,
        )
    ) is True
    terminal = client.get(f"/runs/{run_id}")
    assert terminal.status_code == 200, terminal.text
    assert terminal.json()["status"] == "SUCCEEDED", terminal.text
    return terminal.json()["result"]


@pytest.mark.parametrize("readiness", ["PROCESSING", "FAILED", "CANCELLED"])
def test_direction_rejects_explicit_non_ready_upload_state(client, readiness):
    sid = f"direction-gate-{readiness.lower()}-{uuid.uuid4().hex[:8]}"
    facade.seed_state(
        sid,
        {"csv_path": "/tmp/input.csv", "upload_readiness": readiness},
    )
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json={
                "question": "x on y",
                "dv": "y",
                "iv": "x",
                "controls": [],
                "method": "OLS",
            },
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 409
        assert response.json()["detail"] == {
            "code": "upload_not_ready",
            "upload_readiness": readiness,
        }
    finally:
        facade.drop_session(sid)


@pytest.mark.parametrize("state", [{"upload_readiness": "READY"}, {}])
def test_direction_allows_ready_and_legacy_sessions(client, state):
    sid = f"direction-gate-allowed-{uuid.uuid4().hex[:8]}"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv", **state})
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json={
                "question": "x on y",
                "dv": "y",
                "iv": "x",
                "controls": [],
                "method": "OLS",
            },
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


def test_post_direction_did_missing_statspai_returns_outline(client, tmp_path, monkeypatch):
    """Scout fail: DiD POST /direction must not 500 when `import statspai` raises."""
    import sys

    csv = tmp_path / "panel.csv"
    csv.write_text(
        "y,treat,year,id\n"
        "1.0,0,2000,1\n"
        "1.2,0,2001,1\n"
        "2.0,1,2000,2\n"
        "2.4,1,2001,2\n"
        "1.1,0,2000,3\n"
        "1.3,0,2001,3\n"
        "2.1,1,2000,4\n"
        "2.5,1,2001,4\n",
        encoding="utf-8",
    )
    real_import = __import__

    def blocked(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "statspai" or (isinstance(name, str) and name.startswith("statspai.")):
            raise ModuleNotFoundError("No module named 'statspai'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", blocked)
    monkeypatch.delitem(sys.modules, "statspai", raising=False)
    monkeypatch.setattr(
        "runner.execute_prewrite_supervised",
        facade.execute_prewrite,
    )

    sid = "test-direction-did-no-statspai"
    facade.seed_state(sid, {"csv_path": str(csv)})
    try:
        data = _post_and_finish(
            client,
            sid,
            {
                "question": "treat on y",
                "dv": "y",
                "iv": "treat",
                "controls": [],
                "method": "did",
                "template": "cn_journal",
                "time_col": "year",
                "id_col": "id",
            },
        )
        assert data["identification_failed"] is False
        assert data.get("prewrite_gate") == "awaiting_estimate"
        assert data.get("specification_equation")
        assert not (data.get("estimate") or {}).get("produced_by")
        assert not (data.get("outline") or [])
        continued = _confirm_and_finish(client, sid)
        assert len(continued["outline"]) == 6
        assert any(
            item.get("reason") == "statspai_unavailable"
            for item in (continued.get("degradations") or [])
        )
        assert continued.get("estimate", {}).get("produced_by") == "estimate"
    finally:
        facade.drop_session(sid)


def test_post_direction_runs_identification_without_blocking_ols(client):
    """坐着写路径：提交方向会跑识别；OLS 无套餐不截断，仍出大纲。"""
    sid = "test-direction-ident"
    facade.seed_state(sid, {"csv_path": "/tmp/missing.csv"})
    try:
        data = _post_and_finish(
            client,
            sid,
            {
                "question": "教育对收入的影响",
                "dv": "income",
                "iv": "education",
                "controls": ["age", "gender"],
                "method": "OLS",
                "template": "cn_journal",
            },
        )
        assert data["identification_failed"] is False
        assert data.get("identification_report")
        assert "识别诊断套餐" in data["identification_report"]
        assert data.get("prewrite_gate") == "awaiting_estimate"
        assert data.get("specification_equation")
        assert not (data.get("outline") or [])
        assert not (data.get("estimate") or {}).get("produced_by")
        continued = _confirm_and_finish(client, sid)
        assert len(continued["outline"]) == 6
        assert continued.get("results")
        assert isinstance(continued.get("estimate"), dict)
        assert continued["estimate"].get("produced_by") == "estimate"
        assert continued.get("claim") == "association"
    finally:
        facade.drop_session(sid)


def test_post_direction_endpoint(uploaded_session, client):
    """POST /sessions/{id}/direction 接受研究方向并返回 6 章 outline。"""
    if uploaded_session == "red-stage-dummy-session-id":
        pytest.skip("upload pipeline unavailable in this env (graph/psycopg)")
    data = _post_and_finish(
        client,
        uploaded_session,
        {
            "question": "年龄与收入",
            "dv": "income",
            "iv": "age",
            "controls": [],
            "method": "OLS",
            "template": "cn_journal",
        },
    )
    assert data.get("prewrite_gate") == "awaiting_estimate"
    assert data.get("table1")
    assert data.get("specification_equation")
    assert not (data.get("outline") or [])
    assert not (data.get("estimate") or {}).get("produced_by")
    # research_direction 也应回显
    assert data["research_direction"]["method"] == "OLS"
    # OLS 无识别套餐：不截断，带识别报告
    assert data["identification_failed"] is False
    assert data.get("identification_report")
    assert data.get("claim") == "association"
    continued = _confirm_and_finish(client, uploaded_session)
    outline = continued["outline"]
    assert len(outline) == 6
    types = [ch["type"] for ch in outline]
    assert "intro" in types
    assert "conclusion" in types
    assert continued.get("results")
    assert continued.get("estimate", {}).get("produced_by") == "estimate"
    assert continued["estimate"].get("status") == "ok"
    assert continued.get("literature_source")


def test_get_session_hydrates_instrument_after_direction(client):
    """刷新桌面：GET /sessions/{id} 带回主张、主表、大纲，不要求人再交一次方向。"""
    sid = "test-desk-hydrate"
    facade.seed_state(
        sid,
        {
            "claim": "association",
            "star_rating": None,
            "literature_source": "mock",
            "estimate": {
                "treatment_row": "| age | 0.1234 | 0.0456 | 0.0078 |",
                "produced_by": "estimate",
            },
            "results": "| age | 0.1234 | 0.0456 | 0.0078 |",
            "outline": [{"type": "intro", "title": "引言"}],
            "robustness_results": {"produced_by": "robustness_check"},
        },
    )
    try:
        resp = client.get(f"/sessions/{sid}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["exists"] is True
        assert data["claim"] == "association"
        assert data["star_rating"] is None
        assert data["literature_source"] == "mock"
        assert data["estimate"]["treatment_row"].startswith("| age")
        assert data["robustness_status"] == "ran"
        assert data["outline"][0]["type"] == "intro"
    finally:
        facade.drop_session(sid)


def test_confirm_prewrite_rejects_session_without_direction(client):
    sid = "test-confirm-no-direction"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        resp = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "continue_estimate"},
            headers={"Idempotency-Key": "confirm-empty"},
        )
        assert resp.status_code == 409, resp.text
        assert resp.json()["detail"]["code"] == "prewrite_not_ready"
    finally:
        facade.drop_session(sid)


def test_confirm_prewrite_rejects_zero_star(client):
    sid = "test-confirm-zero-star"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "research_direction": {"question": "q", "dv": "y", "iv": "x"},
            "identification_diag": {"report": "blocked"},
            "identification_failed": True,
            "star_rating": 0,
        },
    )
    try:
        resp = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "continue_estimate"},
            headers={"Idempotency-Key": "confirm-zero"},
        )
        assert resp.status_code == 409, resp.text
        assert resp.json()["detail"]["code"] == "identification_blocked"
    finally:
        facade.drop_session(sid)


def test_get_session_exposes_table1_after_direction_pause(client, tmp_path):
    csv = tmp_path / "desk.csv"
    csv.write_text("income,age\n1,20\n2,30\n", encoding="utf-8")
    sid = "test-desk-table1"
    facade.seed_state(
        sid,
        {
            "csv_path": str(csv),
            "claim": "association",
            "star_rating": 3,
            "identification_diag": {"report": "ok"},
            "research_direction": {"question": "q", "dv": "income", "iv": "age"},
            "main_specification": {
                "method": "ols",
                "formula": "income ~ age",
                "outcome": "income",
                "treatment": "age",
            },
            "table1": {
                "produced_by": "prewrite_preview",
                "columns": ["variable", "count"],
                "rows": [{"variable": "income", "count": 2}],
            },
            "specification_equation": "income = β₀ + β₁ age + ε",
            "prewrite_gate": "awaiting_estimate",
        },
    )
    try:
        resp = client.get(f"/sessions/{sid}")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["prewrite_gate"] == "awaiting_estimate"
        assert data["specification_equation"].startswith("income =")
        assert data["table1"]["produced_by"] == "prewrite_preview"
        assert data["main_specification"]["formula"] == "income ~ age"
        assert data["table1Confirmed"] is False
        assert data["specConfirmed"] is False
        assert data["blockingDecision"]["blocked"] is False
        assert data["blockingDecision"]["isBlock"] is False
    finally:
        facade.drop_session(sid)


def test_confirm_prewrite_requires_both_fe_flags(client):
    sid = "test-confirm-incomplete"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "research_direction": {"question": "q", "dv": "y", "iv": "x"},
            "identification_diag": {"report": "ok"},
            "star_rating": 3,
            "prewrite_gate": "awaiting_estimate",
        },
    )
    try:
        resp = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "continue_estimate", "table1Confirmed": True},
            headers={"Idempotency-Key": "confirm-incomplete"},
        )
        assert resp.status_code == 409, resp.text
        detail = resp.json()["detail"]
        assert detail["code"] == "confirms_incomplete"
        assert detail["table1Confirmed"] is True
        assert detail["specConfirmed"] is False
    finally:
        facade.drop_session(sid)


def test_record_confirms_then_continue_estimate(client, tmp_path, monkeypatch):
    csv = tmp_path / "gate.csv"
    csv.write_text("y,x\n1,2\n3,4\n", encoding="utf-8")
    sid = "test-record-then-continue"
    facade.seed_state(
        sid,
        {
            "csv_path": str(csv),
            "research_direction": {"question": "q", "dv": "y", "iv": "x"},
            "identification_diag": {"report": "ok"},
            "star_rating": 3,
            "prewrite_gate": "awaiting_estimate",
            "main_specification": {
                "method": "ols",
                "formula": "y ~ x",
                "outcome": "y",
                "treatment": "x",
            },
        },
    )
    monkeypatch.setattr("runner.execute_prewrite_supervised", facade.execute_prewrite)
    try:
        table1 = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "record_confirms", "table1Confirmed": True},
            headers={"Idempotency-Key": "record-t1"},
        )
        assert table1.status_code == 200, table1.text
        body = table1.json()
        assert body["table1Confirmed"] is True
        assert body["specConfirmed"] is False
        assert body["blockingDecision"]["isBlock"] is False

        spec = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "record_confirms", "specConfirmed": True},
            headers={"Idempotency-Key": "record-spec"},
        )
        assert spec.status_code == 200, spec.text
        assert spec.json()["specConfirmed"] is True

        accepted = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "continue_estimate"},
            headers={"Idempotency-Key": "continue-after-record"},
        )
        assert accepted.status_code == 202, accepted.text
    finally:
        facade.drop_session(sid)


def test_heterogeneity_without_interaction_blocks_estimate(client):
    sid = "test-hetero-block"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "research_direction": {
                "question": "教育回报是否因地区而异？",
                "dv": "ln_wage",
                "iv": "educ",
                "qType": "heterogeneity",
            },
            "identification_diag": {"report": "ok"},
            "star_rating": 3,
            "prewrite_gate": "awaiting_estimate",
            "main_specification": {
                "method": "ols",
                "formula": "ln_wage ~ educ + region",
                "outcome": "ln_wage",
                "treatment": "educ",
                "controls": ["region"],
            },
            "qType": "heterogeneity",
            "specMode": "level",
        },
    )
    try:
        snap = client.get(f"/sessions/{sid}").json()
        assert snap["blockingDecision"]["blocked"] is True
        assert snap["blockingDecision"]["isBlock"] is True
        assert snap["blockingDecision"]["code"] == "heterogeneity_missing_interaction"
        assert "heterogeneity_missing_interaction" in snap["write_blockers"]

        blocked = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={
                "action": "continue_estimate",
                "table1Confirmed": True,
                "specConfirmed": True,
                "qType": "heterogeneity",
                "specMode": "level",
            },
            headers={"Idempotency-Key": "hetero-block"},
        )
        assert blocked.status_code == 409, blocked.text
        detail = blocked.json()["detail"]
        assert detail["code"] == "estimate_blocked"
        assert detail["blockingDecision"]["isBlock"] is True
        assert "educ×region" in detail["blockingDecision"]["reason"]
    finally:
        facade.drop_session(sid)


def test_heterogeneity_with_interaction_allows_continue(client):
    sid = "test-hetero-ok"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "research_direction": {
                "question": "教育回报是否因地区而异？",
                "dv": "ln_wage",
                "iv": "educ",
                "qType": "heterogeneity",
            },
            "identification_diag": {"report": "ok"},
            "star_rating": 3,
            "prewrite_gate": "awaiting_estimate",
            "main_specification": {
                "method": "ols",
                "formula": "ln_wage ~ educ + educ:region + exper",
                "outcome": "ln_wage",
                "treatment": "educ",
            },
        },
    )
    try:
        accepted = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={
                "action": "continue_estimate",
                "table1Confirmed": True,
                "specConfirmed": True,
                "qType": "heterogeneity",
            },
            headers={"Idempotency-Key": "hetero-ok"},
        )
        assert accepted.status_code == 202, accepted.text
    finally:
        facade.drop_session(sid)


def test_post_resume_endpoint(uploaded_session, client):
    """POST /sessions/{id}/resume 接受调整后的 outline 并写回 session。"""
    if uploaded_session == "red-stage-dummy-session-id":
        pytest.skip("upload pipeline unavailable in this env (graph/psycopg)")
    adjusted = [{"type": "intro", "title": "调整后引言"}]
    resp = client.post(
        f"/sessions/{uploaded_session}/resume",
        json={"outline": adjusted},
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("ok") is True
    # Stage D: response_model=ResumeResponse 会把 outline 规范化为
    # List[OutlineChapterResponse]，每个 item 含 type/title/research_question
    # 三字段（research_question 缺省为 None）。检查关键字段而非整体相等。
    outline = data["outline"]
    assert len(outline) == 1
    assert outline[0]["type"] == "intro"
    assert outline[0]["title"] == "调整后引言"
