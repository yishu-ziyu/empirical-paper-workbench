"""Contract tests for T-08b: GET /sessions/{id}/progress.

Pins the progress contract:
- GET /sessions/{id}/progress → {total: 6, completed, current, body_chapters: [...]}
- completed = status=="approved" 的章节数
- current = state['current_chapter_index']（缺省取 len(body_chapters)）
- body_chapters 为 {type, title, status} 摘要列表
- 未知 session 返回 404
"""
from __future__ import annotations

# Importing the progress router triggers its self-registration on main.app.
import routers.progress  # noqa: F401
from facade import facade

from conftest import make_state


def _seed_session(state: dict) -> str:
    import uuid

    sid = f"test-progress-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def test_progress_empty_session(client):
    """空 session：total=6, completed=0, current=0, body_chapters=[]。"""
    sid = _seed_session({"body_chapters": [], "current_chapter_index": 0})
    resp = client.get(f"/sessions/{sid}/progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 6
    assert data["completed"] == 0
    assert data["current"] == 0
    assert data["body_chapters"] == []


def test_progress_counts_approved(client):
    """completed 只计 status==approved 的章节。"""
    state = make_state(
        body_chapters=[
            {"type": "intro", "title": "引言", "status": "approved"},
            {"type": "lit_review", "title": "文献", "status": "generated"},
            {"type": "methods", "title": "方法", "status": "approved"},
        ],
        current_chapter_index=3,
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 6
    assert data["completed"] == 2
    assert data["current"] == 3
    assert len(data["body_chapters"]) == 3
    assert data["body_chapters"][0]["status"] == "approved"
    assert data["body_chapters"][1]["status"] == "generated"
    assert data["body_chapters"][2]["status"] == "approved"
    assert data["body_chapters"][0]["type"] == "intro"
    assert data["body_chapters"][0]["title"] == "引言"


def test_progress_current_defaults_to_chapter_count(client):
    """无 current_chapter_index 时 current 取 len(body_chapters)。"""
    state = make_state(body_chapters=[{"type": "intro", "status": "approved"}])
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/progress")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current"] == 1
    assert data["completed"] == 1


def test_progress_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.get("/sessions/no-such-session/progress")
    assert resp.status_code == 404
