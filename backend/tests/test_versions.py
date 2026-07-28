"""Contract tests for T-08b: GET /sessions/{id}/chapters/{idx}/versions.

Pins the versions query contract:
- GET /sessions/{id}/chapters/{chapter_index}/versions
  → 返回 {chapter_index, count, versions: [{index, preview}]}
- 每个版本的 preview 截断到前 50 字
- 未知 session 返回 404；chapter_index 越界返回 404
"""
from __future__ import annotations

# Importing the chapter router triggers its self-registration on main.app.
import routers.chapter  # noqa: F401
from facade import facade

from conftest import make_state


def _seed_session(state: dict) -> str:
    import uuid

    sid = f"test-versions-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def test_versions_returns_list_with_previews(client):
    """versions 端点返回版本列表与 50 字预览。"""
    long_v0 = "版本零是一段比较长的内容用来测试前五十字预览的截断行为是否正确工作。" * 2
    state = make_state(
        body_chapters=[
            {
                "type": "intro",
                "title": "引言",
                "content": long_v0,
                "versions": [long_v0, "短版本1", "短版本2"],
                "status": "generated",
            }
        ],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/chapters/0/versions")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["chapter_index"] == 0
    assert data["count"] == 3
    versions = data["versions"]
    assert len(versions) == 3
    assert versions[0]["index"] == 0
    assert versions[1]["index"] == 1
    # 长 version 预览截断到 50 字
    assert len(versions[0]["preview"]) <= 50
    assert versions[0]["preview"] == long_v0[:50]
    # 短 version 预览原样返回
    assert versions[1]["preview"] == "短版本1"
    assert versions[2]["preview"] == "短版本2"


def test_versions_falls_back_to_content_when_no_versions_field(client):
    """章节无 versions 列表时，用 content 作为唯一版本。"""
    state = make_state(
        body_chapters=[
            {"type": "intro", "title": "引言", "content": "唯一内容", "status": "generated"},
        ],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/chapters/0/versions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["versions"][0]["preview"] == "唯一内容"


def test_versions_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.get("/sessions/no-such-session/chapters/0/versions")
    assert resp.status_code == 404


def test_versions_index_out_of_range_returns_404(client):
    """chapter_index 越界返回 404。"""
    sid = _seed_session({"body_chapters": [{"type": "intro", "versions": ["a"]}]})
    resp = client.get(f"/sessions/{sid}/chapters/5/versions")
    assert resp.status_code == 404
