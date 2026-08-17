"""Contract tests for GET /sessions/{id}/journey (8-stage research journey).

Pins the journey contract (收敛版：去掉无节点的"表格图形"站)：
- GET /sessions/{id}/journey → {currentStage, stages: [{status, canIntervene}, ...]}
- 8 stages (0-index), canIntervene set on {0,2,3,5,6}
- currentStage 由 state 真实字段推断（非硬编码节点名）
- identification_failed=True 且停在识别阶段 → status=interrupt
- 空 state → currentStage=0, stage0 active, rest pending
- 未知 session 返回 404
"""
from __future__ import annotations

# Importing the progress router triggers its self-registration on main.app.
import routers.progress  # noqa: F401
from facade import facade

from conftest import make_state


def _seed_session(state: dict) -> str:
    import uuid

    sid = f"test-journey-{uuid.uuid4()}"
    facade.seed_state(sid, state)
    return sid


def test_journey_has_8_stages_with_correct_can_intervene(client):
    """空 session 降级：currentStage=0，stage0 active，其余 pending；
    canIntervene 只落在 {0,2,3,5,6}。"""
    sid = _seed_session({})
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 0
    assert len(data["stages"]) == 8
    statuses = [s["status"] for s in data["stages"]]
    assert statuses == ["active"] + ["pending"] * 7
    intervene = [i for i, s in enumerate(data["stages"]) if s["canIntervene"]]
    assert intervene == [0, 2, 3, 5, 6]


def test_journey_after_research_direction(client):
    """research_direction 已读 → 已过选题/文献，currentStage=2（数据清洗）。
    注意：make_state 默认带非空 uploaded_datasets，故显式清空以隔离本阶段。"""
    state = make_state(
        research_direction={"topic": "测试"},
        uploaded_datasets=[],
        cleaning_report=None,
        cleaned_datasets=[],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 2
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[:2] == ["completed", "completed"]
    assert statuses[2] == "active"
    assert statuses[3:] == ["pending"] * 5


def test_journey_after_estimate_stamp(client):
    """估计节点已跑 → currentStage=5（稳健性审计）。"""
    state = make_state(
        research_direction={"topic": "测试"},
        cleaning_report={"summary": "ok"},
        identification_diag={"balanced": True},
        estimate={"produced_by": "estimate", "status": "ok"},
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 5
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[:5] == ["completed"] * 5
    assert statuses[5] == "active"


def test_journey_after_robustness_stamp(client):
    """稳健性已跑 → currentStage=6（写作评审）。"""
    state = make_state(
        research_direction={"topic": "测试"},
        cleaning_report={"summary": "ok"},
        identification_diag={"balanced": True},
        estimate={"produced_by": "estimate", "status": "ok"},
        robustness_results={"produced_by": "robustness_check", "diagnostics": []},
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 6
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[:6] == ["completed"] * 6
    assert statuses[6] == "active"


def test_journey_after_identification_diag(client):
    """identification_diag 已产生 → 过 0-3 站，currentStage=4（估计建模）。"""
    state = make_state(
        research_direction={"topic": "测试"},
        cleaning_report={"summary": "ok"},
        identification_diag={"balanced": True},
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 4
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[:4] == ["completed"] * 4
    assert statuses[4] == "active"


def test_journey_identification_failed_interrupt(client):
    """identification_failed=True 且停在识别阶段 → index3 标 interrupt。"""
    state = make_state(
        research_direction={"topic": "测试"},
        cleaning_report={"summary": "ok"},
        identification_failed=True,
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 3
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[:3] == ["completed", "completed", "completed"]
    assert statuses[3] == "interrupt"
    assert statuses[4:] == ["pending"] * 4


def test_journey_after_export(client):
    """export_formats 存在 → 全部 completed，currentStage=8。"""
    state = make_state(
        research_direction={"topic": "测试"},
        cleaning_report={"summary": "ok"},
        identification_diag={"balanced": True},
        body_chapters=[{"type": "intro", "status": "approved"}],
        robustness_results=[{"pass": True}],
        export_formats=["pdf"],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 8
    assert all(s["status"] == "completed" for s in data["stages"])


def test_journey_upload_only_stays_at_topic(client):
    """只上传、还没选题：停在第 0 站，不能跳到识别。"""
    state = make_state(
        research_direction=None,
        uploaded_datasets=[{"path": "/tmp/x.csv"}],
        cleaning_report=None,
        cleaned_datasets=[],
    )
    sid = _seed_session(state)
    resp = client.get(f"/sessions/{sid}/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert data["currentStage"] == 0
    statuses = [s["status"] for s in data["stages"]]
    assert statuses[0] == "active"
    assert statuses[3] == "pending"


def test_journey_unknown_session_returns_404(client):
    """未知 session_id 返回 404。"""
    resp = client.get("/sessions/no-such-session/journey")
    assert resp.status_code == 404