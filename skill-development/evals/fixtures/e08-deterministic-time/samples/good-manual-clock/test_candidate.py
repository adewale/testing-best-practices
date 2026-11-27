from types import SimpleNamespace
from unittest.mock import Mock

from app.scheduler import Scheduler


def test_one_delivery_at_the_deadline():
    current = SimpleNamespace(now=20)
    queue = Scheduler(current)
    deliver = Mock()
    queue.schedule_after(4, deliver)

    for instant, expected in [(23, 0), (24, 1), (30, 1)]:
        current.now = instant
        queue.run_pending()
        assert deliver.call_count == expected
