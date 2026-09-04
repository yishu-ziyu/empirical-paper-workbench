"""Process boundary for cancellable durable Run execution."""

from __future__ import annotations

import multiprocessing
import os
import signal
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Literal

from agent.engine.cancellation import ExecutionCancelled


CANCELLATION_GRACE_SECONDS = 0.15
TERMINATION_GRACE_SECONDS = 0.15
SUPERVISOR_POLL_SECONDS = 0.01
MAX_MESSAGES_PER_POLL = 32


RunKind = Literal["prewrite", "upload_pipeline"]


class RemoteExecutionError(RuntimeError):
    """A child failure whose sensitive message must not cross the boundary."""

    def __init__(self, run_kind: RunKind, error_type: str, stage: str) -> None:
        super().__init__(f"{run_kind} child failed")
        self.run_kind = run_kind
        self.error_type = error_type
        self.stage = stage


class RemotePrewriteError(RemoteExecutionError):
    """Backward-compatible pre-write child failure."""

    def __init__(self, error_type: str, stage: str = "executor") -> None:
        super().__init__("prewrite", error_type, stage)


class RemoteUploadError(RemoteExecutionError):
    """Sanitized upload child failure."""

    def __init__(self, error_type: str, stage: str = "executor") -> None:
        super().__init__("upload_pipeline", error_type, stage)


def _terminate_orphaned_child(root_pid: int, process_group_ready: bool) -> None:
    """Terminate the child and descendants after its supervisor disappears."""
    for descendant_pid in _descendant_pids(root_pid):
        _signal_pid(descendant_pid, signal.SIGKILL)
    if process_group_ready:
        try:
            os.killpg(root_pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    os._exit(70)


def _watch_parent_liveness(
    receiver: Connection,
    stop: threading.Event,
    root_pid: int,
    process_group_ready: bool,
    supervisor_pid: int,
) -> None:
    while not stop.is_set():
        if os.getppid() != supervisor_pid:
            _terminate_orphaned_child(root_pid, process_group_ready)
        try:
            if not receiver.poll(0.05):
                continue
            receiver.recv()
            return
        except (EOFError, BrokenPipeError, OSError):
            if not stop.is_set():
                _terminate_orphaned_child(root_pid, process_group_ready)
            return


def _child_main(
    run_kind: RunKind,
    session_id: str,
    command: dict | None,
    initial_state: dict,
    sender: Connection,
    cancellation_receiver: Connection,
    liveness_receiver: Connection,
    child_executor: Callable[..., dict] | None,
) -> None:
    stage = "process_group"
    liveness_stop = threading.Event()
    try:
        process_group_ready = False
        if os.name == "posix":
            try:
                os.setsid()
            except PermissionError:
                # A spawned process may already lead its own process group.
                pass
            process_group_ready = os.getpgrp() == os.getpid()
        sender.send(("ready", os.getpid(), process_group_ready))
        threading.Thread(
            target=_watch_parent_liveness,
            args=(
                liveness_receiver,
                liveness_stop,
                os.getpid(),
                process_group_ready,
                os.getppid(),
            ),
            daemon=True,
            name="runner-liveness-watchdog",
        ).start()
        stage = "executor"

        def progress(node: str, status: str, detail: dict) -> None:
            sender.send(("progress", node, status, detail))

        if child_executor is None:
            from facade import facade

            executor = (
                facade.execute_prewrite
                if run_kind == "prewrite"
                else facade.execute_upload
            )
        else:
            executor = child_executor
        if run_kind == "prewrite":
            result = executor(
                session_id,
                command or {},
                initial_state,
                progress_callback=progress,
                cancellation_check=cancellation_receiver.poll,
            )
        else:
            result = executor(
                session_id,
                initial_state,
                progress_callback=progress,
                cancellation_check=cancellation_receiver.poll,
            )
        sender.send(("result", result))
    except ExecutionCancelled:
        try:
            sender.send(("cancelled",))
        except (BrokenPipeError, EOFError, OSError):
            pass
    except BaseException as exc:
        try:
            sender.send(("error", type(exc).__name__, stage))
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        # A process boundary must not leak provider/helper subprocesses even
        # when the supervisor disappears before the liveness thread runs.
        for descendant_pid in _descendant_pids(os.getpid()):
            _signal_pid(descendant_pid, signal.SIGKILL)
        liveness_stop.set()
        liveness_receiver.close()
        cancellation_receiver.close()
        sender.close()


def _group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _descendant_pids(root_pid: int) -> set[int]:
    """Snapshot descendants, including children that opened a new session."""
    if os.name != "posix":
        return set()
    try:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,ppid="],
            check=True,
            capture_output=True,
            text=True,
            timeout=0.2,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    children: dict[int, list[int]] = {}
    for line in completed.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            pid, parent_pid = (int(field) for field in fields)
        except ValueError:
            continue
        children.setdefault(parent_pid, []).append(pid)
    descendants: set[int] = set()
    pending = list(children.get(root_pid, ()))
    while pending:
        pid = pending.pop()
        if pid in descendants:
            continue
        descendants.add(pid)
        pending.extend(children.get(pid, ()))
    return descendants


def _signal_pid(pid: int, sig: signal.Signals) -> None:
    try:
        os.kill(pid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def _signal_process(process, *, force: bool) -> None:
    if not process.is_alive():
        return
    try:
        if force:
            process.kill()
        else:
            process.terminate()
    except (OSError, ValueError):
        pass


def _terminate_process_tree(
    process,
    *,
    process_group_ready: bool,
    known_descendant_pids: set[int] | None = None,
) -> None:
    if process.pid is None:
        return
    descendant_pids = set(known_descendant_pids or ())
    if process.is_alive():
        descendant_pids.update(_descendant_pids(process.pid))
    process_group_id = (
        process.pid if process_group_ready and process.is_alive() else None
    )
    if process_group_id is not None:
        try:
            os.killpg(process_group_id, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError:
            _signal_process(process, force=False)
    else:
        _signal_process(process, force=False)
    for descendant_pid in descendant_pids:
        _signal_pid(descendant_pid, signal.SIGTERM)

    deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
    while time.monotonic() < deadline:
        if not process.is_alive():
            break
        process.join(timeout=0.01)

    if process_group_id is not None and _group_exists(process_group_id):
        try:
            os.killpg(process_group_id, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            _signal_process(process, force=True)
    else:
        _signal_process(process, force=True)
    for descendant_pid in descendant_pids:
        _signal_pid(descendant_pid, signal.SIGKILL)
    process.join(timeout=TERMINATION_GRACE_SECONDS)


def _remote_error(
    run_kind: RunKind,
    error_type: str,
    stage: str = "executor",
) -> RemoteExecutionError:
    if run_kind == "prewrite":
        return RemotePrewriteError(error_type, stage)
    return RemoteUploadError(error_type, stage)


def _execute_supervised(
    run_kind: RunKind,
    session_id: str,
    command: dict | None,
    initial_state: dict,
    *,
    progress_callback: Callable[[str, str, dict], None],
    cancellation_check: Callable[[], bool],
    child_executor: Callable[..., dict] | None = None,
) -> dict:
    """Run one durable computation in a spawn child process."""
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    cancellation_receiver, cancellation_sender = context.Pipe(duplex=False)
    liveness_receiver, liveness_sender = context.Pipe(duplex=False)
    process = context.Process(
        target=_child_main,
        args=(
            run_kind,
            session_id,
            command,
            initial_state,
            sender,
            cancellation_receiver,
            liveness_receiver,
            child_executor,
        ),
    )
    try:
        process.start()
    except BaseException:
        receiver.close()
        sender.close()
        cancellation_receiver.close()
        cancellation_sender.close()
        liveness_receiver.close()
        liveness_sender.close()
        process.close()
        raise
    sender.close()
    cancellation_receiver.close()
    liveness_receiver.close()
    process_group_ready = False
    cancellation_started: float | None = None
    cancellation_descendants: set[int] = set()

    try:
        while True:
            if cancellation_check():
                if cancellation_started is None:
                    cancellation_started = time.monotonic()
                    try:
                        cancellation_sender.send(True)
                    except (BrokenPipeError, EOFError, OSError):
                        pass
                    if process.pid is not None:
                        cancellation_descendants = _descendant_pids(process.pid)

            for _ in range(MAX_MESSAGES_PER_POLL):
                if not receiver.poll():
                    break
                try:
                    message = receiver.recv()
                except EOFError:
                    break
                kind = message[0]
                if kind == "ready":
                    process_group_ready = (
                        os.name == "posix"
                        and message[1] == process.pid
                        and message[2]
                    )
                elif kind == "progress":
                    if cancellation_started is None:
                        progress_callback(message[1], message[2], message[3])
                elif kind == "result":
                    if cancellation_started is None:
                        process.join(timeout=TERMINATION_GRACE_SECONDS)
                        return message[1]
                elif kind == "cancelled":
                    process.join(timeout=TERMINATION_GRACE_SECONDS)
                    raise ExecutionCancelled(f"{run_kind} execution cancelled")
                elif kind == "error":
                    process.join(timeout=TERMINATION_GRACE_SECONDS)
                    raise _remote_error(run_kind, message[1], message[2])
                if cancellation_check():
                    break

            if cancellation_started is not None:
                if (
                    time.monotonic() - cancellation_started
                    >= CANCELLATION_GRACE_SECONDS
                ):
                    raise ExecutionCancelled(f"{run_kind} execution cancelled")
            elif process.exitcode is not None:
                raise _remote_error(run_kind, "ChildProcessError")
            time.sleep(SUPERVISOR_POLL_SECONDS)
    finally:
        try:
            liveness_sender.send(False)
        except (BrokenPipeError, EOFError, OSError):
            pass
        liveness_sender.close()
        if cancellation_started is None:
            try:
                cancellation_sender.send(True)
            except (BrokenPipeError, EOFError, OSError):
                pass
        if process.is_alive() or cancellation_descendants:
            _terminate_process_tree(
                process,
                process_group_ready=process_group_ready,
                known_descendant_pids=cancellation_descendants,
            )
        receiver.close()
        cancellation_sender.close()
        try:
            process.close()
        except ValueError:
            pass


def execute_prewrite_supervised(
    session_id: str,
    direction: dict,
    initial_state: dict,
    *,
    progress_callback: Callable[[str, str, dict], None],
    cancellation_check: Callable[[], bool],
    child_executor: Callable[..., dict] | None = None,
) -> dict:
    """Run pre-write in a spawn child and terminate its process tree on cancel."""
    return _execute_supervised(
        "prewrite",
        session_id,
        direction,
        initial_state,
        progress_callback=progress_callback,
        cancellation_check=cancellation_check,
        child_executor=child_executor,
    )


def _attempt_workspace_for_cleanup(initial_state: dict) -> Path | None:
    raw_path = initial_state.get("workspace")
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path).resolve(strict=False)
    try:
        attempts_index = len(path.parts) - 1 - path.parts[::-1].index("attempts")
    except ValueError:
        return None
    # Only a lease attempt leaf (attempts/<run>/<epoch>) may be removed here.
    if len(path.parts) - attempts_index < 3:
        return None
    return path


def execute_upload_supervised(
    session_id: str,
    initial_state: dict,
    *,
    progress_callback: Callable[[str, str, dict], None],
    cancellation_check: Callable[[], bool],
    child_executor: Callable[..., dict] | None = None,
) -> dict:
    """Run upload cleaning in a spawn child and clean cancelled attempt output."""
    try:
        return _execute_supervised(
            "upload_pipeline",
            session_id,
            None,
            initial_state,
            progress_callback=progress_callback,
            cancellation_check=cancellation_check,
            child_executor=child_executor,
        )
    except ExecutionCancelled:
        workspace = _attempt_workspace_for_cleanup(initial_state)
        if workspace is not None:
            shutil.rmtree(workspace, ignore_errors=True)
        raise
