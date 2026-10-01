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
| Logic in tests / over-DRY test code | Expected values built by concatenation/arithmetic or from the SUT's own constants; `for`/`if` in test bodies; fixtures mutated in `setUp*` far from the assertion | P1 |
| Always-green or dead gate | `\|\| true`, `continue-on-error`, `scan --baseline`, `::warning::` + skip, coverage/mutation configured but never run, CI not executing at all | P0 |
| Vacuous pass | Assertions only inside a loop over possibly-empty results; `violations == []` with no non-empty check; scanner run over zero targets; test imports nothing from the SUT | P1 |
| Source/config-text assertions | `readFileSync`/`read_text` of `src/`, CSS, or workflow files followed by `toContain`/`assertIn`/`match`; pinned render hashes | P2 |
| Permissive environment | Regex-dispatched SQL fakes, hand-built schemas, bindings missing from the test config, fakes that never fail | P1 |
| Hidden retries / timeout ratchet | Helper loops retrying 5xx; `retries: CI ? n : 0`; repeatedly raised global timeouts; `isCI ? a : b` budgets | P2 |
| Self-authored oracle | Goldens, approvals, or eval questions written by the same actor in the same change as the code they judge | P2 |
| Mutation program without a decision | Calendar-scheduled mutation over unchanged code; round-number or "no survivors" floors; private helpers exported, production markers added, or tie-breaks and cache internals pinned to kill a survivor | P2 |

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

**Fix**: When a real engine can run in-process or locally (SQLite loaded from
migrations, workerd, Pyodide in Node, node-canvas), delete the mock and use it.
For doubles you must keep, take expected values from the real service — recorded
responses, VCR cassettes, or a local emulator run — never from the mock author's
belief. A "fidelity" test whose name says one thing (`changes_0`) while asserting
another (`changes == 1`) pins fiction; question the expected value. Flag contract
tests whose target double no longer exists. Add at least one test against real
infrastructure.

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

Related shapes: `test.skip()` called inside a failure branch (the test skips
exactly when the feature breaks); an imperative `pytest.xfail()` left in a
known-bug test after the fix (a regression reports green); a capability skip
(`skipIf(!resource)`, build tag, OS-only baseline) that no CI lane ever satisfies.
A gated test is real only if some lane provides the resource, selects the test,
and fails when it skips — see `references/gate-integrity.md`.

### 7. Tests coupled to implementation

**What**: Tests that break on refactoring even when behavior is unchanged.
Verifying internal method call counts, SQL query strings, call order.

**Fix**: Test through public interfaces. Assert on outputs and side effects,
not internal mechanics.

Agent-era shapes of the same smell:
- **Source- or config-text assertions**: reading `src/`, CSS, docs, or workflow
  YAML and asserting substrings or regexes. They break on innocent edits and pass
  on real rendering or runtime bugs. Assert computed style, rendered output, or
  parsed-structure invariants ("every step after a precondition is gated on it"),
  or extract a seam.
- **Hash-only goldens**: pinned render or op-stream hashes give no reviewable diff
  and churn on every art change; prefer structural or perceptual goldens with a
  visible diff (see `references/golden-file-testing.md`).
- **E2E through a test facade**: driving the app through `window.__test` hooks
  proves the facade works, not the user journey; keep a golden path on trusted
  input.

### 8. Flaky tests

**What**: Tests that pass sometimes and fail sometimes.

| Cause | Fix |
|-------|-----|
| Wall-clock time | Inject clock or freeze time |
| Shared state | Reset in setUp/tearDown |
| Network | VCR cassettes or committed fixtures |
| Race conditions | Proper synchronization |
| Test ordering | `autouse` fixtures for cleanup |
| Oversized SUT | Shrink the tier/SUT first — size (deps, processes, RAM) predicts flakiness better than tool choice |
| Retry/quarantine reliance | Root-cause instead; retries mask real races and erode trust in red. Required lanes run with `retries: 0` and assert zero flaky results; helper-level retry loops count too |
| Wall-clock budgets in the unit tier | `expect(elapsed).toBeLessThan(n)` fails under contention; assert bounded work or move deadline contracts to an isolated lane with headroom or an injected clock |
| Timeout ratchet | Repeatedly raising a global timeout, or `isCI ? a : b` budgets, means heavy work is in the wrong tier; move the tests, don't raise the budget |

### 9. Test pollution

**What**: Tests modify global state without cleanup.

**Fix**: Use `monkeypatch` (pytest), `afterEach` cleanup, fresh databases per
test, `try/finally` for plugin registration.

### 10. Quantity over quality

**What**: Chasing coverage percentage with weak tests. Execution coverage says
what ran, not what would be caught.

**Fix**: Judge oracle strength, not counts: a test with weak sole assertions is
weak whatever the coverage. To find the weak ones, seed a fault in the code a
test claims to cover and see whether it fails (cheapest first:
`references/gate-integrity.md` §5). Make coverage informational, not blocking, and check its denominator (thresholds only
see files the tests load unless `include` lists the source tree).

**Never turn a heuristic into a quota.** A per-file or per-test assertion minimum
(for example "at least 3 per test") gets met with `isinstance` and not-empty checks,
and the same happens to coverage and mutation score floors. Use counts only to
find tests to read.

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
1. Prefer a smaller public seam or explicit observable diagnostic before
   reaching into private state. If the pre-mask value is a stable, approved
   testability seam, assert it directly; asserting only the clamped/defaulted
   output still cannot see an unrelated infection that the mask absorbs.
2. If a mask hides a genuine defect, surface it (raise/return an error) rather
   than testing around the silent recovery.
3. Run focused mutation testing on masked modules. A survivor is a triage
   question—it may expose a hidden fault, but may also be equivalent, irrelevant,
   or specified masking (see `references/mutation-testing.md`).

**Restraint — when the mask is the specified behavior, don't flag it**: if
clamping volume to `[0,100]`, graceful degradation, a documented fallback, or
saturating arithmetic *is the contract*, that is correct code — test the
specified behavior directly (`set_volume(150) == 100`) and do **not** call it
fault-masking or recommend removing it. The smell is a mask hiding the
*unrelated* computation behind it, not a mask that is itself the feature.

### 15. Logic in tests / over-DRY test code

**What**: Test code optimized like production code. Signals: expected values
built by concatenation/arithmetic or from the SUT's own constants (`assert
url == BASE + "/users/" + name` — the expectation can share the SUT's bug
and stay green); `for`/`if` in a test body deciding which assertion runs; a
shared fixture mutated in `setUp*`/module scope far from the assertion that
depends on it; helpers that hide which inputs a test's outcome depends on.

**Why it matters**: Tests have no tests of their own. An abstraction that
breaks (or shares the SUT's bug) inside test code has nothing to catch it,
and a reader cannot verify an expectation without chasing helper
definitions. Cause and effect should sit together, even at the cost of
duplicated setup — test code leans DAMP (descriptive and meaningful
phrases), not DRY.

**Fix**: One behavior per test; setup local and explicit next to its
assertion, duplicated when necessary; expected results derived independently
of the SUT (often literals for simple examples); loops replaced by named
parameterized rows with no branching in the row body.

**Restraint — the sanctioned DRY**: value-construction builders/factories
with reasonable defaults are correct *when every field an assertion depends
on is set explicitly in the test* (see `references/test-data-builders.md`).
DAMP targets hidden behavior, not value helpers; do not inline a builder's
boilerplate into every test. Named-row table tests (e.g. Go's
`t.Run(tt.name, ...)`) are fine.

### 16. Always-green and dead gates

**What**: A check that cannot fail or is not running: `|| true`,
`continue-on-error`, baseline updaters used as checks (`detect-secrets scan
--baseline` exits 0 and absorbs the new secret), error-swallowing shell, deploys
that `::warning::`-skip and end green, E2E that is green when secrets are missing,
scanners run over an empty directory, coverage thresholds never invoked, CI that
stopped executing (quota, billing, missing runner) while pushes continue.

**Fix**: Make each gate fail closed and prove it by planting a violation in a
scratch copy. An advisory job needs an owner, a change-based trigger, a
notification, and an exit plan. A diagnostic nobody reads is a cost, not a dead
gate: run it on demand or delete it rather than adding a threshold. See
`references/gate-integrity.md`.

### 17. Vacuous passes

**What**: The assertion holds because nothing was checked: assertions only inside
a loop over output that can be empty; "every row satisfies P" over zero rows;
`Math.min(...[])` or other zero-sample aggregates passing a threshold; a test or
script that reimplements the logic and imports nothing from the SUT; tests of code
with no non-test importer.

**Fix**: Assert the precondition (non-empty, HTTP 200, font loaded, n > 0) before
the universal claim and print the denominator. Import the real code. Check that the
subject has a production importer.

### 18. Permissive environment (yes-man doubles)

**What**: The test environment enforces fewer constraints or runs fewer branches
than production: fake databases that ignore `WHERE` clauses or accept wrong bind
counts, hand-written schemas that drift from migrations, bindings omitted from the
test config (so `env.AI && ...` paths never run), fresh-only databases, tiny
fixtures. A variant: production code gains a branch whose only job is to keep a
test double working.

**Fix**: Load schemas from migrations, run a real local engine, add fakes for
every binding production uses, and enumerate capability-gated branches so none
hides. Remove branches that are unreachable with the real dependency.

### 19. Self-authored oracles

**What**: Goldens approved, eval questions written, or expected values chosen by the
same actor in the same change as the code they judge. The suite then measures
agreement with its author, not correctness.

**Fix**: Treat such goldens as characterizations until independently reviewed;
write eval cases before the change or from users' own words; report a trivial
baseline (e.g. title-keyword matching for a retrieval eval) next to the real score
so a non-discriminating eval is visible.

### 20. Silent tier downgrade

**What**: A cleanup or "improve test quality" change replaces a real-engine test
(SQLite, workerd, browser) with a mock or string assertion, or deletes it, without
saying so. Lessons written down the week before are undone.

**Fix**: When removing or replacing tests, list them by tier and keep the tier or
stronger. A lesson or postmortem counts only when a check enforces it.

### 21. Mutation program without a decision

**What**: Mutation testing run as a standing program rather than to answer a
question about specific tests. Signals:
- scheduled runs over unchanged code that repeat the same score;
- floors copied from round numbers, set above the measured score, or taken
  from a loaded local run;
- "no surviving mutants" as a definition of done, or every survivor treated as
  a release blocker;
- private helpers exported, production code marked, or implementation details
  (tie-breaks, epsilons, cache internals) pinned only to kill a survivor;
- tests that enforce enrollment in the mutation lane;
- a mutation tool kept as a dependency that nothing runs;
- source-text "sabotage proofs" for regex change-detectors, which only test the
  regex.

**Why it hurts**: The recurring lanes cost runner-hours and, more lastingly,
couple tests to implementation. The survivors they surface are often
equivalent. Real findings come from cheap one-off checks.

**Fix**: Seed faults cheapest first (`references/gate-integrity.md` §5), then
use a tool scoped to changed code, on demand. Classify a survivor that is
equivalent, unreachable through the public interface, or performance-only; do
not chase it. Delete lanes that have never changed a decision.
