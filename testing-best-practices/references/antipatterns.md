# Testing Anti-Patterns: Detection and Fixes

## Quick Detection Reference

| Anti-Pattern | Search Signal | Severity |
|---|---|---|
| Logging not asserting | `t.Log` in `if` blocks; `console.log` in test conditionals | P0 |
| Not-empty assertions | `!= ""`, `toBeDefined()`, `toBeTruthy()` as sole assertion | P1 |
| Unconditional skips | `@skip`, `xit`, `xdescribe` without `skipif` | P1 |
| Mock-only integration | `@mock.patch` / `vi.mock` in `tests/integration/` | P2 |
| No sad path tests | All test names contain "works", "returns", "success" | P2 |
| Test pollution | `os.environ[...] =` without `monkeypatch` | P2 |
| Flaky time tests | `sleep(`, `time.time()`, `Date.now()` in tests | P2 |
| Testing the mock | Asserted value identical to mock's configured return | P3 |
| Stale snapshots | Snapshot updates with no code changes | P3 |
| Logical defense-in-depth | Same invariant checked & tested at 3+ internal layers; "this should never happen" tests | P2 |

## Anti-Pattern Details

### 1. Logging not asserting

**What**: `t.Log()` / `console.log()` / `print()` in assertion position. Test
logs failure but never fails.

**Fix**: Replace with `t.Errorf()` / `expect().toBe()` / `assert`.

### 2. Not-empty assertions

**What**: Only checks output is non-empty. `return "X"` for all inputs passes.

**Fix**: Assert specific expected content (positive) AND absence of unwanted
content (negative).

### 3. Mock-reality drift

**What**: Mocks return what the test author expects, not what the real system
returns. Real API changes go undetected.

**Fix**: Add contract tests validating mock assumptions against reality. Use VCR
cassettes (recorded real responses) instead of hand-written mocks. Add at least
one E2E test against real infrastructure.

### 4. Integration tests mocking everything

**What**: Tests in `tests/integration/` that mock all external dependencies.
They're unit tests in disguise.

**Fix**: Either rename to `tests/unit/` (honest labeling) or add real
integration tests alongside. An integration test must have at least one real
external dependency.

### 5. Testing the mock

**What**: Test assertion verifies the mock's return value, not the function's
behavior. Test is tautological.

**Detection**: The asserted value is identical to `mock.return_value`.

**Fix**: Assert on the function's *transformation* of mock data, not the data
itself.

### 6. Skipped tests without expiry

**What**: `@skip("broken")` with no tracking issue. Accumulates silently.

**Fix**: Use `@skipif(condition, reason="...")` for legitimate skips. Require
issue links. Delete tests that will never be re-enabled.

### 7. Tests coupled to implementation

**What**: Tests that break on refactoring even when behavior is unchanged.
Verifying internal method call counts, SQL query strings, call order.

**Fix**: Test through public interfaces. Assert on outputs and side effects,
not internal mechanics.

### 8. Flaky tests

**What**: Tests that pass sometimes and fail sometimes.

| Cause | Fix |
|-------|-----|
| Wall-clock time | Inject clock or freeze time |
| Shared state | Reset in setUp/tearDown |
| Network | VCR cassettes or committed fixtures |
| Race conditions | Proper synchronization |
| Test ordering | `autouse` fixtures for cleanup |

### 9. Test pollution

**What**: Tests modify global state without cleanup.

**Fix**: Use `monkeypatch` (pytest), `afterEach` cleanup, fresh databases per
test, `try/finally` for plugin registration.

### 10. Quantity over quality

**What**: Chasing coverage percentage with weak tests. 100% coverage with 1
assertion per test catches fewer bugs than 80% with 5 assertions per test.

**Fix**: Track assertion density alongside coverage. Use mutation testing on
critical code. Make coverage informational, not blocking.

### 11. Missing sad path

**What**: Only happy-path tests. No tests for invalid input, errors, edge cases.

**Fix**: For every feature: test valid input, invalid input, boundary values,
empty/null, error conditions, and (where applicable) concurrency.

### 12. Stale VCR cassettes / snapshots

**What**: Recorded API responses or snapshots that no longer match reality.
Developers blindly update without review.

**Fix**: Delete and re-record periodically. Require explicit reviewer approval
for snapshot changes. Filter volatile data from cassettes.

### 13. Logical defense-in-depth (shotgun validation)

**What**: The same invariant is checked — and tested — at three or more
internal layers (controller, service, repository, …) when no trust boundary
sits between them. Every layer "defends" against the same failure that the
others already catch. "This should never happen" tests are the same antipattern
viewed from the other side: they only exist because the type permits the
state they're guarding against.

**Detection signals**:
- Tests like `test_X_rejects_null`, `test_X_rejects_empty`, `test_X_rejects_negative`
  repeated across several functions in the same module
- `assert x is not None` near the top of many functions whose parameter type is
  `T` (not `Optional[T]`)
- Comments saying "should never happen" / "defensive check" near assertions
- Builder lets you construct an invalid object, then a test asserts it is invalid
- Same `if not user_id` guard appears in 5 places

**Distinguish from**: defense-in-depth at a *trust boundary* (HTTP request
parsing + auth + authz; or parser + contract test + VCR cassette across an
external API). Each of those layers defends against a *different* failure
mode and is not this antipattern.

**Fix**:
1. Lift the invariant into a type at the outermost trust boundary it crosses
   (smart constructor, branded type, `NonEmpty`, `EmailAddress`, newtype).
2. Delete every downstream check and **its test**.
3. Replace per-function "rejects invalid input" tests with one parser test,
   ideally property-based with the *valid-or-absent* invariant.
4. If the language genuinely cannot express the invariant in the type system,
   keep exactly one runtime check at the outermost layer. Do not duplicate it.

See `references/correctness-by-construction.md` for language-specific patterns.
