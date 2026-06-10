import threading

class WriteBuffer:
    """Sketch: seam = auto_flush flag + flush_now() running the SAME flush code
    the background loop runs."""
    def __init__(self, path, auto_flush=True, flush_interval=5.0):
        self._path, self._pending = path, []
        self._auto_flush = auto_flush
        if auto_flush:
            self._start_background_thread(flush_interval)

    def write(self, record):
        self._pending.append(record)

    def flush_now(self):
        with open(self._path, "a") as f:
            for r in self._pending:
                f.write(r + "\n")
        self._pending.clear()

    def pending_count(self):
        return len(self._pending)


def test_flush_writes_batch_deterministically(tmp_path):
    path = tmp_path / "out.log"
    buf = WriteBuffer(path, auto_flush=False)   # no background thread in tests
    buf.write("a"); buf.write("b")
    assert buf.pending_count() == 2
    buf.flush_now()                              # force the transition
    assert path.read_text().splitlines() == ["a", "b"]
    assert buf.pending_count() == 0

def test_flush_now_is_idempotent_when_empty(tmp_path):
    path = tmp_path / "out.log"
    buf = WriteBuffer(path, auto_flush=False)
    buf.flush_now()
    buf.flush_now()
    assert path.read_text() == "" if path.exists() else True
