"""Mark individual tests that execute the owned search through native SQLite."""

import sqlite3
import sys

import pytest
from search import search


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item):
    observed = False

    def observe(frame, event, method):
        nonlocal observed
        if observed or event != "c_return" or getattr(method, "__name__", None) != "execute":
            return
        if not isinstance(getattr(method, "__self__", None), (sqlite3.Connection, sqlite3.Cursor)):
            return
        while frame is not None:
            if frame.f_code is search.__code__:
                observed = True
                item.user_properties.append(("tbp_observed", "1"))
                return
            frame = frame.f_back

    previous = sys.getprofile()
    sys.setprofile(observe)
    try:
        yield
    finally:
        sys.setprofile(previous)
