# E08 Deterministic Time Fixture

A test waits with `sleep(2)` for a scheduled job to run. It flakes in CI.
Write executable Python tests for the scheduler. Use its virtual clock or inject
a clock with a numeric `now` attribute. The fixture exports `Scheduler` and
`FakeClock` from `app.scheduler`. `FakeClock(start=0).advance(seconds)` moves
virtual time. `Scheduler(clock).schedule_after(delay, callback)` schedules work,
and `run_pending()` runs each due callback once.

Check that the callback stays pending before the deadline, runs at the deadline
and runs only once.
