# Testing Anti-Patterns

> A catalog of testing mistakes: how they occur, how to detect them, how to fix them, how to prevent them, and what to do instead.

---

## 1. Mock-Reality Drift

### What It Is
Mocks return whatever the test author expects, not what the real system returns. When the real system's behavior differs from the mock, bugs hide behind passing tests.

### How It Occurs
- Developer writes a mock based on their mental model of the API
- The real API returns different status codes, field names, or data shapes
- Mock tests pass; production breaks

### Real Example (tasche)
Unit tests used `/api/articles/search` with a mock that returned 200. The real endpoint was `/api/search`. Tests passed; production returned 404.

### Detection
- Compare mock return values against real API documentation
- Run periodic "smoke tests" against the real system
- Add mock contract tests (see atlas pattern)
- Look for mocks that return hardcoded values without validation

### Fix
1. Add contract tests that validate mock assumptions against reality
2. Use VCR cassettes (recorded real API responses) instead of hand-written mocks
3. Add E2E tests against staging/production

### Prevention
- Prefer real objects (in-memory databases, test servers) over mocks
- When mocks are necessary, write mock fidelity tests
- Record real API responses as fixtures rather than hand-coding mock returns
- Run at least one E2E test against real infrastructure

### What To Do Instead
```python
# INSTEAD OF: Hand-written mock that might be wrong
mock_response = {"status": 200, "data": {"id": 1}}

# DO: Record real API response as VCR cassette
@pytest.mark.vcr
def test_api_call():
    result = real_api_call()
    assert result.id == 1
```

---

## 2. Logging Instead of Asserting

### What It Is
Using `t.Log()`, `console.log()`, or `print()` in assertion position — the test logs a failure message but never actually fails.

### How It Occurs
- Developer writes a conditional check but uses logging instead of assertion
- Copy-paste from debug code that was never converted to assertions
- Cautious developer adds a "soft check" that they intend to harden later

### Real Example (rogue_planet)
```go
// XSS security test that NEVER FAILS:
if !strings.Contains(output, tt.want) {
    t.Logf("Output may not contain expected string %q", tt.want)  // Should be t.Errorf!
}
```

### Detection
- Search for `t.Log` inside `if` blocks in Go tests
- Search for `console.log` inside test assertions in JavaScript
- Search for `print` inside test functions in Python
- Look for tests with zero assertions (test functions that only log)
- Use mutation testing — mutants will survive these "tests"

### Fix
Replace logging with proper assertions:
```go
// BEFORE (broken):
if !strings.Contains(output, tt.want) {
    t.Logf("Output may not contain %q", tt.want)
}

// AFTER (correct):
if !strings.Contains(output, tt.want) {
    t.Errorf("Expected output to contain %q, got %q", tt.want, output)
}
```

### Prevention
- Lint rule: flag `t.Log`/`t.Logf` inside conditionals in test files
- Code review checklist: verify every conditional in tests uses assertion functions
- Mutation testing catches these immediately

### What To Do Instead
Always use the assertion function appropriate to your test framework: `t.Error`/`t.Fatal` (Go), `assert`/`expect` (JS), `assert` (Python).

---

## 3. "Not Empty" Assertions

### What It Is
Tests that only verify output is non-empty without checking its content. A function returning `"X"` for all inputs would pass.

### How It Occurs
- Developer writes a quick test to verify "something happens"
- Intention to add specific assertions later, but it never happens
- Especially common for complex outputs where the developer isn't sure what to assert

### Real Example
```go
if output == "" {
    t.Error("Sanitizer returned empty string for malformed HTML")
}
// This passes even if the sanitizer returns "<script>alert('xss')</script>"
```

### Detection
- Search for `!= ""`, `!= nil`, `!= null`, `!= undefined` as the only assertion
- Search for `len(result) > 0` as the only check
- Look for `toBeDefined()` or `toBeTruthy()` as the sole assertion in a test
- Measure assertion density: tests with ratio < 2 assertions/test are suspects

### Fix
Add specific content assertions:
```go
// BEFORE (weak):
assert output != ""

// AFTER (strong):
assert "<p>" in output           // Safe content preserved
assert "<script>" not in output  // Dangerous content removed
assert "expected text" in output // Specific expected content present
```

### Prevention
- Establish minimum assertion density standards (3+ assertions per test)
- Require both positive assertions (what SHOULD be present) and negative assertions (what SHOULD NOT be present)
- Property-based tests naturally avoid this — they test invariants, not emptiness

### What To Do Instead
For every test, answer three questions:
1. What specific content should be present?
2. What specific content should be absent?
3. What structural properties should hold?

---

## 4. Integration Tests That Mock Their Integration Points

### What It Is
Tests labeled "integration" that mock the external system they're supposed to integrate with. They're unit tests in disguise.

### How It Occurs
- Team wants integration test coverage but finds real systems hard to test against
- Developer mocks the HTTP client, database, or message queue for "convenience"
- Test passes but never exercises the actual integration

### Real Example (tasche)
`tests/integration/test_processing_pipeline.py` patched `http_fetch` with canned HTML in 6 of 7 tests. The tests never exercised real content extraction, real image downloading, or real redirect handling.

### Detection
- Look for `@mock.patch`, `vi.mock()`, `monkeypatch` in files under `tests/integration/`
- If an integration test has no external dependencies at runtime, it's a unit test
- Ask: "What would break if the external system changed?" If the answer is "nothing in this test," it's not an integration test

### Fix
1. Rename the tests honestly (move to `tests/unit/`)
2. Add actual integration tests that hit real (or realistic) systems
3. Use test containers, in-memory databases, or staging environments

### Prevention
- Define clear criteria for each test tier:
  - **Unit**: Tests a single function/class in isolation
  - **Integration**: Tests two or more components working together, with at least one real external dependency
  - **E2E**: Tests the full system from user-facing entry point to output
- Review test files: if everything in `tests/integration/` is mocked, flag it

### What To Do Instead
If you can't afford real integration tests, at least be honest about what you have. A well-organized unit test suite is more valuable than a falsely labeled integration test suite.

---

## 5. Testing the Mock, Not the System

### What It Is
Tests where the assertion verifies the mock's return value rather than the system's behavior. The test is tautological.

### How It Occurs
```python
# Setup: mock returns {"status": "ok"}
mock_api.return_value = {"status": "ok"}

# Test: calls function that uses mock
result = my_function()

# Assertion: verifies the mock's return value
assert result == {"status": "ok"}  # This is testing the mock, not the function
```

### Detection
- If you can delete the function under test and the test still passes by returning the mock value, it's testing the mock
- Look for tests where the asserted value is identical to the mock's configured return value
- Ask: "What production bug would this test catch?" If the answer is "none," it's testing the mock

### Fix
Assert on the function's *transformation* of the mock data, not the mock data itself:
```python
# BETTER: Assert on what the function DOES with the data
mock_api.return_value = {"status": "ok", "data": [1, 2, 3]}
result = my_function()
assert result.count == 3           # Tests the function's logic
assert result.is_successful        # Tests the function's interpretation
```

### Prevention
- Ask for every test: "What would this test catch if the implementation changed?"
- Prefer property-based tests for pure functions
- Use real objects where feasible

---

## 6. Skipped Tests Without Expiry

### What It Is
Tests marked as `@skip` or `@pytest.mark.skip` with a reason but no plan to re-enable them. They accumulate over time.

### How It Occurs
- A test breaks during a refactor; developer skips it "temporarily"
- A test depends on an environment that's currently unavailable
- Nobody tracks skipped tests as tech debt

### Detection
- Search for `@skip`, `@pytest.mark.skip`, `test.skip`, `xit`, `xdescribe`
- Track the number of skipped tests over time — it should not grow
- Check git blame: if a skip was added more than 30 days ago without a tracking issue, flag it

### Fix
1. Fix the test and remove the skip
2. If the test is no longer relevant, delete it entirely
3. If the skip is legitimate (e.g., platform-specific), add a conditional: `@pytest.mark.skipif(condition, reason="...")`

### Prevention
- Require a tracking issue link in every skip reason
- Add a CI check that fails if skipped test count exceeds a threshold
- Periodic review of all skipped tests (quarterly)

### What To Do Instead
```python
# AVOID: Unconditional skip
@pytest.mark.skip("broken after refactor")

# BETTER: Conditional skip with clear reason
@pytest.mark.skipif(not os.environ.get("RUN_E2E_TESTS"),
                    reason="Requires RUN_E2E_TESTS=1 and live staging")

# BEST: Fix the test or delete it
```

---

## 7. Tests Coupled to Implementation Details

### What It Is
Tests that break whenever the implementation changes, even if the behavior stays the same. They verify *how* something works, not *what* it does.

### How It Occurs
- Asserting on internal method call counts
- Verifying the order of internal operations
- Checking that specific private methods are called
- Asserting on exact SQL queries rather than query results

### Detection
- Tests that use `mock.assert_called_with()` on internal methods
- Tests that break during refactoring even though behavior is unchanged
- Tests that verify intermediate state rather than final output
- High test maintenance burden relative to feature changes

### Fix
Test behavior, not implementation:
```python
# BEFORE (implementation-coupled):
mock_db.execute.assert_called_with("SELECT * FROM users WHERE id = ?", [1])

# AFTER (behavior-coupled):
result = get_user(1)
assert result.name == "Alice"
assert result.email == "alice@example.com"
```

### Prevention
- Ask: "Would this test break if I refactored the internals without changing the API?"
- Test through public interfaces
- Use real objects that verify end-to-end behavior

---

## 8. Flaky Tests Left in the Suite

### What It Is
Tests that sometimes pass and sometimes fail, usually due to timing, ordering, or external dependencies. Teams learn to "just re-run."

### How It Occurs
- Tests depend on wall-clock time
- Tests share state through global variables or databases
- Tests depend on network availability
- Tests depend on test execution order

### Detection
- Track test failures over time — intermittent failures are flaky
- Run the test suite 10x in a row — flaky tests will fail at least once
- Look for `sleep()`, `time.time()`, `Date.now()` in test code
- Look for tests that pass alone but fail when run with other tests

### Fix
1. **Time-dependent**: Inject a clock or freeze time
2. **Order-dependent**: Reset shared state in setUp/tearDown
3. **Network-dependent**: Use VCR cassettes or test fixtures
4. **Race conditions**: Add proper synchronization or use deterministic alternatives

### Prevention
- Network tests behind build tags/markers (rogue_planet pattern)
- Capture real-world data as committed fixtures (rogue_planet testdata/ pattern)
- Randomize test execution order in CI
- No `sleep()` in tests — wait for specific conditions instead

---

## 9. Test Pollution (Shared Mutable State)

### What It Is
Tests that modify global state (environment variables, module-level variables, databases) without cleanup, causing subsequent tests to fail or pass incorrectly.

### How It Occurs
- Setting environment variables without restoring them
- Modifying module-level configuration
- Inserting data into shared databases without cleanup
- Registering plugins/handlers without unregistering

### Detection
- Tests that fail when run in a different order
- Tests that pass in isolation but fail in the suite
- Tests that fail only when run after a specific other test

### Fix
```python
# Use fixtures with cleanup:
@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.setenv("API_KEY", "test")
    # monkeypatch automatically restores after test

# Use fresh databases:
@pytest.fixture
def fresh_db():
    return Database(memory=True)  # New database per test

# Register/unregister:
pm.register(plugin, name="test-plugin")
try:
    yield
finally:
    pm.unregister(name="test-plugin")
```

### Prevention
- Use `monkeypatch` (pytest) instead of direct `os.environ` modification
- Prefer in-memory databases with per-test isolation
- Always unregister test plugins in `finally` blocks

---

## 10. Snapshot Testing Without Review

### What It Is
Using snapshot/golden-file tests where developers blindly update snapshots without reviewing the diff. The snapshots become a rubber stamp.

### How It Occurs
- Snapshot test fails → developer runs `--update-snapshots` → test passes
- Nobody reviews what changed in the snapshot
- Snapshots capture incidental details (timestamps, ordering) that change frequently

### Detection
- Frequent snapshot updates in PRs without corresponding code changes
- Very large snapshot files that nobody reads
- Snapshots that include timestamps, random IDs, or environment-specific data

### Fix
1. Keep snapshots small and focused
2. Exclude volatile data (timestamps, IDs) from snapshots
3. Require PR reviewers to explicitly approve snapshot changes
4. Use component-level snapshots, not full-page snapshots

### Prevention
- Snapshot only stable, meaningful output
- Add comments explaining what each snapshot verifies
- Treat snapshot updates as seriously as code changes in review

---

## 11. Tests That Verify Quantity Without Quality

### What It Is
Chasing coverage percentage or test count without considering what the tests actually verify.

### How It Occurs
- Team has a coverage gate (e.g., 80% required)
- Developers write minimal tests to hit the target
- Tests exercise lines but don't assert meaningful behavior

### Real Example (rogue_planet)
XSS security tests had 88.4% coverage but only 1.0 assertion per test. The most critical security tests were the weakest.

### Detection
- Measure assertion density alongside coverage
- Run mutation testing — low mutation kill rate means tests lack assertive power
- Review tests for "what would this catch if the code changed?"

### Fix
Focus on assertion quality:
- Increase assertion density to 3+ per test
- Add both positive and negative assertions
- Add property-based tests for invariant verification

### Prevention
- Use coverage as informational, not blocking (simonw pattern: `informational: true`)
- Track assertion density as a quality metric
- Periodic test quality audits (rogue_planet pattern)
- Mutation testing to validate test effectiveness

---

## 12. Tests That Don't Test the Sad Path

### What It Is
Tests that only verify the happy path — successful inputs, valid data, expected behavior — without testing error handling, edge cases, or failure modes.

### How It Occurs
- Developer tests the feature they just built
- Error paths feel less important
- Edge cases aren't obvious without systematic thinking

### Detection
- Look for test files where every test name is positive ("test_X_works", "test_X_returns")
- No tests for invalid input, missing data, network failures, permission errors
- No tests for boundary conditions (empty lists, max values, zero, negative)

### Fix
For every feature, write tests for:
1. **Happy path**: Normal valid input → expected output
2. **Invalid input**: Bad data → appropriate error
3. **Edge cases**: Empty, null, max, min, boundary values
4. **Error handling**: Network failure, timeout, permission denied
5. **Concurrency**: Race conditions, parallel access (where applicable)

### Prevention
- Property-based testing naturally explores edge cases
- Requirement: for every happy path test, write at least one sad path test
- Use boundary-first generators (qc pattern: yield min/max before random values)

---

## 13. Logical Defense-in-Depth (Shotgun Validation)

### What It Is

The same invariant is checked — and tested — at three or more internal layers
of a system, when no trust boundary sits between them. Every layer "defends"
against the same failure that the others already catch. "This should never
happen" tests are the dual: they only exist because the type permits the state
they're guarding against.

This is the test-design face of the LangSec community's "shotgun parsing"
antipattern: validation scattered everywhere, none of it remembered, none of
it definitive.

### How It Occurs

- Team treats security-style "defense in depth" as a universal good and
  applies it to internal program logic
- A bug escaped at the boundary; the team adds a downstream check "just in
  case" instead of fixing the boundary
- Language is dynamic or has nominal-only types; invariants cannot be encoded
  structurally, so they get spread across runtime checks
- "This should never happen" assertions accumulate as developers refuse to
  trust the type they're holding

### Real Pattern

```python
# Controller
def update_user(user_id):
    if user_id is None:                    # check #1
        raise BadRequest()
    return service.update(user_id)

# Service
def update(user_id):
    if not user_id:                        # check #2 (slightly different!)
        raise ValueError()
    return repo.find_and_update(user_id)

# Repository
def find_and_update(user_id):
    assert user_id is not None             # check #3 ("should never happen")
    db.execute("UPDATE … WHERE id = ?", (user_id,))
```

Three checks, three different shapes, three test files asserting "rejects
None." The boundary check (the controller) is the only one that defends
against an actual failure: a malformed HTTP request. The other two defend
against the absence of a `UserId` type.

### Distinguish From

Defense-in-depth at a *trust boundary* is **not** this antipattern. Examples
that should keep all their layers and all their tests:

- HTTP request parsing + authentication + authorization + parameterized SQL
- Mock + contract test + VCR cassette + E2E across an external API
- Retry + circuit breaker + fallback for an unreliable downstream

In each case the layers defend against *different* failure modes. The rule:

> Defense-in-depth is virtue when each layer defends against a *different*
> failure mode. It is an antipattern when each layer defends against the
> *same* failure mode.

### Detection

- The same invariant is asserted in 3+ test files for functions in the same
  module
- Tests named `test_X_rejects_null`, `test_X_rejects_empty`,
  `test_X_rejects_negative` repeated across functions
- `if x is None: raise ...` near the top of many functions whose parameter
  type is `T` (not `Optional[T]`)
- Comments like "this should never happen" / "defensive check"
- A builder lets you construct an invalid object, and a test asserts that the
  invalid object is rejected
- Coverage of internal validation branches is high while the boundary parser
  has no property-based test

### Fix

1. **Lift the invariant into a type** at the outermost trust boundary it
   crosses: smart constructor, branded type, `NonEmpty`, `EmailAddress`,
   newtype.
2. **Delete every downstream check and its test.** This is the win.
3. **Replace per-function "rejects invalid" tests with one parser test**,
   ideally property-based with the *valid-or-absent* invariant: for any
   input, the result is either `None` or it satisfies every promise the
   type makes.
4. **If the language cannot express the invariant in the type system**, keep
   exactly one runtime check at the outermost layer. Do not duplicate it.

### Prevention

- Code review: for every new defensive check, ask "what trust boundary does
  this defend?" If the answer is "none" or "the same one as the layer above,"
  reject it.
- Test review: for every "rejects invalid input" test, ask "could the
  function's type make this input unconstructible?" If yes, fix the type
  instead.
- During Assess mode: count layers that re-check the same invariant. Three
  or more is a smell.

### What To Do Instead

See `CORRECTNESS_BY_CONSTRUCTION.md` for the full thesis and language-specific
patterns. The short version:

- Parse, don't validate. Make illegal states unrepresentable.
- Test the parser at the boundary. Trust the type inside the boundary.
- Every "this should never happen" comment is a confession that the type is
  too loose. Tighten it; delete the comment and the assertion.

---

## Quick Reference: Detection Signals

| Anti-Pattern | Grep/Search Signal |
|---|---|
| Logging not asserting | `t.Log` in `if` blocks; `console.log` in test files |
| Not-empty assertions | `!= ""`, `toBeDefined()`, `toBeTruthy()` as sole assertion |
| Unconditional skips | `@skip`, `xit`, `xdescribe` without `skipif` |
| Mock-only integration | `@mock.patch` in `tests/integration/` |
| No sad path | All test names contain "works", "returns", "success" |
| Test pollution | `os.environ[...] =` without monkeypatch |
| Flaky time tests | `sleep(`, `time.time()`, `Date.now()` in test files |
| Stale snapshots | Snapshot update commits with no code changes |
| Logical defense-in-depth | Same `is None`/`!= ""` guard repeated across layers; "should never happen" comments; multiple test files asserting the same rejection |
