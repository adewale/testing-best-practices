import threading

class LogStore:
    """Sketch: seam = start_worker flag + compact_now() running the SAME
    compaction code the background worker runs."""
    def __init__(self, path, segment_size=64, start_worker=True):
        self._path, self._segment_size = path, segment_size
        self._open_segment, self._closed_segments = [], []
        self._lock = threading.Lock()
        if start_worker:
            self._start_worker()

    def append(self, record):
        with self._lock:
            self._open_segment.append(record)
            if len(self._open_segment) >= self._segment_size:
                self._closed_segments.append(self._open_segment)
                self._open_segment = []

    def compact_now(self):
        """One compaction cycle, synchronously — same code the worker runs."""
        with self._lock:
            segments, self._closed_segments = self._closed_segments, []
        with open(self._path, "a") as f:
            for seg in segments:
                for r in seg:
                    f.write(r + "\n")

    def pending_segments(self):
        with self._lock:
            return len(self._closed_segments)


def test_compaction_writes_closed_segments(tmp_path):
    path = tmp_path / "log"
    store = LogStore(path, segment_size=4, start_worker=False)  # no thread
    for i in range(10):
        store.append(f"r{i}")
    assert store.pending_segments() == 2          # 2 closed, 2 records open
    store.compact_now()                            # force the transition
    assert path.read_text().splitlines() == [f"r{i}" for i in range(8)]
    assert store.pending_segments() == 0

def test_compact_now_with_nothing_pending_is_noop(tmp_path):
    path = tmp_path / "log"
    store = LogStore(path, segment_size=4, start_worker=False)
    store.append("only-one")
    store.compact_now()
    assert store.pending_segments() == 0
    assert not path.exists() or path.read_text() == ""
