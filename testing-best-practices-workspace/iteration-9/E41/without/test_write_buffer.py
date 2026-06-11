"""
WriteBuffer: batches write() calls in memory; a background thread flushes
them to the file every `interval` seconds.

Modification for testability: inject the flush interval and expose a
manual flush() method so tests can trigger flushing deterministically
without sleeping.  The background thread is an implementation detail that
tests never rely on directly.
"""

import threading
import time
from pathlib import Path
from typing import Callable


# ---------------------------------------------------------------------------
# Production code (sketch)
# ---------------------------------------------------------------------------

class WriteBuffer:
    """
    Batches records in memory and flushes to *path* on a background thread
    every *interval* seconds.

    Testability seam
    ----------------
    * ``interval`` is injectable so tests can set it to a very large value
      (effectively disabling the background timer) and call ``flush()``
      manually.
    * ``flush()`` is public so tests can trigger a flush synchronously.
    * The clock used to drive the background loop is injectable via
      ``_clock`` (defaults to ``time.monotonic``).  Tests that do want to
      exercise timer-driven behaviour can substitute a fake clock.
    """

    def __init__(
        self,
        path: str,
        interval: float = 5.0,
        _clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._path = Path(path)
        self._interval = interval
        self._clock = _clock
        self._lock = threading.Lock()
        self._buffer: list[str] = []
        self._stop_event = threading.Event()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write(self, record: str) -> None:
        with self._lock:
            self._buffer.append(record)

    def flush(self) -> None:
        """Write all buffered records to the file immediately."""
        with self._lock:
            records, self._buffer = self._buffer, []

        if records:
            with self._path.open("a") as fh:
                for record in records:
                    fh.write(record + "\n")

    def close(self) -> None:
        """Stop the background thread and perform a final flush."""
        self._stop_event.set()
        self._thread.join(timeout=2)
        self.flush()

    # ------------------------------------------------------------------
    # Background thread
    # ------------------------------------------------------------------

    def _run(self) -> None:
        next_flush = self._clock() + self._interval
        while not self._stop_event.is_set():
            now = self._clock()
            if now >= next_flush:
                self.flush()
                next_flush = now + self._interval
            self._stop_event.wait(timeout=min(0.05, self._interval))


# ---------------------------------------------------------------------------
# Deterministic pytest tests
# ---------------------------------------------------------------------------

import pytest
import os


@pytest.fixture
def buf_path(tmp_path):
    """Return a Path for the buffer output file inside a temp directory."""
    return tmp_path / "output.txt"


# --- Helper -----------------------------------------------------------------

def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text().splitlines()


# --- Tests ------------------------------------------------------------------

class TestWriteBufferManualFlush:
    """Tests that call flush() directly — no time dependency whatsoever."""

    def test_flush_writes_single_record(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("hello")
        wb.flush()
        assert _read_lines(buf_path) == ["hello"]

    def test_flush_writes_multiple_records_in_order(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("first")
        wb.write("second")
        wb.write("third")
        wb.flush()
        assert _read_lines(buf_path) == ["first", "second", "third"]

    def test_flush_clears_buffer(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("a")
        wb.flush()
        wb.flush()          # second flush should add nothing
        assert _read_lines(buf_path) == ["a"]

    def test_flush_empty_buffer_creates_no_file(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.flush()
        assert not buf_path.exists()

    def test_multiple_flushes_append(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("batch1")
        wb.flush()
        wb.write("batch2")
        wb.flush()
        assert _read_lines(buf_path) == ["batch1", "batch2"]

    def test_close_flushes_remaining_records(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("last")
        wb.close()
        assert _read_lines(buf_path) == ["last"]

    def test_write_after_flush_is_captured(self, buf_path):
        wb = WriteBuffer(str(buf_path), interval=9999)
        wb.write("before")
        wb.flush()
        wb.write("after")
        wb.flush()
        assert _read_lines(buf_path) == ["before", "after"]

    def test_concurrent_writes_all_captured(self, buf_path):
        """Thread-safety: many concurrent writers, then one flush."""
        wb = WriteBuffer(str(buf_path), interval=9999)
        threads = [
            threading.Thread(target=wb.write, args=(f"record-{i}",))
            for i in range(50)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wb.flush()
        lines = _read_lines(buf_path)
        assert len(lines) == 50
        assert set(lines) == {f"record-{i}" for i in range(50)}


class TestWriteBufferFakeClock:
    """
    Tests that exercise the background-thread timer path using a fake,
    manually-advanced clock — zero wall-clock time consumed.
    """

    class FakeClock:
        """A callable clock whose time advances on demand."""

        def __init__(self, start: float = 0.0) -> None:
            self._now = start

        def __call__(self) -> float:
            return self._now

        def advance(self, seconds: float) -> None:
            self._now += seconds

    def _wait_for_flush(self, path: Path, expected_count: int, timeout: float = 1.0) -> None:
        """Poll (real wall clock, short timeout) until the file has the expected lines."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if len(_read_lines(path)) >= expected_count:
                return
            time.sleep(0.01)
        raise AssertionError(
            f"Expected {expected_count} lines in {path} within {timeout}s; "
            f"got {_read_lines(path)}"
        )

    def test_background_flush_triggered_by_clock_advance(self, buf_path):
        clock = self.FakeClock(start=0.0)
        # Use a small real interval so the background thread wakes quickly,
        # but the *timer* is driven by our fake clock.
        wb = WriteBuffer(str(buf_path), interval=5.0, _clock=clock)
        try:
            wb.write("timed-record")
            # Advance fake time past the 5-second interval.
            clock.advance(6.0)
            # The background thread will see clock() >= next_flush and flush.
            self._wait_for_flush(buf_path, expected_count=1)
            assert _read_lines(buf_path) == ["timed-record"]
        finally:
            wb.close()

    def test_no_flush_before_interval_elapses(self, buf_path):
        clock = self.FakeClock(start=0.0)
        wb = WriteBuffer(str(buf_path), interval=5.0, _clock=clock)
        try:
            wb.write("premature")
            # Advance less than the interval — no flush should happen.
            clock.advance(3.0)
            time.sleep(0.1)   # give the thread a chance to run
            assert not buf_path.exists(), "File should not exist before interval elapses"
        finally:
            wb.close()

    def test_second_flush_at_second_interval(self, buf_path):
        clock = self.FakeClock(start=0.0)
        wb = WriteBuffer(str(buf_path), interval=5.0, _clock=clock)
        try:
            wb.write("first")
            clock.advance(6.0)
            self._wait_for_flush(buf_path, expected_count=1)

            wb.write("second")
            clock.advance(5.0)   # now at t=11, past the second interval (t=10)
            self._wait_for_flush(buf_path, expected_count=2)

            assert _read_lines(buf_path) == ["first", "second"]
        finally:
            wb.close()
