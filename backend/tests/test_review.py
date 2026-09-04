"""ADR-0007 Stage 1: HITL 人工评审端点契约测试。

契约：
1. GET /sessions/{id}/review 返回当前章评审信息（feedback / suggestions /
   score / 5 维 rubric / iteration / max / auto_decision）
2. GET /review 无评审数据时返回 200 + 空字段（非 404）
3. GET /review 未知 session 返回 404
4. POST /sessions/{id}/review/decision 写入 hitl_decision / hitl_reviewer /
   hitl_comment 到 state
5. accept / force_pass → next_action="proceed"
6. reject → next_action="regenerate"（触发 regenerate_chapter）
7. 非法 decision → 400
8. Fitness Function：POST 不写 review_feedback / review_scores / review_rubrics
9. auto_decision 由 score 阈值 0.7 计算
"""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import routers.chapter  # noqa: F401  # 触发 generate-chapter 注册
import routers.review  # noqa: F401  # 触发 self-registration
from facade import facade

from conftest import make_state, make_write_ready_state

# 评审通过的高分 rubric（综合分 >= 0.7）
HIGH_RUBRIC = {
    "endogeneity": 0.9,
    "identification": 0.85,
    "robustness": 0.8,
    "contribution": 0.9,
    "readability": 0.85,
}
# 评审不通过的低分 rubric（综合分 < 0.7）
LOW_RUBRIC = {
    "endogeneity": 0.2,
    "identification": 0.3,
    "robustness": 0.4,
    "contribution": 0.3,
    "readability": 0.5,
}


def _seed_session(state: dict) -> str:
    sid = f"test-review-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def _make_reviewed_state(score_pass: bool = True) -> dict:
    """构造一个含完整评审数据的 state。"""
    rubric = HIGH_RUBRIC if score_pass else LOW_RUBRIC
    # 综合分：0.3*endo + 0.25*ident + 0.2*rob + 0.15*contrib + 0.1*read
    score = (
        0.3 * rubric["endogeneity"]
        + 0.25 * rubric["identification"]
        + 0.2 * rubric["robustness"]
        + 0.15 * rubric["contribution"]
        + 0.1 * rubric["readability"]
    )
    return make_state(
        current_chapter_index=1,
        review_chapter_index=0,
        review_feedback=["章节质量良好，内生性处理得当。"],
        revision_suggestions=["建议补充稳健性检验。"],
        review_scores=[score],
        review_rubrics=[rubric],
        review_iteration=1,
        max_review_iterations=2,
        hitl_review_enabled=False,
    )


# ---------------------------------------------------------------------------
# GET /sessions/{id}/review
# ---------------------------------------------------------------------------
def test_get_review_returns_full_info(client):
    """GET /review 返回完整评审信息（含 5 维 rubric）。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.get(f"/sessions/{sid}/review")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["chapter_index"] == 0
    assert data["feedback"] == "章节质量良好，内生性处理得当。"
    assert data["suggestions"] == "建议补充稳健性检验。"
    assert data["review_iteration"] == 1
    assert data["max_review_iterations"] == 2
    # 5 维 rubric 全部存在
    rubric = data["rubric"]
    for dim in ("endogeneity", "identification", "robustness",
                "contribution", "readability"):
        assert dim in rubric, f"rubric 缺 {dim}"
        assert rubric[dim] is not None


def test_get_review_auto_decision_pass(client):
    """auto_decision = pass 当 score >= 0.7。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.get(f"/sessions/{sid}/review")
    data = resp.json()
    assert data["score"] >= 0.7
    assert data["auto_decision"] == "pass"


def test_get_review_auto_decision_fail(client):
    """auto_decision = fail 当 score < 0.7。"""
    sid = _seed_session(_make_reviewed_state(score_pass=False))
    resp = client.get(f"/sessions/{sid}/review")
    data = resp.json()
    assert data["score"] < 0.7
    assert data["auto_decision"] == "fail"


def test_get_review_empty_defaults_when_no_review_data(client):
    """无评审数据时返回 200 + 空字段（非 404）。"""
    sid = _seed_session(make_state(current_chapter_index=1))
    resp = client.get(f"/sessions/{sid}/review")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["feedback"] == ""
    assert data["suggestions"] == ""
    assert data["score"] == 0.0
    assert data["auto_decision"] == "fail"
    assert data["chapter_index"] == 0
    # rubric 全 None
    rubric = data["rubric"]
    for dim in ("endogeneity", "identification", "robustness",
                "contribution", "readability"):
        assert rubric[dim] is None


def test_get_review_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.get("/sessions/no-such-session/review")
    assert resp.status_code == 404


def test_get_review_falls_back_to_current_chapter_index(client):
    """review_chapter_index 缺失时回退 current_chapter_index - 1。"""
    state = make_state(
        current_chapter_index=3,  # 回退 idx=2
        review_feedback=["f0", "f1", "f2"],
        revision_suggestions=["s0", "s1", "s2"],
        review_scores=[0.5, 0.8, 0.6],
        review_rubrics=[LOW_RUBRIC, HIGH_RUBRIC, LOW_RUBRIC],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/review")
    data = resp.json()
    assert data["chapter_index"] == 2
    assert data["feedback"] == "f2"
    assert data["score"] == 0.6


# ---------------------------------------------------------------------------
# POST /sessions/{id}/review/decision
# ---------------------------------------------------------------------------
def test_post_decision_accept_writes_state_and_proceeds(client):
    """accept → 写 hitl_decision，next_action=proceed。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept", "reviewer": "alice", "comment": "ok"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["decision"] == "accept"
    assert data["next_action"] == "proceed"
    assert data["chapter_index"] == 0
    # state 持久化
    state = facade.get_state(sid)
    assert state["hitl_decision"] == "accept"
    assert state["hitl_reviewer"] == "alice"
    assert state["hitl_comment"] == "ok"


def test_post_decision_force_pass_proceeds(client):
    """force_pass → next_action=proceed。"""
    sid = _seed_session(_make_reviewed_state(score_pass=False))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "force_pass", "reviewer": "bob"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["next_action"] == "proceed"
    state = facade.get_state(sid)
    assert state["hitl_decision"] == "force_pass"
    assert state["hitl_reviewer"] == "bob"


def test_post_decision_reject_triggers_regenerate(client, monkeypatch):
    """reject → next_action=regenerate，触发 regenerate_chapter。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    # mock regenerate_chapter 避免真实 LLM 调用
    regenerate_calls = []

    def _fake_regenerate(self_inner, session_id, chapter_index):
        regenerate_calls.append((session_id, chapter_index))
        # 模拟 regenerate 后 state 更新
        state = self_inner.get_state(session_id)
        state["current_chapter_index"] = chapter_index + 1
        self_inner.save_state(session_id, state)
        return state

    monkeypatch.setattr(
        "facade.AgentFacade.regenerate_chapter", _fake_regenerate
    )
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "reject"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["next_action"] == "regenerate"
    assert data["decision"] == "reject"
    # regenerate_chapter 被调用，操作 chapter_index=0
    assert len(regenerate_calls) == 1
    assert regenerate_calls[0] == (sid, 0)
    # decision 仍写入 state
    state = facade.get_state(sid)
    assert state["hitl_decision"] == "reject"


def test_post_decision_invalid_returns_400(client):
    """非法 decision 值返回 400。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "maybe"},
    )
    assert resp.status_code == 400


def test_post_decision_unknown_session_returns_404(client):
    """未知 session 返回 404。"""
    resp = client.post(
        "/sessions/no-such-session/review/decision",
        json={"decision": "accept"},
    )
    assert resp.status_code == 404


def test_post_decision_does_not_write_review_fields(client):
    """Fitness Function: POST 不写 review_feedback / review_scores / review_rubrics。"""
    state = _make_reviewed_state(score_pass=True)
    sid = _seed_session(state)
    # 记录原始 review_* 值
    orig_feedback = list(state["review_feedback"])
    orig_scores = list(state["review_scores"])
    orig_rubrics = list(state["review_rubrics"])

    client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept"},
    )
    new_state = facade.get_state(sid)
    assert new_state["review_feedback"] == orig_feedback
    assert new_state["review_scores"] == orig_scores
    assert new_state["review_rubrics"] == orig_rubrics


def test_post_decision_writes_hitl_fields(client):
    """Fitness Function: POST 必须写入 hitl_decision / hitl_reviewer。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept", "reviewer": "carol", "comment": "good"},
    )
    state = facade.get_state(sid)
    assert state.get("hitl_decision") == "accept"
    assert state.get("hitl_reviewer") == "carol"
    assert state.get("hitl_comment") == "good"


def test_post_decision_accept_without_reviewer(client):
    """accept 不带 reviewer → hitl_reviewer=None，仍成功。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept"},
    )
    assert resp.status_code == 200
    state = facade.get_state(sid)
    assert state["hitl_decision"] == "accept"
    assert state.get("hitl_reviewer") is None


def test_post_decision_reject_degrades_when_regenerate_unavailable(client, monkeypatch):
    """regenerate_chapter 不可用（503）时，decision 仍写入，next_action=regenerate。"""
    from fastapi import HTTPException

    sid = _seed_session(_make_reviewed_state(score_pass=True))

    def _raise_503(self_inner, session_id, chapter_index):
        raise HTTPException(status_code=503, detail="node unavailable")

    monkeypatch.setattr(
        "facade.AgentFacade.regenerate_chapter", _raise_503
    )
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "reject"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["next_action"] == "regenerate"
    # decision 仍写入
    state = facade.get_state(sid)
    assert state["hitl_decision"] == "reject"


def test_post_decision_reject_writes_negative_learning_label(client, monkeypatch):
    """人点否决 → 写一条负标签，且标签里没有分数。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))

    def _fake_regenerate(self_inner, session_id, chapter_index):
        return self_inner.get_state(session_id)

    monkeypatch.setattr(
        "facade.AgentFacade.regenerate_chapter", _fake_regenerate
    )
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "reject"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    labels = state.get("learning_labels") or []
    assert any(
        item.get("source") == "hitl_reject" and item.get("polarity") == "negative"
        for item in labels
    )
    for item in labels:
        assert "score" not in item
        assert "reward" not in item
        assert "review_score" not in item


def test_post_decision_accept_writes_positive_learning_label(client):
    """人点通过 → 写一条正标签。"""
    sid = _seed_session(_make_reviewed_state(score_pass=True))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    labels = state.get("learning_labels") or []
    assert any(
        item.get("source") == "hitl_accept" and item.get("polarity") == "positive"
        for item in labels
    )
    for item in labels:
        assert "score" not in item
        assert "reward" not in item


def test_post_decision_force_pass_is_not_true_accept_label(client):
    """强制通过不是真通过，不写 hitl_accept。"""
    sid = _seed_session(_make_reviewed_state(score_pass=False))
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "force_pass"},
    )
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    sources = [item.get("source") for item in (state.get("learning_labels") or [])]
    assert "hitl_accept" not in sources
    assert "hitl_reject" not in sources


# ---------------------------------------------------------------------------
# 批次 1b：写章调用之后 GET /review，不是只读手写 state
# ---------------------------------------------------------------------------
def test_generate_chapter_then_get_review_has_review_source(client):
    """POST generate-chapter 之后 GET /review 含 review_source。"""
    sid = f"test-review-gen-{uuid.uuid4()}"
    facade.seed_state(sid, make_write_ready_state())
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text
    gen_body = gen.json()
    assert "review_source" in gen_body
    assert gen_body["review_source"] in {"mock", "llm", "mock_fallback"}

    resp = client.get(f"/sessions/{sid}/review")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "review_source" in data
    assert data["review_source"] in {"mock", "llm", "mock_fallback"}
    assert "review_degraded" in data
    assert "grounding_failures" in data
    facade.drop_session(sid)


def test_generate_chapter_review_rollback_still_200_fail(client):
    """评审回退 current_chapter_index 时写章仍 200，auto_decision=fail。"""
    sid = f"test-review-fail-{uuid.uuid4()}"
    facade.seed_state(sid, make_write_ready_state())
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert body["auto_decision"] == "fail"
    assert body["chapter"]["type"] == "intro"
    assert body["chapter"].get("content")

    state = facade.get_state(sid)
    # 占位 intro 综合分 < 0.7，评审应回退到刚写的那一章
    assert state.get("current_chapter_index") == state.get("review_chapter_index")
    facade.drop_session(sid)


def test_generate_chapter_bad_review_json_get_review_is_mock_fallback(
    client, monkeypatch
):
    """坏 JSON 走 mock 后，GET /review 必须写出 mock_fallback，不能假装真审。"""

    def boom(*_a, **_k):
        raise ValueError("bad json")

    def fake_config(node):
        if node == "review":
            return SimpleNamespace(provider="anthropic", model="claude")
        return SimpleNamespace(provider="mock", model="default")

    monkeypatch.setattr("agent.nodes.review_chapter.invoke_review_llm", boom)
    monkeypatch.setattr("agent.llm.router.router.get_config", fake_config)

    sid = f"test-review-fallback-{uuid.uuid4()}"
    facade.seed_state(sid, make_write_ready_state())
    gen = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "intro", "title": "引言"}},
    )
    assert gen.status_code == 200, gen.text
    assert gen.json()["review_source"] == "mock_fallback"
    assert gen.json()["review_degraded"] is True

    resp = client.get(f"/sessions/{sid}/review")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["review_source"] == "mock_fallback"
    assert data["review_degraded"] is True
    assert data["rubric"]
    degs = facade.get_degradations(sid)
    assert any(
        d.get("node") == "review_chapter" and d.get("visible") is True
        for d in degs
    )
    facade.drop_session(sid)
    facade.clear_degradations(sid)
