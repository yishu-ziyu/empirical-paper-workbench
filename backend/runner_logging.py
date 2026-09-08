"""Logging lifecycle for the runner process family (issue #30).

The runner's stdout/stderr may be bound to a pipe whose read end died with
its parent shell (documented production incident, 2026-09-06). In that state
two independent escape paths turned healthy runs into FAILED:

1. Logging ``emit`` failures: any ``StreamHandler`` on a dead console raises
   ``BrokenPipeError``. ``Handler.handleError`` absorbs it on CPython 3.12,
   but only while ``logging.raiseExceptions`` semantics hold, and every
   attempt still re-raises internally against the dead stderr.
2. Unguarded std-stream flushes: ``multiprocessing`` spawn calls
   ``util._flush_std_streams()`` (``sys.stdout.flush()``) inside
   ``process.start()`` with only ``(AttributeError, ValueError)`` guarded, so
   the ``BrokenPipeError`` propagated straight into
   ``prewrite_supervisor._execute_supervised`` and was misreported by
   ``runner._stable_failure`` as ``BrokenPipeError: upload_pipeline
   execution failed`` even though the business work had committed.

This module owns the whole output-channel lifecycle for runner processes:

- ``logging.raiseExceptions = False``: process-level backstop so no emit
  failure can ever cross the logging stack into business code.
- A rotating file handler as the durable channel (default
  ``config._state_path("ECONPAPER_RUNNER_LOG_FILE", "log", "runner.log")``).
- A stderr console handler that disables itself after its first channel
  failure and leaves exactly one degradation trace on the surviving channel.
- ``sys.stdout``/``sys.stderr`` replaced by tolerant wrappers that absorb
  write/flush failures from *non-logging* writers (``print``, multiprocessing
  spawn flush, third-party progress bars). Business sockets/pipes are never
  touched, so genuine business ``BrokenPipeError`` still surfaces.

Idempotency: configuration is marked on the root logger object, so repeated
calls and module re-imports never stack handlers (a respawned runner would
otherwise accumulate handlers and duplicate every record).

Spawn children (``prewrite_supervisor._child_main``) call
:func:`configure_runner_logging` with ``child=True``: spawn does not inherit
the parent's logging configuration, so each child re-applies the process-level
backstop and stream hardening, but deliberately installs no file handler —
several supervised children rotating the same file concurrently would race
inside :class:`~logging.handlers.RotatingFileHandler`. Children keep console
output only; their durable traces live in the run event store.
"""

from __future__ import annotations

import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

RUNNER_LOG_FILE_ENV = "ECONPAPER_RUNNER_LOG_FILE"
DEFAULT_LOG_PARTS = ("log", "runner.log")
MAX_LOG_BYTES = 5 * 1024 * 1024
LOG_BACKUPS = 3

_CONFIGURED_FLAG = "_econpaper_runner_logging_configured"

_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

# Exactly one degradation trace per process: the first output-channel failure
# explains the failed channel and the surviving channels; every later failure
# is absorbed silently (its channel disables itself and records are dropped).
_DEGRADATION_TRACED = threading.Event()


def _trace_degradation_once(failed_channel: str, exc: BaseException) -> None:
    if _DEGRADATION_TRACED.is_set():
        return
    _DEGRADATION_TRACED.set()
    try:
        logging.getLogger(__name__).warning(
            "runner log channel %s is unavailable (%s: %s); "
            "remaining channels: %s",
            failed_channel,
            type(exc).__name__,
            exc,
            _remaining_channel_description(exclude_channel=failed_channel),
        )
    except Exception:
        # Degradation tracing is observability; it must never re-raise.
        pass


def default_log_file() -> Path:
    """Default runner log file, overridable via ``ECONPAPER_RUNNER_LOG_FILE``."""
    # Imported lazily: the spawn-child path must not pay for the app config
    # import (child-startup latency), and it never uses this function.
    from config import _state_path

    return _state_path(RUNNER_LOG_FILE_ENV, *DEFAULT_LOG_PARTS)


class SelfDisablingStreamHandler(logging.StreamHandler):
    """Console handler that retires itself when its channel fails.

    The first failed write/flush disables the handler and leaves one
    degradation trace (failed channel + surviving channels) for the remaining
    handlers — normally the rotating file handler. With the channel disabled
    the handler becomes a no-op, so a dead pipe can never trigger a
    "--- Logging error ---" storm.
    """

    # Marker attribute instead of isinstance(): module re-imports (the
    # "import re-entry" form this module must survive) recreate classes and
    # would silently break identity-based detection.
    _econpaper_channel_guard = True

    def __init__(self, stream: Any, channel_name: str) -> None:
        super().__init__(stream)
        self.channel_name = channel_name
        self._econpaper_channel_disabled = False

    def emit(self, record: logging.LogRecord) -> None:
        if self._econpaper_channel_disabled:
            return
        try:
            message = self.format(record)
            stream = self.stream
            stream.write(message + self.terminator)
            self.flush()
        except (OSError, ValueError) as exc:
            # ValueError mirrors logging.StreamHandler.emit's closed-stream
            # handling; OSError covers BrokenPipeError and friends.
            self.disable_channel(exc)
        except RecursionError:  # pragma: no cover - mirrors stdlib emit
            raise
        except Exception:
            self.handleError(record)

    def disable_channel(self, exc: BaseException) -> None:
        if self._econpaper_channel_disabled:
            return
        self._econpaper_channel_disabled = True
        _trace_degradation_once(self.channel_name, exc)


def _remaining_channel_description(exclude_channel: str | None = None) -> str:
    parts: list[str] = []
    for handler in logging.getLogger().handlers:
        if getattr(handler, "_econpaper_channel_disabled", False):
            continue
        if isinstance(handler, RotatingFileHandler):
            parts.append(f"file({getattr(handler, 'baseFilename', '?')})")
        elif getattr(handler, "_econpaper_channel_guard", False):
            if handler.channel_name != exclude_channel:
                parts.append(handler.channel_name)
        else:
            parts.append(type(handler).__name__)
    if not parts:
        return "none (log records will be dropped)"
    return ", ".join(parts)


class TolerantStream:
    """``sys.stdout``/``sys.stderr`` stand-in that absorbs channel failures.

    Only write/flush failures on the console channel are absorbed (dropped
    text, one trace on surviving log channels); every other attribute is
    delegated untouched. This is what keeps ``multiprocessing`` spawn's
    unguarded ``_flush_std_streams()`` — and any ``print`` in imported
    modules — from turning a dead console pipe into a business exception.
    Business ``BrokenPipeError`` from sockets, subprocess pipes, or provider
    calls does not pass through this class and still propagates unchanged.
    """

    # Marker attribute (see SelfDisablingStreamHandler) so detection survives
    # module re-imports that would invalidate isinstance identity checks.
    _econpaper_tolerant = True

    def __init__(self, stream: Any, channel_name: str) -> None:
        self._stream = stream
        self._channel_name = channel_name
        self._drop_traced = False

    def write(self, data: Any, *args: Any, **kwargs: Any) -> int:
        try:
            return self._stream.write(data, *args, **kwargs)
        except (OSError, ValueError) as exc:
            self._trace_drop(exc)
            return len(data) if isinstance(data, str) else 0

    def flush(self, *args: Any, **kwargs: Any) -> None:
        try:
            return self._stream.flush(*args, **kwargs)
        except (OSError, ValueError) as exc:
            self._trace_drop(exc)

    def _trace_drop(self, exc: BaseException) -> None:
        if self._drop_traced:
            return
        self._drop_traced = True
        _trace_degradation_once(self._channel_name, exc)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)


def _underlying_stream(stream: Any) -> Any:
    if getattr(stream, "_econpaper_tolerant", False):
        return stream._stream
    return stream


def harden_standard_streams() -> None:
    """Wrap ``sys.stdout``/``sys.stderr`` so channel failures cannot escape.

    Idempotent: streams already wrapped (or absent, as under ``pythonw``) are
    left alone.
    """
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None or getattr(stream, "_econpaper_tolerant", False):
            continue
        setattr(sys, name, TolerantStream(stream, name))


def _build_file_handler(path: Path) -> RotatingFileHandler | None:
    """Best-effort file channel; None degrades the runner to console-only."""
    from config import ensure_private_directory

    try:
        ensure_private_directory(path.parent)
        handler = RotatingFileHandler(
            path,
            maxBytes=MAX_LOG_BYTES,
            backupCount=LOG_BACKUPS,
            encoding="utf-8",
            delay=False,
        )
    except OSError:
        return None
    handler.setFormatter(_FORMATTER)
    return handler


def configure_runner_logging(
    *,
    child: bool = False,
    level: int = logging.INFO,
    log_file: Path | None = None,
) -> None:
    """Configure the output-channel lifecycle for one runner process.

    Idempotent per process (marked on the root logger), safe to call again on
    re-entry or module re-import. Spawn children pass ``child=True`` to get
    the backstop and stream hardening without a file handler (see module
    docstring for the rotation-race tradeoff).
    """
    root = logging.getLogger()
    if getattr(root, _CONFIGURED_FLAG, False):
        return
    setattr(root, _CONFIGURED_FLAG, True)

    # Process-level backstop: no emit failure may cross the logging stack.
    logging.raiseExceptions = False
    harden_standard_streams()
    if child:
        return

    file_path = log_file or default_log_file()
    file_handler = _build_file_handler(file_path)
    console_handler = SelfDisablingStreamHandler(
        _underlying_stream(sys.stderr), "stderr"
    )
    root.setLevel(level)
    if file_handler is not None:
        root.addHandler(file_handler)
    root.addHandler(console_handler)
    logging.getLogger(__name__).info(
        "runner logging lifecycle configured: file=%s console=stderr",
        str(file_path) if file_handler is not None else "unavailable (degraded to console-only)",
    )
