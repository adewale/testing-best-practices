from app.scheduler import FakeClock, Scheduler


def test_due_job_runs():
    clock = FakeClock()
    queue = Scheduler(clock)
    deliveries = []
    queue.schedule_after(2, lambda: deliveries.append(1))
    clock.advance(2)
    queue.run_pending()
    assert deliveries == [1]
