"""Contract tests for T-07: POST /sessions/{id}/generate-chapter +
POST /sessions/{id}/approve-chapter.

Pins the T-07 contract from ticket 07-first-chapter-prompts.md:
- POST /sessions/{id}/generate-chapter 接受 {chapter: {type, title}}
  → 跑 generate_chapter 节点 → 返回生成的章节 (status="generated")
- POST /sessions/{id}/approve-chapter 标记章节 status="approved"
- 6 种 chapter_type 都能通过 endpoint 触发

HITL 简化 (同 T-06): 不走 LangGraph interrupt()，router 直接调
generate_chapter 函数。
"""
from __future__ import annotations

# Importing the chapter router triggers its self-registration on main.app.
import routers.chapter  # noqa: F401


def _seed_session_state(client, session_id: str, state: dict) -> None:
    """Helper: seed session state via the direction endpoint (T-06 contract).

    T-06 的 POST /sessions/{id}/direction 写入 research_direction + outline，
    间接为 chapter 生成提供 research_question / data_summary 等字段。
    """
    resp = client.post(
        f"/sessions/{session_id}/direction",
        json={
            "question": state.get("research_question", "教育对收入的影响"),
            "dv": "income",
            "iv": "education",
            "controls": ["age"],
            "method": state.get("method", "OLS"),
            "template": "cn_journal",
        },
    )
    assert resp.status_code == 200, resp.text


def test_generate_chapter_endpoint_returns_generated_chapter(
    uploaded_session, client
):
    """POST /sessions/{id}/generate-chapter 触发 intro 章节生成。"""
    _seed_session_state(client, uploaded_session, {})
    resp = client.post(
        f"/sessions/{uploaded_session}/generate-chapter",
        json={
            "chapter": {"type": "intro", "title": "引言"},
            "render_kwargs": {
                "research_question": "教育对收入的影响",
                "data_summary": "CHARLS 5 列 1000 行",
            },
        },
    )
    assert resp.status_code == 200, f"expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "chapter" in data
    ch = data["chapter"]
    assert ch["type"] == "intro"
    assert ch["status"] == "generated"
    # content 由 generate_chapter.call_llm 占位返回（"Placeholder chapter content from LLM"）
    assert isinstance(ch.get("content"), str) and len(ch["content"]) > 0
    assert "body_chapters" in data
    assert len(data["body_chapters"]) >= 1


def test_approve_chapter_endpoint_marks_approved(uploaded_session, client):
    """POST /sessions/{id}/approve-chapter 标记最后生成章节 status=approved。"""
    _seed_session_state(client, uploaded_session, {})
    # 先生成
    gen = client.post(
        f"/sessions/{uploaded_session}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text
    # 再 approve
    resp = client.post(
        f"/sessions/{uploaded_session}/approve-chapter",
        json={},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["chapter"]["status"] == "approved"
    assert data["chapter"]["type"] == "intro"


def test_approve_chapter_endpoint_with_explicit_type(uploaded_session, client):
    """approve-chapter 支持 chapter_type 参数定位特定章节。"""
    _seed_session_state(client, uploaded_session, {})
    client.post(
        f"/sessions/{uploaded_session}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    client.post(
        f"/sessions/{uploaded_session}/generate-chapter",
        json={"chapter": {"type": "methods", "title": "方法"}},
    )
    resp = client.post(
        f"/sessions/{uploaded_session}/approve-chapter",
        json={"chapter_type": "intro"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["chapter"]["type"] == "intro"
    assert data["chapter"]["status"] == "approved"
    # methods 章节不受影响
    methods_ch = next(
        c for c in data["body_chapters"] if c["type"] == "methods"
    )
    assert methods_ch["status"] == "generated"


def test_generate_chapter_unknown_type_returns_400(uploaded_session, client):
    """未知 chapter_type 触发 ValueError → endpoint 返回 500（FastAPI 默认）。

    这里只断言非 200，不锁死 4xx/5xx，避免限制实现细节。
    """
    _seed_session_state(client, uploaded_session, {})
    resp = client.post(
        f"/sessions/{uploaded_session}/generate-chapter",
        json={"chapter": {"type": "unknown_xyz", "title": "x"}},
    )
    assert resp.status_code != 200, (
        f"unknown chapter_type should not return 200: {resp.text}"
    )


def test_generate_chapter_all_six_types_via_endpoint(uploaded_session, client):
    """6 种 chapter_type 都能通过 endpoint 触发生成（端到端覆盖）。"""
    _seed_session_state(client, uploaded_session, {})
    cases = [
        ("intro", {"research_question": "Q", "data_summary": "D"}),
        ("lit_review", {"research_question": "Q", "key_references": "REF"}),
        ("data_desc", {"data_summary": "D", "eda_results": "EDA"}),
        ("methods", {"method": "OLS", "research_question": "Q"}),
        ("results", {"results": "R", "method": "OLS"}),
        ("conclusion", {"results": "R", "research_question": "Q"}),
    ]
    for chapter_type, kwargs in cases:
        resp = client.post(
            f"/sessions/{uploaded_session}/generate-chapter",
            json={
                "chapter": {"type": chapter_type, "title": chapter_type},
                "render_kwargs": kwargs,
            },
        )
        assert resp.status_code == 200, (
            f"{chapter_type}: expected 200, got {resp.status_code}: {resp.text}"
        )
        ch = resp.json()["chapter"]
        assert ch["type"] == chapter_type
        assert ch["status"] == "generated"


def test_generate_chapter_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.post(
        "/sessions/nonexistent-session/generate-chapter",
        json={"chapter": {"type": "intro", "title": "x"}},
    )
    assert resp.status_code == 404
