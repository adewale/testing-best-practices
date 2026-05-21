# Candidate Answer

This is test pollution, not a product behavior failure: plugin tests mutate shared process state (a global registry and/or environment variable) and do not restore it, so later tests depend on execution order.

Fix the tests by making state isolation explicit:

- Replace direct environment writes with the test framework's scoped helper (`monkeypatch.setenv/delenv`, `patch.dict`, Jest/Vitest `stubEnv` + restore, etc.).
- Snapshot and restore the global registry in `teardown`/`afterEach`, preferably through an `autouse` fixture so every test starts from a clean registry.
- If a plugin is registered inside a test, unregister it in `finally` or use a context manager/fixture that guarantees cleanup.
- Add a regression test that runs with a polluted registry/env setup and asserts the affected behavior still gets a fresh clean state.
- Add randomized-order execution in CI (`pytest-randomly`, Jest randomization equivalent) to catch future order dependencies.

Example pytest fixture:

```python
import os
import pytest

@pytest.fixture(autouse=True)
def isolate_plugin_state(monkeypatch):
    original_registry = plugin_registry.copy()
    monkeypatch.delenv("PLUGIN_PATH", raising=False)
    try:
        yield
    finally:
        plugin_registry.clear()
        plugin_registry.update(original_registry)
```

Do not fix this by renaming tests, forcing test order, or skipping the failing test; the correct quality fix is cleanup/isolation of all shared mutable state.