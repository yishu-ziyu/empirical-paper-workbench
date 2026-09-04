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
        assert len(data["outline"]) == 6
        assert any(
            item.get("reason") == "statspai_unavailable"
            for item in (data.get("degradations") or [])
        )
        assert data.get("estimate", {}).get("produced_by") == "estimate"
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
        assert len(data["outline"]) == 6
        assert data.get("results")
        assert isinstance(data.get("estimate"), dict)
        assert data["estimate"].get("produced_by") == "estimate"
        assert data.get("claim") == "association"
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
    assert "outline" in data
    outline = data["outline"]
    assert len(outline) == 6
    types = [ch["type"] for ch in outline]
    assert "intro" in types
    assert "conclusion" in types
    # research_direction 也应回显
    assert data["research_direction"]["method"] == "OLS"
    # OLS 无识别套餐：不截断，带识别报告
    assert data["identification_failed"] is False
    assert data.get("identification_report")
    assert data.get("results")
    assert data.get("estimate", {}).get("produced_by") == "estimate"
    assert data["estimate"].get("status") == "ok"
    assert data.get("claim") == "association"
    assert data.get("literature_source")


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
