# E33 Python Fault-Injection Fixture

Write tests for `save_report(report: dict, store) -> str`.

`store.put(key: str, data: bytes)` persists data to a remote object store and
may raise `ConnectionError` on transient network failure. `save_report`
serializes the report, then calls `store.put`, retrying up to 3 attempts on
`ConnectionError`. If all attempts fail it raises `ReportSaveError`; on success
it returns the storage key. An empty report raises `ValueError`.

A good suite must do more than test the happy path and reject empty reports: it
must inject the downstream `ConnectionError` failure and assert the
error-handling path behaves correctly (transient failures are retried and
recover; exhausted retries surface a `ReportSaveError`, not a raw
`ConnectionError` or a crash).
