These tests for `suggest()` have never failed, but a bug that made `suggest()` return an
empty list shipped anyway. Upgrade `test_geists.py` so it would catch that class of bug.
Keep testing through the public `suggest()` function.
