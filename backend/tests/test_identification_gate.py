"""#40 增量一（后端侧）：同一份 state 在 HTTP 入口上也只允许一个判定。

契约：docs/acceptance/identification-state-gate.md（C2、C4、C5）

钉住三件事：

1. 识别未评估时，``passed`` 是 ``None``，不是 ``True`` —— 未知不等于通过；
2. 主结果晋升只在「必须拦住」那一档被拦，未知**不**构成拒绝依据；
3. 证据面板报的 execution / assessment / permissions 与流程判定同源。
"""

from __future__ import annotations

from conftest import make_write_ready_state
from facade import facade

import uuid


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def _hard_blocked_state() -> dict:
    return {
        "star_rating": 0,
        "identification_failed": True,
        "identification_diag": {
            "strategy": "did",
            "diagnostics": [{"test": "bacon_decomposition", "status": "fail"}],
            "execution": "completed",
            "assessment": "risk_found",
            "passed": False,
            "star_rating": 0,
        },
    }


def _unknown_state() -> dict:
    return {
        "identification_diag": {
            "strategy": "did",
            "diagnostics": [{"test": "bacon_decomposition", "status": "error"}],
            "execution": "failed",
            "assessment": "insufficient_evidence",
            "passed": None,
            "star_rating": None,
        },
        "star_rating": None,
    }


# ---------------------------------------------------------------------------
# 主结果晋升：只有「必须拦住」那一档拦
# ---------------------------------------------------------------------------


def _promote(client, sid: str):
    return client.post(
        f"/sessions/{sid}/research/preview/promote",
        json={"run_id": "run-anything"},
    )


def test_promote_is_blocked_when_identification_hard_blocks(client):
    sid = _unique("promote-blocked")
    facade.seed_state(sid, _hard_blocked_state())

    resp = _promote(client, sid)

    assert resp.status_code == 409, resp.text
    detail = resp.json()["detail"]
    assert detail["code"] == "identification_blocks_main_result"
    assert detail["star_rating"] == 0


def test_promote_is_not_blocked_by_unassessed_identification(client):
    """未知不是拒绝的依据：护栏不得把「还没评估」当成「不许晋升」。

    这一份 state 没有研究台（lab），所以请求仍会失败 —— 但失败的**不是**识别护栏。
    """
    sid = _unique("promote-unknown")
    facade.seed_state(sid, _unknown_state())

    resp = _promote(client, sid)

    detail = resp.json().get("detail") if resp.status_code != 200 else {}
    code = detail.get("code") if isinstance(detail, dict) else None
    assert code != "identification_blocks_main_result"


# ---------------------------------------------------------------------------
# 串行预写确认：识别失败但没有星级时也要拦住
# ---------------------------------------------------------------------------


def test_prewrite_confirm_blocks_on_identification_failed_flag(client):
    """只看 star_rating == 0 的写法会漏掉这一种 state：失败标记在，星级不在。"""
    sid = _unique("confirm-blocked")
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "research_direction": {"question": "Q", "dv": "y", "iv": "x"},
            "identification_diag": {"strategy": "did", "report": "r"},
            "identification_failed": True,
        },
    )

    resp = client.post(
        f"/sessions/{sid}/prewrite/confirm",
        json={"action": "continue_estimate"},
        headers={"Idempotency-Key": f"confirm-{sid}"},
    )

    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "identification_blocked"


# ---------------------------------------------------------------------------
# 证据面板：三轴 + passed 三态
# ---------------------------------------------------------------------------


def test_evidence_reports_three_axes_and_tristate_passed(client):
    sid = _unique("evidence-axes")
    facade.seed_state(sid, {**make_write_ready_state(), **_unknown_state()})

    resp = client.get(f"/sessions/{sid}/evidence")
    assert resp.status_code == 200, resp.text
    identification = resp.json()["identification"]

    assert identification["passed"] is None, "尚未评估不等于通过"
    assert identification["execution"] == "failed"
    assert identification["assessment"] == "insufficient_evidence"
    permissions = identification["permissions"]
    assert permissions["continue_to_estimate"] == "allow"
    assert permissions["causal_language"] == "forbid"
    assert permissions["requires_disclosure"] is True


def test_evidence_reports_clean_pass_axis_values(client):
    sid = _unique("evidence-clean")
    facade.seed_state(
        sid,
        {
            **make_write_ready_state(),
            "star_rating": 3,
            "identification_failed": False,
            "identification_diag": {
                "strategy": "did",
                "diagnostics": [{"test": "bacon_decomposition", "status": "pass"}],
                "execution": "completed",
                "assessment": "risk_not_found",
                "passed": True,
                "star_rating": 3,
            },
        },
    )

    identification = client.get(f"/sessions/{sid}/evidence").json()["identification"]

    assert identification["passed"] is True
    assert identification["assessment"] == "risk_not_found"
    assert identification["permissions"]["promote_main_result"] == "allow"
    assert identification["permissions"]["requires_disclosure"] is False


# ---------------------------------------------------------------------------
# 识别接口：未知不能被序列化成 True
# ---------------------------------------------------------------------------


def test_identification_endpoint_keeps_unknown_as_null(client, monkeypatch):
    sid = _unique("ident-unknown")
    facade.seed_state(sid, {"research_direction": {"question": "Q", "dv": "y"}})

    def fake_node(_state):
        return {
            "identification_diag": {
                "strategy": "did",
                "diagnostics": [{"test": "bacon_decomposition", "status": "error"}],
                "execution": "failed",
                "assessment": "insufficient_evidence",
                "passed": None,
                "star_rating": None,
                "report": "诊断工具没有运行成功，识别策略的风险尚未核查。",
            },
            "identification_failed": False,
            "star_rating": None,
        }

    monkeypatch.setattr("facade.identification_verify_node", fake_node)

    resp = client.post(f"/sessions/{sid}/identification")
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["passed"] is None, "未知被序列化成 True 就是把没核过的风险说成没风险"
    assert body["star_rating"] is None
    assert body["identification_failed"] is False
    assert body["diagnosis"]["assessment"] == "insufficient_evidence"
