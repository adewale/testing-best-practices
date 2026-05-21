# Candidate answer: E19 order pollution

Diagnosis: this is test pollution. A plugin test mutates process-global state (plugin registry and/or `os.environ`) and does not restore it, so later order-related tests observe leaked plugins/config and fail only when run after the plugin suite.

Fix the mutating tests, not the downstream failing test:

```python
import os
import pytest

@pytest.fixture
def isolated_plugin_state(monkeypatch):
    registry_snapshot = dict(plugin_registry.items())  # or public snapshot API
    env_snapshot = {name: os.environ.get(name) for name in ("APP_PLUGINS", "PLUGIN_PATH")}
    yield
    plugin_registry.clear()
    plugin_registry.update(registry_snapshot)
    for name, value in env_snapshot.items():
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)


def test_plugin_registration(isolated_plugin_state, monkeypatch):
    monkeypatch.setenv("APP_PLUGINS", "test_plugin")
    plugin_registry.register("test_plugin", TestPlugin)

    assert discover_plugins() == [TestPlugin]
```

Prefer `monkeypatch.setenv/delenv` over direct `os.environ[...] = ...`, and wrap registry mutations in a fixture or `try/finally` using the registry's public clear/unregister API. If many tests can leak state, add an `autouse` fixture around each test to snapshot/restore the registry and relevant env vars.

Add a regression command/check that reproduces the original order dependency:

```bash
pytest tests/plugins tests/test_ordering.py -q
pytest --random-order -q
```

Tests changed/assessed: plugin/order tests affected by leaked global registry/env state.
Behavior covered: plugin registration/discovery is isolated per test; order behavior no longer depends on previous plugin tests.
Commands run: not run; fixture provided prompt only.
Results: candidate fix written.
Gaps / risks: exact registry/env variable names need adapting to the project.
Follow-ups: enable randomized test ordering in CI periodically to catch future order pollution.
