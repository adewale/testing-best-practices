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

**Dependency**: Add `hypothesis` to test dependencies.

**Key strategies**: `st.text()`, `st.integers()`, `st.binary()`,
`st.floats(allow_nan=False)`, `st.lists()`, `st.from_regex()`,
`st.builds()` and `@st.composite` for structured values, and `st.recursive()` for recursive formats.

### Collection, Input Domains, and Replay

A `@given` test generates and shrinks cases only when the configured runner executes it. Standalone pytest functions are invisible to `unittest` discovery; keep them as `TestCase` methods or deliberately use pytest. When projects, filters, or mixed runners make reachability uncertain, inspect the exact CI runner's collection output.

Keep two parser domains explicit:

- raw bytes/text for totality and documented-error properties;
- independently constructed, specification-valid values for semantic properties (`st.builds`, `@st.composite`, or `st.recursive`).

Validate a “valid” generator independently; otherwise malformed data can make deep behavior unreachable.

Generation cost matters: a large bounded `st.from_regex(...)` or a filter that rejects most candidates trips the `too_slow`/`filter_too_much` health checks under coverage or CI load. Build values directly (`st.text(alphabet=..., min_size=..., max_size=...)`), and register a CI settings profile (`settings.register_profile("ci", ...)`) rather than suppressing health checks.

Treat Hypothesis's example database as a cache, not the only permanent regression record. Promote important minimized inputs with `@example` or a deterministic regression; use `--hypothesis-seed` for short-lived reproduction. See `references/property-based-testing.md` for shared generator and oracle guidance.

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

The gated lane must exist: some CI job (nightly or post-deploy) sets `RUN_E2E_TESTS=1`, provides the staging URL, and fails if these tests skip there.

## Known bugs and expected failures

Use `@pytest.mark.xfail(strict=True, reason=...)` with the bug condition as the assertion, so an upstream fix turns the run red and prompts cleanup. Do not call `pytest.xfail()` imperatively inside the test body: it reports "xfailed" whether or not the bug is still present, and a regression after the fix stays green. Once the bug is fixed, delete the xfail so the test fails hard on regression.

## Declared compatibility

Test the floor you declare. If `requires-python = ">=3.12"`, some CI leg (and the type checker's `pythonVersion`) must run 3.12; otherwise raise the floor to what is tested.

## Coverage commands

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
pytest --cov-fail-under=80  # Optional threshold
```

A `fail_under` in `pyproject.toml` does nothing unless CI runs pytest with `--cov`. Measure `source` over the package, and exclude test doubles (`testing/fakes.py`) so 100% is not earned by covering the fakes.

## Choosing values and matchers

- Include distinct, non-default test values so at least one case exposes a
  dropped, defaulted, or swapped argument. Still cover `0`, `""`, `None`, and
  equal-value cases when they are boundaries or part of the contract.
- When order is not part of the contract, use `assertCountEqual` /
  `sorted(...) ==` / `set(...) ==` instead of pinning incidental order.
- Derive expected results independently of the SUT. Literals are clearest for
  simple examples; properties and independent reference models are valid for
  broader cases. Do not reuse the SUT's logic or constants in the oracle.
