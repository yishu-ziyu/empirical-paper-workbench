"""Contract tests for POST /sessions/{id}/edit-chapter (T-08c / GS-E4).

Pins the live Copaper refine contract:
- POST /sessions/{id}/edit-chapter 接受 {chapter_index, instruction}
  → 把 instruction 写入 revision_suggestions → 调 generate_chapter
  → 返回更新后的章节并持久化（后续导出读 content）
- 同一路由也接受 {chapter_index, content}，把用户 markdown 落盘，
  status="edited"，versions[0] 为新正文（不调 LLM）
- 未知 session_id / 越界 chapter_index 返回 404
- 两者都缺返回 400

instruction 路径复用 regenerate 的 generate_chapter 节点，测试与
test_regenerate.py 一样 monkeypatch 假节点，避免真 LLM。
"""
from __future__ import annotations

import routers.chapter  # noqa: F401
from facade import facade


def _seed_session(state: dict) -> str:
    import uuid

    sid = f"test-edit-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def _state_one_chapter() -> dict:
    return {
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


def test_edit_chapter_instruction_applies_via_generate_chapter(monkeypatch, client):
    """Live fail: POST {chapter_index, instruction} 走 generate_chapter 并改章。"""
    sid = _seed_session(_state_one_chapter())
    captured = {}

    def mock_generate(s):
        captured["current_chapter_index"] = s.get("current_chapter_index")
        captured["revision_suggestions"] = list(s.get("revision_suggestions") or [])
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            new_content = "改短后的引言。"
            versions = [new_content] + list(ch.get("versions") or [])
            ch["content"] = new_content
            ch["versions"] = versions
            ch["status"] = "generated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

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


def test_edit_chapter_instruction_persists_for_later_export(monkeypatch, client):
    """refine 后 session 状态更新，versions 端点可见新正文（导出读同一 content）。"""
    sid = _seed_session(_state_one_chapter())

    def mock_generate(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["content"] = "导出应包含这段。"
            ch["versions"] = ["导出应包含这段。"] + list(ch.get("versions") or [])
            ch["status"] = "generated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)
    monkeypatch.setattr("facade.review_chapter_node", lambda state: {})

    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "instruction": "把引言第一段写短一点"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    assert state["body_chapters"][0]["content"] == "导出应包含这段。"
    versions = client.get(f"/sessions/{sid}/chapters/0/versions")
    assert versions.status_code == 200
    assert versions.json()["count"] == 2
    facade.drop_session(sid)


def test_edit_chapter_content_persists_markdown_without_llm(monkeypatch, client):
    """save-edit：{content} 落盘，不调 generate_chapter，status=edited。"""
    sid = _seed_session(_state_one_chapter())
    called = {"n": 0}

    def mock_generate(_s):
        called["n"] += 1
        return {}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    edited = "## 研究背景\n\n教育回报。\n"
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "content": edited},
    )
    assert resp.status_code == 200, resp.text
    assert called["n"] == 0
    ch = resp.json()["chapter"]
    assert ch["content"] == edited
    assert ch["status"] == "edited"
    assert ch["versions"][0] == edited
    assert facade.get_state(sid)["body_chapters"][0]["content"] == edited
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
