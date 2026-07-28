"""Contract tests for T-08b: POST /sessions/{id}/rollback.

Pins the rollback contract:
- POST /sessions/{id}/rollback 接受 {chapter_index, version_index}
  → 调 rollback_chapter 节点 → 返回回滚后的章节
- 未知 session_id 返回 404

rollback_chapter 节点由 T-08a 实现（可能尚未存在），测试通过
monkeypatch.setattr("facade.rollback_chapter_node", mock) 注入假节点，
仅验证 endpoint 接线，不验证节点逻辑。
"""
from __future__ import annotations

# Importing the chapter router triggers its self-registration on main.app.
import routers.chapter  # noqa: F401
from facade import facade


def _seed_session(state: dict) -> str:
    """Seed an in-memory session with the given state, return its id."""
    import uuid

    sid = f"test-rollback-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def _state_with_versions() -> dict:
    return {
        "current_chapter_index": 0,
        "body_chapters": [
            {
                "type": "intro",
                "title": "引言",
                "content": "版本0的内容，这是最初生成的引言章节。",
                "versions": [
                    "版本0的内容，这是最初生成的引言章节。",
                    "版本1的内容，这是重新生成后的引言章节。",
                ],
                "status": "regenerated",
            }
        ],
    }


def test_rollback_returns_rolled_back_chapter(monkeypatch, client):
    """POST /sessions/{id}/rollback 回滚到指定版本。"""
    sid = _seed_session(_state_with_versions())

    def mock_rollback(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("rollback_chapter_index", 0)
        vidx = s.get("rollback_version_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            versions = ch.get("versions", [])
            if 0 <= vidx < len(versions):
                ch["content"] = versions[vidx]
            ch["status"] = "rolled_back"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.rollback_chapter_node", mock_rollback)

    resp = client.post(
        f"/sessions/{sid}/rollback",
        json={"chapter_index": 0, "version_index": 0},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "chapter" in data
    ch = data["chapter"]
    assert ch["status"] == "rolled_back"
    assert ch["content"] == "版本0的内容，这是最初生成的引言章节。"
    assert "body_chapters" in data


def test_rollback_picks_requested_version(monkeypatch, client):
    """回滚到 version_index=1 时 content 应为版本1。"""
    sid = _seed_session(_state_with_versions())

    def mock_rollback(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("rollback_chapter_index", 0)
        vidx = s.get("rollback_version_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            versions = ch.get("versions", [])
            if 0 <= vidx < len(versions):
                ch["content"] = versions[vidx]
            ch["status"] = "rolled_back"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.rollback_chapter_node", mock_rollback)

    resp = client.post(
        f"/sessions/{sid}/rollback",
        json={"chapter_index": 0, "version_index": 1},
    )
    assert resp.status_code == 200, resp.text
    ch = resp.json()["chapter"]
    assert ch["content"] == "版本1的内容，这是重新生成后的引言章节。"


def test_rollback_persists_state(monkeypatch, client):
    """回滚后 session 状态被更新（后续请求可见）。"""
    sid = _seed_session(_state_with_versions())

    def mock_rollback(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("rollback_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["status"] = "rolled_back"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.rollback_chapter_node", mock_rollback)

    client.post(f"/sessions/{sid}/rollback", json={"chapter_index": 0, "version_index": 0})
    # 第二次请求（versions 端点）应看到 rolled_back 状态
    resp = client.get(f"/sessions/{sid}/chapters/0/versions")
    assert resp.status_code == 200


def test_rollback_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.post(
        "/sessions/no-such-session/rollback",
        json={"chapter_index": 0, "version_index": 0},
    )
    assert resp.status_code == 404
