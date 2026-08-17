"""Contract tests for T-07: POST /sessions/{id}/generate-chapter +
POST /sessions/{id}/approve-chapter.

章节 HTTP 单测直接 seed 就绪态，不经 POST /direction。
样本 CSV 没有 education 列；方向端到端见 test_outline.py。
"""
from __future__ import annotations

import uuid

# Importing the chapter router triggers its self-registration on main.app.
import routers.chapter  # noqa: F401
from facade import facade

from conftest import make_six_chapter_outline, make_state, make_write_ready_state


def _seed_write_ready(**overrides) -> str:
    sid = f"test-ch-{uuid.uuid4()}"
    facade.seed_state(sid, make_write_ready_state(**overrides))
    return sid


def test_generate_chapter_endpoint_returns_generated_chapter(client):
    """POST /sessions/{id}/generate-chapter 触发 intro 章节生成。"""
    sid = _seed_write_ready()
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
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
    assert isinstance(ch.get("content"), str) and len(ch["content"]) > 0
    assert "body_chapters" in data
    assert len(data["body_chapters"]) >= 1


def test_approve_chapter_endpoint_marks_approved(client):
    """POST /sessions/{id}/approve-chapter 标记最后生成章节 status=approved。"""
    sid = _seed_write_ready()
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text
    resp = client.post(
        f"/sessions/{sid}/approve-chapter",
        json={},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["chapter"]["status"] == "approved"
    assert data["chapter"]["type"] == "intro"


def test_approve_chapter_endpoint_with_explicit_type(client):
    """approve-chapter 支持 chapter_type 参数定位特定章节。"""
    sid = _seed_write_ready()
    client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "methods", "title": "方法"}},
    )
    resp = client.post(
        f"/sessions/{sid}/approve-chapter",
        json={"chapter_type": "intro"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["chapter"]["type"] == "intro"
    assert data["chapter"]["status"] == "approved"
    methods_ch = next(
        c for c in data["body_chapters"] if c["type"] == "methods"
    )
    assert methods_ch["status"] == "generated"


def test_generate_chapter_unknown_type_returns_400(client):
    """未知 chapter_type 直接 400。"""
    sid = _seed_write_ready()
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "unknown_xyz", "title": "x"}},
    )
    assert resp.status_code != 200, (
        f"unknown chapter_type should not return 200: {resp.text}"
    )


def test_generate_chapter_all_six_types_via_endpoint(client):
    """6 种 chapter_type 都能通过 endpoint 触发生成。"""
    sid = _seed_write_ready()
    cases = [
        ("intro", {"research_question": "Q", "data_summary": "D"}),
        ("lit_review", {"research_question": "Q", "key_references": "REF"}),
        ("data_desc", {"data_summary": "D", "eda_results": "EDA"}),
        ("methods", {"method": "OLS", "research_question": "Q"}),
        ("results", {"method": "OLS"}),
        ("conclusion", {"research_question": "Q"}),
    ]
    for chapter_type, kwargs in cases:
        resp = client.post(
            f"/sessions/{sid}/generate-chapter",
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


def test_intro_blocked_without_identification(client):
    """无识别诊断时引言 409。"""
    sid = f"test-ch-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        make_state(
            outline=make_six_chapter_outline(),
            current_chapter_index=0,
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["write_blocked"] is True
    assert "no_identification" in detail["write_blockers"]


def test_intro_ok_with_only_identification(client):
    """引言只需要识别诊断。"""
    sid = f"test-ch-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        make_state(
            outline=make_six_chapter_outline(),
            current_chapter_index=0,
            identification_diag={"report": "ok"},
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={
            "chapter": {"type": "intro", "title": "引言"},
            "render_kwargs": {"research_question": "Q", "data_summary": "D"},
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["chapter"]["type"] == "intro"


def test_results_blocked_without_estimate_stamp(client):
    """假 results 字符串不能开结果章。"""
    sid = f"test-ch-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        make_state(
            outline=make_six_chapter_outline(),
            current_chapter_index=4,
            identification_diag={"report": "ok"},
            results="FAKE TABLE",
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={
            "chapter": {"type": "results", "title": "结果"},
            "render_kwargs": {"results": "STILL FAKE"},
        },
    )
    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["write_blocked"] is True
    assert "no_results" in detail["write_blockers"]
    assert facade.get_state(sid).get("results") == "FAKE TABLE"
