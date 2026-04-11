# Lessons from github.com/simonw Repositories

> Extracted from scanning datasette, sqlite-utils, llm, and plugin ecosystem.
> Date: 2026-04-11

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Testing Ecosystem Overview](#testing-ecosystem-overview)
3. [Documentation-as-Tests](#documentation-as-tests)
4. [Property-Based Testing](#property-based-testing)
5. [VCR Cassette Testing for External APIs](#vcr-cassette-testing)
6. [CLI Testing Patterns](#cli-testing-patterns)
7. [Plugin Architecture Testing](#plugin-architecture-testing)
8. [Fixture and Test Data Patterns](#fixture-and-test-data-patterns)
9. [Cross-Platform and Cross-Version Testing](#cross-platform-and-cross-version-testing)
10. [Coverage Strategy](#coverage-strategy)
11. [Real Databases over Mocks](#real-databases-over-mocks)
12. [Async Testing Patterns](#async-testing-patterns)
13. [Test Organization and Infrastructure](#test-organization-and-infrastructure)
14. [Anti-Patterns and Lessons](#anti-patterns-and-lessons)

---

## Executive Summary

Simon Willison's projects demonstrate a distinctive testing philosophy:

- **Documentation-is-tested**: Tests verify that every CLI command, plugin hook, setting, and utility function is documented. If you add a feature without updating docs, tests fail.
- **Real databases, not mocks**: sqlite-utils and datasette test against real in-memory SQLite databases. No ORM mocks, no fake SQL engines.
- **Hypothesis for roundtrip properties**: sqlite-utils uses Hypothesis to verify that data roundtrips through SQLite correctly for all data types.
- **VCR cassettes for API tests**: LLM plugins use pytest-recording (VCR.py) to record and replay real API interactions, avoiding flaky network tests.
- **Cross-platform, cross-version matrix**: Tests run on Ubuntu + macOS + Windows, across Python 3.10-3.14, and multiple SQLite versions.
- **Plugin architecture enables test plugins**: Datasette loads test plugins from a `tests/plugins/` directory, testing the plugin system with real plugins.
- **Informational coverage, not blocking**: Codecov is configured as `informational: true` — coverage reports but never blocks PRs.

---

## Testing Ecosystem Overview

| Repo | Tests | Framework | PBT | VCR | CI Matrix |
|------|-------|-----------|-----|-----|-----------|
| datasette | 40+ test files | pytest + pytest-asyncio + pytest-xdist | -- | -- | 5 Python × 1 OS + SQLite version matrix |
| sqlite-utils | 40+ test files | pytest + hypothesis | Hypothesis | -- | 5 Python × 4 OS × numpy toggle |
| llm | 20+ test files | pytest + pytest-httpx + pytest-recording | -- | VCR cassettes | 5 Python × 3 OS |
| llm-anthropic | 2 test files | pytest + VCR | -- | VCR cassettes | -- |
| llm-gemini | 2 test files | pytest + VCR | -- | VCR cassettes | -- |
| datasette-graphql | tests/ | pytest | -- | -- | -- |
| sqlite-migrate | tests/ | pytest | -- | -- | -- |

---

## Documentation-as-Tests

This is the most distinctive pattern across simonw's repos. Tests verify that documentation is complete and consistent.

### Pattern 1: Every CLI Command Must Be Documented

```python
# sqlite-utils: test_docs.py
@pytest.mark.parametrize("command", cli.cli.commands.keys())
def test_commands_are_documented(documented_commands, command):
    assert command in documented_commands

@pytest.mark.parametrize("command", cli.cli.commands.values())
def test_commands_have_help(command):
    assert command.help, "{} is missing its help".format(command)
```

**Lesson**: Parametrize test cases over the actual CLI command registry. If a developer adds a new command, the test automatically fails until docs are updated.

### Pattern 2: Every Plugin Hook Must Be Documented

```python
# datasette: test_docs.py
def test_plugin_hooks_are_documented(plugin_hooks_content, subtests):
    plugins = [name for name in dir(app.pm.hook) if not name.startswith("_")]
    for plugin in plugins:
        with subtests.test(plugin=plugin):
            assert plugin in headings
            # Check for plugin_name(arg1, arg2, arg3) signature
            expected = f"{plugin}({', '.join(arg_names)})"
            assert expected in plugin_hooks_content
```

**Lesson**: Not just "is the hook name in the docs" but "is the hook documented with its correct argument signature."

### Pattern 3: Every Setting Must Be Documented

```python
# datasette: test_docs.py
def test_settings_are_documented(settings_headings, subtests):
    for setting in app.SETTINGS:
        with subtests.test(setting=setting.name):
            assert setting.name in settings_headings
```

### Pattern 4: Every Recipe Must Be Documented

```python
# sqlite-utils: test_docs.py
@pytest.mark.parametrize("recipe", [n for n in dir(recipes) if callable(getattr(recipes, n))])
def test_recipes_are_documented(documented_recipes, recipe):
    assert recipe in documented_recipes
```

### Pattern 5: RST Heading Underlines Must Match Title Length

```python
# datasette: test_docs.py
def test_rst_heading_underlines_match_title_length():
    """Test that RST heading underlines are the same length as their titles."""
    for rst_file in docs_path.glob("*.rst"):
        # ... checks underline characters match title length
```

**Lesson**: Even documentation formatting is tested. This prevents subtle RST rendering bugs.

### Pattern 6: Functions Marked as Documented Actually Are

```python
# datasette: test_docs.py
def test_functions_marked_with_documented_are_documented(documented_fns, subtests):
    for fn in utils.functions_marked_as_documented:
        with subtests.test(fn=fn.__name__):
            assert fn.__name__ in documented_fns
```

**Key Insight**: These tests use the code itself as the source of truth (inspecting registries, command lists, function decorators) and verify docs match. This is the inverse of most documentation tests — instead of testing that documented features work, they test that working features are documented.

---

## Property-Based Testing

### Roundtrip Properties (sqlite-utils)

```python
# sqlite-utils: test_hypothesis.py
@given(st.integers(-9223372036854775808, 9223372036854775807))
def test_roundtrip_integers(integer):
    db = sqlite_utils.Database(memory=True)
    row = {"integer": integer}
    db["test"].insert(row)
    assert list(db["test"].rows) == [row]

@given(st.text())
def test_roundtrip_text(text):
    db = sqlite_utils.Database(memory=True)
    row = {"text": text}
    db["test"].insert(row)
    assert list(db["test"].rows) == [row]

@given(st.binary(max_size=1024 * 1024))
def test_roundtrip_binary(binary):
    db = sqlite_utils.Database(memory=True)
    row = {"binary": binary}
    db["test"].insert(row)
    assert list(db["test"].rows) == [row]

@given(st.floats(allow_nan=False))
def test_roundtrip_floats(floats):
    db = sqlite_utils.Database(memory=True)
    row = {"floats": floats}
    db["test"].insert(row)
    assert list(db["test"].rows) == [row]
```

**Key Design Decisions**:
- Uses SQLite's actual integer range: `-(2^63)` to `2^63 - 1`
- Excludes NaN from floats (SQLite doesn't preserve NaN)
- Limits binary to 1MB (practical upper bound)
- Tests against **real in-memory SQLite**, not a mock
- Each test creates a fresh database — no shared state

**Lesson**: Roundtrip tests are the purest form of property-based testing for data storage. "What goes in must come out identical" is a universal invariant.

---

## VCR Cassette Testing for External APIs

### Pattern: Record and Replay Real API Calls

The `llm` project and its plugins use `pytest-recording` (VCR.py wrapper) to handle external API testing:

```python
# llm: test_tools.py
@pytest.mark.vcr
def test_tool_use_basic(vcr):
    model = llm.get_model("gpt-4o-mini")
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
    chain_response = model.chain("What is 1231 * 2331?", tools=[multiply], key=API_KEY)
    output = "".join(chain_response)
    assert output == "The result of \\( 1231 \\times 2331 \\) is \\( 2,869,461 \\)."
```

**How it works**:
- First run: Makes real API calls, records responses to YAML cassette files
- Subsequent runs: Replays from cassettes — no network needed
- Cassettes stored in `tests/cassettes/` directory
- Sensitive headers filtered: `filter_headers: ["Authorization", "X-API-KEY"]`

**Advantages**:
- Tests exercise real API response formats
- No hand-written mock responses that drift from reality
- Deterministic after first recording
- Easy to update: delete cassette and re-run

**Disadvantages**:
- Cassettes become stale when APIs change
- First recording requires real API keys
- Large cassettes bloat the repo

### Plugin Testing with VCR

```python
# llm-anthropic: conftest.py
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["X-API-KEY"]}
```

Every LLM plugin follows this same pattern: VCR cassettes for API testing with filtered credentials.

---

## CLI Testing Patterns

### Pattern: Click's CliRunner

All three major repos test CLI commands via Click's `CliRunner`:

```python
# sqlite-utils: test_cli.py
def test_tables(db_path):
    result = CliRunner().invoke(cli.cli, ["tables", db_path])
    assert '[{"table": "Gosh"},\n {"table": "Gosh2"}]' == result.output.strip()
```

### Pattern: Parametrized Output Formats

```python
# sqlite-utils: test_cli.py
@pytest.mark.parametrize("format,expected", [
    ("--csv", "table,count\nGosh,0\n..."),
    ("--tsv", "table\tcount\nGosh\t0\n..."),
])
def test_tables_counts_csv(db_path, format, expected):
    result = CliRunner().invoke(cli.cli, ["tables", "--counts", format, db_path])
    assert result.output.strip() == expected
```

**Lesson**: Test every output format (JSON, CSV, TSV, table) as separate parametrized cases.

### Pattern: Test Help Text Exists

```python
@pytest.mark.parametrize("options", (["-h"], ["--help"], ["insert", "-h"]))
def test_help(options):
    result = CliRunner().invoke(cli.cli, options)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
```

### Pattern: Test Error Messages

```python
def test_install_error_if_no_packages():
    runner = CliRunner()
    result = runner.invoke(cli, ["install"])
    assert result.exit_code == 2
    assert "Error: Please specify at least one package" in result.output
```

---

## Plugin Architecture Testing

### Pattern: Real Test Plugins (datasette)

Datasette loads real plugin files from `tests/plugins/`:

```
tests/plugins/
  my_plugin.py           # Tests most hook points
  my_plugin_2.py         # Tests secondary hooks
  sleep_sql_function.py  # Tests prepare_connection
  view_name.py           # Tests template vars
```

Tests verify the expected plugin list:
```python
EXPECTED_PLUGINS = [
    {"name": "my_plugin.py", "hooks": ["actor_from_request", "asgi_wrapper", ...]},
    # ...
]
```

**Lesson**: Test plugin systems with actual plugins, not by mocking the plugin interface.

### Pattern: Plugin Registration/Unregistration in Fixtures

```python
# llm: conftest.py
@pytest.fixture(autouse=True)
def register_embed_demo_model(embed_demo, mock_model, async_mock_model):
    class MockModelsPlugin:
        @llm.hookimpl
        def register_models(self, register):
            register(mock_model, async_model=async_mock_model)

    pm.register(MockModelsPlugin(), name="undo-mock-models-plugin")
    try:
        yield
    finally:
        pm.unregister(name="undo-mock-models-plugin")
```

**Lesson**: Register test plugins in fixtures and clean up after. The `try/finally` ensures unregistration even on test failure.

### Pattern: Hook Call Monitoring (datasette)

```python
# datasette: conftest.py
@pytest.fixture(scope="session", autouse=True)
def check_actions_are_documented():
    def before(hook_name, hook_impls, kwargs):
        if hook_name == "permission_resources_sql":
            assert kwargs["action"] in datasette.actions
    pm.add_hookcall_monitoring(before=before, after=lambda *a: None)
```

**Lesson**: Use pluggy's hook monitoring to validate that all permission actions are registered and documented — this catches unregistered actions at test time.

---

## Fixture and Test Data Patterns

### Pattern: Session-Scoped Client with Shared Fixture Database

```python
# datasette: conftest.py
_ds_client = None

@pytest_asyncio.fixture
async def ds_client():
    global _ds_client
    if _ds_client is not None:
        return _ds_client
    ds = Datasette(metadata=METADATA, config=CONFIG, plugins_dir=PLUGINS_DIR)
    db = ds.add_database(Database(ds, memory_name=f"fixtures_{secrets.token_hex(8)}"))
    # ... setup tables
    _ds_client = ds.client
    return _ds_client
```

**Key decisions**:
- Manual singleton pattern (module-level `_ds_client`) rather than session-scoped fixture
- Unique memory database name per process (avoids collisions with pytest-xdist)
- Tables populated once, reused across all tests

### Pattern: Context Manager Fixture Factory

```python
# datasette: fixtures.py
@contextlib.contextmanager
def make_app_client(sql_time_limit_ms=None, cors=False, memory=False, ...):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, filename)
        conn = sqlite3.connect(filepath)
        conn.executescript(TABLES)
        # ...
        ds = Datasette(files, settings=settings, ...)
        yield TestClient(ds)
        for db in ds.databases.values():
            if not db.is_memory:
                db.close()
```

**Lesson**: Context manager fixtures ensure cleanup even on failure. The factory pattern allows tests to customize the Datasette configuration.

### Pattern: Automatic Database Cleanup

```python
# sqlite-utils: conftest.py
@pytest.fixture(autouse=True)
def close_all_databases():
    """Automatically close all Database objects created during a test."""
    databases = []
    original_init = Database.__init__

    def tracking_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        databases.append(self)

    Database.__init__ = tracking_init
    yield
    Database.__init__ = original_init
    for db in databases:
        try:
            db.close()
        except Exception:
            pass
```

**Lesson**: Monkey-patch the constructor to track all instances created during a test, then clean up all of them. Prevents "too many open files" errors in large test suites.

### Pattern: Test Ordering to Avoid Async Pollution

```python
# datasette: conftest.py
def pytest_collection_modifyitems(items):
    # Ensure test_cli.py runs first before any asyncio code kicks in
    move_to_front(items, "test_cli")
    move_to_front(items, "test_black")
```

**Lesson**: Some tests must run before async event loops are created. Use `pytest_collection_modifyitems` to enforce ordering when needed.

---

## Cross-Platform and Cross-Version Testing

### Python Version Matrix

All three major repos test across Python 3.10-3.14 (including pre-releases):

```yaml
# datasette: test.yml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
```

### SQLite Version Matrix

Datasette has a dedicated workflow testing against multiple SQLite versions:

```yaml
# datasette: test-sqlite-support.yml
strategy:
  matrix:
    sqlite-version: ["3.46", "3.25"]
```

**Lesson**: When your software depends on a C library with version-specific features (like SQLite's window functions or UPSERT), test against the minimum and recent versions.

### OS Matrix

```yaml
# llm: test.yml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### Optional Dependency Testing (numpy)

```yaml
# sqlite-utils: test.yml
strategy:
  matrix:
    numpy: [0, 1]  # Test with and without numpy
steps:
  - name: Optionally install numpy
    if: matrix.numpy == 1
    run: pip install numpy
```

**Lesson**: When your library has optional dependencies, test both with and without them installed. sqlite-utils has numpy-specific code paths that need verification.

### Pyodide Testing

```yaml
# datasette: test-pyodide.yml
- name: Run test
  run: ./test-in-pyodide-with-shot-scraper.sh
```

Datasette tests itself running in Pyodide (browser-based Python) using shot-scraper (headless browser tool).

**Lesson**: If your Python library claims to work in Pyodide/WASM, automate that verification in CI.

---

## Coverage Strategy

### Informational, Not Blocking

```yaml
# datasette & sqlite-utils: codecov.yml
coverage:
  status:
    project:
      default:
        informational: true
    patch:
      default:
        informational: true
```

**Lesson**: Coverage is reported but never blocks PRs. This avoids the perverse incentive of writing low-quality tests just to hit a coverage target.

### Coverage Configuration

```ini
# datasette: .coveragerc
[run]
omit = datasette/_version.py, datasette/utils/shutil_backport.py
```

Only meaningful code is measured — auto-generated version files and backport shims are excluded.

---

## Real Databases over Mocks

### sqlite-utils: Every Test Uses a Real Database

```python
@pytest.fixture
def fresh_db():
    return Database(memory=True)

@pytest.fixture
def existing_db():
    database = Database(memory=True)
    database.executescript("""
        CREATE TABLE foo (text TEXT);
        INSERT INTO foo (text) values ("one");
    """)
    return database
```

No mock databases. Every test creates a real in-memory SQLite database. This means:
- Tests verify actual SQL execution
- Schema changes are tested against real constraints
- Foreign keys, triggers, and FTS features work as in production

### datasette: Full Application Testing

```python
# datasette: test_docs.py
@pytest.mark.asyncio
async def test_homepage():
    ds = Datasette(memory=True)
    response = await ds.client.get("/")
    html = response.text
    assert "<h1>" in html
```

Tests use Datasette's built-in async test client (`ds.client`) which exercises the full ASGI application stack — routing, middleware, template rendering, database queries — without a real HTTP server.

### llm: MockModel is a Real Model Implementation

```python
# llm: conftest.py
class MockModel(llm.Model):
    model_id = "mock"
    supports_schema = True
    supports_tools = True

    def execute(self, prompt, stream, response, conversation):
        self.history.append((prompt, stream, response, conversation))
        while self._queue:
            messages = self._queue.pop(0)
            for message in messages:
                yield message
```

The MockModel is not a `unittest.mock.Mock` — it's a real implementation of the `llm.Model` interface. It records history and plays back enqueued responses. This means the test exercises the full model execution pipeline.

**Lesson**: A purpose-built fake that implements the real interface is more valuable than a generic mock that returns whatever you tell it to.

---

## Async Testing Patterns

### Pattern: pytest-asyncio with Strict Mode

```ini
# datasette: pytest.ini
asyncio_mode = strict
```

Strict mode requires every async test to be explicitly marked:
```python
@pytest.mark.asyncio
async def test_homepage(ds_client):
    response = await ds_client.get("/.json")
    assert response.status_code == 200
```

### Pattern: Serial Test Marking

```ini
# datasette: pytest.ini
markers =
    serial: tests to avoid using with pytest-xdist
```

```yaml
# CI splits runs:
pytest -n auto -m "not serial"   # Parallel
pytest -m "serial"               # Sequential
```

**Lesson**: Some tests (like those that modify global state or start subprocesses) can't run in parallel. Mark them and run them separately.

---

## Test Organization and Infrastructure

### Pattern: Reporting SQLite Version in Test Headers

```python
# datasette: conftest.py
def pytest_report_header(config):
    return "SQLite: {}".format(
        sqlite3.connect(":memory:").execute("select sqlite_version()").fetchone()[0]
    )
```

**Lesson**: When your tests depend on external library versions, report them in the test output for debugging.

### Pattern: Test-Aware Code

```python
# Both datasette and sqlite-utils:
def pytest_configure(config):
    sys._called_from_test = True

def pytest_unconfigure(config):
    del sys._called_from_test
```

This allows production code to detect when it's running under tests and adjust behavior (e.g., skip analytics, use different defaults).

### Pattern: Event Tracking Plugin for Test Assertions

```python
# datasette: conftest.py
class TrackEventPlugin:
    @hookimpl
    def track_event(self, datasette, event):
        datasette._tracked_events = getattr(datasette, "_tracked_events", [])
        datasette._tracked_events.append(event)
```

Then in tests:
```python
event = last_event(ds_write)
assert event.name == "insert-rows"
assert event.num_rows == 1
```

**Lesson**: For event-driven architectures, install a test plugin that records events, then assert on the event stream.

### Pattern: Integration Tests for Server Lifecycle

```python
# datasette: conftest.py
@pytest.fixture(scope="session")
def ds_localhost_http_server():
    ds_proc = subprocess.Popen(
        [sys.executable, "-m", "datasette", "--memory", "-p", "8041"],
    )
    wait_until_responds("http://localhost:8041/")
    yield ds_proc
    ds_proc.terminate()
```

**Lesson**: Some tests need a real server process. Use session-scoped fixtures to start it once and share across tests.

---

## Anti-Patterns and Lessons

### 1. Coverage as a Gate Causes Bad Tests

Both datasette and sqlite-utils use `informational: true` for codecov. The philosophy: coverage is a useful metric but should never be a merge blocker. Blocking on coverage creates perverse incentives to write low-value tests.

### 2. Mock Databases Hide Real SQL Bugs

sqlite-utils tests every feature against real SQLite. This catches:
- Type coercion issues (SQLite's dynamic typing)
- SQL syntax differences between versions
- FTS configuration bugs
- Foreign key constraint violations

### 3. Stale API Cassettes

VCR cassettes (used in llm plugins) can become stale when APIs change. Mitigation:
- Store cassettes in `tests/cassettes/` with clear naming
- Delete and re-record when API versions change
- Filter sensitive headers to avoid committing credentials

### 4. Test Ordering Dependencies

Datasette has to explicitly order some tests before others using `pytest_collection_modifyitems`. This is a code smell that indicates some tests have implicit dependencies on global state.

### 5. "Too Many Open Files" in Large Test Suites

Both datasette and sqlite-utils had to add explicit database cleanup fixtures to avoid exhausting file descriptors. The `close_all_databases` autouse fixture in sqlite-utils is the solution.

---

## Key Takeaways

1. **Test that features are documented, not just that code works** — parametrize over command registries, hook lists, and function decorators
2. **Roundtrip property tests are the highest-value PBT pattern** for data storage/serialization
3. **VCR cassettes are the pragmatic choice for external API testing** — better than hand-written mocks, cheaper than live API calls in CI
4. **Real databases over mocks** — in-memory SQLite is fast enough for tests and catches real SQL bugs
5. **Cross-version testing matters** — test across Python versions, OS, SQLite versions, and optional dependency presence
6. **Coverage should inform, not block** — `informational: true` in codecov
7. **Test the plugin system with real plugins** — load actual plugin files, not mocked interfaces
8. **Purpose-built fakes over generic mocks** — MockModel implements the real interface with history tracking
9. **Test error messages and help text** — users read these; they should be tested
10. **Clean up database connections aggressively** — autouse fixtures that track and close all database handles
