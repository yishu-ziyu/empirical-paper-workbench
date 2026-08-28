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


def test_edit_chapter_instruction_can_write_new_review(monkeypatch, client):
    """instruction 路径走 generate_chapter，允许写入新评审。"""
    sid = _seed_session(
        {
            **_state_one_chapter(),
            "review_scores": [0.95],
            "review_feedback": ["旧评审"],
        }
    )

    def mock_review(state):
        return {"review_scores": [0.81], "review_feedback": ["改写后新评审"]}

    monkeypatch.setattr(
        "facade.generate_chapter_node", _mock_generate_with("改短后的引言。")
    )
    monkeypatch.setattr("facade.review_chapter_node", mock_review)

    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "instruction": "把引言第一段写短一点"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    assert state["review_scores"][0] == 0.81
    assert state["review_feedback"][0] == "改写后新评审"
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


def test_edit_chapter_content_clears_review_so_approve_cannot_pass(client):
    """save-edit 清掉该章评审；approve 不得凭编辑前分数通过。"""
    sid = _seed_session(
        {
            **_state_one_chapter(),
            "review_scores": [0.95],
            "review_feedback": ["编辑前已过审。"],
            "review_chapter_index": 0,
        }
    )
    edited = "## 研究背景\n\n用户改过的引言。"
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "content": edited},
    )
    assert resp.status_code == 200, resp.text

    state = facade.get_state(sid)
    scores = list(state.get("review_scores") or [])
    feedback = list(state.get("review_feedback") or [])
    assert scores, "review_scores 应对齐章节，清空该槽而非整表删除"
    assert scores[0] in (None, "")
    assert feedback[0] in (None, "")

    review = client.get(f"/sessions/{sid}/review")
    assert review.status_code == 200, review.text
    assert review.json()["auto_decision"] == "fail"
    assert review.json()["score"] in (0, 0.0)

    blocked = client.post(f"/sessions/{sid}/approve-chapter", json={})
    assert blocked.status_code == 409, blocked.text
    detail = blocked.json()["detail"]
    assert detail["review_gate"] is True
    assert detail["needs_force"] is True
    facade.drop_session(sid)


def test_edit_chapter_content_preserves_other_chapter_review(client):
    """只清被编辑章的评审槽，邻章分数不动。"""
    sid = _seed_session(
        {
            "body_chapters": [
                {
                    "type": "intro",
                    "title": "引言",
                    "content": "引言原文。",
                    "versions": ["引言原文。"],
                    "status": "generated",
                    "chapter_index": 0,
                },
                {
                    "type": "methods",
                    "title": "方法",
                    "content": "方法原文。",
                    "versions": ["方法原文。"],
                    "status": "generated",
                    "chapter_index": 1,
                },
            ],
            "outline": [
                {"type": "intro", "title": "引言"},
                {"type": "methods", "title": "方法"},
            ],
            "current_chapter_index": 2,
            "review_scores": [0.95, 0.91],
            "review_feedback": ["引言过审。", "方法过审。"],
        }
    )
    resp = client.post(
        f"/sessions/{sid}/edit-chapter",
        json={"chapter_index": 0, "content": "改过的引言。"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    assert list(state["review_scores"])[0] in (None, "")
    assert list(state["review_scores"])[1] == 0.91
    assert list(state["review_feedback"])[1] == "方法过审。"

    methods_ok = client.post(
        f"/sessions/{sid}/approve-chapter",
        json={"chapter_type": "methods"},
    )
    assert methods_ok.status_code == 200, methods_ok.text

    intro_blocked = client.post(
        f"/sessions/{sid}/approve-chapter",
        json={"chapter_type": "intro"},
    )
    assert intro_blocked.status_code == 409, intro_blocked.text
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
