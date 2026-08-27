"""Contract tests for T-06: HITL outline endpoints (backend layer).

Agent 节点测试（set_direction / generate_outline）已迁移至
agent/tests/test_generate_outline.py（ADR-0003 Stage C 命名约定）。

本文件只保留 backend endpoint 契约：
- POST /sessions/{id}/direction 接受 {question, dv, iv, controls, method, template}
- POST /sessions/{id}/resume 接受调整后的 outline
"""
import pytest

from facade import facade


def test_post_direction_runs_identification_without_blocking_ols(client):
    """坐着写路径：提交方向会跑识别；OLS 无套餐不截断，仍出大纲。"""
    sid = "test-direction-ident"
    facade.seed_state(sid, {"csv_path": "/tmp/missing.csv"})
    try:
        resp = client.post(
            f"/sessions/{sid}/direction",
            json={
                "question": "教育对收入的影响",
                "dv": "income",
                "iv": "education",
                "controls": ["age", "gender"],
                "method": "OLS",
                "template": "cn_journal",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["identification_failed"] is False
        assert data.get("identification_report")
        assert "识别诊断套餐" in data["identification_report"]
        assert len(data["outline"]) == 6
        assert data.get("results")
        assert isinstance(data.get("estimate"), dict)
        assert data["estimate"].get("produced_by") == "estimate"
        assert data.get("claim") == "association"
        entries = data.get("literature_entries") or []
        assert isinstance(entries, list)
        assert entries
        assert "abstract" not in entries[0]
        assert entries[0].get("url") == "" or entries[0]["url"].startswith(
            "https://doi.org/"
        )
        assert entries[0].get("stance") in (None, "支持", "不支持", "说不清")
    finally:
        facade.drop_session(sid)


def test_post_direction_endpoint(uploaded_session, client):
    """POST /sessions/{id}/direction 接受研究方向并返回 6 章 outline。"""
    if uploaded_session == "red-stage-dummy-session-id":
        pytest.skip("upload pipeline unavailable in this env (graph/psycopg)")
    resp = client.post(
        f"/sessions/{uploaded_session}/direction",
        json={
            "question": "年龄与收入",
            "dv": "income",
            "iv": "age",
            "controls": [],
            "method": "OLS",
            "template": "cn_journal",
        },
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
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
    entries = data.get("literature_entries") or []
    assert isinstance(entries, list)
    assert entries, "提交方向后读数台应带回检索到的文献"
    first = entries[0]
    assert "abstract" not in first
    assert first.get("url") == "" or first["url"].startswith("https://doi.org/")
    assert first.get("stance") in (None, "支持", "不支持", "说不清")


def test_get_session_hydrates_instrument_after_direction(client):
    """刷新桌面：GET /sessions/{id} 带回主张、主表、大纲，不要求人再交一次方向。"""
    sid = "test-desk-hydrate"
    facade.seed_state(
        sid,
        {
            "claim": "association",
            "star_rating": None,
            "literature_source": "mock",
            "literature_entries": [
                {
                    "title": "Returns to Education",
                    "authors": ["Zhang"],
                    "year": 2023,
                    "doi": "10.1016/j.jceco.2023.001",
                    "url": "https://doi.org/10.1016/j.jceco.2023.001",
                    "stance": "支持",
                }
            ],
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
        assert data["literature_entries"][0]["url"] == (
            "https://doi.org/10.1016/j.jceco.2023.001"
        )
        assert data["literature_entries"][0]["stance"] == "支持"
        assert "abstract" not in data["literature_entries"][0]
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
