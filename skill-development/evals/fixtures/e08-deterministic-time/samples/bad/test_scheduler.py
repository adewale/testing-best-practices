import time


def test_scheduled_job_runs():
    schedule_job()
    time.sleep(5)
    assert job_ran()
