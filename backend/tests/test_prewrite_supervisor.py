"""Focused contracts for the durable pre-write process boundary."""

from __future__ import annotations

import asyncio
import multiprocessing
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from agent.engine.cancellation import ExecutionCancelled
from prewrite_supervisor import (
    RemotePrewriteError,
    RemoteUploadError,
    _attempt_workspace_for_cleanup,
    execute_prewrite_supervised,
    execute_upload_supervised,
)
from tests.spawn_helpers import fail_with_sensitive_text, return_requested_state


def _upload_result(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    return {**initial_state, "completed": True}


def _upload_error(
    _session_id: str,
    _initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    raise ValueError("secret upload path /private/customer.csv")


def test_attempt_cleanup_rejects_legacy_workspace_shape(tmp_path):
    legacy = tmp_path / "runs" / "session-1" / "workspace"
    valid = tmp_path / "attempts" / "run-1" / "epoch-1"

    assert _attempt_workspace_for_cleanup({"workspace": str(legacy)}) is None
    assert _attempt_workspace_for_cleanup({"workspace": str(valid)}) == valid


def _blocked_upload(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    started = Path(initial_state["_started"])
    descendant_done = Path(initial_state["_descendant_done"])
    descendant = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import pathlib,time; time.sleep(1.5); "
                f"pathlib.Path({str(descendant_done)!r}).write_text('done')"
            ),
        ],
        start_new_session=True,
    )
    started.write_text(
        f"{os.getpid()}:{descendant.pid}",
        encoding="utf-8",
    )
    time.sleep(10)
    return {"unexpected": True}


def _progress_flood_upload(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    Path(initial_state["_started"]).write_text("started", encoding="utf-8")
    while True:
        if progress_callback:
            progress_callback("clean_data", "running", {})
        if cancellation_check and cancellation_check():
            raise ExecutionCancelled("cancelled")


def _supervisor_parent(initial_state: dict) -> None:
    execute_upload_supervised(
        "liveness-session",
        initial_state,
        progress_callback=lambda *_args: None,
        cancellation_check=lambda: False,
        child_executor=_blocked_upload,
    )


def _process_is_running(pid: int) -> bool:
    completed = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)],
        check=False,
        capture_output=True,
        text=True,
    )
    status = completed.stdout.strip()
    return bool(status) and not status.startswith("Z")


def test_supervisor_preserves_remote_error_category_from_worker_thread():
    async def scenario():
        return await asyncio.to_thread(
            execute_prewrite_supervised,
            "test-session",
            {},
            {},
            progress_callback=lambda *_args: None,
            cancellation_check=lambda: False,
            child_executor=fail_with_sensitive_text,
        )

    with pytest.raises(RemotePrewriteError) as raised:
        asyncio.run(scenario())
    assert raised.value.error_type == "RuntimeError", raised.value.stage
    assert "secret-token" not in str(raised.value)


def test_prewrite_adapter_preserves_existing_result_contract():
    expected = {"outline": [{"title": "result"}]}
    result = execute_prewrite_supervised(
        "test-session",
        {"topic": "direction"},
        {"_test_child_result": expected},
        progress_callback=lambda *_args: None,
        cancellation_check=lambda: False,
        child_executor=return_requested_state,
    )
    assert result == expected


def test_facade_execute_upload_never_reads_or_writes_session_store(monkeypatch):
    from facade import AgentFacade

    class ExplodingStore:
        def __getattr__(self, name):
            raise AssertionError(f"SessionStore I/O attempted: {name}")

    facade = AgentFacade.__new__(AgentFacade)
    facade._store = ExplodingStore()
    captured = {}

    def fake_run_upload(state, progress=None, should_cancel=None):
        captured.update(state)
        return {**state, "pure": True}

    monkeypatch.setattr("agent.engine.upload.run_upload", fake_run_upload)
    result = facade.execute_upload(
        "pure-session",
        {"workspace": "/tmp/attempts/run/epoch"},
        progress_callback=lambda *_args: None,
        cancellation_check=lambda: False,
    )

    assert result["pure"] is True
    assert captured == {
        "session_id": "pure-session",
        "workspace": "/tmp/attempts/run/epoch",
    }


def test_upload_adapter_returns_state_and_sanitizes_remote_errors(tmp_path):
    workspace = tmp_path / "attempts" / "run-1" / "epoch-1"
    result = execute_upload_supervised(
        "upload-session",
        {"workspace": str(workspace)},
        progress_callback=lambda *_args: None,
        cancellation_check=lambda: False,
        child_executor=_upload_result,
    )
    assert result["completed"] is True

    with pytest.raises(RemoteUploadError) as raised:
        execute_upload_supervised(
            "upload-session",
            {"workspace": str(workspace)},
            progress_callback=lambda *_args: None,
            cancellation_check=lambda: False,
            child_executor=_upload_error,
        )
    assert raised.value.error_type == "ValueError"
    assert raised.value.stage == "executor"
    assert "customer.csv" not in str(raised.value)


def test_upload_cancellation_is_not_starved_and_removes_attempt_workspace(tmp_path):
    workspace = tmp_path / "attempts" / "run-2" / "epoch-3"
    workspace.mkdir(parents=True)
    (workspace / "partial.csv").write_text("partial", encoding="utf-8")
    started = tmp_path / "started"
    descendant_done = tmp_path / "descendant-done"
    began = time.monotonic()

    with pytest.raises(ExecutionCancelled):
        execute_upload_supervised(
            "upload-session",
            {
                "workspace": str(workspace),
                "_started": str(started),
                "_descendant_done": str(descendant_done),
            },
            progress_callback=lambda *_args: None,
            cancellation_check=lambda: started.exists(),
            child_executor=_blocked_upload,
        )

    assert time.monotonic() - began < 1.0
    assert not workspace.exists()
    time.sleep(1.7)
    assert not descendant_done.exists()


def test_high_frequency_progress_does_not_starve_cooperative_cancellation(tmp_path):
    started = tmp_path / "progress-started"
    began = time.monotonic()
    with pytest.raises(ExecutionCancelled):
        execute_upload_supervised(
            "upload-session",
            {
                "workspace": str(
                    tmp_path / "attempts" / "run-progress" / "epoch-1"
                ),
                "_started": str(started),
            },
            progress_callback=lambda *_args: None,
            cancellation_check=lambda: started.exists(),
            child_executor=_progress_flood_upload,
        )
    assert time.monotonic() - began < 1.0


@pytest.mark.skipif(os.name != "posix", reason="POSIX process liveness contract")
def test_parent_sigkill_liveness_pipe_terminates_child_and_independent_descendant(
    tmp_path,
):
    workspace = tmp_path / "attempts" / "run-3" / "epoch-5"
    started = tmp_path / "liveness-started"
    descendant_done = tmp_path / "liveness-descendant-done"
    context = multiprocessing.get_context("spawn")
    parent = context.Process(
        target=_supervisor_parent,
        args=(
            {
                "workspace": str(workspace),
                "_started": str(started),
                "_descendant_done": str(descendant_done),
            },
        ),
    )
    parent.start()
    deadline = time.monotonic() + 3.0
    while not started.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert started.exists()
    child_pid, descendant_pid = (
        int(value) for value in started.read_text(encoding="utf-8").split(":")
    )

    os.kill(parent.pid, signal.SIGKILL)
    parent.join(timeout=1.0)
    assert not parent.is_alive()
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline and (
        _process_is_running(child_pid) or _process_is_running(descendant_pid)
    ):
        time.sleep(0.01)
    assert not _process_is_running(child_pid)
    assert not _process_is_running(descendant_pid)
    time.sleep(1.7)
    assert not descendant_done.exists()
