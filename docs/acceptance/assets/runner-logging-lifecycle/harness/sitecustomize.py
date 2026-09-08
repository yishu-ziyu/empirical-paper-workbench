"""Evidence-only instrumentation for the runner broken-pipe reproduction.

Loaded automatically (``sitecustomize``) into every Python process whose
PYTHONPATH includes this directory -- the runner main process and every
multiprocessing spawn child. It only RECORDS observations; it never swallows,
translates, or replaces exceptions, so the reproduction stays faithful:

- ``logging.Handler.handleError`` is wrapped to snapshot ``sys.exc_info()``
  (the emit failure) plus the surrounding stack before delegating to the
  original handler. This documents where a logging emit failed and from which
  business call stack.
- ``sys.stdout`` / ``sys.stderr`` are replaced by proxies whose ``write`` and
  ``flush`` record failures before re-raising them unchanged. This documents
  direct (non-logging) writes escaping into business code.
- ``sys.excepthook`` / ``threading.excepthook`` / ``sys.unraisablehook`` record
  anything that dies outside the normal try/except boundaries.

Activated only when ``RUNNER_LOG_EVIDENCE_FILE`` is set by the harness driver.
Everything is best-effort: any error inside this module is silently ignored so
that evidence collection can never perturb the reproduction.
"""

from __future__ import annotations

import os
import sys
import threading
import traceback

_EVIDENCE_PATH = os.environ.get("RUNNER_LOG_EVIDENCE_FILE", "")
_LOCK = threading.Lock()


def _record(text: str) -> None:
    if not _EVIDENCE_PATH:
        return
    try:
        with _LOCK:
            with open(_EVIDENCE_PATH, "a", encoding="utf-8") as fh:
                fh.write(text)
    except Exception:
        pass


def _snapshot(prefix: str) -> str:
    parts = [
        f"=== {prefix} === pid={os.getpid()} thread={threading.current_thread().name}",
        traceback.format_exc(),
        "".join(traceback.format_stack()),
    ]
    return "\n".join(parts)


def _install() -> None:
    if not _EVIDENCE_PATH:
        return

    # 1. logging emit failures (handleError entry point).
    try:
        import logging

        original_handle_error = logging.Handler.handleError

        def handle_error_with_evidence(self, record):  # noqa: ANN001
            _record(_snapshot("logging.handleError called (emit failure)"))
            return original_handle_error(self, record)

        logging.Handler.handleError = handle_error_with_evidence  # type: ignore[method-assign]
    except Exception:
        pass

    # 2. Direct stdout/stderr writes that escape (record, then re-raise).
    class _RecordingStream:
        def __init__(self, stream, label: str) -> None:
            self._stream = stream
            self._label = label

        def write(self, *args, **kwargs):
            try:
                return self._stream.write(*args, **kwargs)
            except BaseException:
                _record(
                    _snapshot(f"direct {self._label}.write FAILED (re-raising)")
                )
                raise

        def flush(self, *args, **kwargs):
            try:
                return self._stream.flush(*args, **kwargs)
            except BaseException:
                _record(
                    _snapshot(f"direct {self._label}.flush FAILED (re-raising)")
                )
                raise

        def __getattr__(self, name):
            return getattr(self._stream, name)

        @property
        def closed(self):  # pragma: no cover - delegation via __getattr__
            return self._stream.closed

    try:
        for name in ("stdout", "stderr"):
            stream = getattr(sys, name)
            if isinstance(stream, _RecordingStream):
                continue
            setattr(
                sys,
                name,
                _RecordingStream(stream, name),
            )
    except Exception:
        pass

    # 3. Outside-any-handler deaths.
    try:
        original_excepthook = sys.excepthook

        def _excepthook(exc_type, exc_value, exc_tb):
            _record(_snapshot("sys.excepthook (uncaught main-thread exception)"))
            original_excepthook(exc_type, exc_value, exc_tb)

        sys.excepthook = _excepthook

        original_threading_hook = getattr(threading, "excepthook", None)

        def _threading_hook(args):  # noqa: ANN001
            _record(_snapshot("threading.excepthook (uncaught thread exception)"))
            if original_threading_hook is not None:
                original_threading_hook(args)

        threading.excepthook = _threading_hook

        original_unraisable = getattr(sys, "unraisablehook", None)

        def _unraisable_hook(unraisable):  # noqa: ANN001
            _record(_snapshot("sys.unraisablehook"))
            if original_unraisable is not None:
                original_unraisable(unraisable)

        sys.unraisablehook = _unraisable_hook
    except Exception:
        pass


try:
    _install()
except Exception:
    pass
