# Lessons from github.com/adewale Repositories

> Extracted from scanning ~30 repositories across Go, Python, TypeScript, and Vue.
> Date: 2026-04-11

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Testing Ecosystem Overview](#testing-ecosystem-overview)
3. [Property-Based Testing](#property-based-testing)
4. [Mock Fidelity and Contract Testing](#mock-fidelity-and-contract-testing)
5. [Test Quality over Quantity](#test-quality-over-quantity)
6. [E2E Testing](#e2e-testing)
7. [Screenshot and Visual Regression Testing](#screenshot-and-visual-regression-testing)
8. [Real Objects over Mocks](#real-objects-over-mocks)
9. [Flaky Test Patterns](#flaky-test-patterns)
10. [Test Architecture Patterns](#test-architecture-patterns)
11. [Coverage Configuration](#coverage-configuration)
12. [Skipped and Sabotaged Tests](#skipped-and-sabotaged-tests)
13. [Testability and Refactoring for Testability](#testability-and-refactoring-for-testability)
14. [CI/CD Integration](#cicd-integration)
15. [Anti-Patterns Observed](#anti-patterns-observed)

---

## Executive Summary

The adewale repos demonstrate a mature, evolving testing philosophy. Key themes:

- **Property-based testing is used extensively** across TypeScript (fast-check) and Python (Hypothesis), not just for utility functions but for domain-specific invariants.
- **Mock fidelity is a first-class concern**: dedicated `test_mock_fidelity.py` files and Playwright-based "mock contract tests" validate that mocks behave like the real thing.
- **Test quality is measured and audited**: assertion density, assertion quality audits, and mutation testing readiness assessments exist in multiple repos.
- **E2E tests against real infrastructure** are treated as non-optional for platform-specific runtimes (Cloudflare Workers, Pyodide FFI).
- **Three-tier test architecture** (unit → integration → E2E) is the standard pattern, with clear rules about what each tier catches.
- **Real objects are strongly preferred**: the tasche project has extensive documentation about how mock-based tests masked production bugs.

---

## Testing Ecosystem Overview

| Repo | Language | Unit Framework | PBT | E2E | Coverage Config |
|------|----------|---------------|-----|-----|-----------------|
| atlas | TypeScript | Vitest + jsdom | fast-check | Playwright (5 device profiles) | -- |
| flux-search | TypeScript | Vitest | fast-check | -- | -- |
| embed.oshineye.dev | TypeScript | Vitest | -- | Playwright | -- |
| tasche | Python | pytest + pytest-asyncio | Hypothesis | httpx against staging | pytest-cov, branch=true |
| skill_scanner | Python | pytest | -- | -- | 80% fail_under |
| rogue_planet | Go | testing + httptest | -- (table-driven) | go test -tags=network | 75% target |
| geist_fabrik | Python | pytest + pytest-cov | -- | Integration tests | branch=true, --cov-branch |
| planet_cf | Python | pytest | -- | Playwright + real Workers | -- |
| bobbin | TypeScript | Vitest + @cloudflare/vitest-pool-workers | -- | -- | -- |
| qc | Python | Custom QuickCheck | qc itself | -- | -- |
| gaetestbed | Python | unittest mixins | -- | -- | -- |

### Notable: The `qc` Repo

This is a custom Python QuickCheck implementation predating Hypothesis (2012). It provides:
- Generator-based random data: `integers()`, `floats()`, `lists()`, `tuples()`, `dicts()`, `unicodes()`, `objects()`
- **Boundary-first testing**: generators yield low/high bounds before random values
- A `@forall` decorator for property-based test specification
- Demonstrates that the owner has been thinking about property-based testing since at least 2012

---

## Property-Based Testing

### TypeScript (fast-check)

**flux-search** and **atlas** show the most sophisticated PBT usage.

#### Pattern 1: Safety Properties — "Never throws on arbitrary input"

```typescript
// flux-search: properties.test.ts
it('never throws on arbitrary input', () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      const result = parseQuery(input);
      expect(result).toBeDefined();
      expect(result.freeText).toBeDefined();
    }),
    { numRuns: 500 }
  );
});
```

**Lesson**: Every parser/normalizer should have a "never crashes" property test. This is the cheapest, highest-value PBT pattern.

#### Pattern 2: Domain Invariants — "Output must satisfy business rules"

```typescript
// flux-search: properties.test.ts
it('year filter is always in valid range or undefined', () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      const result = parseQuery(`year:${input}`);
      if (result.filters.year !== undefined) {
        expect(result.filters.year).toBeGreaterThanOrEqual(2000);
        expect(result.filters.year).toBeLessThanOrEqual(2100);
      }
    }),
    { numRuns: 200 }
  );
});
```

**Lesson**: "Valid or absent" is a powerful invariant pattern. Parse functions should either produce valid output or gracefully produce nothing.

#### Pattern 3: Structural Invariants — "Indices are sequential, IDs are consistent"

```typescript
// flux-search: properties.test.ts
it('chunk indices are sequential starting from 0', () => {
  fc.assert(
    fc.property(fc.string({ minLength: 1 }), fc.option(fc.string()), (title, body) => {
      const chunks = chunkIssue('issue-1', title, null, body ?? null);
      for (let i = 0; i < chunks.length; i++) {
        expect(chunks[i].chunk_index).toBe(i);
      }
    }),
    { numRuns: 200 }
  );
});
```

#### Pattern 4: Data Integrity — "Neighbor symmetry must hold"

```typescript
// atlas: data.property.test.ts
it('forAll(a, adjacent b): neighbor symmetry', () => {
  for (const el of allElements) {
    for (const neighborSym of el.neighbors) {
      const neighbor = getElement(neighborSym)!;
      expect(neighbor.neighbors).toContain(el.symbol);
    }
  }
});
```

**Lesson**: Bidirectional relationships must be tested for symmetry. This pattern catches data corruption that example-based tests miss.

#### Pattern 5: PBT-Driven Bug Finding — "Audit-targeted properties"

```typescript
// flux-search: pbt-audit.test.ts
// "PBT tests targeting the 5 HIGH-priority bugs found by the test audit."
it('output never contains script/style/nav/footer/header tags', async () => {
  await fc.assert(
    fc.asyncProperty(fc.string(), fc.string(), async (safeContent, tagContent) => {
      const html = `<script>${tagContent}</script><p>${safeContent}</p>`;
      mockFetch.mockResolvedValue(new Response(html, { status: 200 }));
      const result = await fetchPage('https://example.com/p/test');
      if (result) {
        expect(result.markdown).not.toMatch(/<script/i);
      }
    }),
    { numRuns: 50 }
  );
});
```

**Lesson**: PBT is not just for green-field code. After an audit identifies bugs, write property tests that encode the invariants those bugs violated.

### Python (Hypothesis)

**tasche** has the most comprehensive Hypothesis usage.

#### Pattern 6: Independent Oracles

```python
# tasche: test_property.py
@given(text=st.text())
@settings(max_examples=200)
def test_content_preserved(self, text: str) -> None:
    """Joining all chunks must produce the same words as the input.
    Uses whitespace normalisation as an independent oracle."""
    chunks = chunk_text(text)
    joined = " ".join(chunks)
    assert " ".join(joined.split()) == " ".join(text.split())
```

**Lesson**: Use whitespace normalisation or character counting as independent oracles to verify content preservation without re-implementing the function under test.

#### Pattern 7: Idempotency Properties

```python
# tasche: test_property.py
@given(text=st.text())
def test_idempotent(self, text: str) -> None:
    """Applying strip_markdown twice gives the same result as once."""
    once = strip_markdown(text)
    twice = strip_markdown(once)
    assert twice == once
```

#### Pattern 8: Monotonicity Properties

```python
# tasche: test_property.py
@given(base=st.text(min_size=1).filter(lambda t: t.strip()),
       extra_words=st.lists(st.text(...), min_size=1))
def test_monotonic_with_more_words(self, base, extra_words):
    """Adding more words should not decrease the estimated duration."""
    longer = base + " " + " ".join(extra_words)
    assert _estimate_duration(longer) >= _estimate_duration(base)
```

**Lesson**: Monotonicity is an underused invariant. For counting/measuring functions, "more input = equal or greater output" catches off-by-one and truncation bugs.

#### Pattern 9: "No New Characters" — Conservation Laws

```python
# tasche: test_property.py
@given(text=st.text())
def test_no_new_characters(self, text: str) -> None:
    """Every alphanumeric character in the output must come from the input."""
    from collections import Counter
    result = strip_markdown(text)
    output_chars = Counter(ch for ch in result if ch.isalnum())
    input_chars = Counter(ch for ch in text if ch.isalnum())
    for ch, count in output_chars.items():
        assert count <= input_chars.get(ch, 0)
```

**Lesson**: "Output is a subset of input" is a powerful conservation-law property for any transformation that strips/removes content.

---

## Mock Fidelity and Contract Testing

### The Mock-Reality Gap (Lesson from tasche)

From tasche's LESSONS_LEARNED.md, Lesson #38:

> "Mock-based tests verify the test author's mental model of the system, not the system itself. When the mental model is wrong (wrong URL path, wrong status code for duplicates), the mock obligingly returns whatever the test expects."

This is the single most important testing lesson across all the repos.

### Pattern: Mock Contract Tests (atlas)

atlas has dedicated Playwright E2E tests (`tests/e2e/mock-contracts.spec.ts`) that validate assumptions made by jsdom mocks:

```typescript
// atlas: mock-contracts.spec.ts
// "Lesson #2: computeLineHeight used layout(ref, 9999, 0) which returned 0,
//  but the unit test mock returned { height: 20 } — masking the bug."

test('text measurement returns positive height for real fonts', async ({ page }) => {
  await page.goto('/');
  const result = await page.evaluate(async () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = '16px system-ui';
    const metrics = ctx.measureText('The quick brown fox');
    return {
      width: metrics.width,
      ascent: metrics.fontBoundingBoxAscent ?? 0,
      descent: metrics.fontBoundingBoxDescent ?? 0,
    };
  });
  // The mock assumes line height ~20px for 16px font.
  // Verify that real line height is in a reasonable range.
  const lineHeight = result.ascent + result.descent;
  expect(lineHeight).toBeGreaterThan(10);
  expect(lineHeight).toBeLessThan(40);
});
```

**Lesson**: When your unit tests use mocks that return fixed values, add contract tests in a real browser that verify the mock's assumptions still hold.

### Pattern: Mock Fidelity Tests (tasche)

tasche has `tests/unit/test_mock_fidelity.py` that validates the mock infrastructure itself:

- Verifies MockD1 parameter binding catches mismatches
- Verifies MockKV TTL tracking works correctly
- Verifies MockR2 list pagination matches the real API contract
- Verifies MockQueue message storage format

**Lesson**: If your test infrastructure includes custom mocks (as opposed to using a mocking framework), write tests *for* those mocks. A broken mock silently passes everything.

### Pattern: Metrics Contract Tests (atlas)

```typescript
// atlas: metrics-contract.test.ts
// "If a component changes its font or text format, this test will fail
//  until the precompute script is updated to match."

it('has metrics for all 118 elements', () => {
  expect(Object.keys(metrics.elements)).toHaveLength(118);
});

it('every element has all required metric fields', () => {
  const required = ['identityWidth', 'nameWidth14', 'chipWidth11'];
  for (const [sym, m] of Object.entries(metrics.elements)) {
    for (const field of required) {
      expect(m[field]).toBeGreaterThan(0);
    }
  }
});
```

**Lesson**: When you precompute data that rendering depends on, write contract tests that verify the precomputed data matches the assumptions of the consuming code.

---

## Test Quality over Quantity

### Assertion Density (rogue_planet)

rogue_planet has a formal `TEST_ASSERTION_QUALITY_AUDIT.md` that grades test files:

| Quality | Ratio | Example |
|---------|-------|---------|
| Excellent | 8-11 assertions/test | crawler_test.go (9.2), normalizer_realworld_test.go (11.0) |
| Good | 5-7 assertions/test | config_test.go (6.0) |
| Moderate | 3-4 assertions/test | generator_test.go (3.3) |
| **Weak** | **1 assertion/test** | **normalizer_xss_test.go (1.0)** |

**Critical Finding**: The XSS security tests — arguably the most important tests — had the lowest assertion density.

### Anti-Pattern: `t.Log` instead of `t.Error`

```go
// WRONG: This test always passes, even when the assertion fails
if !strings.Contains(output, tt.want) {
    t.Logf("Output may not contain expected string %q", tt.want)  // Should be t.Errorf!
}
```

**Lesson**: Logging is not asserting. A test that logs a failure instead of failing is worse than no test — it provides false confidence.

### Anti-Pattern: "Not Empty" Assertions

```go
// WEAK: Function could return "X" for all inputs and this passes
if output == "" {
    t.Error("Sanitizer returned empty string for malformed HTML")
}
```

**Better**:
```go
// STRONG: Verifies both presence of safe content AND absence of dangerous content
if !strings.Contains(output, "<p>") {
    t.Error("Paragraph tag incorrectly removed")
}
if strings.Contains(output, "<script>") {
    t.Error("Script tag not removed")
}
```

**Lesson**: Every assertion should verify a specific expected outcome, not just "something happened." Test both what should be present AND what should be absent.

### Quality Assessment Framework

From the audit, a good test should:
1. **Verify dangerous content is removed** (negative assertions)
2. **Verify safe content is preserved** (positive assertions)
3. **Verify structure** (structural assertions)
4. **Use `t.Error`/`assert` not logging** for all checks

---

## E2E Testing

### E2E Against Real Infrastructure (tasche)

tasche's E2E tests run against a live staging Cloudflare Worker:

```python
# tasche: test_integrations.py
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="Requires RUN_E2E_TESTS=1 and live staging",
    ),
]
```

These tests caught two bugs that hundreds of unit tests missed:
1. **Wrong search endpoint path** — unit tests used `/api/articles/search`, real endpoint was `/api/search`
2. **Wrong duplicate URL behavior** — unit tests asserted 409, real code returned 201

**Lesson**: "For platform-specific runtimes, E2E tests against real infrastructure are not optional — they are the only tier that validates the actual contract between your code and the platform."

### E2E with Playwright (atlas, embed.oshineye.dev, planet_cf, tts-playground)

atlas has the most sophisticated Playwright setup:

- **5 device profiles**: desktop, mobile, iPhone 15 Pro Max, iPhone 16 Pro Max, iPhone 17
- **35+ E2E test files** covering navigation, performance, accessibility, layout
- **Visual regression tests** with pixel-diff comparison
- **User journey tests** that exercise complete workflows

#### E2E Test Categories Found Across Repos

| Category | Example Repo | What It Catches |
|----------|-------------|----------------|
| User journey flows | tts-playground, planet_cf | Broken workflows |
| Visual regression | atlas | Layout/style regressions |
| Mock contract validation | atlas | Mock-reality drift |
| API contract | tasche | Wrong endpoints, wrong status codes |
| Accessibility (WCAG) | atlas | Contrast, keyboard nav issues |
| Performance | atlas | Layout shift, load time |
| Responsive layout | atlas | Mobile breakpoint bugs |
| Search accuracy | planet_cf | Relevance regressions |
| UI interaction | planet_cf | Button/form behavior |

### E2E Test Organization Pattern

```
tests/
  unit/          # Pure logic, mocked dependencies
  integration/   # Multiple components, some mocks
  e2e/           # Real browser or real infrastructure
    conftest.py  # E2E-specific fixtures
```

Gated by environment variables:
- `RUN_E2E_TESTS=1` for infrastructure tests
- `process.env.CI` for skipping visual regression in CI

---

## Screenshot and Visual Regression Testing

### atlas Visual Regression Approach

```typescript
// atlas: visual-regression.spec.ts
test.skip(!!process.env.CI, 'Visual regression tests are skipped in CI');

test('folio layout', async ({ page }) => {
  await page.goto('/elements/Fe');
  await page.waitForSelector('[data-testid="data-plate"]');
  await waitForAnimations(page);

  const main = page.locator('.folio-main');
  await expect(main).toHaveScreenshot('folio-Fe-desktop.png', {
    maxDiffPixelRatio: 0.01,
    animations: 'disabled',
  });
});
```

**Key decisions**:
- **Skipped in CI**: Font rendering differs between macOS, Linux CI, and Chromium versions
- **Animations disabled**: Prevents timing-dependent pixel differences
- **Component-level screenshots**: Capture `.folio-main` not full page (reduces noise)
- **Named snapshots per device**: `folio-Fe-desktop.png` vs `folio-Fe-mobile.png`
- **Low tolerance**: `maxDiffPixelRatio: 0.01` (1% pixel diff allowed)

### Screenshot Test Challenges

1. **Cross-platform font rendering** makes CI-based screenshot comparison unreliable
2. **Animation timing** causes false positives unless explicitly disabled
3. **Dynamic content** (timestamps, random IDs) must be masked or frozen

**Lesson**: Visual regression tests are most valuable run locally before push, not in CI. Use them as a pre-commit safety net, not a gate.

---

## Real Objects over Mocks

### The Hierarchy of Test Doubles

From the repos, a clear preference hierarchy emerges:

1. **Real objects** (strongly preferred) — rogue_planet uses `t.TempDir()` for real filesystem, real SQLite databases
2. **In-memory fakes** (acceptable) — tasche's `MockD1`, `MockR2`, `MockKV` are substantial re-implementations
3. **Stubs with contract validation** — geist_fabrik's `SentenceTransformerStub` generates deterministic embeddings
4. **Framework mocks** (last resort) — `vi.mock()`, `unittest.mock.AsyncMock`

### Pattern: Real Database in Tests (rogue_planet)

```go
func TestSomething(t *testing.T) {
    dir := t.TempDir()  // Automatically cleaned up after test
    dbPath := filepath.Join(dir, "test.db")
    repo, err := repository.New(dbPath)
    // ... test with real SQLite
}
```

### Pattern: Testing Constructor for Real Objects (rogue_planet)

```go
// crawler.go has NewForTesting() that disables SSRF checks
// This allows tests to use real HTTP servers (httptest.NewServer)
// without being blocked by security validation
```

**Lesson**: Provide test-specific constructors that disable security/network checks, rather than mocking the entire dependency.

### Pattern: Deterministic Stubs (geist_fabrik)

```python
class SentenceTransformerStub:
    """Generates deterministic embeddings based on text content hash."""
    def encode(self, sentences, **kwargs):
        embeddings = []
        for text in texts:
            text_hash = hashlib.sha256(text.encode()).digest()
            extended = (text_hash * num_repeats)[:SEMANTIC_DIM]
            embedding = np.array([b / 128.0 - 1.0 for b in extended])
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        return np.array(embeddings)
```

**Lesson**: When you must stub an expensive dependency (ML model downloads), make the stub deterministic by hashing input. This gives consistent test results while avoiding network/compute costs.

### Pattern: Conditional Stub Injection (geist_fabrik)

```python
def pytest_configure(config):
    markexpr = config.getoption("-m", default="")
    should_use_stub = "not slow" in markexpr
    if not should_use_stub:
        return  # Integration tests use real model
    # Only inject stub for unit tests
    sys.modules["sentence_transformers"] = fake_module
```

**Lesson**: Make the decision between real objects and stubs explicit and marker-driven. Unit tests (`-m "not slow"`) get stubs; integration tests get real dependencies.

---

## Flaky Test Patterns

### Pattern: Network Test Isolation (rogue_planet)

```go
// Tests marked with // +build network require internet access
// Excluded from regular test runs to maintain reliability
go test -tags=network ./pkg/crawler -v
```

**Lesson**: Network-dependent tests should be behind build tags/markers, excluded from the default test run.

### Pattern: Time-Invariant Tests (rogue_planet)

Integration tests using real-world feed snapshots from `testdata/` ensure tests remain stable without network dependencies. Feed snapshots are committed to the repo.

**Lesson**: Capture real-world data as fixtures rather than fetching it live. This eliminates network flakiness and makes tests reproducible.

### Pattern: Animation Waiting (atlas E2E)

```typescript
async function waitForAnimations(page, ms = 600) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(ms);
}
```

**Note**: While `waitForTimeout` is generally an anti-pattern, for animation-driven UIs it's sometimes necessary. Better alternatives include waiting for CSS `animation-iteration-count` or checking computed styles.

### Anti-Pattern: Visual Tests in CI

atlas explicitly skips visual regression tests in CI because font rendering differs across environments. This is the right call — don't let cross-platform rendering differences make your tests flaky.

---

## Test Architecture Patterns

### Three-Tier Testing (skill_scanner)

skill_scanner's `TESTING.md` defines the clearest three-tier architecture:

**Tier 1: Infrastructure** — Benign content only. Tests building blocks in isolation.
**Tier 2: Detection** — Minimal synthetic triggers. Tests what patterns detect and don't detect.
**Tier 3: Documentation Consistency** — Cross-references docs against code. No payloads.

Each tier has strict content rules:
- Tier 1: No malicious payloads
- Tier 2: Shortest non-functional fragment that exercises the regex, RFC 5737/2606 safe addresses only
- Tier 3: No scanning, no payloads — pure documentation verification

**Lesson**: When testing security tools, separate concerns: test the *mechanism* with benign data, test *detection* with minimal synthetic triggers, test *documentation* with cross-referencing.

### Spec-Driven Development

Multiple repos use a `specs/` directory containing detailed specifications that tests verify:

- atlas: `specs/atlas.spec`, `specs/atlas.impl.spec`
- flux-search: `specs/flux.spec.md`
- rogue_planet: `specs/rogue-planet-spec.md`
- geist_fabrik: `specs/geistfabrik_spec.md`

**Lesson**: Specs serve as the authoritative source of truth. Tests verify specs. When specs change, tests must change to match.

### Self-Scan Safety Gate (skill_scanner)

```python
# The test suite runs the scanner against its own source files.
# Files that contain pattern definitions will self-match by design.
# We verify the count is bounded (< 200 findings each).
# Other project files must produce zero HIGH/CRITICAL findings.
```

**Lesson**: Security tools should scan themselves as a regression test. This catches false positive rate regressions.

---

## Coverage Configuration

### Python Coverage Best Practices (observed across repos)

```toml
# geist_fabrik: pyproject.toml
[tool.coverage.run]
branch = true                    # Branch coverage, not just line
source = ["geistfabrik"]
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

```toml
# skill_scanner: pyproject.toml
[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Go Coverage (rogue_planet)

```makefile
make coverage    # Generate HTML coverage report
go test ./... -cover    # Quick terminal summary
```

Target: >75% for all packages, with per-package breakdown.

### Key Coverage Patterns

1. **Branch coverage** (`branch = true`) — not just line coverage
2. **Explicit source** — only measure production code, not tests
3. **Pragmatic thresholds** — 75-80%, not 100%
4. **Show missing** — always show which lines are uncovered
5. **Exclude boilerplate** — `__main__`, abstract methods, type checking blocks

---

## Skipped and Sabotaged Tests

### Legitimate Skip Patterns

```python
# tasche: E2E tests gated by environment variable
@pytest.mark.skipif(not os.environ.get("RUN_E2E_TESTS"),
                    reason="Requires RUN_E2E_TESTS=1")
```

```typescript
// atlas: Visual regression tests skipped in CI
test.skip(!!process.env.CI, 'Visual regression tests are skipped in CI');
```

```go
// rogue_planet: Network tests behind build tags
// +build network
```

### Detection Signals for Sabotaged Tests

From the audits, watch for:
1. **`t.Log` in assertion position** — logs failure instead of failing
2. **`skip` without clear environment reason** — tests just turned off
3. **Empty test bodies** — test function exists but does nothing
4. **Assertion on wrong value** — tests that assert on the mock return value, not the system output
5. **`t.Skip()` in test body** without conditional — unconditional skip

---

## Testability and Refactoring for Testability

### Pattern: Output Injection for Testability (rogue_planet)

```go
// Commands write to opts.Output for testability
// Production: opts.Output = os.Stdout
// Tests: opts.Output = &bytes.Buffer{}
type InitOptions struct {
    Output io.Writer
    // ...
}
```

**Lesson**: Accept `io.Writer` / output streams as parameters rather than writing directly to stdout. This makes CLI output testable without process-level capture.

### Pattern: Safe Wrappers for Testability (tasche)

The FFI boundary evolved toward construction-time wrapping:

```python
# SafeEnv wraps all bindings at construction time
class SafeEnv:
    def __init__(self, env):
        self.DB = SafeD1(env.DB)
        self.CONTENT = SafeR2(env.CONTENT)
        # ...
```

Tests can inject `MockEnv` at the same construction point, ensuring the mock path exactly mirrors the production path.

### Pattern: Factory Functions for Test Setup (tasche)

```python
def make_test_helpers(*routers):
    """Create _make_app and _authenticated_client helpers for a set of routers."""
    def _make_app(env):
        return _make_test_app(env, *routers)
    async def _auth_client(env, user_data=None):
        return await _authenticated_client(env, *routers, user_data=user_data)
    return _make_app, _auth_client
```

**Lesson**: When multiple test files need the same setup pattern, extract it as a conftest factory. Each test file declares its routers once.

### Pattern: Test Data Builders (tasche)

```python
class ArticleFactory:
    _counter = 0
    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {"id": generate_id(), "title": f"Test Article {cls._counter}", ...}
        defaults.update(overrides)
        return defaults
```

With auto-reset between tests:
```python
@pytest.fixture(autouse=True)
def _reset_article_factory():
    ArticleFactory._counter = 0
```

**Lesson**: Factory/builder patterns for test data reduce boilerplate without hiding intent. Tests only specify the fields they care about.

### Pattern: Dual Vitest Configs (bobbin)

```typescript
// vitest.config.ts — Cloudflare Workers pool (WASM environment)
// vitest.node.config.ts — Node.js (filesystem access)
```

**Lesson**: When code runs in multiple environments, maintain separate test configs rather than trying to make one config work everywhere.

---

## CI/CD Integration

### Pre-commit Quality Gates

Multiple repos use pre-commit hooks and Makefile targets:

```makefile
# rogue_planet
make quick    # Format + test + build (fast iteration)
make check    # All quality checks: fmt + vet + test + race
```

### CI Workflow Patterns

- **rogue_planet**: `go.yml` — test, race detection, coverage
- **skill_scanner**: `ci.yml` — lint, test with coverage, security scan
- **geist_fabrik**: `test.yml` — test with markers, coverage report
- **planet_cf**: `check.yml` + `e2e.yml` — separate workflows for unit and E2E

**Lesson**: Separate fast checks (lint, unit tests) from slow checks (E2E, visual regression). Fast checks block merge; slow checks can be advisory.

---

## Anti-Patterns Observed

### 1. Integration Tests That Mock Their Integration Points

From tasche Lesson #50:

> "`tests/integration/test_processing_pipeline.py` patched `http_fetch` with canned HTML in 6 of 7 tests. The intent was to test 'the full pipeline end-to-end,' but with HTTP mocked, the tests never exercised real content extraction."

**Rule**: If a test mocks the thing it's supposed to integrate with, it's a unit test in disguise.

### 2. Mocked Signals Are Not Reactive

From tasche Lesson #44:

```javascript
// WRONG: Signal assignment doesn't trigger component re-render
vi.mock('../state.js', () => ({ tags: { value: [] } }));
tagsSignal.value = [{ id: 'tag-1' }]; // Component won't see this
```

**Fix**: Mock the data-fetching function, not the state container:
```javascript
listTags.mockResolvedValueOnce([{ id: 'tag-1', name: 'JavaScript' }]);
render(<Tags />);
```

### 3. Tests That Only Check Non-Empty Output

A function that returns `"X"` for all inputs would pass `assert output != ""`. Always verify *specific* expected content.

### 4. Tests That Grow Without Pruning

From tasche Lesson #46: After feature addition, dead test code accumulates. Run dead code audits after large changes.

### 5. Relying on Miniflare/Simulator for Platform Validation

From tasche Lesson #31: Local platform simulators are useful for development but unreliable for verifying platform-specific behavior. Always have at least one smoke test against the real platform.

---

## Key Takeaways for Skill Design

1. **Every parser/normalizer needs a "never crashes on arbitrary input" property test**
2. **Mock contract tests should validate that mock return values match reality**
3. **Measure assertion density, not just test count or coverage percentage**
4. **E2E tests against real infrastructure are the only tier that validates platform contracts**
5. **Three-tier architecture (unit → integration → E2E) with clear rules for each tier**
6. **Prefer real objects; when you must mock, test the mocks themselves**
7. **Visual regression tests belong in local dev, not CI (font rendering differs)**
8. **Gate network/platform-dependent tests behind markers or environment variables**
9. **Boundary-first generators (test low/high bounds before random values) catch edge cases**
10. **Conservation laws make excellent property tests** ("no new characters", "monotonic with more input")
