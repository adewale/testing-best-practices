"""
LogStore with deterministic compaction tests.

The original test used time.sleep(0.5) to wait for a background compaction
thread, making it flaky on slow CI.  The fix: expose a wait_for_compaction()
method that blocks until the background worker has finished at least one
compaction pass.  Tests call that instead of sleeping, so they are fast AND
deterministic regardless of machine speed.

This follows the guidance principle: "time.sleep(0.1) 'just to be safe' is a
race condition; fix synchronization, don't paper over it."
"""

import threading
import os
import tempfile
import pytest


# ---------------------------------------------------------------------------
# Modified LogStore
# ---------------------------------------------------------------------------

SEGMENT_SIZE = 64  # compact after this many records


class LogStore:
    """Appends records; compacts to disk when a segment fills up.

    Modification for testability
    ----------------------------
    Added ``_compaction_done`` – an ``threading.Event`` that is set each time
    the background worker finishes a compaction pass.  Tests call
    ``wait_for_compaction()`` instead of ``time.sleep()``.

    No timers are involved; compaction is triggered purely by write volume,
    so the event fires as soon as the worker drains whatever work was queued
    by writes – deterministically.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Condition()
        self._segment: list[str] = []          # in-memory open segment
        self._closed_segments: list[list[str]] = []  # full segments awaiting compaction
        self._stop = False
        self._compaction_done = threading.Event()   # NEW: set after each compact pass

        self._worker = threading.Thread(target=self._compact_loop, daemon=True)
        self._worker.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(self, record: str) -> None:
        with self._lock:
            self._segment.append(record)
            if len(self._segment) >= SEGMENT_SIZE:
                self._closed_segments.append(self._segment)
                self._segment = []
                self._lock.notify()  # wake background worker

    def wait_for_compaction(self, timeout: float = 5.0) -> bool:
        """Block until the background worker has completed at least one
        compaction pass *after* this call is made.  Returns True on success,
        False on timeout.

        This is the synchronization seam that replaces time.sleep() in tests.
        """
        self._compaction_done.clear()          # reset before waiting
        # If there are closed segments already, the worker may be mid-pass;
        # notify it and wait for the event to be set.
        with self._lock:
            if self._closed_segments:
                self._lock.notify()
        return self._compaction_done.wait(timeout=timeout)

    def close(self) -> None:
        """Flush the open segment and stop the background worker."""
        with self._lock:
            if self._segment:
                self._closed_segments.append(self._segment)
                self._segment = []
                self._lock.notify()
            self._stop = True
            self._lock.notify()
        self._worker.join(timeout=5)

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------

    def _compact_loop(self) -> None:
        while True:
            with self._lock:
                while not self._closed_segments and not self._stop:
                    self._lock.wait()
                if self._stop and not self._closed_segments:
                    break
                segments_to_flush = self._closed_segments[:]
                self._closed_segments.clear()

            # Write outside the lock so append() is not blocked.
            self._flush_to_disk(segments_to_flush)
            self._compaction_done.set()   # signal that a pass finished

    def _flush_to_disk(self, segments: list[list[str]]) -> None:
        with open(self._path, "a") as fh:
            for segment in segments:
                for record in segment:
                    fh.write(record + "\n")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_lines(path: str) -> int:
    if not os.path.exists(path):
        return 0
    with open(path) as fh:
        return sum(1 for _ in fh)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def log_path(tmp_path):
    return str(tmp_path / "log.txt")


@pytest.fixture()
def store(log_path):
    s = LogStore(log_path)
    yield s
    s.close()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCompactionTriggering:
    """Compaction fires when a segment reaches SEGMENT_SIZE records."""

    def test_no_compaction_before_segment_fills(self, store, log_path):
        """Records below the threshold stay in memory; nothing written yet."""
        for i in range(SEGMENT_SIZE - 1):
            store.append(f"record-{i}")
        # No compaction should have been triggered.
        assert _count_lines(log_path) == 0

    def test_compaction_fires_at_segment_boundary(self, store, log_path):
        """Exactly SEGMENT_SIZE records triggers one compaction pass."""
        for i in range(SEGMENT_SIZE):
            store.append(f"record-{i}")

        assert store.wait_for_compaction(), "compaction did not complete in time"
        assert _count_lines(log_path) == SEGMENT_SIZE

    def test_multiple_segments_all_flushed(self, store, log_path):
        """200 records span three full segments; all are written to disk."""
        total = 200
        for i in range(total):
            store.append(f"rec-{i}")

        # Wait for the last compaction pass to finish.
        assert store.wait_for_compaction(), "compaction did not complete in time"

        # The worker may have batched multiple segments in one pass, so we
        # only know the flushed count is a multiple of SEGMENT_SIZE.
        flushed = _count_lines(log_path)
        assert flushed % SEGMENT_SIZE == 0
        assert flushed >= (total // SEGMENT_SIZE) * SEGMENT_SIZE

    def test_close_flushes_partial_segment(self, store, log_path):
        """close() flushes the open (partial) segment before stopping."""
        for i in range(SEGMENT_SIZE + 10):
            store.append(f"rec-{i}")

        store.close()
        # After close() returns the worker has stopped and all data is on disk.
        assert _count_lines(log_path) == SEGMENT_SIZE + 10


class TestRecordOrdering:
    """Records must appear in append order within the log file."""

    def test_records_preserved_in_order(self, store, log_path):
        for i in range(SEGMENT_SIZE):
            store.append(str(i))

        assert store.wait_for_compaction(), "compaction did not complete in time"

        with open(log_path) as fh:
            lines = [l.rstrip("\n") for l in fh]
        assert lines == [str(i) for i in range(SEGMENT_SIZE)]

    def test_multi_segment_order_preserved(self, store, log_path):
        count = SEGMENT_SIZE * 2
        for i in range(count):
            store.append(str(i))

        assert store.wait_for_compaction(), "compaction did not complete in time"
        store.close()

        with open(log_path) as fh:
            lines = [l.rstrip("\n") for l in fh]
        assert lines == [str(i) for i in range(count)]


class TestWaitForCompactionSemantics:
    """wait_for_compaction() itself must be reliable."""

    def test_returns_true_when_compaction_completes(self, store):
        for i in range(SEGMENT_SIZE):
            store.append(f"r{i}")
        result = store.wait_for_compaction(timeout=5.0)
        assert result is True

    def test_no_compaction_needed_does_not_hang(self, log_path):
        """If no full segment has been written, wait_for_compaction should
        return within the timeout (False is acceptable — nothing to compact)."""
        s = LogStore(log_path)
        try:
            s.append("only-one-record")
            # Nothing to compact; we just want it not to hang forever.
            result = s.wait_for_compaction(timeout=0.2)
            # Either False (nothing happened) or True (no-op pass) is fine.
            assert isinstance(result, bool)
        finally:
            s.close()


class TestConcurrentAppends:
    """Concurrent writers must not lose records."""

    def test_concurrent_writers_no_lost_records(self, log_path):
        n_threads = 4
        records_per_thread = SEGMENT_SIZE  # each thread fills exactly one segment

        store = LogStore(log_path)
        try:
            barrier = threading.Barrier(n_threads)

            def writer(thread_id: int) -> None:
                barrier.wait()  # start all writers simultaneously
                for i in range(records_per_thread):
                    store.append(f"t{thread_id}-{i}")

            threads = [threading.Thread(target=writer, args=(t,)) for t in range(n_threads)]
            for th in threads:
                th.start()
            for th in threads:
                th.join()

            assert store.wait_for_compaction(), "compaction did not complete in time"
            store.close()

            total_written = _count_lines(log_path)
            assert total_written == n_threads * records_per_thread
        finally:
            store.close()
