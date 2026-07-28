"""Contract tests for T-06: HITL outline endpoints (backend layer).

Agent 节点测试（set_direction / generate_outline）已迁移至
agent/tests/test_generate_outline.py（ADR-0003 Stage C 命名约定）。

本文件只保留 backend endpoint 契约：
- POST /sessions/{id}/direction 接受 {question, dv, iv, controls, method, template}
- POST /sessions/{id}/resume 接受调整后的 outline
"""
import pytest


def test_post_direction_endpoint(uploaded_session, client):
    """POST /sessions/{id}/direction 接受研究方向并返回 6 章 outline。"""
    resp = client.post(
        f"/sessions/{uploaded_session}/direction",
        json={
            "question": "教育对收入的影响",
            "dv": "income",
            "iv": "education",
            "controls": ["age", "gender"],
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


def test_post_resume_endpoint(uploaded_session, client):
    """POST /sessions/{id}/resume 接受调整后的 outline 并写回 session。"""
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
