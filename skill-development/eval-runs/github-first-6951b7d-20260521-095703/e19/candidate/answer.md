# Candidate answer

Diagnosis: this is **test pollution**. Plugin tests mutate shared process state (global plugin registry and/or `os.environ`) and do not restore it, so later tests pass in isolation but fail when run after those tests.

Fix:
- Do not make tests depend on execution order.
- Use scoped cleanup for every global mutation:
  - pytest: use `monkeypatch.setenv/delenv` instead of direct `os.environ[...] = ...`.
  - snapshot/clear/restore the global registry in an `autouse` fixture or register plugins with `try/finally` cleanup.
- Prefer creating a fresh registry per test if the production API allows dependency injection.
- Add a regression test that runs/registers the plugin path first, then asserts the previously failing test still sees a clean registry/environment.

Example pytest fixture:

```python
import os
import pytest

from package.plugins import registry

@pytest.fixture(autouse=True)
def isolate_plugin_state(monkeypatch):
    original_registry = registry.copy()
    original_env = os.environ.copy()
    try:
        yield
    finally:
        registry.clear()
        registry.update(original_registry)
        os.environ.clear()
        os.environ.update(original_env)
```

Then update plugin tests to use `monkeypatch` and this fixture instead of leaving registered plugins or environment variables behind.
