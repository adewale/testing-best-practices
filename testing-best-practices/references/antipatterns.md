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
| Asserting through fault-masking code | Output-only assertion behind a `clamp`/`max(min())`/blanket `except`→default/`recover()`→zero; test passes even if the computation is wholly broken | P1 |

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
component-boundary integration tests alongside. An integration test should
exercise at least one real dependency or component boundary: an in-process
controller + service + repository can be integration even without a live
external service. Do not add network/database dependencies just to satisfy a
label.

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

**What**: Defense-in-depth applied to internal program logic in a
non-adversarial, already-typed context. Every layer defends against the
*same* failure mode in the *absence* of an adversary, instead of lifting
the invariant into a type, schema, or contract once at the boundary.

**Detection signals** (any one is enough; co-occurrence is diagnostic):
- **Repeated validation everywhere** — same `is None` / `!= ""` / `len > 0`
  guard at controller, service, and repo
- **Loose strings** flowing through the whole system instead of being
  parsed into a precise type at the boundary
- **Status enums duplicated across layers** — `OrderStatus` redeclared in
  DTO, service, repo, UI
- **Catch-all retries** — `for _ in range(3): try: ... except Exception:`
- **Silent fallback behavior** — `lookup() or default()` hiding failure
- **Post-hoc sanitizer patches** — regex stripping characters that should
  never have been representable
- **Runtime guards instead of state machines / types / schema constraints**
- **"This should never happen"** comments and assertions
- **Tests `test_X_rejects_null` / `_empty` / `_negative`** duplicated
  across many functions in one module
- **Builders that permit invalid objects** plus tests asserting the
  invalid objects are rejected

**Distinguish from**: defense-in-depth where each layer faces a
*different* failure mode or *different* adversary — hostile input, auth
boundaries, SSRF/XSS/injection, external system failure, rate limits,
retries, observability, recovery. Those layers and their tests are
not this antipattern.

**Fix**:
1. Lift the invariant into a type, schema, or sealed enum at the outermost
   trust boundary (smart constructor, branded type, `NonEmpty`,
   `EmailAddress`, newtype, state machine, schema constraint).
2. Delete every downstream check and **its test**.
3. Add the two tests that survive: (A) a property-based test that *proves*
   the invariant holds for valid inputs, and (B) a test that tries to
   construct each invalid state the type claims to forbid and asserts the
   construction fails. If (B) passes by *succeeding* in construction, the
   model has a hole — fix the model, not the test.
4. If the language cannot express the invariant in the type system, keep
   exactly one runtime check at the outermost layer and one test for it.

See `references/correctness-by-construction.md` for language-specific
patterns and the canonical lineage (Hoare → Dijkstra → Meyer →
Praxis/SPARK → seL4 → Minsky → King → LangSec).

### 14. Asserting through fault-masking code

A specialization of #2 worth naming: when the code under test silently absorbs
anomalies before they reach the output — `max(0, min(100, score))`, `except
Exception: return 0`, a Go `recover()`→zero, `value or DEFAULT`, or any
high-domain/range coercion — even a *specific* assertion on the final output
can't catch a fault. Voas & Miller's model: a fault must be **Executed**,
**Infect** the data state, and **Propagate** to output to be caught; a mask
breaks propagation, so the computation can be wholly broken and the test still
passes. (In #2 the *assertion* is weak; here the *SUT* destroys the signal.)

**Fix — surface the infection so it can propagate:**
1. The move other reviews miss: assert on the **pre-mask / internal value**, not
   the masked output — test the inner function directly, or assert the value
   *before* it is clamped/defaulted (Voas's "assertions in their place").
   Asserting the clamped output still can't see an infection that clamps to a
   valid value.
2. If a mask hides a genuine defect, surface it (raise/return an error) rather
   than testing around the silent recovery.
3. Run mutation testing on masked modules — surviving mutants are exactly the
   faults the mask hides (see `references/mutation-testing.md`).

**Restraint — when the mask is the specified behavior, don't flag it**: if
clamping volume to `[0,100]`, graceful degradation, a documented fallback, or
saturating arithmetic *is the contract*, that is correct code — test the
specified behavior directly (`set_volume(150) == 100`) and do **not** call it
fault-masking or recommend removing it. The smell is a mask hiding the
*unrelated* computation behind it, not a mask that is itself the feature.
