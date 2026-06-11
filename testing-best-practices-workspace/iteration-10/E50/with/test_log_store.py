"""
LogStore sketch + deterministic pytest tests.

Design changes from the original (flaky) implementation
--------------------------------------------------------
The original test appended 200 records, called time.sleep(0.5), then read
the file.  That is flaky because it relies on the background thread finishing
within the sleep window — a race condition, not a deterministic wait.

Fix strategy: Seam 1 (forced transitions) from the testability guide.
  - Add `auto_compact=True` constructor parameter.  Tests pass False to
    suppress the background thread entirely.
  - Add `compact_now()` — a public method that runs exactly one compaction
    cycle synchronously.  The background loop calls the same method, so no
    separate "test path" exists.
  - Add `pending_count()` — a read-only introspection seam (Seam 2) that
    lets tests assert the buffer actually emptied without inferring it from
    timing or side effects.

Production code is unchanged in behaviour: `auto_compact=True` (the default)
keeps the background thread running exactly as before.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Modified LogStore
# ---------------------------------------------------------------------------

SEGMENT_SIZE = 64  # compact when a segment reaches this many records


class LogStore:
    """Append-only log with background compaction.

    Parameters
    ----------
    path:
        File path for the persistent log.
    auto_compact:
        If True (default), a background worker thread compacts closed
        segments automatically.  Pass False in tests to disable the thread
        and drive compaction manually via compact_now().
    """

    def __init__(self, path: str | os.PathLike, *, auto_compact: bool = True) -> None:
        self._path = Path(path)
        self._auto_compact = auto_compact

        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)

        # In-memory segments: _open_segment accumulates new records; when it
        # reaches SEGMENT_SIZE it is moved to _closed_segments and a new open
        # segment starts.  The background worker compacts closed segments into
        # the file.
        self._open_segment: List[str] = []
        self._closed_segments: List[List[str]] = []

        if self._auto_compact:
            self._worker = threading.Thread(target=self._compact_loop, daemon=True)
            self._worker.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(self, record: str) -> None:
        """Append a record.  Closes the current segment when it is full."""
        with self._cv:
            self._open_segment.append(record)
            if len(self._open_segment) >= SEGMENT_SIZE:
                self._closed_segments.append(self._open_segment)
                self._open_segment = []
                self._cv.notify_all()  # wake background worker

    def compact_now(self) -> None:
        """Flush all closed segments to the file synchronously.

        This is the same work the background loop performs.  Call it
        directly in tests (with auto_compact=False) for deterministic
        behaviour; also called by the background loop in production.
        """
        with self._lock:
            segments_to_write = self._closed_segments[:]
            self._closed_segments.clear()

        if not segments_to_write:
            return

        with self._path.open("a") as fh:
            for segment in segments_to_write:
                for record in segment:
                    fh.write(record + "\n")

    def flush_open_segment(self) -> None:
        """Force the partially-filled open segment to be written to the file.

        The open segment has not yet reached SEGMENT_SIZE, so the background
        worker would never compact it on its own.  This method closes the
        open segment and immediately writes it.  Useful in tests and on
        graceful shutdown.
        """
        with self._lock:
            if self._open_segment:
                self._closed_segments.append(self._open_segment)
                self._open_segment = []
        self.compact_now()

    def pending_count(self) -> int:
        """Return the number of records not yet written to disk.

        Includes records in the open segment and in closed-but-not-compacted
        segments.  Zero means the file is up to date.
        """
        with self._lock:
            return len(self._open_segment) + sum(
                len(s) for s in self._closed_segments
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compact_loop(self) -> None:
        """Background worker: sleep until segments are ready, then compact."""
        while True:
            with self._cv:
                # Wait until there is at least one closed segment to compact.
                self._cv.wait_for(lambda: bool(self._closed_segments))
            self.compact_now()


# ---------------------------------------------------------------------------
# Deterministic pytest tests
# ---------------------------------------------------------------------------

import pytest


@pytest.fixture()
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "store.log"


def _read_records(path: Path) -> List[str]:
    """Read all records from the log file."""
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    return [ln for ln in lines if ln]


# ------------------------------------------------------------------
# Test 1 – basic append + forced compaction (replaces the flaky test)
# ------------------------------------------------------------------

def test_200_records_all_persisted_after_compact_now(log_path: Path) -> None:
    """Appending 200 records then calling compact_now() writes them all.

    This is the direct replacement for the original flaky test that used
    time.sleep(0.5).  No sleep, no race — compaction is forced.
    """
    store = LogStore(log_path, auto_compact=False)

    for i in range(200):
        store.append(f"record-{i}")

    # 200 records / 64 per segment = 3 full closed segments (192 records)
    # + 8 records still in the open segment.
    store.compact_now()          # flush closed segments
    store.flush_open_segment()   # flush the partial open segment

    records = _read_records(log_path)
    assert len(records) == 200
    assert records[0] == "record-0"
    assert records[199] == "record-199"


# ------------------------------------------------------------------
# Test 2 – pending_count reflects in-memory state (Seam 2)
# ------------------------------------------------------------------

def test_pending_count_decreases_after_compact_now(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)

    for i in range(SEGMENT_SIZE):
        store.append(f"r{i}")

    # Exactly one full segment has been closed; the open segment is empty.
    assert store.pending_count() == SEGMENT_SIZE

    store.compact_now()

    assert store.pending_count() == 0


# ------------------------------------------------------------------
# Test 3 – compaction threshold: only full segments are compacted
# ------------------------------------------------------------------

def test_partial_segment_not_written_by_compact_now(log_path: Path) -> None:
    """compact_now() does not flush a partially-filled open segment."""
    store = LogStore(log_path, auto_compact=False)

    # Write fewer than SEGMENT_SIZE records — no closed segments created.
    for i in range(10):
        store.append(f"partial-{i}")

    store.compact_now()   # nothing to compact

    assert not log_path.exists() or _read_records(log_path) == []
    assert store.pending_count() == 10   # still in the open segment


# ------------------------------------------------------------------
# Test 4 – flush_open_segment writes partial data too
# ------------------------------------------------------------------

def test_flush_open_segment_writes_partial_records(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)

    for i in range(10):
        store.append(f"p{i}")

    store.flush_open_segment()

    records = _read_records(log_path)
    assert records == [f"p{i}" for i in range(10)]
    assert store.pending_count() == 0


# ------------------------------------------------------------------
# Test 5 – multiple segment boundaries
# ------------------------------------------------------------------

def test_multiple_full_segments_all_written(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)

    total = SEGMENT_SIZE * 3   # exactly 3 full segments, no remainder
    for i in range(total):
        store.append(f"rec-{i}")

    assert store.pending_count() == total

    store.compact_now()

    assert store.pending_count() == 0
    records = _read_records(log_path)
    assert len(records) == total
    assert records == [f"rec-{i}" for i in range(total)]


# ------------------------------------------------------------------
# Test 6 – ordering is preserved across segment boundaries
# ------------------------------------------------------------------

def test_record_ordering_preserved_across_segments(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)

    count = SEGMENT_SIZE + 1   # one full segment + one partial
    for i in range(count):
        store.append(f"item-{i:04d}")

    store.compact_now()          # flush full segment
    store.flush_open_segment()   # flush the trailing partial record

    records = _read_records(log_path)
    assert records == [f"item-{i:04d}" for i in range(count)]


# ------------------------------------------------------------------
# Test 7 – idempotent: compact_now() with no closed segments is a no-op
# ------------------------------------------------------------------

def test_compact_now_is_noop_when_no_closed_segments(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)
    store.compact_now()   # should not raise or create the file
    assert not log_path.exists()


# ------------------------------------------------------------------
# Test 8 – successive appends across multiple compact_now() calls
# ------------------------------------------------------------------

def test_successive_compactions_append_to_file(log_path: Path) -> None:
    store = LogStore(log_path, auto_compact=False)

    # First batch: one full segment.
    for i in range(SEGMENT_SIZE):
        store.append(f"batch1-{i}")
    store.compact_now()

    # Second batch: one full segment.
    for i in range(SEGMENT_SIZE):
        store.append(f"batch2-{i}")
    store.compact_now()

    records = _read_records(log_path)
    assert len(records) == SEGMENT_SIZE * 2
    assert records[0] == "batch1-0"
    assert records[SEGMENT_SIZE] == "batch2-0"
