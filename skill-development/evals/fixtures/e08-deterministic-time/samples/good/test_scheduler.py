from app.scheduler import FakeClock, Scheduler


def test_scheduled_job_runs_when_clock_advances():
    fake_clock = FakeClock(start=0)
    scheduler = Scheduler(clock=fake_clock)
    ran = []

    scheduler.schedule_after(2, lambda: ran.append('job'))
    fake_clock.advance(2)
    scheduler.run_pending()

    assert ran == ['job']
