# Python Testing Reference

## Framework: pytest

### Project setup

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"  # or "strict"
addopts = "-v --strict-markers --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests (requires RUN_E2E_TESTS=1)",
    "slow: Slow tests requiring network/model downloads",
]

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod",
]
```

### Directory structure

```
tests/
  conftest.py          # Shared fixtures
  unit/
    conftest.py        # Unit-specific fixtures
    test_*.py
  integration/
    conftest.py
    test_*.py
  e2e/
    conftest.py
    test_*.py
```

## Property-Based Testing: Hypothesis

```python
from hypothesis import given, settings
from hypothesis import strategies as st

@given(text=st.text())
@settings(max_examples=200)
def test_never_crashes(text):
    result = parse(text)
    assert isinstance(result, str)

@given(data=st.binary())
def test_roundtrip(data):
    assert decode(encode(data)) == data

@given(text=st.text())
def test_idempotent(text):
    assert normalize(normalize(text)) == normalize(text)
```

**Dependencies**: Add `hypothesis` to test dependencies.

**Key strategies**: `st.text()`, `st.integers()`, `st.binary()`,
`st.floats(allow_nan=False)`, `st.lists()`, `st.from_regex()`,
`st.builds()` for custom types.

## Fixtures and Test Data

### conftest.py patterns

```python
@pytest.fixture
def fresh_db():
    return Database(memory=True)

@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    # monkeypatch auto-restores after test

@pytest.fixture(autouse=True)
def reset_factory():
    ArticleFactory._counter = 0
```

### Test data builders

```python
class ArticleFactory:
    _counter = 0
    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {"id": f"art_{cls._counter}", "title": f"Article {cls._counter}"}
        defaults.update(overrides)
        return defaults
```

## Async testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    response = await client.get("/api/items")
    assert response.status_code == 200
```

**Dependency**: `pytest-asyncio`

## VCR cassette testing (for external APIs)

```python
@pytest.mark.vcr
def test_api_call(vcr):
    result = call_external_api()
    assert result.status == "ok"

# conftest.py
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization", "X-API-KEY"]}
```

**Dependency**: `pytest-recording` (wraps VCR.py)

## CLI testing

```python
from click.testing import CliRunner

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["command", "--flag"])
    assert result.exit_code == 0
    assert "expected output" in result.output
```

## E2E tests gated by environment

```python
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="Requires RUN_E2E_TESTS=1 and live staging",
    ),
]
```

## Coverage commands

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
pytest --cov-fail-under=80  # Optional threshold
```
