"""Contract tests for POST /sessions/{id}/edit-chapter (T-08c / GS-E4).

Pins the live Copaper refine contract:
- POST /sessions/{id}/edit-chapter 接受 {chapter_index, instruction}
  → 把 instruction 写入 revision_suggestions → 调 generate_chapter
  → 章节正文改写并落盘：随后 GET /sessions/{id} 与 doc-export 看到新正文
- 同一路由也接受 {chapter_index, content}，把用户 markdown 落盘，
  status="edited"，versions[0] 为新正文（不调 LLM）
- 未知 session_id / 越界 chapter_index 返回 404
- 两者都缺返回 400

instruction 路径复用 regenerate 的 generate_chapter 节点，测试与
test_regenerate.py 一样 monkeypatch 假节点，避免真 LLM。
"""
from __future__ import annotations

import routers.chapter  # noqa: F401
import routers.doc_export  # noqa: F401
from facade import facade


def _seed_session(state: dict) -> str:
    import uuid

    sid = f"test-edit-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def _state_one_chapter() -> dict:
    return {
        "title_chapter": {
            "type": "title",
            "title": "教育回报率研究",
            "content": "\\title{教育回报率研究}",
            "status": "generated",
        },
        "body_chapters": [
            {
                "type": "intro",
                "title": "引言",
                "content": "原始引言第一段很长很长。",
                "versions": ["原始引言第一段很长很长。"],
                "status": "generated",
                "chapter_index": 0,
            }
        ],
        "outline": [{"type": "intro", "title": "引言"}],
        "current_chapter_index": 1,
    }


def _mock_generate_with(new_content: str):
    def mock_generate(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["content"] = new_content
            ch["versions"] = [new_content] + list(ch.get("versions") or [])
            ch["status"] = "generated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    return mock_generate


def test_edit_chapter_instruction_applies_via_generate_chapter(monkeypatch, client):
    """Live fail: POST {chapter_index, instruction} 走 generate_chapter 并改章。"""
    sid = _seed_session(_state_one_chapter())
    captured = {}

    def mock_generate(s):
        captured["current_chapter_index"] = s.get("current_chapter_index")
        captured["revision_suggestions"] = list(s.get("revision_suggestions") or [])
        return _mock_generate_with("改短后的引言。")(s)

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "instruction": "把引言第一段写短一点"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    ch = data["chapter"]
    assert ch["content"] == "改短后的引言。"
    assert ch["versions"][0] == "改短后的引言。"
    assert len(ch["versions"]) == 2
    assert captured["current_chapter_index"] == 0
    assert captured["revision_suggestions"]
    assert "把引言第一段写短一点" in captured["revision_suggestions"][0]
    assert "原始引言第一段很长很长。" in captured["revision_suggestions"][0]
    facade.drop_session(sid)


def test_edit_chapter_instruction_saved_on_get_session_and_doc_export(
    monkeypatch, client
):
    """Firstmate lock: POST 之后 GET session 与 doc-export 必须看到新正文。"""
    sid = _seed_session(_state_one_chapter())
    new_text = "改短后的引言，导出必须带上。"
    monkeypatch.setattr(
        "facade.generate_chapter_node", _mock_generate_with(new_text)
    )
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "instruction": "把引言第一段写短一点"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["chapter"]["content"] == new_text

    session = client.get(f"/sessions/{sid}")
    assert session.status_code == 200, session.text
    chapters = session.json()["body_chapters"]
    assert chapters[0]["content"] == new_text
    assert "原始引言第一段很长很长。" not in (chapters[0]["content"] or "")

    tex = client.get(
        f"/sessions/{sid}/doc-export",
        params={"format": "tex", "template": "cn_journal"},
    )
    assert tex.status_code == 200, tex.text
    assert new_text in tex.text
    assert "原始引言第一段很长很长。" not in tex.text
    facade.drop_session(sid)


def test_edit_chapter_content_saved_on_get_session_and_doc_export(
    monkeypatch, client
):
    """save-edit markdown 落盘后，刷新会话与导出都读到新正文。"""
    sid = _seed_session(_state_one_chapter())
    called = {"n": 0}

    def mock_generate(_s):
        called["n"] += 1
        return {}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    edited = "## 研究背景\n\n教育回报是课设题目。"
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "content": edited},
    )
    assert resp.status_code == 200, resp.text
    assert called["n"] == 0
    assert resp.json()["chapter"]["content"] == edited
    assert resp.json()["chapter"]["status"] == "edited"

    session = client.get(f"/sessions/{sid}")
    assert session.status_code == 200, session.text
    assert session.json()["body_chapters"][0]["content"] == edited

    tex = client.get(
        f"/sessions/{sid}/doc-export",
        params={"format": "tex", "template": "cn_journal"},
    )
    assert tex.status_code == 200, tex.text
    assert "教育回报是课设题目。" in tex.text
    facade.drop_session(sid)


def test_edit_chapter_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.post(
        "/sessions/no-such-session/edit-chapter",
        json={"chapter_index": 0, "instruction": "把引言第一段写短一点"},
    )
    assert resp.status_code == 404


def test_edit_chapter_missing_instruction_and_content_returns_400(client):
    """instruction 与 content 都缺 → 400。"""
    sid = _seed_session(_state_one_chapter())
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0},
    )
    assert resp.status_code == 400, resp.text
    facade.drop_session(sid)


def test_edit_chapter_index_out_of_range_returns_404(client):
    """chapter_index 越界返回 404。"""
    sid = _seed_session(_state_one_chapter())
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 5, "instruction": "改短"},
    )
    assert resp.status_code == 404
    facade.drop_session(sid)
