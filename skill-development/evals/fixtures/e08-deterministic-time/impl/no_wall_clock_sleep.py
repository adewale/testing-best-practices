"""Load before collection so tests importing time.sleep also see the guard."""

import time


def pytest_configure():
    original_sleep = time.sleep

    def forbid_wait(seconds):
        if seconds > 0:
            raise AssertionError(f"virtual-time test attempted time.sleep({seconds})")
        return original_sleep(seconds)

    time.sleep = forbid_wait
