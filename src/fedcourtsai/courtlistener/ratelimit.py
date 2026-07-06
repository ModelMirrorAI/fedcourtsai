"""Client-side rate limiting for the CourtListener REST API.

CourtListener enforces per-token request budgets (see issue #1):

    5 requests / minute
    50 requests / hour
    125 requests / day

The deterministic ``seed`` / ``pull`` scripts can blow through these while
paging docket entries, so :class:`RateLimiter` throttles every request *before*
it is sent. It keeps a sliding-window log of request timestamps and, when a
window is full, sleeps just long enough for the oldest request in that window to
age out — staying under every limit simultaneously rather than only the tightest
one.

The clock and sleep function are injectable so the behaviour is unit-testable
without real waits; in production they default to ``time.monotonic`` /
``time.sleep``.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Final

# CourtListener's published per-token limits (issue #1).
DEFAULT_PER_MINUTE: Final = 5
DEFAULT_PER_HOUR: Final = 50
DEFAULT_PER_DAY: Final = 125


class RateBudgetExceeded(RuntimeError):
    """The wait to fit another request under the limits exceeds ``max_wait``.

    Minute-window pacing sleeps are seconds long; a wait beyond ``max_wait``
    means an hour- or day-scale window is exhausted, so the caller should wrap
    up the run (deferring remaining work to the next window) rather than sleep
    silently — inside a CI job such a sleep looks like a hang and gets the whole
    run killed at the job timeout, losing the work already done.
    """


class _Window:
    """A single ``max_requests`` per ``period`` sliding window."""

    __slots__ = ("_log", "max_requests", "period")

    def __init__(self, max_requests: int, period: float) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if period <= 0:
            raise ValueError("period must be > 0")
        self.max_requests = max_requests
        self.period = period
        self._log: deque[float] = deque()

    def _prune(self, now: float) -> None:
        cutoff = now - self.period
        while self._log and self._log[0] <= cutoff:
            self._log.popleft()

    def wait_seconds(self, now: float) -> float:
        """Seconds to wait before another request fits in this window (0 if free)."""
        self._prune(now)
        if len(self._log) < self.max_requests:
            return 0.0
        # The oldest request must age out of the window before we may proceed.
        return self._log[0] + self.period - now

    def record(self, now: float) -> None:
        self._log.append(now)


class RateLimiter:
    """Blocks until a request fits within every configured window, then records it.

    :param limits: ``(max_requests, period_seconds)`` pairs, e.g. ``(5, 60)``.
    :param max_wait: longest single wait ``acquire`` may sleep; beyond it,
        :class:`RateBudgetExceeded` is raised instead (None = wait forever).
    :param time_fn: monotonic clock source (injected for testing).
    :param sleep_fn: blocking sleep (injected for testing).
    """

    def __init__(
        self,
        limits: list[tuple[int, float]],
        *,
        max_wait: float | None = None,
        time_fn: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if not limits:
            raise ValueError("at least one limit is required")
        self._windows = [_Window(max_requests, period) for max_requests, period in limits]
        self._max_wait = max_wait
        self._time = time_fn
        self._sleep = sleep_fn
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Wait until a request is permitted under all windows, then count it.

        Raises :class:`RateBudgetExceeded` when the required wait exceeds
        ``max_wait`` — the request is not counted, and the windows are left
        as-is so a later call may succeed once they age out.
        """
        with self._lock:
            while True:
                now = self._time()
                wait = max(window.wait_seconds(now) for window in self._windows)
                if wait <= 0:
                    break
                if self._max_wait is not None and wait > self._max_wait:
                    raise RateBudgetExceeded(
                        f"next request must wait {wait:.0f}s, over the {self._max_wait:.0f}s bound"
                    )
                self._sleep(wait)
            now = self._time()
            for window in self._windows:
                window.record(now)


def default_rate_limiter(
    per_minute: int = DEFAULT_PER_MINUTE,
    per_hour: int = DEFAULT_PER_HOUR,
    per_day: int = DEFAULT_PER_DAY,
    *,
    max_wait: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> RateLimiter:
    """Build a :class:`RateLimiter` with CourtListener's published limits."""
    return RateLimiter(
        [(per_minute, 60.0), (per_hour, 3600.0), (per_day, 86400.0)],
        max_wait=max_wait,
        time_fn=time_fn,
        sleep_fn=sleep_fn,
    )
