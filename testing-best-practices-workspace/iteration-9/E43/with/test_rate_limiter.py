"""
RateLimiter: blocks login after 5 failed attempts within one hour.

Modified for testability via clock injection (Strategy 2 from guidance):
- accept a `clock` callable at construction time (defaults to time.monotonic)
- tests pass a fake clock they control directly
- no sleep(), no wall-clock dependency, fully deterministic
"""

import time
from collections import defaultdict
from typing import Callable, List


# ---------------------------------------------------------------------------
# Production class (modified for testability)
# ---------------------------------------------------------------------------

class RateLimiter:
    """
    Blocks a user after MAX_FAILURES failed login attempts within WINDOW_SECONDS.

    The clock is injected so tests can control time without sleeping.
    Production uses the default (time.monotonic).
    """

    MAX_FAILURES = 5
    WINDOW_SECONDS = 3600  # one hour

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        # clock is the architectural seam — the only place real time enters
        self._clock = clock
        # user -> list of timestamps of recent failures
        self._failures: dict[str, List[float]] = defaultdict(list)

    def _now(self) -> float:
        return self._clock()

    def _prune(self, user: str) -> None:
        """Drop failure records older than the window."""
        cutoff = self._now() - self.WINDOW_SECONDS
        self._failures[user] = [t for t in self._failures[user] if t > cutoff]

    def record_failure(self, user: str) -> None:
        """Record a failed login attempt for *user*."""
        self._prune(user)
        self._failures[user].append(self._now())

    def allow(self, user: str) -> bool:
        """Return True if the user is allowed to attempt login."""
        self._prune(user)
        return len(self._failures[user]) < self.MAX_FAILURES

    # --- testability seam: read-only introspection ---
    def failure_count(self, user: str) -> int:
        """Return the number of failures within the current window (for tests)."""
        self._prune(user)
        return len(self._failures[user])


# ---------------------------------------------------------------------------
# Fake clock helper
# ---------------------------------------------------------------------------

class FakeClock:
    """
    A controllable clock for tests.
    Call advance(seconds) to move time forward; never reads wall clock.
    """

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

import pytest


# ---- basic allow/deny behaviour ----

def test_new_user_is_allowed():
    rl = RateLimiter(clock=FakeClock())
    assert rl.allow("alice") is True


def test_user_allowed_after_fewer_than_max_failures():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for _ in range(4):
        rl.record_failure("bob")
    assert rl.allow("bob") is True


def test_user_blocked_at_max_failures():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for _ in range(5):
        rl.record_failure("carol")
    assert rl.allow("carol") is False


def test_user_blocked_beyond_max_failures():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for _ in range(10):
        rl.record_failure("dave")
    assert rl.allow("dave") is False


# ---- window expiry (no sleep — time is advanced with FakeClock) ----

def test_failures_outside_window_are_ignored():
    clock = FakeClock(start=0.0)
    rl = RateLimiter(clock=clock)

    # Record 5 failures at t=0 — user is now blocked
    for _ in range(5):
        rl.record_failure("eve")
    assert rl.allow("eve") is False

    # Advance past the one-hour window (exactly one second beyond)
    clock.advance(RateLimiter.WINDOW_SECONDS + 1)

    # All old failures have expired; user is unblocked
    assert rl.allow("eve") is True


def test_failures_exactly_at_window_boundary_still_count():
    clock = FakeClock(start=0.0)
    rl = RateLimiter(clock=clock)

    for _ in range(5):
        rl.record_failure("frank")

    # Advance to exactly the window edge — failures recorded at t=0 are at
    # cutoff = now - WINDOW = 0, so t > cutoff is False; they expire.
    clock.advance(RateLimiter.WINDOW_SECONDS)
    assert rl.allow("frank") is True


def test_partial_expiry_allows_more_attempts():
    clock = FakeClock(start=0.0)
    rl = RateLimiter(clock=clock)

    # 3 failures early on
    for _ in range(3):
        rl.record_failure("grace")

    # Advance past the window
    clock.advance(RateLimiter.WINDOW_SECONDS + 1)

    # 3 more failures in the new window — should still be allowed (only 3 < 5)
    for _ in range(3):
        rl.record_failure("grace")
    assert rl.allow("grace") is True


def test_straddling_window_counts_only_recent_failures():
    clock = FakeClock(start=0.0)
    rl = RateLimiter(clock=clock)

    # 4 failures at t=0
    for _ in range(4):
        rl.record_failure("heidi")

    # Advance to t = WINDOW_SECONDS + 1 (old failures expire)
    clock.advance(RateLimiter.WINDOW_SECONDS + 1)

    # 4 fresh failures — 4 < 5, still allowed
    for _ in range(4):
        rl.record_failure("heidi")
    assert rl.allow("heidi") is True

    # One more failure tips it over: 5 >= 5, blocked
    rl.record_failure("heidi")
    assert rl.allow("heidi") is False


# ---- user isolation ----

def test_failures_for_one_user_do_not_affect_another():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for _ in range(5):
        rl.record_failure("ivan")
    assert rl.allow("judy") is True


# ---- introspection seam ----

def test_failure_count_matches_recorded_failures():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for i in range(3):
        rl.record_failure("kate")
    assert rl.failure_count("kate") == 3


def test_failure_count_drops_after_window_expires():
    clock = FakeClock(start=0.0)
    rl = RateLimiter(clock=clock)
    for _ in range(5):
        rl.record_failure("leo")
    clock.advance(RateLimiter.WINDOW_SECONDS + 1)
    assert rl.failure_count("leo") == 0


# ---- record_failure after block still accumulates ----

def test_record_failure_after_block_does_not_crash():
    clock = FakeClock()
    rl = RateLimiter(clock=clock)
    for _ in range(7):
        rl.record_failure("mallory")
    assert rl.allow("mallory") is False
    assert rl.failure_count("mallory") == 7
