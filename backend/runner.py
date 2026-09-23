"""Independent worker process for durable econpaper runs."""

from __future__ import annotations

import argparse
import asyncio
import logging
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
from runner_logging import configure_runner_logging
from services.research_lab import reattach_research_lab
from services.spec_run import execute_spec_run
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
AUTHORITY_PROBE_TIMEOUT_SECONDS = 0.65
# A negative authority answer stops work immediately. A slow-but-successful
# probe is allowed enough room for short SQLite/Postgres contention, while a
# continuously unavailable/stuck authority still trips the existing <1s
# cancellation contract. Every progress/terminal write remains owner+epoch
# fenced, so a stale worker cannot publish even inside this bounded window.
AUTHORITY_FAILURE_GRACE_SECONDS = 0.5
PROGRESS_WRITE_TIMEOUT_SECONDS = 0.2
DEFAULT_CONCURRENCY = 3
logger = logging.getLogger("econpaper.runner")


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
    from services.spec_run import SpecRunRejected

    if isinstance(exc, SpecRunRejected):
        return exc.code
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
    *,
    poll_seconds: float = CANCELLATION_POLL_SECONDS,
    probe_timeout_seconds: float = AUTHORITY_PROBE_TIMEOUT_SECONDS,
    authority_failure_grace_seconds: float = AUTHORITY_FAILURE_GRACE_SECONDS,
    heartbeat_seconds: float = HEARTBEAT_SECONDS,
) -> None:
    next_heartbeat = time.monotonic() + heartbeat_seconds
    authority_failure_started: float | None = None
    while True:
        await asyncio.sleep(poll_seconds)
        probe_started = time.monotonic()
        try:
            lease_is_current = await asyncio.wait_for(
                repo.lease_is_current(
                    run_id,
                    owner=owner,
                    lease_epoch=lease_epoch,
                ),
                timeout=probe_timeout_seconds,
            )
            if not lease_is_current:
                logger.warning("authority_lost run=%s epoch=%s reason=not_current", run_id, lease_epoch)
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
                    timeout=probe_timeout_seconds,
                )
                next_heartbeat = time.monotonic() + heartbeat_seconds
        except LeaseLost:
            lease_lost.set()
            return
        except Exception as exc:
            now = time.monotonic()
            if authority_failure_started is None:
                # Count time already spent waiting for a stuck probe. Without
                # this, a timeout only starts the grace clock after it returns,
                # stretching a nominal sub-second fence well past one second.
                authority_failure_started = probe_started
            if now - authority_failure_started >= authority_failure_grace_seconds:
                logger.warning("authority_lost run=%s epoch=%s reason=%s elapsed=%.3f",
                               run_id, lease_epoch, type(exc).__name__, now - probe_started)
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
    started = time.monotonic()
    logger.info("execution_start run=%s kind=%s attempt=%s epoch=%s",
                claimed.run_id, claimed.kind, claimed.attempt, claimed.lease_epoch)

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

    async def relinquish_stopped_work() -> None:
        try:
            released = await asyncio.wait_for(repo.relinquish(
                claimed.run_id, owner=worker, lease_epoch=claimed.lease_epoch,
            ), timeout=1.0)
            if released:
                logger.info("execution_requeued run=%s epoch=%s", claimed.run_id, claimed.lease_epoch)
                await asyncio.sleep(0.25)
        except Exception as exc:
            # If the store remains unavailable, the existing lease-expiry
            # recovery still applies. Never pretend that it was relinquished.
            logger.warning("relinquish_unavailable run=%s reason=%s", claimed.run_id, type(exc).__name__)

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
            phase = claimed.payload.get("phase") or initial_state.get("prewrite_phase")
            if phase:
                initial_state["prewrite_phase"] = phase
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
            state = reattach_research_lab(state, initial_state)
        elif claimed.kind == "spec_run":
            state = await asyncio.to_thread(
                execute_spec_run,
                claimed.session_id,
                claimed.run_id,
                claimed.payload,
                progress,
            )
        else:
            raise RuntimeError("unsupported run kind")
    except (ExecutionCancelled, LeaseLost):
        logger.warning("execution_cancelled run=%s epoch=%s elapsed=%.3f",
                       claimed.run_id, claimed.lease_epoch, time.monotonic() - started)
        _remove_upload_attempt(upload_attempt)
        await relinquish_stopped_work()
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
        if claimed.kind == "spec_run":
            from services.research_lab import strip_spec_run_result

            result = strip_spec_run_result(result)
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
            except Exception as exc:
                logger.warning("terminal_commit_retry run=%s epoch=%s attempt=%s reason=%s",
                               claimed.run_id, claimed.lease_epoch, attempt + 1, type(exc).__name__)
                if attempt < 2:
                    await asyncio.sleep(0.1 * (2**attempt))
                    continue
                # Execution succeeded, but its atomic terminal commit did not.
                # Return a still-owned lease promptly instead of imposing an
                # idle 60-second expiry wait after local work already stopped.
                await relinquish_stopped_work()
                break
    finally:
        logger.info("execution_end run=%s epoch=%s elapsed=%.3f", claimed.run_id,
                    claimed.lease_epoch, time.monotonic() - started)
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
    # Output-channel lifecycle first: a dead console pipe must never turn a
    # healthy run into FAILED (issue #30). Business failure semantics below
    # are unchanged.
    configure_runner_logging()
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
