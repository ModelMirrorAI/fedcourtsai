from fedcourtsai.courtlistener.ratelimit import (
    DEFAULT_PER_DAY,
    DEFAULT_PER_HOUR,
    DEFAULT_PER_MINUTE,
    RateLimiter,
    default_rate_limiter,
)


class FakeClock:
    """Deterministic monotonic clock whose ``sleep`` advances time, no real wait."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def _limiter(clock: FakeClock, limits: list[tuple[int, float]]) -> RateLimiter:
    return RateLimiter(limits, time_fn=clock.time, sleep_fn=clock.sleep)


def test_under_limit_never_sleeps() -> None:
    clock = FakeClock()
    limiter = _limiter(clock, [(5, 60.0)])
    for _ in range(5):
        limiter.acquire()
    assert clock.sleeps == []
    assert clock.now == 0.0


def test_blocks_until_oldest_request_ages_out() -> None:
    clock = FakeClock()
    limiter = _limiter(clock, [(2, 60.0)])
    limiter.acquire()  # t=0
    clock.now = 10.0
    limiter.acquire()  # t=10, window now full (2 in last 60s)
    limiter.acquire()  # must wait for the t=0 request to age out: 60 - 10 = 50s
    assert clock.sleeps == [50.0]
    assert clock.now == 60.0


def test_window_slides_so_budget_recovers() -> None:
    clock = FakeClock()
    limiter = _limiter(clock, [(3, 60.0)])
    for _ in range(3):
        limiter.acquire()  # all at t=0, window full
    clock.now = 61.0  # everything aged out
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()
    assert clock.sleeps == []  # no throttling needed once the window cleared


def test_most_restrictive_window_wins() -> None:
    clock = FakeClock()
    # Per-minute (2/60s) is tighter than per-hour (10/3600s) at this rate.
    limiter = _limiter(clock, [(2, 60.0), (10, 3600.0)])
    limiter.acquire()
    limiter.acquire()
    limiter.acquire()  # blocked by the minute window, not the hour window
    assert clock.sleeps == [60.0]


def test_default_limiter_uses_published_limits() -> None:
    clock = FakeClock()
    limiter = default_rate_limiter(time_fn=clock.time, sleep_fn=clock.sleep)
    # Issue #1: 5/min. The 6th request within the minute must wait.
    for _ in range(DEFAULT_PER_MINUTE):
        limiter.acquire()
    assert clock.sleeps == []
    limiter.acquire()
    assert clock.sleeps == [60.0]
    assert DEFAULT_PER_HOUR == 50
    assert DEFAULT_PER_DAY == 125
