Replace the fixed `sleep(2)` with deterministic time control.

- Inject a clock/timer into the scheduler instead of calling real wall-clock time directly.
- In the test, use a fake/frozen clock and advance it to the scheduled run time.
- Run/drain the scheduler after advancing the clock, then assert the job side effect occurred.
- If the scheduler is asynchronous, wait on a condition/event with a short timeout; do not sleep for a fixed duration.

Example shape:

```python
def test_scheduled_job_runs_when_clock_reaches_due_time():
    clock = FakeClock(start="2026-05-21T09:00:00Z")
    jobs = []
    scheduler = Scheduler(clock=clock)
    scheduler.schedule(at="2026-05-21T09:00:10Z", job=lambda: jobs.append("ran"))

    clock.advance(seconds=10)
    scheduler.run_due_jobs()

    assert jobs == ["ran"]
    assert scheduler.pending_jobs() == []
```

This makes the test fast and deterministic because it verifies the scheduling boundary directly instead of relying on CI timing.
