# E08 Deterministic Time Fixture

A test waits with `sleep(2)` for a scheduled job to run. It flakes in CI. Improve it without increasing sleeps or skipping the test.
