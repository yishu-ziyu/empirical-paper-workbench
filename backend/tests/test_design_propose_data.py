"""Own-data path: design/propose maps slots to real columns; overrides are validated."""
from __future__ import annotations

import json

import routers.design as design_router
from facade import facade

DATASET = {
    "name": "CGSS2023.dta",
    "rows": 100,
    "columns": ["a8a", "a7a", "a2", "a3a", "a18", "isurban"],
    "variable_labels": {"a8a": "个人去年全年总收入", "a7a": "最高教育程度"},
}


def _sid(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _fake_llm(monkeypatch, answer):
    import agent.llm.call_llm as call_llm_mod

    def fake(prompt, node_type="default", system=None):
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(call_llm_mod, "call_llm", fake)


def test_propose_with_dataset_maps_to_real_columns(client, monkeypatch):
    monkeypatch.setattr(design_router, "_session_dataset", lambda sid: dict(DATASET))
    _fake_llm(monkeypatch, json.dumps({
        "method": "ols", "outcome": "a8a", "treatment": "a7a",
        "controls": ["a2", "a3a", "not_a_column"], "heterogeneity_groups": [],
        "notes": ["a8a 含 9999996–9 特殊码"], "question_to_user": "",
    }, ensure_ascii=False))
    sid = _sid(client)
    resp = client.post(f"/sessions/{sid}/design/propose",
                       json={"title": "受教育程度对个人收入的影响", "question": "控制性别和年龄"})
    assert resp.status_code == 200, resp.text
    design = facade.get_state(sid)["design"]
    assert design["outcome"] == "a8a"
    assert design["treatment"] == "a7a"
    assert design["controls"] == ["a2", "a3a"]
    assert design["proposal"]["source"] == "llm"
    assert "not_a_column" in design["proposal"]["dropped"]
    assert design["status"] == "draft"
    assert resp.json()["proposal"]["notes"] == ["a8a 含 9999996–9 特殊码"]


def test_propose_model_down_clears_fake_slots(client, monkeypatch):
    monkeypatch.setattr(design_router, "_session_dataset", lambda sid: dict(DATASET))
    _fake_llm(monkeypatch, RuntimeError("LLM HTTP 503"))
    sid = _sid(client)
    resp = client.post(f"/sessions/{sid}/design/propose", json={"title": "教育对工资的影响"})
    assert resp.status_code == 200, resp.text
    design = facade.get_state(sid)["design"]
    assert design["outcome"] == "" and design["treatment"] == ""
    assert set(design["proposal"]["cleared"]) >= {"wages", "schooling"}


def test_overrides_edit_draft_and_reject_unknown_columns(client, monkeypatch):
    monkeypatch.setattr(design_router, "_session_dataset", lambda sid: dict(DATASET))
    _fake_llm(monkeypatch, "not json")
    sid = _sid(client)
    ok = client.post(f"/sessions/{sid}/design/propose", json={
        "title": "教育对工资的影响",
        "overrides": {"outcome": "a8a", "treatment": "a7a", "controls": ["a2"],
                      "heterogeneity_groups": ["isurban"]},
    })
    assert ok.status_code == 200, ok.text
    design = facade.get_state(sid)["design"]
    assert (design["outcome"], design["treatment"], design["controls"]) == ("a8a", "a7a", ["a2"])
    assert design["qType"] == "heterogeneity"
    assert {"kind": "het", "left": "a7a", "right": "isurban", "term": "a7a:isurban"} in design["interactions"]
    bad = client.post(f"/sessions/{sid}/design/propose", json={
        "title": "教育对工资的影响", "overrides": {"outcome": "wages"},
    })
    assert bad.status_code == 400
    assert bad.json()["detail"] == {"code": "unknown_column", "column": "wages"}


def test_propose_without_dataset_is_rule_only(client, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("no LLM call without data")

    import agent.llm.call_llm as call_llm_mod
    monkeypatch.setattr(call_llm_mod, "call_llm", boom)
    sid = _sid(client)
    resp = client.post(f"/sessions/{sid}/design/propose", json={"title": "教育对工资的影响"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["outcome"] == "wages"
