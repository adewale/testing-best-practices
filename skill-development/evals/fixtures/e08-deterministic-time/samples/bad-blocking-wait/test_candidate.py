from time import sleep

from app.scheduler import FakeClock, Scheduler


def test_delivery_with_an_extra_wall_clock_wait():
    clock = FakeClock()
    queue = Scheduler(clock)
    deliveries = []
    queue.schedule_after(2, lambda: deliveries.append(1))
    queue.run_pending()
    assert deliveries == []
    clock.advance(2)
    sleep(0.01)
    queue.run_pending()
    assert deliveries == [1]
    queue.run_pending()
    assert deliveries == [1]
