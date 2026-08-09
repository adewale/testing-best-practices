---
name: testing-best-practices
description: >
  Enforce testing best practices when writing, reviewing, or improving tests.
  Covers TDD/red-green-refactor, property-based testing, real objects over
  mocks, correctness by construction, assertion quality, E2E/contract tests,
  flaky-test upgrades, mock-reality drift, mutation-style gap analysis, and
  sabotaged/skipped/weak tests. Use when writing tests, reviewing test quality,
  fixing flaky tests, improving coverage quality, or when the user mentions
  TDD, testing, coverage, mocks, invariants, types vs tests, defense in depth,
  or test quality.
compatibility: Agent Skills clients including Codex, OpenCode, Pi, Gemini CLI, and Claude Code.
metadata:
  author: adewale
  version: "0.3.1"
---

# Testing Best Practices

This skill has four modes:

1. **Write** — add tests or test-first bug fixes/features.
2. **Assess** — review an existing suite for quality, not just coverage.
3. **Upgrade** — strengthen weak/flaky/over-mocked tests.
4. **Detect** — find skipped, sabotaged, fake-coverage, or gap-prone tests.

## First 90 seconds

Before writing or changing tests:

1. **Detect language/framework** from repo files and adjacent tests.
2. **Read nearby tests** for naming, fixtures, builders, assertion style, and runner commands.
3. **Find the nearest validation command** before broad full-suite commands.
4. **Identify the risk boundary**: pure logic, internal component boundary, external API, UI/user journey, security boundary, or type/schema invariant.
5. **Classify the change and asset**: behavior change vs. structure/tidying, reusable library vs. throwaway probe, customer-facing rule vs. internal helper.
6. **Choose the smallest useful test tier** from `references/test-types.md`.
7. **Load only relevant references** from the matrix below.

If the language is unsupported by a dedicated reference, follow project conventions plus the generic principles here.

## Reference matrix

Always consider:
- Test type selection → `references/test-types.md`
- Anti-pattern detection → `references/antipatterns.md`

Language/framework references:
- Python / pytest / Hypothesis → `references/python.md`
- TypeScript/JavaScript / Vitest/Jest/fast-check/Playwright → `references/typescript.md`
- Go → `references/go.md`
- Rust → `references/rust.md`

Topical references by trigger:
- Legacy/refactor safety → `references/characterization-testing.md`
- Reimplementation, port, multi-language SDK, custom data structure with no reference, or approximate/probabilistic/ANN/ranking output → `references/differential-testing.md`
- Complex outputs, snapshots, transformation pipelines, save/load or migration roundtrips → `references/golden-file-testing.md`
- Time, timers, schedules, sleeps, flaky time tests, background threads/async work tests can only reach by sleeping → `references/deterministic-time.md`
- External APIs, recorded real responses, mock drift → `references/vcr-cassettes.md`
- CLI/plugin/docs registry sync → `references/doc-sync-testing.md`
- Suite that never fails, auditing tests you did not write, suspiciously green lanes, tests that may not run at all, or before deleting a test → `references/false-green.md`
- High coverage but escaping bugs → `references/mutation-testing.md`
- Small finite state spaces → `references/exhaustive-testing.md`
- Arithmetic/domain operators/laws → `references/mathematical-properties.md`
- Fixtures/builders/assertion helpers → `references/test-data-builders.md`
- Same invariant checked across layers, type-vs-test decisions, invalid states → `references/correctness-by-construction.md`

## Core principles

### Test behavior through public contracts

Good tests describe observable behavior: outputs, state transitions, side effects, rendered UI, persisted data, API contracts, or invariants. Avoid tests that break under behavior-preserving refactors: private methods, incidental call order, exact SQL strings, or broad mock choreography.

When a user brings examples, tables, bug reports, spreadsheet rows, or support cases, treat them as communication artifacts first and assertions second. Preserve the business language, then run the examples against the narrowest honest seam: usually the domain/service/API contract, not a full UI path for every business-rule row. UI/E2E tests should prove the wiring and golden path; rule tables should exercise the domain layer directly.

### Calibrate test investment to lifetime and change kind

Do not give every artifact the same test plan. Reusable libraries, parsers, payment/auth/security boundaries, migrations, and code that will be refactored deserve stronger regression/property/contract coverage. Throwaway probes, one-off research scripts, or generated exploration may need only a smoke check or no tests if the user accepts that lifecycle.

Separate **behavior changes** from **structure changes**. Behavior changes need tests that can fail for the new/changed behavior. Pure tidying/refactoring should ride an existing green suite; if no such suite exists, add characterization tests for the behavior you need to preserve before refactoring.

For a new service with no pipeline, start with a walking skeleton: the thinnest build/deploy/test slice. Track unfinished acceptance tests as visible in-progress items tied to a story/issue, not silent skips. Keep unit tests green; do not commit failing unit tests as proof.

### Use red-green-refactor when feasible

For bug fixes and new behavior, default to:

1. **Red** — add a focused test that fails for the current bug/missing behavior.
2. **Green** — implement the smallest change that passes.
3. **Refactor** — clean up while tests stay green.

The evidence matters. Separate **red evidence** (exact command and failing output before the fix) from **green evidence** (passing command/result after the fix). Only claim completed TDD/red-green-refactor when both were observed in order. If only a passing/green run is available, say tests were added and now pass, but the red phase was not observed/unverified; do not backfill a TDD claim from a green-only log. For exploratory prototypes, generated code, or user-scoped “tests only” tasks, stay within scope and state the deviation.

When practicing TDD, keep a visible **test list**. Park new edge-case ideas there instead of chasing them mid-cycle. If stuck, downshift: write the assertion first, extract a smaller child test, use a learning test for third-party APIs, or use a crash-test-dummy fake to trigger hard error paths. Choose Fake It, Triangulate, or Obvious Implementation according to uncertainty; never leave fake constants as the final behavior.

### Quality beats coverage

Coverage shows what ran; it does not prove bugs would be caught. Prefer branch coverage over line coverage and treat coverage as a map for finding untested paths, not a quality gate by itself.

Assertion count is a heuristic, not a law. Example-based behavior tests often need multiple meaningful assertions to verify structure, state, and negative cases. But a property test, table row, or exception test may have one excellent oracle. Flag weak sole assertions such as “not empty,” `toBeDefined()`, `toBeTruthy()`, `Assert.IsNotNull(result)`, or logging without assertions.

For sanitizers, validators, filters, auth/security checks, and transformations, verify both directions where applicable: dangerous/invalid content is rejected or removed, and safe/valid content is preserved.

### A green test is a claim; sabotage is the evidence

Coverage, test names, and grep show a test *ran*, not that it *can fail*. Tests that cannot fail, that never touch the code they name, or that no runner collects are invisible to coverage and test counts alike (signals under Detect mode). Before citing a test as coverage, break the code it names and confirm that specific test goes red.

Hold your own findings to the same standard. These detectors over-report badly: in one 250-file audit, linkage checks went 34 findings → 17 real, and a text scan 17 → 5 because 13 matches were the audit's own prose describing the antipattern. Report the sabotage that confirmed a finding, or mark it **unconfirmed**. A grep is evidence of neither coverage nor its absence. `references/false-green.md` has the catalog, and the look-alikes to leave alone.

### Prefer real behavior over mocks

Prefer, in order:

1. Real in-memory/local objects, temp dirs, in-memory databases, real parsers.
2. Purpose-built fakes that implement the same interface and can record history.
3. Deterministic stubs for controlled edge cases.
4. Framework mocks as a last resort.

Prefer visible state over call choreography: assert the saved row, emitted event, response body, file on disk, or a small logging fake's recorded effects. Do not mock values; construct them. Mock roles you own, not third-party libraries directly; wrap provider SDKs behind an owned interface and add a contract/VCR check for the real provider shape. For interaction tests, allow queries and expect commands: getters can be called freely, side-effecting commands are where expectations earn their keep.

### Use properties for broad input spaces

Use property-based testing when functions process arbitrary strings, numbers, binary data, parser inputs, encodings, orderings, or transformations. Common properties:

| Pattern | Example |
|---|---|
| Never crashes | parser handles arbitrary bytes/strings without throwing unexpectedly |
| Valid-or-error | result is a valid value or a structured error, never malformed |
| Roundtrip | `decode(encode(x)) == x` |
| Idempotent | `normalize(normalize(x)) == normalize(x)` |
| Conservation | filtered output contains only allowed input-derived data |
| Monotonic | adding input cannot decrease count/score where domain requires |
| Algebraic laws | associativity, commutativity, distributivity where operations claim them |

For small finite spaces, prefer exhaustive generation over sampling; see `references/exhaustive-testing.md`.

### Test error-handling paths, not just invalid input

Most critical production failures are shallow: they live in error-handling code that only runs when a dependency *already* failed — a disk-write error, a dropped connection, a timeout, a partial response. Empirical studies of catastrophic distributed-systems failures find the majority were reachable by simple tests that exercised those paths. So "sad path" means more than rejecting bad arguments: inject the downstream failure (a fake/stub that raises, an injected I/O error, a `side_effect` exception) and assert the system degrades correctly.

Assert the failure behavior the code *actually* has, not one you wish it had. Read the spec or observe the code to learn what a failure should do — propagate, retry, wrap, fall back, roll back — and test that. Do not invent a retry budget, a custom error type, or rollback semantics the contract never promised; that tests a fictional contract and is scope creep. If the intended failure behavior is unspecified, characterize what the code does today and flag the gap as a follow-up rather than designing new production behavior inside a test.

### Push internal invariants into types/schemas/contracts

Types and tests answer different questions:

- Types/schemas/contracts: “Can this invalid state exist?”
- Tests: “Does observable behavior match the spec?”

When an invariant is repeated across internal layers, consider lifting it to a boundary parser, smart constructor, schema, sealed enum, state machine, or database constraint. Before deleting checks or their tests, verify all of this:

- the context is internal and non-adversarial,
- the invariant is actually enforced by the type/schema/constructor,
- boundary tests cover hostile or malformed input,
- security/auth/external-failure layers defend different failure modes,
- production type changes are in scope or explicitly approved.

If user scope says “tests only” or “do not change production code,” add tests for the current API and list type/schema tightening as a follow-up.

### Test concurrent code under a race detector, and pin the concurrency contract

For code meant to be used by multiple goroutines/threads, sequential tests prove almost nothing. Drive the shared state from many workers released together (a start barrier maximizes contention) and run under a race detector or thread sanitizer (`go test -race`, ThreadSanitizer / `-fsanitize=thread`, repeated runs via `-count`). Treat a green concurrent test as weaker evidence than a sequential one — races are probabilistic.

Assert the invariant the API actually promises — no lost updates, a monotonic/linearizable count, compute-at-most-once — instead of logging whatever count you happened to observe and moving on. If the implementation can violate that contract (e.g. it computes outside the lock, so two callers double-compute), that is a defect to surface with a failing test or an explicit flag, not a `t.Logf` that quietly bakes the race into the expected behavior.

## Mode workflows

### Write mode

1. Read adjacent tests/config and load the relevant language reference.
2. Choose test tier from `references/test-types.md`.
3. For bugs/new behavior, add the failing regression test first when feasible.
4. Convert user/customer examples into readable test cases without forcing every example through the UI.
5. Use builders/factories/helpers where setup noise hides intent; test custom helpers when they become a mini-DSL.
6. Prefer user-facing/public interfaces over internals.
7. Pin nondeterminism: time, randomness, network, filesystem, order.
8. Run nearest tests, then broader checks when practical.

For transformations or complex generated output, use golden files with explicit review discipline; see `references/golden-file-testing.md`. For external APIs, prefer recorded real fixtures/cassettes or contract checks over live CI calls; see `references/vcr-cassettes.md`.

### Assess mode

Report evidence by severity and include positive observations. Check:

1. **Sabotage / false confidence**: skipped/focused tests, no assertions, logging-not-asserting, commented-out assertions, always-true assertions, self-comparisons, assertions swallowed by their own `catch`, and suites whose case list can be empty.
2. **Linkage and scheduling**: tests that never import the module they name or re-implement it, and test files no runner collects or that sit in a `continue-on-error` lane. See `references/false-green.md`.
3. **Oracle strength**: weak sole assertions, missing negative/error/state/structural assertions, tautologies.
4. **Mock-reality drift**: hardcoded mocks that would not notice real API/schema changes.
5. **Tier integrity**: unit tests hitting live network, integration tests mocking every boundary they claim to exercise, E2E tests that mock the system under test.
6. **Determinism**: sleeps, wall-clock time, unseeded random, order dependence, global state leaks.
7. **Coverage quality**: branch coverage, mutation/gap analysis for high-coverage suites with escaping bugs.
8. **Invariant placement**: repeated internal validation that should be a type/schema/contract.
9. **Lifecycle fit**: throwaway probes over-tested, reusable assets under-tested, or structure-only changes getting behavior-test theater.
10. **Example quality**: business examples buried in UI scripts, unreadable fixtures, or helpers that form a DSL but have no tests of their own.

Confirm findings by sabotage before reporting them as defects, and say which ones remain unconfirmed.

### Upgrade mode

Prioritize by risk:

1. **P0**: security/auth/injection/sanitizer tests with weak or missing assertions.
2. **P1**: tests that only assert not-null/not-empty/truthy.
3. **P2**: flaky tests: sleeps, live network, wall-clock, order coupling.
4. **P3**: mock-heavy “integration” tests and implementation-coupled mocks.
5. **P4**: fixture noise, duplication, unclear names, missing builders.

Common upgrades:
- Replace `sleep()` with virtual time, injected clocks, or condition-based waits.
- Replace live API calls with recorded cassettes or committed fixtures.
- Replace broad mocks with fakes, contract tests, or assertions on public behavior.
- Replace repeated object literals with builders that keep behavior-specific fields explicit.

### Detect mode

Use concrete search signals from `references/antipatterns.md`:

- `@skip`, `skip`, `skipif` without real condition, `test.only`, `fit`, `xit`, `xdescribe`.
- `print`, `console.log`, `t.Log`, `Debug.WriteLine` used instead of assertions.
- Assertion-free tests or only truthy/not-empty/not-null checks.
- `sleep`, `waitForTimeout`, `Thread.Sleep`, `Task.Delay` for synchronization.
- Try/catch swallowing exceptions.
- Mock return values identical to assertions.
- Global state/env/registry mutations without cleanup.
- Snapshot/golden updates without diff review.
- Self-comparisons (`assertEqual(x, x)`), `expect(true).toBe(true)`, assertions inside `try` with a `catch` that accepts any error, `.catch(() => {})`, `skip(true, ...)`, guards false on every run.
- Case lists read from a directory/glob with no floor assertion on the count.
- Test files no runner collects, `continue-on-error` CI jobs, and tests that never import the module their name claims (or define their own copy of it).

Strip comments and docstrings before matching — prose describing an antipattern matches it — then confirm each hit by sabotage before calling it a defect.

## Validation loop

After writing or changing tests:

1. Run the nearest relevant test command.
2. If bug-fix TDD was intended, report red evidence separately from green evidence; if the pre-fix failing run was not observed, call the red phase unverified instead of claiming completed TDD.
3. Scan the changed tests for weak sole assertions, skips/focus markers, logging-not-asserting, sleeps, live network, and implementation-detail coupling.
4. Confirm each new test can fail: verify the runner actually collected it (counts went up), and that it goes red when the behavior it names is broken. A test that passes before the fix is not a regression test.
5. For security/transformation tests, verify both rejection/removal and preservation.
6. For invariant work, verify both tactics where relevant: property/invariant proof and invalid-state reachability.
7. If validation is blocked, report the exact command, failure, and next-best check. Never claim tests passed without running them.

## Final report contract

End testing work with:

```md
Tests changed/assessed:
Behavior covered:
Commands run:
Results:
TDD evidence (if claimed):
Gaps / risks:
Follow-ups:
```

Keep it concise, but make validation and remaining risk auditable.
