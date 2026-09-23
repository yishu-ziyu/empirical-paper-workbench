"""A stopped worker must not leave its still-owned lease idle for 60 seconds."""
import asyncio
import uuid

import pytest

from agent.engine.cancellation import ExecutionCancelled
from facade import facade
from run_repository import LeaseLost, RunRepository
import runner


def test_locally_cancelled_worker_relinquishes_only_its_own_lease(monkeypatch):
    sid = f"relinquish-{uuid.uuid4().hex}"
    facade.seed_state(sid, {})

    def interrupted(*args, **kwargs):
        raise ExecutionCancelled("simulated authority interruption")

    monkeypatch.setattr(runner, "execute_prewrite_supervised", interrupted)

    async def run():
        repo = RunRepository()
        accepted = await repo.enqueue(session_id=sid, kind="prewrite", payload={"research_direction": {}, "initial_state": {}}, idempotency_key="intent")
        assert await runner.process_one_run(owner="old", run_id=accepted.run_id)
        stopped = await repo.get(accepted.run_id)
        assert stopped.status == "PENDING"
        next_claim = await repo.claim(owner="new", run_id=accepted.run_id)
        assert next_claim.run_id == accepted.run_id
        assert next_claim.lease_epoch == 2
        with pytest.raises(LeaseLost):
            await repo.complete(accepted.run_id, owner="old", lease_epoch=1, result={})
        events = await repo.events_after(accepted.run_id, 0)
        assert any(event.event_type == "run.requeued" for event in events)

    try:
        asyncio.run(run())
    finally:
        facade.drop_session(sid)


def test_relinquish_does_not_revive_terminal_or_stolen_work():
    sid = f"relinquish-fence-{uuid.uuid4().hex}"
    facade.seed_state(sid, {})

    async def run():
        repo = RunRepository()
        accepted = await repo.enqueue(session_id=sid, kind="prewrite", payload={}, idempotency_key="intent")
        claim = await repo.claim(owner="rightful", run_id=accepted.run_id)
        assert not await repo.relinquish(accepted.run_id, owner="stale", lease_epoch=claim.lease_epoch)
        assert (await repo.get(accepted.run_id)).lease_owner == "rightful"
        await repo.fail(accepted.run_id, owner="rightful", lease_epoch=claim.lease_epoch, error="test terminal")
        assert not await repo.relinquish(accepted.run_id, owner="rightful", lease_epoch=claim.lease_epoch)
        assert (await repo.get(accepted.run_id)).status == "FAILED"

    try:
        asyncio.run(run())
    finally:
        facade.drop_session(sid)
