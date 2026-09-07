"""M1 Card canonical research lab: demo boot, expectation, freeze, snapshot."""
from __future__ import annotations

import asyncio
import uuid

import pytest

from facade import facade
from models.run import Run
from run_repository import RunRepository
from services.research_lab import REQUIRED_CARD_COLUMNS, comparable_spec_ids, evaluate_surprise


def _headers(key: str | None = None) -> dict[str, str]:
    return {"Idempotency-Key": key or str(uuid.uuid4())}


@pytest.fixture(autouse=True)
def _cleanup_card_sessions(client):
    from sqlalchemy import select
    from models.research_session import ResearchSession

    async def ids() -> set[str]:
        repo = RunRepository()
        async with repo._factory() as db:
            return set(await db.scalars(select(ResearchSession.session_id)))

    before = asyncio.run(ids())
    yield
    for session_id in asyncio.run(ids()) - before:
        facade.delete_session(session_id)


def _boot(client) -> dict:
    resp = client.post("/demos/card", headers=_headers())
    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert data["session_id"]
    assert data["run_id"]
    assert data["events_url"] == f"/api/runs/{data['run_id']}/events"
    return data


def test_card_demo_boots_3010_rows_required_columns_and_provenance(client):
    data = _boot(client)
    sid = data["session_id"]
    snapshot = client.get(f"/sessions/{sid}").json()
    research = snapshot["research"]
    dataset = snapshot["dataset"]
    assert research["teaching_case"] == "card_1995"
    assert dataset["rows"] == 3010
    for col in REQUIRED_CARD_COLUMNS:
        assert col in dataset["columns"], col
    provenance = research["provenance"]
    assert provenance["citation"].startswith("Card, D. (1995)")
    assert provenance["checksum"]
    assert "StatsPAI" in provenance["redistribution"]
    assert provenance["extract_kind"] in {"wooldridge_card_34", "statspai_card_9"}
    assert provenance["source"]
    space = research["specification_space"]
    defs = space["definitions"]
    assert 6 <= len(defs) <= 12
    for item in defs:
        assert item["id"]
        assert item["label"]
        assert item["rationale"]
        assert item["dimension"]
        assert item["value"]
        assert isinstance(item["admissible"], bool)
        assert item["user_decision"]


def test_nine_col_path_marks_region_specs_unavailable(client, monkeypatch):
    monkeypatch.setenv("ECONPAPER_CARD_EXTRACT", "statspai_card_9")
    data = _boot(client)
    sid = data["session_id"]
    lab = client.get(f"/sessions/{sid}/research").json()
    assert lab["provenance"]["extract_kind"] == "statspai_card_9"
    by_id = {item["id"]: item for item in lab["specification_space"]["definitions"]}
    for spec_id in ("ols_region_dummies", "iv_region_dummies"):
        assert by_id[spec_id]["admissible"] is False
        assert by_id[spec_id]["user_decision"] == "unavailable"
        assert by_id[spec_id]["unavailable_reason"] == "missing_columns"
    assert by_id["iv_nearc4_linear"]["admissible"] is True
    criterion = lab["expectation"]["criteria"][0]
    assert criterion["left"]["spec_id"] == "iv_nearc4_full"
    assert criterion["right"]["spec_id"] == "ols_full_controls"
    assert criterion["left"]["estimator"] == "iv"
    assert criterion["right"]["estimator"] == "ols"


def test_seed_expectation_carries_single_structured_criterion(client):
    """C1 / C29: Card seed establishes one ordering criterion bound to comparable specs."""
    sid = _boot(client)["session_id"]
    lab = client.get(f"/sessions/{sid}/research").json()
    criteria = lab["expectation"]["criteria"]
    assert isinstance(criteria, list) and len(criteria) == 1
    criterion = criteria[0]
    assert criterion["source"] == "seed"
    assert criterion["kind"] == "ordering"
    assert criterion["operator"] == "lt"
    assert criterion["left"]["metric"] == "estimate.coef"
    assert criterion["left"]["estimator"] == "iv"
    ols_id, iv_id = comparable_spec_ids(lab["specification_space"]["definitions"])
    assert criterion["left"]["spec_id"] == iv_id
    assert criterion["right"]["metric"] == "estimate.coef"
    assert criterion["right"]["estimator"] == "ols"
    assert criterion["right"]["spec_id"] == ols_id
    assert "IV estimate < OLS estimate" in criterion["label"]
    seed_history = lab["expectation"]["history"][0]
    assert seed_history["criteria"][0]["left"]["spec_id"] == iv_id
    assert seed_history["criteria"][0]["right"]["spec_id"] == ols_id


def _strip_nones(value):
    """Drop schema-injected null fields for verbatim comparison."""
    if isinstance(value, dict):
        return {k: _strip_nones(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_strip_nones(item) for item in value]
    return value


def test_expectation_put_explicit_criteria_persist_verbatim(client):
    """C2①: a PUT carrying criteria stores them exactly as submitted.

    The read model projects the full public schema (optional keys may be
    null); every submitted key/value must come back unchanged.
    """
    sid = _boot(client)["session_id"]
    criteria = [
        {
            "id": "criterion.user.iv-above-ols",
            "kind": "ordering",
            "operator": "gt",
            "left": {"metric": "estimate.coef", "estimator": "iv"},
            "right": {"metric": "estimate.coef", "estimator": "ols"},
            "label": "IV estimate > OLS estimate",
            "source": "user",
        }
    ]
    put = client.put(
        f"/sessions/{sid}/research/expectation",
        json={
            "text": "Now I think IV is larger.",
            "confidence": "high",
            "criteria": criteria,
        },
    )
    assert put.status_code == 200, put.text
    stored = put.json()["expectation"]
    assert _strip_nones(stored["criteria"]) == criteria
    # criteria sit beside version/history in the same response
    assert stored["version"] == 2
    assert len(stored["history"]) >= 2


def test_expectation_put_without_criteria_keeps_existing(client):
    """C2②: editing text alone never re-derives or drops the criteria."""
    sid = _boot(client)["session_id"]
    before = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    assert before
    put = client.put(
        f"/sessions/{sid}/research/expectation",
        json={
            "text": "我觉得 IV 应该会更小一些，但并不确定。随意写的别的句子。",
            "confidence": "low",
        },
    )
    assert put.status_code == 200, put.text
    stored = put.json()["expectation"]
    assert stored["criteria"] == before


def test_expectation_put_rejects_malformed_criterion(client):
    sid = _boot(client)["session_id"]
    put = client.put(
        f"/sessions/{sid}/research/expectation",
        json={
            "text": "bad criterion",
            "confidence": "medium",
            "criteria": [{"id": "x", "kind": "nonsense", "left": {}, "operator": "sideways"}],
        },
    )
    assert put.status_code == 422


def _put_criteria(client, sid: str, criteria: list, text: str = "criteria edit"):
    return client.put(
        f"/sessions/{sid}/research/expectation",
        json={"text": text, "confidence": "medium", "criteria": criteria},
    )


def test_expectation_put_rejects_invalid_criterion_combinations(client):
    sid = _boot(client)["session_id"]
    before = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    iv = {"metric": "estimate.coef", "estimator": "iv", "spec_id": "iv_region_dummies"}
    ols = {"metric": "estimate.coef", "estimator": "ols", "spec_id": "ols_region_dummies"}
    illegal = [
        {
            "id": "c.sign-with-right",
            "kind": "sign",
            "operator": "positive",
            "left": iv,
            "right": ols,
            "label": "illegal sign",
            "source": "user",
        },
        {
            "id": "c.ordering-missing-right",
            "kind": "ordering",
            "operator": "lt",
            "left": iv,
            "label": "illegal ordering",
            "source": "user",
        },
        {
            "id": "c.distance-missing-right",
            "kind": "distance",
            "operator": "approx",
            "left": iv,
            "label": "illegal distance",
            "source": "user",
        },
        {
            "id": "c.sign-with-tolerance",
            "kind": "sign",
            "operator": "positive",
            "left": iv,
            "tolerance": {"abs": 0.1},
            "label": "illegal sign tolerance",
            "source": "user",
        },
    ]
    for item in illegal:
        put = _put_criteria(client, sid, [item])
        assert put.status_code == 422, item["id"]
    stored = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    assert stored == before


def test_expectation_put_rejects_empty_selector(client):
    sid = _boot(client)["session_id"]
    before = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    put = _put_criteria(
        client,
        sid,
        [
            {
                "id": "c.empty-selector",
                "kind": "sign",
                "operator": "positive",
                "left": {"metric": "estimate.coef"},
                "label": "no selector",
                "source": "user",
            }
        ],
    )
    assert put.status_code == 422
    stored = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    assert stored == before


def test_expectation_put_rejects_negative_tolerance(client):
    sid = _boot(client)["session_id"]
    before = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    put = _put_criteria(
        client,
        sid,
        [
            {
                "id": "c.neg-tol",
                "kind": "distance",
                "operator": "approx",
                "left": {
                    "metric": "estimate.coef",
                    "estimator": "iv",
                    "spec_id": "iv_region_dummies",
                },
                "right": {
                    "metric": "estimate.coef",
                    "estimator": "ols",
                    "spec_id": "ols_region_dummies",
                },
                "tolerance": {"rel": -0.1},
                "label": "negative tolerance",
                "source": "user",
            }
        ],
    )
    assert put.status_code == 422
    stored = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"]
    assert stored == before


def test_expectation_response_includes_criteria_with_version_history(client):
    """C2③: the ExpectationResponse read model carries criteria."""
    sid = _boot(client)["session_id"]
    lab = client.get(f"/sessions/{sid}/research").json()
    expect = lab["expectation"]
    for key in ("criteria", "version", "history"):
        assert key in expect


def test_expectation_put_round_trips_and_is_not_a_chat_message(client):
    sid = _boot(client)["session_id"]
    body = {
        "text": "OLS positive; IV may be smaller if ability biases upward.",
        "confidence": "high",
        "locale": "en",
    }
    put = client.put(f"/sessions/{sid}/research/expectation", json=body)
    assert put.status_code == 200, put.text
    lab = put.json()
    expect = lab["expectation"]
    assert expect["text"] == body["text"]
    assert expect["confidence"] == "high"
    assert expect["version"] == 2
    assert len(expect["history"]) >= 2
    snapshot = client.get(f"/sessions/{sid}").json()["research"]
    assert snapshot["expectation"]["text"] == body["text"]
    assert snapshot["expectation"]["confidence"] == "high"
    research = client.get(f"/sessions/{sid}/research").json()
    assert research["expectation"] == snapshot["expectation"]
    assert snapshot.get("claim") in (None, {})
    # Not a desk/chat transcript.
    state = facade.get_state(sid)
    assert "desk" not in (state.get("research_lab") or {})
    assert expect["history"][-1]["kind"] == "edit"


def test_freeze_persists_before_results(client):
    sid = _boot(client)["session_id"]
    frozen = client.post(f"/sessions/{sid}/research/specification-space/freeze")
    assert frozen.status_code == 200, frozen.text
    space = frozen.json()["specification_space"]
    assert space["frozen_at"]
    assert space["frozen_before_results"] is True
    assert space["status"] == "frozen"
    again = client.get(f"/sessions/{sid}").json()["research"]["specification_space"]
    assert again["frozen_at"] == space["frozen_at"]
    research = client.get(f"/sessions/{sid}/research").json()
    assert research["specification_space"]["frozen_at"] == space["frozen_at"]


def test_snapshot_research_matches_research_read_model(client):
    sid = _boot(client)["session_id"]
    snapshot = client.get(f"/sessions/{sid}").json()["research"]
    research = client.get(f"/sessions/{sid}/research").json()
    assert snapshot == research


def test_server_state_survives_without_client_storage(client):
    sid = _boot(client)["session_id"]
    client.put(
        f"/sessions/{sid}/research/expectation",
        json={"text": "Keep this on the server.", "confidence": "low"},
    )
    client.post(f"/sessions/{sid}/research/specification-space/freeze")
    later = client.get(f"/sessions/{sid}").json()["research"]
    assert later["expectation"]["text"] == "Keep this on the server."
    assert later["expectation"]["confidence"] == "low"
    assert later["specification_space"]["frozen_at"]
    assert later["teaching_case"] == "card_1995"


def test_research_lab_reattached_if_upload_drops_unknown_keys(client, monkeypatch):
    import runner as runner_mod

    def dropping(session_id, initial_state, **_kwargs):
        result = dict(initial_state)
        result.pop("research_lab", None)
        result["cleaning_report"] = {"steps": []}
        return result

    monkeypatch.setattr(runner_mod, "execute_upload_supervised", dropping)
    accepted = _boot(client)
    assert asyncio.run(
        runner_mod.process_one_run(
            owner="card-lab-reattach",
            run_id=accepted["run_id"],
        )
    )
    sid = accepted["session_id"]
    lab = facade.get_state(sid).get("research_lab") or {}
    assert lab.get("teaching_case") == "card_1995"

    async def stored_result() -> dict:
        repo = RunRepository()
        async with repo._factory() as db:
            run = await db.get(Run, accepted["run_id"])
            assert run is not None
            return dict(run.result or {})

    result = asyncio.run(stored_result())
    assert (result.get("research_lab") or {}).get("teaching_case") == "card_1995"


def _flipped_gt_criterion(seed: dict) -> dict:
    return {
        **seed,
        "operator": "gt",
        "label": "IV estimate > OLS estimate",
        "source": "user",
    }


def test_pre_reveal_criterion_history_keeps_full_snapshots(client):
    sid = _boot(client)["session_id"]
    seed = client.get(f"/sessions/{sid}/research").json()["expectation"]["criteria"][0]
    assert seed["operator"] == "lt"
    put = _put_criteria(
        client,
        sid,
        [_flipped_gt_criterion(seed)],
        text="Now I think IV is larger.",
    )
    assert put.status_code == 200, put.text
    expectation = put.json()["expectation"]
    history = expectation["history"]
    assert history[0]["criteria"][0]["operator"] == "lt"
    assert history[0]["criteria"][0]["left"]["spec_id"] == seed["left"]["spec_id"]
    assert history[0]["criteria"][0]["right"]["spec_id"] == seed["right"]["spec_id"]
    assert seed["left"]["spec_id"]
    assert seed["right"]["spec_id"]
    assert history[-1]["criteria"][0]["operator"] == "gt"
    assert history[-1]["criteria"][0]["left"]["spec_id"] == seed["left"]["spec_id"]
    assert history[-1]["criteria"][0]["right"]["spec_id"] == seed["right"]["spec_id"]
    events = put.json()["decision_events"]
    set_event = next(item for item in reversed(events) if item["kind"] == "expectation_set")
    payload = set_event["payload"]
    assert payload["expectation_version"] == expectation["version"]
    assert payload["criterion_ids"] == [seed["id"]]
    assert payload["criteria"][0]["kind"] == "ordering"
    assert payload["criteria"][0]["operator"] == "gt"
    assert payload["criteria"][0]["left"]["spec_id"] == seed["left"]["spec_id"]
    assert payload["criteria"][0]["right"]["spec_id"] == seed["right"]["spec_id"]
    assert payload["phase"] == "pre_reveal"
    assert payload.get("criteria") != len(expectation["criteria"])


def test_post_reveal_criterion_lock_allows_text_but_rejects_criteria_change(client):
    sid = _boot(client)["session_id"]
    seeded = client.get(f"/sessions/{sid}/research").json()
    before = seeded["expectation"]
    seed = before["criteria"][0]
    history_len = len(before["history"])
    surprise_before = evaluate_surprise(
        before,
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.0747, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.1315, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    state = facade.get_state(sid)
    lab = dict(state["research_lab"])
    space = dict(lab.get("specification_space") or {})
    space["revealed"] = True
    lab["specification_space"] = space
    lab["surprise"] = surprise_before
    facade.update_state(sid, research_lab=lab)
    lab = client.get(f"/sessions/{sid}/research").json()
    assert lab["specification_space"]["revealed"] is True
    surprise_before = lab["surprise"]
    text_put = client.put(
        f"/sessions/{sid}/research/expectation",
        json={
            "text": "我觉得 IV 应该会更小一些，但并不确定。",
            "confidence": "low",
            "criteria": before["criteria"],
        },
    )
    assert text_put.status_code == 200, text_put.text
    after_text = text_put.json()
    assert after_text["expectation"]["text"] == "我觉得 IV 应该会更小一些，但并不确定。"
    assert after_text["expectation"]["criteria"][0]["operator"] == "lt"
    assert after_text["expectation"]["criteria"][0]["left"]["spec_id"] == seed["left"]["spec_id"]
    assert after_text["expectation"]["criteria"][0]["right"]["spec_id"] == seed["right"]["spec_id"]
    assert after_text["surprise"]["status"] == surprise_before["status"]
    assert after_text["surprise"]["observed"] == surprise_before["observed"]
    assert after_text["surprise"]["expectation_version"] == surprise_before["expectation_version"]
    assert after_text["surprise"]["criterion_ids"] == [seed["id"]]
    locked = _put_criteria(client, sid, [_flipped_gt_criterion(seed)], text="try to rewrite after reveal")
    assert locked.status_code == 409, locked.text
    detail = locked.json()["detail"]
    assert detail["code"] == "expectation_criterion_locked"
    later = client.get(f"/sessions/{sid}/research").json()
    assert later["expectation"]["criteria"][0]["operator"] == "lt"
    assert later["expectation"]["criteria"][0]["left"]["spec_id"] == seed["left"]["spec_id"]
    assert later["expectation"]["criteria"][0]["right"]["spec_id"] == seed["right"]["spec_id"]
    assert later["expectation"]["text"] == "我觉得 IV 应该会更小一些，但并不确定。"
    assert later["surprise"]["observed"] == surprise_before["observed"]
    assert later["surprise"]["status"] == surprise_before["status"]
    assert len(later["expectation"]["history"]) == history_len + 1
    set_event = next(
        item for item in reversed(later["decision_events"]) if item["kind"] == "expectation_set"
    )
    assert set_event["payload"]["phase"] == "post_reveal"
    assert set_event["payload"]["criteria"][0]["operator"] == "lt"


def test_challenge_wording_neutral_effective_f():
    from services.research_lab import next_card_challenge

    lab = {
        "specification_space": {
            "definitions": [
                {
                    "id": "ols_region_dummies",
                    "admissible": True,
                },
                {
                    "id": "iv_region_dummies",
                    "admissible": True,
                },
            ],
        },
        "specification_runs": [
            {
                "spec_id": "iv_region_dummies",
                "diagnostics": {"F_eff": 14.14, "first_stage_F": 14.14},
            }
        ],
    }
    challenge = next_card_challenge(lab)
    assert challenge is not None
    assert "may be a weak instrument" not in challenge["rationale"]
    assert "Instrument strength deserves inspection" in challenge["rationale"]
    assert "Effective F = 14.14" in challenge["rationale"]
    assert "Strength diagnostics alone do not establish instrument validity" in challenge["rationale"]
    assert "工具变量强度值得检查" in challenge["rationale_zh"]
    assert "强度诊断本身不能证明工具变量有效" in challenge["rationale_zh"]



