"""Contract tests for T-08b: POST /sessions/{id}/regenerate.

Pins the regenerate contract:
- POST /sessions/{id}/regenerate 接受 {chapter_index}
  → 设置 state['current_chapter_index'] → 调 generate_chapter 节点
  → 返回更新后的章节（含新版本）
- 未知 session_id 返回 404

generate_chapter 节点存在（T-07）但其占位逻辑不产生 versions 列表，
测试通过 monkeypatch 注入假节点以验证 endpoint 接线与版本追加语义。
"""
from __future__ import annotations

# Importing the chapter router triggers its self-registration on main.app.
import routers.chapter  # noqa: F401
from facade import facade


def _seed_session(state: dict) -> str:
    """Seed an in-memory session with the given state, return its id."""
    import uuid

    sid = f"test-regen-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def _state_one_chapter() -> dict:
    return {
        "body_chapters": [
            {
                "type": "intro",
                "title": "引言",
                "content": "原始内容",
                "versions": ["原始内容"],
                "status": "generated",
            }
        ],
    }


def test_regenerate_adds_new_version(monkeypatch, client):
    """regenerate 调用节点后返回含新版本的章节。"""
    sid = _seed_session(_state_one_chapter())

    def mock_generate(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            versions = list(ch.get("versions", []))
            new_content = "重新生成的内容 v2"
            versions.append(new_content)
            ch["versions"] = versions
            ch["content"] = new_content
            ch["status"] = "regenerated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    resp = client.post(
        f"/sessions/{sid}/regenerate",
        json={"chapter_index": 0},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    ch = data["chapter"]
    assert ch["status"] == "regenerated"
    assert ch["content"] == "重新生成的内容 v2"
    assert len(ch["versions"]) == 2
    assert ch["versions"][-1] == "重新生成的内容 v2"


def test_regenerate_sets_current_chapter_index(monkeypatch, client):
    """endpoint 必须在调用节点前把 chapter_index 写入 state。"""
    sid = _seed_session(_state_one_chapter())
    captured = {}

    def mock_generate(s):
        captured["current_chapter_index"] = s.get("current_chapter_index")
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["content"] = "new"
            ch["versions"] = list(ch.get("versions", [])) + ["new"]
            ch["status"] = "regenerated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    resp = client.post(f"/sessions/{sid}/regenerate", json={"chapter_index": 0})
    assert resp.status_code == 200, resp.text
    assert captured["current_chapter_index"] == 0


def test_regenerate_persists_state(monkeypatch, client):
    """regenerate 后 session 状态更新，versions 端点可见新版本。"""
    sid = _seed_session(_state_one_chapter())

    def mock_generate(s):
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["versions"] = list(ch.get("versions", [])) + ["新版本"]
            ch["content"] = "新版本"
            ch["status"] = "regenerated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    client.post(f"/sessions/{sid}/regenerate", json={"chapter_index": 0})
    resp = client.get(f"/sessions/{sid}/chapters/0/versions")
    assert resp.status_code == 200
    assert resp.json()["count"] == 2


def test_regenerate_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.post(
        "/sessions/no-such-session/regenerate",
        json={"chapter_index": 0},
    )
    assert resp.status_code == 404


def test_regenerate_accepts_instruction(monkeypatch, client):
    """instruction 写入 revision_suggestions 后再跑 generate_chapter。"""
    sid = _seed_session(_state_one_chapter())
    captured = {}

    def mock_generate(s):
        captured["revision_suggestions"] = s.get("revision_suggestions")
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["content"] = "按意见改写"
            ch["status"] = "regenerated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    resp = client.post(
        f"/sessions/{sid}/regenerate",
        json={"chapter_index": 0, "instruction": "写短一点"},
    )
    assert resp.status_code == 200, resp.text
    assert captured["revision_suggestions"][0] == "写短一点"
    assert resp.json()["chapter"]["content"] == "按意见改写"


def test_regenerate_empty_instruction_still_runs(monkeypatch, client):
    """空 instruction 仍重生成，且不覆盖已有 revision_suggestions。"""
    sid = _seed_session({
        **_state_one_chapter(),
        "revision_suggestions": ["原建议"],
    })
    captured = {}

    def mock_generate(s):
        captured["revision_suggestions"] = s.get("revision_suggestions")
        body_chapters = list(s.get("body_chapters", []))
        idx = s.get("current_chapter_index", 0)
        if 0 <= idx < len(body_chapters):
            ch = dict(body_chapters[idx])
            ch["content"] = "empty-ok"
            ch["status"] = "regenerated"
            body_chapters[idx] = ch
        return {"body_chapters": body_chapters}

    monkeypatch.setattr("facade.generate_chapter_node", mock_generate)

    resp = client.post(
        f"/sessions/{sid}/regenerate",
        json={"chapter_index": 0, "instruction": ""},
    )
    assert resp.status_code == 200, resp.text
    assert captured["revision_suggestions"] == ["原建议"]
    assert resp.json()["chapter"]["content"] == "empty-ok"
