"""Cooperative cancellation shared by prewrite nodes and provider calls."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar


class ExecutionCancelled(RuntimeError):
    """Raised when a durable run loses authority while work is executing."""


_cancellation_check: ContextVar[Callable[[], bool] | None] = ContextVar(
    "econpaper_cancellation_check",
    default=None,
)


@contextmanager
def cancellation_scope(check: Callable[[], bool] | None) -> Iterator[None]:
    token = _cancellation_check.set(check)
    try:
        yield
    finally:
        _cancellation_check.reset(token)


def cancellation_enabled() -> bool:
    return _cancellation_check.get() is not None


def raise_if_cancelled() -> None:
    check = _cancellation_check.get()
    if check is not None and check():
        raise ExecutionCancelled("run execution cancelled")
