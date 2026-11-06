# E08 Deterministic Time Fixture

A test waits with `sleep(2)` for a scheduled job to run. It flakes in CI. Improve it without increasing sleeps or skipping the test.

Submit executable Python pytest tests importing `FakeClock` and `Scheduler`
from `app.scheduler`. `FakeClock(start=0).advance(seconds)` moves virtual time;
`Scheduler(clock).schedule_after(delay, callback)` schedules work and
`run_pending()` runs due callbacks once. Verify no early execution, execution
at the deadline and no repeated execution after completion. No wall-clock wait
is needed. Names, helper layout and assertion spelling are up to you.
