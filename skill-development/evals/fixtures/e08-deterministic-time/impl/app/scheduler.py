class FakeClock:
    def __init__(self, start=0):
        self.now = start

    def advance(self, seconds):
        self.now += seconds


class Scheduler:
    def __init__(self, clock):
        self.clock = clock
        self.pending = []

    def schedule_after(self, delay, callback):
        self.pending.append((self.clock.now + delay, callback))

    def run_pending(self):
        ready = [
            (due, callback) for due, callback in self.pending if due <= self.clock.now
        ]
        self.pending = [
            (due, callback) for due, callback in self.pending if due > self.clock.now
        ]
        for _, callback in ready:
            callback()
