---
name: testing-best-practices
description: >
  Enforce testing best practices when writing, reviewing, or improving tests.
  Covers Red-Green TDD, property-based testing, real objects over mocks, test
  quality assessment (assertion density, not just coverage), E2E testing,
  contract tests, flaky test upgrades, and detection of sabotaged/skipped tests.
  Use when writing tests, reviewing test quality, fixing flaky tests, or when
  the user mentions TDD, testing, coverage, mocks, or test quality.
compatibility: Works with any language. Language-specific guidance in references/.
metadata:
  author: adewale
  version: "0.1"
---

# Testing Best Practices

## How to use this skill

This skill operates in four modes depending on what's needed:

1. **Write** — Writing new tests using Red-Green TDD
2. **Assess** — Evaluating existing test quality (not just coverage)
3. **Upgrade** — Improving weak, flaky, or low-quality tests
4. **Detect** — Finding tests that are skipped, sabotaged, or faking coverage

Before writing or modifying tests, determine the project's primary language and
read the matching reference file for framework-specific guidance:

- Python: read `references/python.md`
- TypeScript/JavaScript: read `references/typescript.md`
- Go: read `references/go.md`
- Rust: read `references/rust.md`

For antipattern detection and fixes, read `references/antipatterns.md`.
For deciding which test types to use, read `references/test-types.md`.
For advanced patterns (characterization testing, differential testing, mutation
testing, exhaustive testing, VCR cassettes, doc-sync testing, test data
builders), read `references/advanced-patterns.md`.

## Core principles

These apply to every language and every project.

### 1. Red-Green TDD

Always follow the Red-Green-Refactor cycle:

1. **Red** — Write a failing test that describes the desired behavior
2. **Green** — Write the minimum code to make the test pass
3. **Refactor** — Clean up while keeping tests green

For bug fixes: write the test that reproduces the bug BEFORE fixing it. This
test becomes a permanent regression test.

### 2. Test quality over quantity

A test suite's value is measured by what bugs it catches, not by coverage
percentage or test count.

**Assertion density**: Aim for 3+ meaningful assertions per test. Tests with
only 1 assertion — especially "not empty" checks — are weak.

**Both directions**: Every test should verify what SHOULD be present (positive)
AND what SHOULD NOT be present (negative). A sanitizer test must check that
safe content survives AND dangerous content is removed.

**Coverage as informational, not blocking**: Use coverage to find untested code
paths, not as a merge gate. Branch coverage is more valuable than line coverage.

### 3. Real objects over mocks

Prefer this hierarchy (best to worst):

1. **Real objects** — in-memory databases, real filesystems with temp dirs
2. **Purpose-built fakes** — implementations of real interfaces with history tracking
3. **Deterministic stubs** — hash-based stubs that produce consistent output
4. **Framework mocks** — `unittest.mock`, `vi.mock()` as last resort

When you must use mocks: write mock fidelity tests that verify mock behavior
matches the real system. Add contract tests that validate mock assumptions
in a real environment.

### 4. Property-based testing

Use property-based tests for any function that processes arbitrary input. Every
parser and normalizer needs at minimum a "never crashes on arbitrary input"
property test.

**Key invariant patterns**:

| Pattern | When to use | Example |
|---------|-------------|---------|
| Never crashes | Every parser/normalizer | `parse(arbitrary_string)` doesn't throw |
| Roundtrip | Serialization/encoding | `decode(encode(x)) == x` |
| Idempotent | Normalization/formatting | `f(f(x)) == f(x)` |
| Monotonic | Counting/measuring | `f(x + more) >= f(x)` |
| Conservation | Stripping/filtering | Output characters are a subset of input |
| Valid-or-absent | Parsing with fallback | Result is valid or `None`, never invalid |

**Boundary-first**: Configure generators to yield min/max boundary values
before random values. This catches edge cases in the first few iterations.

**Exhaustive testing**: When the state space is small (boolean flags, enums,
short arrays), use PBT to test *every* combination rather than sampling.
For a 5-element array, test all 120 permutations, all 32 subsets. See
`references/advanced-patterns.md` for the exhaustive testing pattern.

### 5. E2E testing

Every project with user-facing endpoints needs E2E tests. These catch bugs that
unit tests fundamentally cannot: wrong routes, broken integration contracts,
platform-specific behavior.

- Test the golden path first (most common user workflow)
- Gate infrastructure-dependent tests behind environment variables
- Limit to 5-15 E2E tests (supplement, don't replace unit tests)
- For platform-specific runtimes (Cloudflare Workers, Pyodide): E2E against real
  infrastructure is non-optional

### 6. Documentation-code sync

Test that documented features exist and working features are documented. Use
the code itself as the source of truth — inspect registries, command lists,
hook names — and verify docs match. The key pattern: parametrize over the
code's actual registry and assert each entry appears in docs.

Read `references/advanced-patterns.md` for the concrete pattern.

### 7. Characterization testing for legacy code

Before refactoring unfamiliar code, write tests that capture its *current*
behavior — not what you think it should do, but what it actually does. These
"characterization tests" become a safety net: if a refactoring changes behavior,
the test breaks and tells you exactly what changed.

Read `references/advanced-patterns.md` for the full pattern.

### 8. Differential testing

When reimplementing an algorithm, porting code, or building a simplified
version of a complex system, test against a trusted reference implementation.
Run the same inputs through both and assert outputs match. The reference IS
the oracle — no hand-calculated expected values needed.

Read `references/advanced-patterns.md` for examples.

### 9. Test data builders and fixtures

Test setup should express *intent*, not *structure*. Use factory functions or
builders so tests only specify the fields they care about:
```
article = ArticleFactory.create(title="Custom")  # all other fields default
user = make(a(User, with(role, "admin")))
```
Read `references/advanced-patterns.md` for the full pattern.

### 10. Test the sad path

For every happy-path test, write at least one sad-path test: invalid input,
missing data, permission denied, network failure. Use boundary values:
empty, null, max, min, zero, one-past-max.

Pre-build invalid input collections for validation testing:
```
INVALID_EMAILS = ['', 'notanemail', 'user@', '@domain.com']
CONTENT_LENGTHS = {EMPTY: '', MIN: 'a', MAX: 'a' * 280, OVERFLOW: 'a' * 281}
```

## Assess mode: evaluating test quality

When assessing existing tests, check these in order:

### Step 1: Detect sabotage

Search for tests being silently disabled. Read `references/antipatterns.md`
for the full detection signal list. Key signals:

- `@skip`, `@pytest.mark.skip`, `test.skip`, `xit`, `xdescribe` without conditions
- `t.Log` / `console.log` / `print` inside conditional blocks (logging not asserting)
- Empty test bodies or tests with no assertions
- Tests where the only assertion is `!= ""` / `toBeDefined()` / `toBeTruthy()`

### Step 2: Measure assertion density

Count assertions per test function. Flag files where the ratio is below 3.
Security-critical tests (XSS, auth, injection) with low assertion density are
P0 issues.

### Step 3: Check for mock-reality drift

Look for mocks that return hardcoded values. Ask: "If the real API changed,
would this test notice?" If no, flag it. Recommend VCR cassettes (recorded
real API responses) as a replacement for hand-written mocks — see
`references/advanced-patterns.md`.

### Step 4: Verify test tier integrity

- Files in `tests/integration/` that mock all dependencies are unit tests in
  disguise — flag them
- Files in `tests/unit/` that hit the network are integration tests — flag them
- E2E tests that mock the system under test are not E2E tests — flag them

### Step 5: Check coverage configuration

- Branch coverage (`branch = true`) should be enabled, not just line coverage
- Coverage should measure production code only (exclude test files)
- Coverage thresholds should be pragmatic (75-90%), not 100%

### Step 6: Recommend mutation testing for high-coverage, low-quality suites

When coverage is high (80%+) but assertion density is low, recommend mutation
testing to verify the tests actually catch bugs. See
`references/advanced-patterns.md` for tool recommendations per language.

## Upgrade mode: improving weak tests

When upgrading tests, prioritize by risk:

1. **P0**: Security tests with low assertion density or logging-not-asserting
2. **P1**: Tests with only "not empty" assertions — add specific content checks
3. **P2**: Flaky tests — replace `sleep()` with condition-based waiting, network
   tests behind markers, committed fixtures instead of live data
4. **P3**: Integration tests that mock everything — either rename to unit tests
   or add real integration tests alongside them

### Upgrading flaky tests

| Flake cause | Fix |
|-------------|-----|
| Time-dependent | Inject a clock or freeze time |
| Order-dependent | Reset shared state in setup/teardown |
| Network-dependent | Use VCR cassettes or committed fixtures |
| Race conditions | Add synchronization or use deterministic alternatives |
| Visual/font rendering | Skip in CI, run locally with `animations: 'disabled'` |

## Write mode: generating new tests

When writing tests for new code:

1. Determine which test types are needed (read `references/test-types.md`)
2. Read the language-specific reference for framework conventions
3. Follow Red-Green TDD: write the failing test first
4. Use test data builders/factories for setup — express intent, not structure
5. Use domain-specific assertion helpers for readability
6. Include regression test comments linking to the bug/issue being fixed

## Gotchas

- `t.Logf` in Go is NOT an assertion — it never fails the test. Use `t.Errorf`.
- `expect(x).toBeDefined()` passes for any non-undefined value including errors.
  Use specific value assertions.
- Coverage of 100% with 1 assertion per test is worse than 80% with 5
  assertions per test. Assertion density reveals test quality; coverage reveals
  test quantity.
- A mock that returns `{status: 200}` will pass even if the real API returns
  `{statusCode: 200}`. Mock shape must match reality.
- Visual regression tests that pass locally but fail in CI are usually font
  rendering differences, not real bugs. Skip in CI or use high pixel tolerance.
- `@pytest.mark.skip("broken")` without a tracking issue is tech debt that grows
  silently. Require `skipif(condition)` or delete the test.
- Integration tests that patch `http_fetch` are unit tests wearing a costume.
