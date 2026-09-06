"""Independent worker process for durable econpaper runs."""

from __future__ import annotations

import argparse
import asyncio
import os
import random
import shutil
import socket
import threading
import time
import uuid
from pathlib import Path

import run_store
from config import ensure_private_directory
from database import create_tables
from run_repository import LeaseLost, RunRepository, UploadResultInvalid
from agent.engine.cancellation import ExecutionCancelled
from prewrite_supervisor import (
    RemoteExecutionError,
    RemotePrewriteError,
    execute_prewrite_supervised,
    execute_upload_supervised,
)
from upload_artifacts import (
    reconcile_upload_artifacts,
    reconcile_upload_artifacts_forever,
)


LEASE_SECONDS = 60
HEARTBEAT_SECONDS = 20
CANCELLATION_POLL_SECONDS = 0.25
AUTHORITY_PROBE_TIMEOUT_SECONDS = 0.2
AUTHORITY_FAILURE_GRACE_SECONDS = 0.4
PROGRESS_WRITE_TIMEOUT_SECONDS = 0.2
DEFAULT_CONCURRENCY = 3


def _default_owner() -> str:
    return f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:8]}"


def _stamp_estimate_producer(
    result: dict, run_id: str, initial_state: dict
) -> dict:
    """Bind estimate to this run only when this run produced or replaced it."""
    estimate = result.get("estimate")
    if not isinstance(estimate, dict):
        return result
    if estimate.get("produced_by") != "estimate":
        return result
    initial_estimate = (
        initial_state.get("estimate") if isinstance(initial_state, dict) else None
    )
    if estimate == initial_estimate:
        return result
    existing = estimate.get("source_run_id")
    if isinstance(existing, str) and existing.strip():
        return result
    return {**result, "estimate": {**estimate, "source_run_id": run_id}}


def _upload_attempt_workspace(
    session_id: str,
    run_id: str,
    lease_epoch: int,
) -> str:
    path = (
        run_store.run_dir(session_id)
        / "attempts"
        / run_id
        / f"epoch-{lease_epoch}"
    )
    ensure_private_directory(path)
    return str(path)


def _remove_upload_attempt(path: Path | None) -> None:
    if path is None:
        return
    shutil.rmtree(path, ignore_errors=True)
    # Remove only empty ownership parents. A reclaimed epoch makes rmdir fail,
    # so a stale worker cannot erase another worker's attempt.
    for parent in (path.parent, path.parent.parent, path.parent.parent.parent):
        try:
            parent.rmdir()
        except OSError:
            break


def _stable_failure(exc: Exception, run_kind: str) -> str:
    if isinstance(exc, UploadResultInvalid):
        return "UnreadableOutput: upload_pipeline output_validation failed"
    if isinstance(exc, RemoteExecutionError):
        if isinstance(exc, RemotePrewriteError):
            return f"{exc.error_type}: prewrite execution failed"
        return f"{exc.error_type}: upload_pipeline {exc.stage} failed"
    return f"{type(exc).__name__}: {run_kind} execution failed"


async def _heartbeat(
    repo: RunRepository,
    run_id: str,
    owner: str,
    lease_epoch: int,
    lease_lost: threading.Event,
) -> None:
    next_heartbeat = time.monotonic() + HEARTBEAT_SECONDS
    authority_failure_started: float | None = None
    while True:
        await asyncio.sleep(CANCELLATION_POLL_SECONDS)
        try:
            lease_is_current = await asyncio.wait_for(
                repo.lease_is_current(
                    run_id,
                    owner=owner,
                    lease_epoch=lease_epoch,
                ),
                timeout=AUTHORITY_PROBE_TIMEOUT_SECONDS,
            )
            if not lease_is_current:
                lease_lost.set()
                return
            authority_failure_started = None
            if time.monotonic() >= next_heartbeat:
                await asyncio.wait_for(
                    repo.heartbeat(
                        run_id,
                        owner=owner,
                        lease_epoch=lease_epoch,
                        lease_seconds=LEASE_SECONDS,
                    ),
                    timeout=AUTHORITY_PROBE_TIMEOUT_SECONDS,
                )
                next_heartbeat = time.monotonic() + HEARTBEAT_SECONDS
        except LeaseLost:
            lease_lost.set()
            return
        except Exception:
            now = time.monotonic()
            if authority_failure_started is None:
                authority_failure_started = now
            elif now - authority_failure_started >= AUTHORITY_FAILURE_GRACE_SECONDS:
                lease_lost.set()
                return


async def process_one_run(
    *,
    owner: str | None = None,
    run_id: str | None = None,
) -> bool:
    """Claim and execute one run. Return False when the queue is empty."""
    repo = RunRepository()
    worker = owner or _default_owner()
    claimed = (
        await repo.claim(run_id, worker, lease_seconds=LEASE_SECONDS)
        if run_id
        else await repo.claim_next(worker, lease_seconds=LEASE_SECONDS)
    )
    if claimed is None:
        return False

    loop = asyncio.get_running_loop()
    lease_lost = threading.Event()
    heartbeat = asyncio.create_task(
        _heartbeat(
            repo,
            claimed.run_id,
            worker,
            claimed.lease_epoch,
            lease_lost,
        )
    )
    upload_attempt: Path | None = None

    def progress(node: str, status: str, detail: dict) -> None:
        if lease_lost.is_set():
            raise LeaseLost(f"run {claimed.run_id} lease heartbeat expired")
        payload = {"node": node, "status": status, **detail}
        future = asyncio.run_coroutine_threadsafe(
            repo.append_worker_event(
                claimed.run_id,
                "run.progress",
                payload,
                owner=worker,
                lease_epoch=claimed.lease_epoch,
            ),
            loop,
        )
        try:
            future.result(timeout=PROGRESS_WRITE_TIMEOUT_SECONDS)
        except LeaseLost:
            raise
        except Exception:
            future.cancel()
            # Progress is observability, not the business result. A temporary
            # event-store delay must not turn valid research work into FAILED;
            # lease heartbeat remains the authority for stopping stale work.
            if lease_lost.is_set():
                raise LeaseLost(f"run {claimed.run_id} lease heartbeat expired")

    try:
        initial_state = dict(claimed.payload["initial_state"])
        if claimed.kind == "prewrite":
            initial_state["source_run_id"] = claimed.run_id
            direction = claimed.payload["research_direction"]
            state = await asyncio.to_thread(
                execute_prewrite_supervised,
                claimed.session_id,
                direction,
                initial_state,
                progress_callback=progress,
                cancellation_check=lease_lost.is_set,
            )
        elif claimed.kind == "upload_pipeline":
            upload_attempt = Path(
                _upload_attempt_workspace(
                    claimed.session_id,
                    claimed.run_id,
                    claimed.lease_epoch,
                )
            )
            initial_state["workspace"] = str(upload_attempt)
            state = await asyncio.to_thread(
                execute_upload_supervised,
                claimed.session_id,
                initial_state,
                progress_callback=progress,
                cancellation_check=lease_lost.is_set,
            )
        else:
            raise RuntimeError("unsupported run kind")
    except (ExecutionCancelled, LeaseLost):
        _remove_upload_attempt(upload_attempt)
        return True
    except Exception as exc:
        try:
            await repo.fail(
                claimed.run_id,
                owner=worker,
                lease_epoch=claimed.lease_epoch,
                # The status API is user-visible. Provider errors can contain
                # response bodies or credentials, so persist only a stable,
                # non-sensitive failure category here.
                error=_stable_failure(exc, claimed.kind),
            )
        except LeaseLost:
            pass
        finally:
            _remove_upload_attempt(upload_attempt)
    else:
        result = {**state, "_source_run_id": claimed.run_id}
        if claimed.kind == "prewrite":
            result = _stamp_estimate_producer(
                result,
                claimed.run_id,
                dict((claimed.payload or {}).get("initial_state") or {}),
            )
        for attempt in range(3):
            try:
                await repo.complete(
                    claimed.run_id,
                    owner=worker,
                    lease_epoch=claimed.lease_epoch,
                    result=result,
                )
                break
            except LeaseLost:
                _remove_upload_attempt(upload_attempt)
                break
            except UploadResultInvalid as exc:
                try:
                    await repo.fail(
                        claimed.run_id,
                        owner=worker,
                        lease_epoch=claimed.lease_epoch,
                        error=_stable_failure(exc, claimed.kind),
                    )
                except LeaseLost:
                    pass
                finally:
                    _remove_upload_attempt(upload_attempt)
                break
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(0.1 * (2**attempt))
                    continue
                # Execution succeeded, but its atomic terminal commit did not.
                # Keep the run reclaimable instead of reporting a false business
                # failure; another leased attempt can safely recompute it.
                break
    finally:
        heartbeat.cancel()
        try:
            await heartbeat
        except asyncio.CancelledError:
            pass
    return True


async def _worker_loop(*, poll_seconds: float, owner: str) -> None:
    failures = 0
    while True:
        try:
            processed = await process_one_run(owner=owner)
            failures = 0
        except Exception:
            failures += 1
            delay = min(30.0, poll_seconds * (2 ** min(failures, 5)))
            await asyncio.sleep(delay + random.uniform(0, delay * 0.2))
            continue
        if not processed:
            await asyncio.sleep(poll_seconds)


async def run_forever(
    *,
    poll_seconds: float = 1.0,
    owner: str | None = None,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> None:
    await create_tables()
    await reconcile_upload_artifacts()
    worker = owner or _default_owner()
    reconciler = asyncio.create_task(reconcile_upload_artifacts_forever())
    try:
        await asyncio.gather(
            *(
                _worker_loop(poll_seconds=poll_seconds, owner=f"{worker}:{slot}")
                for slot in range(max(1, concurrency))
            )
        )
    finally:
        reconciler.cancel()
        try:
            await reconciler
        except asyncio.CancelledError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="econpaper durable run worker")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.getenv("RUNNER_CONCURRENCY", str(DEFAULT_CONCURRENCY))),
    )
    args = parser.parse_args()
    if args.once:
        async def run_once() -> None:
            await create_tables()
            await reconcile_upload_artifacts()
            await process_one_run()

        asyncio.run(run_once())
    else:
        asyncio.run(
            run_forever(
                poll_seconds=args.poll_seconds,
                concurrency=args.concurrency,
            )
        )


if __name__ == "__main__":
    main()
