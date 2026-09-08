"""Runner logging lifecycle contracts (issue #30).

A dead console pipe (runner fd1/fd2 bound to a pipe whose read end closed)
must never turn a healthy run into FAILED, while genuine business failures --
including a business-path ``BrokenPipeError`` -- must still be reported as
FAILED with a stable, diagnosable error string.

Process-level reproduction (before/after) lives in
``docs/acceptance/assets/runner-logging-lifecycle/harness/``; these pytest
contracts pin the unit-level behavior that the full-stack run depends on.
"""

from __future__ import annotations

import asyncio
import importlib
import io
import logging
import sys
import uuid
from functools import partial
from pathlib import Path

import pytest

import runner_logging
from facade import facade
from logging.handlers import RotatingFileHandler
from prewrite_supervisor import execute_upload_supervised
from run_repository import RunRepository, upload_fingerprint
from runner import _stable_failure, process_one_run
from tests.spawn_helpers import (
    fail_upload_with_broken_pipe,
    fail_upload_with_sensitive_text,
    write_upload_result,
)


class _FailingStream:
    """A console stream whose read end died: every write/flush raises."""

    def write(self, *args, **kwargs):
        raise BrokenPipeError(32, "Broken pipe")

    def flush(self, *args, **kwargs):
        raise BrokenPipeError(32, "Broken pipe")

    def __getattr__(self, name):
        raise AttributeError(name)


@pytest.fixture
def isolated_root_logging():
    """Snapshot and restore process-global logging state around a test."""
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    saved_raise = logging.raiseExceptions
    saved_streams = (sys.stdout, sys.stderr)
    saved_flag = getattr(root, "_econpaper_runner_logging_configured", None)
    yield root
    root.handlers[:] = saved_handlers
    root.setLevel(saved_level)
    logging.raiseExceptions = saved_raise
    sys.stdout, sys.stderr = saved_streams
    if saved_flag is None:
        if hasattr(root, "_econpaper_runner_logging_configured"):
            del root._econpaper_runner_logging_configured
    else:
        root._econpaper_runner_logging_configured = saved_flag
    runner_logging._DEGRADATION_TRACED.clear()


# ---------------------------------------------------------------------------
# C3: business failures stay FAILED and diagnosable
# ---------------------------------------------------------------------------


def test_stable_failure_classification_is_unchanged():
    assert (
        _stable_failure(BrokenPipeError(32, "Broken pipe"), "upload_pipeline")
        == "BrokenPipeError: upload_pipeline execution failed"
    )
    assert (
        _stable_failure(RuntimeError("boom"), "prewrite")
        == "RuntimeError: prewrite execution failed"
    )


def _admit_upload(tmp_path: Path, sid: str):
    source = tmp_path / f"{sid}.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    return asyncio.run(
        RunRepository().admit_upload(
            session_id=sid,
            user_id=None,
            csv_path=str(source),
            dataset_meta={"columns": ["x", "y"], "rows": 1},
            initial_state={
                "session_id": sid,
                "csv_path": str(source),
                "uploaded_datasets": [{"path": str(source), "format": "csv"}],
            },
            idempotency_key=f"{sid}-key",
            input_fingerprint=upload_fingerprint(source.read_bytes(), source.name),
        )
    )


def _use_upload_child_executor(monkeypatch, executor) -> None:
    monkeypatch.setattr(
        "runner.execute_upload_supervised",
        partial(execute_upload_supervised, child_executor=executor),
    )


@pytest.mark.parametrize(
    ("executor", "expected_error"),
    [
        (
            fail_upload_with_broken_pipe,
            "BrokenPipeError: upload_pipeline executor failed",
        ),
        (
            fail_upload_with_sensitive_text,
            "RuntimeError: upload_pipeline executor failed",
        ),
    ],
)
def test_business_failures_still_fail_the_run_with_stable_error(
    tmp_path, monkeypatch, executor, expected_error
):
    """A business BrokenPipeError must not be swallowed by the log fix."""
    from config import settings

    sid = f"runner-log-c3-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, executor)
    admission = _admit_upload(tmp_path, sid)
    try:
        assert asyncio.run(
            process_one_run(owner="c3-business-failure", run_id=admission.run.run_id)
        ) is True
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "FAILED"
        assert durable.error == expected_error
    finally:
        facade.delete_session(sid)


# ---------------------------------------------------------------------------
# C4(b)/(c): no duplicate execution or submission
# ---------------------------------------------------------------------------


def test_successful_upload_run_leaves_single_records_and_result(
    tmp_path, monkeypatch
):
    from config import settings

    sid = f"runner-log-c4-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, write_upload_result)
    admission = _admit_upload(tmp_path, sid)
    try:
        assert asyncio.run(
            process_one_run(owner="c4-uniqueness", run_id=admission.run.run_id)
        ) is True
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "SUCCEEDED"
        assert durable.attempt == 1

        events = asyncio.run(
            RunRepository().events_after(admission.run.run_id, 0)
        )
        assert len([e for e in events if e.event_type == "run.succeeded"]) == 1
        assert len([e for e in events if e.event_type == "run.claimed"]) == 1

        entry = facade.get_session_entry(sid)
        assert entry["state"]["upload_readiness"] == "READY"
        cleaned = Path(entry["csv_path"])
        assert cleaned.name == "cleaned.csv"
        # One submitted result: the referenced artifact exists exactly once
        # and no sibling cleaned.csv duplicates were produced.
        assert list(cleaned.parent.glob("cleaned*.csv")) == [cleaned]
    finally:
        facade.delete_session(sid)


# ---------------------------------------------------------------------------
# C4(d): configuration idempotency (re-entry + import re-entry)
# ---------------------------------------------------------------------------


def _own_handlers(root: logging.Logger) -> list[logging.Handler]:
    """Handlers installed by the runner logging lifecycle."""
    return [
        h
        for h in root.handlers
        if isinstance(h, RotatingFileHandler)
        or getattr(h, "_econpaper_channel_guard", False)
    ]


def test_configure_is_idempotent_across_reentry_and_reload(
    isolated_root_logging, tmp_path
):
    root = isolated_root_logging
    log_file = tmp_path / "log" / "runner.log"

    runner_logging.configure_runner_logging(log_file=log_file)
    own_first = _own_handlers(root)
    assert [type(h).__name__ for h in own_first] == [
        "RotatingFileHandler",
        "SelfDisablingStreamHandler",
    ]

    # Re-entry (same process, repeated calls, different arguments).
    runner_logging.configure_runner_logging(log_file=tmp_path / "other.log")
    runner_logging.configure_runner_logging()
    assert _own_handlers(root) == own_first

    # Import re-entry: reload the module and configure again.
    importlib.reload(runner_logging)
    runner_logging.configure_runner_logging(log_file=tmp_path / "third.log")
    assert _own_handlers(root) == own_first

    assert logging.raiseExceptions is False


def test_child_configuration_installs_no_file_handler(isolated_root_logging):
    root = isolated_root_logging
    before = len(root.handlers)
    runner_logging.configure_runner_logging(child=True)
    runner_logging.configure_runner_logging(child=True)
    assert len(root.handlers) == before
    assert logging.raiseExceptions is False
    # Stream hardening still applies: spawn children re-import fresh and must
    # not inherit fragile raw streams.
    assert getattr(sys.stdout, "_econpaper_tolerant", False)


# ---------------------------------------------------------------------------
# C4(a) + C5: degradation behavior
# ---------------------------------------------------------------------------


def test_multiprocessing_spawn_flush_cannot_escape(isolated_root_logging):
    """Pin the actual pre-fix escape path.

    multiprocessing.util._flush_std_streams() flushes sys.stdout inside
    process.start() with only (AttributeError, ValueError) guarded; with raw
    failing streams the BrokenPipeError propagated into
    _execute_supervised -> process_one_run -> FAILED. The tolerant wrappers
    close that path.
    """
    import multiprocessing.util

    runner_logging.harden_standard_streams()
    assert getattr(sys.stdout, "_econpaper_tolerant", False)
    assert getattr(sys.stderr, "_econpaper_tolerant", False)
    # Point the wrappers at dead console streams (as with a closed pipe).
    sys.stdout._stream = _FailingStream()
    sys.stderr._stream = _FailingStream()

    # The exact stdlib call that killed production runs.
    multiprocessing.util._flush_std_streams()
    sys.stdout.write("dropped")
    sys.stdout.flush()


def test_dead_console_degrades_once_and_file_survives(
    isolated_root_logging, tmp_path
):
    root = isolated_root_logging
    log_file = tmp_path / "log" / "runner.log"
    runner_logging.configure_runner_logging(log_file=log_file)

    # Rebind the console handler to a dead stream (the file handler stays).
    console = next(
        h
        for h in root.handlers
        if getattr(h, "_econpaper_channel_guard", False)
    )
    console.stream = _FailingStream()

    for index in range(300):
        logging.getLogger("runner.dead-pipe-flood").info("record %d", index)

    assert console._econpaper_channel_disabled is True
    content = log_file.read_text(encoding="utf-8")
    traces = [line for line in content.splitlines() if "unavailable" in line]
    assert len(traces) == 1, traces
    assert "stderr" in traces[0]
    assert "file(" in traces[0] and "runner.log" in traces[0]
    # The file channel keeps receiving records after the console died.
    assert "record 299" in content


def test_healthy_channels_log_to_file_and_console(
    isolated_root_logging, tmp_path
):
    root = isolated_root_logging
    log_file = tmp_path / "log" / "runner.log"
    console_buffer = io.StringIO()
    runner_logging.configure_runner_logging(log_file=log_file)
    console = next(
        h
        for h in root.handlers
        if getattr(h, "_econpaper_channel_guard", False)
    )
    console.stream = console_buffer

    logging.getLogger("runner.healthy").info("healthy channel record")

    assert "healthy channel record" in console_buffer.getvalue()
    assert "healthy channel record" in log_file.read_text(encoding="utf-8")


def test_all_channels_unavailable_process_and_business_survive(
    isolated_root_logging, tmp_path, monkeypatch
):
    """File and console both unusable: records drop, nothing raises."""
    root = isolated_root_logging
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")

    monkeypatch.setattr(sys, "stderr", _FailingStream())
    # The log path cannot be created: its parent is a regular file.
    runner_logging.configure_runner_logging(log_file=blocker / "log" / "runner.log")

    # The file channel degraded away; only our console handler was added.
    own = _own_handlers(root)
    assert len(own) == 1
    console = own[0]
    assert getattr(console, "_econpaper_channel_guard", False)

    def business_payload() -> str:
        for index in range(20):
            logging.getLogger("runner.all-dead").info("dropped %d", index)
        return "business-complete"

    assert business_payload() == "business-complete"
    assert console._econpaper_channel_disabled is True


def test_tolerant_stream_drops_without_raising():
    stream = runner_logging.TolerantStream(_FailingStream(), "stderr")
    assert stream.write("payload") == len("payload")
    stream.flush()
    # Unknown attributes still delegate to the wrapped stream.
    with pytest.raises(AttributeError):
        stream.unavailable_attribute
