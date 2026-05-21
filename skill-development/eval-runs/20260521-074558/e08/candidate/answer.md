Replace the real wait with a deterministic time seam. Do not increase `sleep(2)` and do not skip the test.

```python
# Shape of the improved test: fake/injected clock + explicit scheduler drain.
def test_scheduled_job_runs_when_due(fake_clock):
    scheduler = Scheduler(clock=fake_clock.now)
    job = RecordingJob()

    scheduler.schedule(job.run, delay=2.0)
    assert job.run_count == 0          # not run early

    fake_clock.advance(2.0)            # exact due time, no wall-clock sleep
    scheduler.run_due()                # or: await scheduler.drain()/idle()

    assert job.run_count == 1
    assert job.completed is True
```

If the framework supports timer virtualization, use that instead of changing production code, e.g. fake timers/freezegun/time-machine and advance by exactly the scheduled delay. For async/background workers, expose/await a completion signal such as `drain()`, `idle()`, a future, or a condition tied to the job result; never synchronize with real `sleep()`.

Tests changed/assessed: flaky scheduled-job test using `sleep(2)`.
Behavior covered: job does not run before the scheduled time and does run once when virtual time reaches the due instant.
Commands run: not run in fixture.
Results: proposed deterministic-time rewrite.
Gaps / risks: production code may need an injected clock/scheduler seam if fake timers cannot intercept the current scheduler.