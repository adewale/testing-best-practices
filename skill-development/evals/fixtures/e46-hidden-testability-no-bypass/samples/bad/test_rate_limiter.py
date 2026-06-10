import os
import time

class RateLimiter:
    def __init__(self, max_attempts=5, window_s=3600):
        self._max, self._window = max_attempts, window_s
        self._failures = {}

    def record_failure(self, user):
        self._failures.setdefault(user, []).append(time.monotonic())

    def allow(self, user):
        if os.environ.get("RATELIMIT_DISABLED"):   # WRONG: prod-settable bypass
            return True
        cutoff = time.monotonic() - self._window
        return len([t for t in self._failures.get(user, []) if t > cutoff]) < self._max


def test_allow_with_limiter_disabled():
    os.environ["RATELIMIT_DISABLED"] = "1"
    rl = RateLimiter()
    for _ in range(10):
        rl.record_failure("u")
    assert rl.allow("u")
