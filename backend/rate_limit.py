"""In-process rate limiting for auth endpoints (F10-hardening).

Two independent guards:

- **Per-account lockout** (always active): ``LOCKOUT_FAILURES`` consecutive
  failed logins for one email lock that email for ``LOCKOUT_SECONDS``.
  Correct passwords do not reset the counter early — the lock must expire.
- **Per-IP sliding window** (production only, ``settings.DEBUG`` false):
  at most ``IP_WINDOW_LIMIT`` auth attempts per IP per ``IP_WINDOW_SECONDS``.
  In DEBUG the IP guard is a no-op so local dev / the pytest suite (one
  shared test-client "IP") is never throttled.

State is in-process memory by design: correct for the current single-process
deployment. For multi-instance production, swap ``_store`` for Redis
(``INCR`` + ``EXPIRE``) behind the same class interface — call sites do not
change.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

from config import settings

LOCKOUT_FAILURES = 5
LOCKOUT_SECONDS = 600  # 10 minutes
IP_WINDOW_SECONDS = 60.0
IP_WINDOW_LIMIT = 30


class _RateLimitStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._failures: dict[str, list[float]] = defaultdict(list)
        self._locked_until: dict[str, float] = {}
        self._ip_window: dict[str, deque[float]] = defaultdict(deque)

    # -- per-account ------------------------------------------------------

    def assert_not_locked(self, email: str) -> None:
        """Raise 423 when this email is inside a lockout window."""
        until = self._locked_until.get(email.strip().lower())
        if until and until > time.monotonic():
            raise HTTPException(
                status_code=423,
                detail="Too many failed attempts. Try again later.",
            )

    def record_failure(self, email: str) -> None:
        key = email.strip().lower()
        now = time.monotonic()
        with self._lock:
            recent = [t for t in self._failures[key] if now - t < LOCKOUT_SECONDS]
            recent.append(now)
            self._failures[key] = recent
            if len(recent) >= LOCKOUT_FAILURES:
                self._locked_until[key] = now + LOCKOUT_SECONDS
                self._failures.pop(key, None)

    def record_success(self, email: str) -> None:
        self._failures.pop(email.strip().lower(), None)

    # -- per-IP -----------------------------------------------------------

    def assert_ip_allowed(self, ip: str) -> None:
        """Raise 429 when the IP exceeds the window. DEBUG: never raises."""
        if settings.DEBUG:
            return
        now = time.monotonic()
        with self._lock:
            window = self._ip_window[ip]
            while window and now - window[0] > IP_WINDOW_SECONDS:
                window.popleft()
            if len(window) >= IP_WINDOW_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Slow down.",
                )
            window.append(now)


# Module-level singleton: one process, one store. Redis swap replaces this
# object behind the same two-method surface.
store = _RateLimitStore()
