Replace the wall-clock wait with a controllable time seam and drive the scheduler in the test.

```python
# shape of the fix, independent of framework
clock = FakeClock(start="2026-01-01T00:00:00Z")
job = RecordingJob()
scheduler = Scheduler(clock=clock)

scheduler.schedule_after(seconds=2, job=job)

assert job.runs == []              # not run early
clock.advance(seconds=2)           # no real sleep
scheduler.run_due_jobs()           # or drain/flush pending timers

assert len(job.runs) == 1
assert job.runs[0].scheduled_for == clock.now()
```

For existing code, use the framework's fake timers/freezegun equivalent; for new code, inject a `Clock`/scheduler. Pin the start time, advance exactly to the due time, drain pending jobs, and assert both that the job did not run early and ran once when due. Use any real-time timeout only as a deadlock guard, not as the mechanism that makes the test pass.
