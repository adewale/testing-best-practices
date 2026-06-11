"""
WriteBuffer: batches write() calls in memory; background thread flushes to
file every 5 seconds.

Testability seam added (per guidance): `auto_flush` constructor parameter.
When False, no background thread is started and callers invoke flush_now()
directly — the same code path the background loop uses. A `pending_count()`
introspection method lets tests assert buffer state without relying on timing.
"""

import os
import threading
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Production class (sketch)
# ---------------------------------------------------------------------------

class WriteBuffer:
    """Batch-writes records to *path*, flushing every *interval* seconds.

    Parameters
    ----------
    path:       Destination file.
    interval:   Flush interval in seconds (default 5).
    auto_flush: If True (default) a background thread flushes automatically.
                Pass False in tests to disable the thread and call flush_now()
                manually. Production code never touches this parameter.
    """

    def __init__(self, path, interval: float = 5.0, *, auto_flush: bool = True):
        self._path = Path(path)
        self._interval = interval
        self._buffer: list[str] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        if auto_flush:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        else:
            self._thread = None  # no background work in tests

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write(self, record: str) -> None:
        """Enqueue a record for the next flush."""
        with self._lock:
            self._buffer.append(record)

    def flush_now(self) -> None:
        """Flush all pending records to disk immediately (synchronous).

        This is the *same* code the background loop calls.  Tests call it
        directly instead of sleeping; production shutdown code may also call
        it to drain the buffer cleanly.
        """
        with self._lock:
            batch = self._buffer[:]
            self._buffer.clear()

        if batch:
            with open(self._path, "a") as fh:
                for record in batch:
                    fh.write(record + "\n")

    def pending_count(self) -> int:
        """Return the number of records waiting in memory (not yet flushed).

        Read-only introspection seam — lets tests assert buffer state without
        guessing from timing or file contents.
        """
        with self._lock:
            return len(self._buffer)

    def close(self) -> None:
        """Stop the background thread and flush any remaining records."""
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
        self.flush_now()

    # ------------------------------------------------------------------
    # Background loop (production only)
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            self.flush_now()
        # Final flush after stop signal
        self.flush_now()


# ---------------------------------------------------------------------------
# Helpers used by tests
# ---------------------------------------------------------------------------

def _read_records(path) -> list[str]:
    """Return all lines written to *path*, stripped of newlines."""
    p = Path(path)
    if not p.exists():
        return []
    return p.read_text().splitlines()


# ---------------------------------------------------------------------------
# Tests — deterministic, no sleep()
# ---------------------------------------------------------------------------

import pytest
import tempfile


@pytest.fixture()
def tmp_path_file(tmp_path):
    """Return a Path inside pytest's tmp_path that does not yet exist."""
    return tmp_path / "output.txt"


# --- flush_now() correctness -----------------------------------------------

def test_flush_writes_single_record(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("hello")
    buf.flush_now()
    assert _read_records(tmp_path_file) == ["hello"]


def test_flush_writes_multiple_records_in_order(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("first")
    buf.write("second")
    buf.write("third")
    buf.flush_now()
    assert _read_records(tmp_path_file) == ["first", "second", "third"]


def test_flush_appends_across_multiple_flushes(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("a")
    buf.flush_now()
    buf.write("b")
    buf.flush_now()
    assert _read_records(tmp_path_file) == ["a", "b"]


def test_flush_with_empty_buffer_is_a_noop(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.flush_now()  # must not raise or create the file with garbage
    assert _read_records(tmp_path_file) == []


# --- pending_count() introspection -----------------------------------------

def test_pending_count_zero_on_creation(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    assert buf.pending_count() == 0


def test_pending_count_increases_with_writes(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("x")
    assert buf.pending_count() == 1
    buf.write("y")
    assert buf.pending_count() == 2


def test_pending_count_resets_after_flush(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("x")
    buf.write("y")
    buf.flush_now()
    assert buf.pending_count() == 0


def test_pending_count_tracks_partial_flush(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("a")
    buf.flush_now()
    buf.write("b")
    buf.write("c")
    # After one flush followed by two more writes, two records are pending.
    assert buf.pending_count() == 2


# --- batching behaviour ----------------------------------------------------

def test_records_written_before_flush_appear_atomically(tmp_path_file):
    """All records enqueued before flush_now() must appear together."""
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    for i in range(100):
        buf.write(str(i))
    buf.flush_now()
    assert _read_records(tmp_path_file) == [str(i) for i in range(100)]


def test_unflushed_records_do_not_appear_in_file(tmp_path_file):
    """Records not yet flushed must not be visible on disk."""
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("secret")
    # No flush — file must be absent or empty.
    assert _read_records(tmp_path_file) == []


# --- close() drains buffer -------------------------------------------------

def test_close_flushes_remaining_records(tmp_path_file):
    """close() must write any records buffered since the last flush."""
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    buf.write("final")
    buf.close()
    assert _read_records(tmp_path_file) == ["final"]


# --- file creation ---------------------------------------------------------

def test_file_is_created_on_first_flush(tmp_path_file):
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    assert not tmp_path_file.exists()
    buf.write("record")
    buf.flush_now()
    assert tmp_path_file.exists()


# --- concurrent writes do not lose records ---------------------------------

def test_concurrent_writes_all_flushed(tmp_path_file):
    """Thread-safety: records from multiple threads must all be preserved."""
    buf = WriteBuffer(tmp_path_file, auto_flush=False)
    n_threads = 10
    records_per_thread = 50

    def writer(thread_id):
        for i in range(records_per_thread):
            buf.write(f"t{thread_id}-{i}")

    threads = [threading.Thread(target=writer, args=(tid,)) for tid in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    buf.flush_now()
    written = _read_records(tmp_path_file)
    assert len(written) == n_threads * records_per_thread
    # Every expected record must appear exactly once.
    expected = {f"t{tid}-{i}" for tid in range(n_threads) for i in range(records_per_thread)}
    assert set(written) == expected
