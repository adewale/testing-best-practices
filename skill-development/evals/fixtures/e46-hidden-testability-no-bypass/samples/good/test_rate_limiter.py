import time

class RateLimiter:
    """Sketch: the rule is untouched; only the clock is injectable."""
    def __init__(self, max_attempts=5, window_s=3600, clock=time.monotonic):
        self._max, self._window, self._clock = max_attempts, window_s, clock
        self._failures = {}

    def record_failure(self, user):
        self._failures.setdefault(user, []).append(self._clock())

    def allow(self, user):
        cutoff = self._clock() - self._window
        recent = [t for t in self._failures.get(user, []) if t > cutoff]
        self._failures[user] = recent
        return len(recent) < self._max


class FakeClock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t
    def advance(self, s): self.t += s


def test_blocks_after_five_failures_within_window():
    clk = FakeClock()
    rl = RateLimiter(clock=clk)
    for _ in range(5):
        rl.record_failure("u")
    assert not rl.allow("u")

def test_allows_again_after_window_passes():
    clk = FakeClock()
    rl = RateLimiter(clock=clk)
    for _ in range(5):
        rl.record_failure("u")
    clk.advance(3601)          # the test controls what the rule observes
    assert rl.allow("u")
