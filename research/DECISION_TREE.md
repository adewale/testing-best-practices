# Test Type Decision Tree

> Which tests to write, when they're required, and when they're optional.

---

## Tier 1: Always Required

These tests must exist for every project. They catch the most common and most dangerous bugs with the lowest maintenance cost.

### Unit Tests

**When**: Always. Every function with non-trivial logic.

**What they catch**: Logic errors, off-by-one bugs, wrong return types, missing edge cases.

**Cost**: Low. Fast to write, fast to run, stable.

**Rules**:
- Test through public interfaces, not internal methods
- Minimum 3 assertions per test (assertion density)
- Both happy path AND sad path for every feature
- No network, no filesystem, no external services

**Decision**: Is there a function with `if`, a loop, or arithmetic? → Write a unit test.

---

### Smoke Tests

**When**: Always. At least one per deployable unit.

**What they catch**: "The app starts." Import errors, configuration problems, missing dependencies, broken endpoints.

**Cost**: Very low. A single test that boots the application and hits the main endpoint.

**Rules**:
- Must exercise the real startup path (not mocked)
- Should take < 10 seconds
- Should be the first test written for any new project

**Decision**: Can a user reach the front door? → Write a smoke test.

```python
# Minimum viable smoke test:
async def test_app_starts():
    app = create_app()
    response = await app.client.get("/")
    assert response.status_code == 200
```

---

### Regression Tests

**When**: Always, after every bug fix.

**What they catch**: The same bug happening again.

**Cost**: Low. Write the test that reproduces the bug, then fix the bug.

**Rules**:
- Write the test BEFORE fixing the bug (red-green TDD)
- Name the test after the bug/issue number
- Include a comment explaining the original bug

**Decision**: Did you just fix a bug? → Write a regression test.

```python
# Regression test pattern:
def test_double_slice_bug():
    """Regression: explicit dropCap.char caused double-slicing.
    See atlas LESSONS_LEARNED, Bug #2."""
    result = render_text("Hello world", drop_cap="H")
    assert result == "ello world"  # Not "llo world" (the old bug)
```

---

## Tier 2: Required When Applicable

These tests are required when the project has specific characteristics. The trigger condition determines applicability.

### Property-Based Tests

**When**: The code processes arbitrary input (parsers, serializers, validators, transformers).

**What they catch**: Edge cases you didn't think of. Boundary conditions. Unicode handling. Overflow. Input shapes that example-based tests miss.

**Cost**: Medium. Requires thinking about invariants rather than examples. Slower to run.

**Trigger conditions** (if ANY apply, write PBT):
- [ ] Function accepts strings, numbers, or binary from users
- [ ] Function serializes/deserializes data (roundtrip)
- [ ] Function transforms data (the output should preserve some property of the input)
- [ ] Function is a parser (should never crash on arbitrary input)
- [ ] Function computes rankings, scores, or orderings (monotonicity, transitivity)

**Best invariant patterns** (from adewale/simonw repos):
| Pattern | Example | When to use |
|---------|---------|-------------|
| Never crashes | `parseQuery(arbitrary_string)` doesn't throw | Every parser |
| Roundtrip | `deserialize(serialize(x)) == x` | Serialization |
| Idempotent | `f(f(x)) == f(x)` | Normalization, formatting |
| Monotonic | `f(x + more) >= f(x)` | Counting, measuring |
| Conservation | `chars_out ⊆ chars_in` | Stripping, filtering |
| Valid-or-absent | `f(x)` is valid or `None` | Parsing with fallback |

**Decision**: Does the function accept user input or transform data? → Write property tests.

---

### E2E Tests

**When**: The project has a user-facing interface (web app, API, CLI workflow).

**What they catch**: Routing bugs, integration failures, platform-specific behavior, workflow breakdowns. The bugs that unit tests fundamentally cannot catch.

**Cost**: High. Slow to run, complex to set up, can be flaky.

**Trigger conditions** (if ANY apply, write E2E):
- [ ] Project has HTTP endpoints
- [ ] Project has a CLI with multi-command workflows
- [ ] Project runs on a specific platform (Cloudflare Workers, Pyodide, etc.)
- [ ] Project integrates with external services (databases, APIs)
- [ ] Previous bugs were missed by unit tests but would have been caught by E2E

**Rules**:
- Test the golden path first (most common user workflow)
- Gate behind environment variable for tests that need infrastructure
- Limit to 5-15 E2E tests (not a replacement for unit tests)
- Each E2E test should exercise a complete user journey

**Decision**: Would a user interact with this through a browser, API, or CLI? → Write E2E tests.

---

### Documentation-Code Sync Tests

**When**: The project has public documentation (README, docs/, API docs).

**What they catch**: Documentation drift. Features that exist but aren't documented. Documentation that references deleted features.

**Cost**: Low-medium. Easy to write, catches embarrassing gaps.

**Trigger conditions**:
- [ ] Project has CLI commands listed in docs
- [ ] Project has a plugin/hook system with documented extension points
- [ ] Project has configuration settings described in docs
- [ ] Project has public API functions documented in a reference

**The simonw pattern**:
```python
@pytest.mark.parametrize("command", cli.cli.commands.keys())
def test_commands_are_documented(documented_commands, command):
    assert command in documented_commands
```

**Decision**: Does the project have docs that describe features? → Write sync tests.

---

### Snapshot Tests (umbrella: golden file, structured-output, session/trace)

**When**: The code produces complex output that is hard to assert on
field-by-field, OR the system is a multi-step process where the *trace* of
operations matters more than any single assertion.

**What they catch**: Drift. Unanticipated behavioral change anywhere in the
recorded surface — including the *absence* of an expected event, the
reordering of steps, or a silently-changed field that no targeted assertion
covered.

**Cost**: Low setup. Medium maintenance (must review baseline diffs with
code-review rigor; rubber-stamping `--update` defeats the purpose).

**Three dialects** — pick the one whose recorded artifact matches your system:

| Dialect | Record what | Use when | Example tools |
|---|---|---|---|
| **A. Golden file** | Output file from input file | Transformation pipelines (HTML→Markdown, compiler, formatter) | Go `testdata/`, kepano/defuddle pattern |
| **B. Structured-output snapshot** | Serialized in-memory value | Single function returns complex JSON/HTML/object | `syrupy`, Jest snapshot, `insta`, `Verify` |
| **C. Session / trace golden** | Full execution trace (args, HTTP, DB, LLM, tool calls, side effects) | Multi-step agents, LLM apps, pipelines | Custom (Zod/Pydantic schemas → YAML traces) |

**Trigger conditions** (if ANY apply, write snapshot tests):
- [ ] Output is structured text (JSON/HTML/Markdown) and changes should be reviewed
- [ ] Tests would otherwise need 20+ field-by-field assertions
- [ ] You have real-world inputs/scenarios to test against
- [ ] The system has multi-step execution where ordering and side effects matter
- [ ] You're refactoring legacy code and need a behavior safety net (combine with characterization testing)

**Rules**:
- Normalize unstable fields (timestamps, IDs, random) at write time
- Tag every field as stable or unstable in your serializer
- Review baseline diffs as you would code
- Shard by scenario; avoid monolithic snapshots
- For security-sensitive output, layer programmatic assertions on top of the diff

**Anti-patterns** (especially Dialect C):
- Regex-matching stable fields (hides values you control)
- Surgical extraction with grep/jq/awk (reverts to unit-test mentality)
- Snapshotting non-deterministic output without scrubbers (flaky)
- Auto-running `--update` in CI

**Decision**: Is your output structured and stable enough to diff, or is your
system a multi-step trace where "what happened" is the spec? → Write snapshot
tests. See `references/snapshot-testing.md` for dialect selection.

> **Network boundary special case**: if the snapshot is HTTP traffic, prefer
> VCR cassettes (Tier 2 entry below) — they add replay semantics on top.

---

### Contract Tests

**When**: The code uses mocks in unit tests OR depends on external APIs.

**What they catch**: Mock-reality drift. API contract changes. Assumptions that were true when the mock was written but are no longer true.

**Cost**: Medium. Requires access to the real system (at least periodically).

**Trigger conditions**:
- [ ] Unit tests use mocks for external services
- [ ] Project depends on third-party APIs
- [ ] Unit tests use stubs for browser APIs (canvas, ResizeObserver, etc.)
- [ ] There are precomputed data files that code depends on

**The atlas pattern**:
```typescript
// Mock says: line height is ~20px for 16px font
// Contract test proves: real browser confirms this
test('text measurement returns positive height', async ({ page }) => {
  const lineHeight = await page.evaluate(() => {
    // Measure with real browser canvas
  });
  expect(lineHeight).toBeGreaterThan(10);
  expect(lineHeight).toBeLessThan(40);
});
```

**Decision**: Do your tests use mocks? → Write contract tests to validate the mocks.

---

## Tier 3: Sometimes Helpful (Use With Caution)

These tests provide value in specific situations but have significant costs. Use them deliberately, not by default.

### Visual Regression / Screenshot Tests

**When helpful**: UI-heavy projects where layout correctness matters.

**Cost**: High. Cross-platform font rendering differences cause false positives. Snapshots bloat the repo. Animations cause flakiness.

**Mitigations**:
- Skip in CI (`test.skip(!!process.env.CI)`) — run locally only
- Disable animations before capturing
- Capture components, not full pages
- Set low pixel diff tolerance (1-2%)

**Decision**: Is pixel-perfect layout critical AND you can run locally before push? → Consider screenshot tests.

**When to avoid**: When the UI is still actively evolving. When CI runs on different OS than dev.

---

### Mutation Testing

**When helpful**: After a test quality audit reveals low assertion density or when you need confidence in critical code (security, financial).

**Cost**: Very high compute cost. Slow (10-100x test runtime). Requires interpretation.

**Mitigations**:
- Run on specific critical modules, not the whole codebase
- Run nightly, not on every commit
- Focus on files with assertion density < 3

**Decision**: Do you have critical code (security, data integrity) and suspect your tests might not catch all bugs? → Run mutation testing on that module.

**When to avoid**: Early in development. On non-critical code. When test suite is already slow.

---

### Performance / Benchmark Tests

**When helpful**: Performance-sensitive code where regressions would be noticeable to users.

**Cost**: Medium. Requires stable benchmarking environment. Results vary between machines.

**Mitigations**:
- Run on dedicated hardware or with performance counters (not wall clock)
- Compare against baseline, not absolute values
- Separate from regular test suite (use markers like `@pytest.mark.benchmark`)

**Decision**: Would a 2x slowdown be a bug? → Write benchmark tests.

**When to avoid**: When performance isn't a user-visible concern. When results aren't reproducible.

---

### Fuzz Testing

**When helpful**: Security-sensitive code that processes untrusted input (parsers, deserializers, network protocols).

**Cost**: High. Requires infrastructure for continuous fuzzing. Hard to reproduce failures.

**Mitigations**:
- Use structured fuzzing (Hypothesis/fast-check) over raw fuzzing
- Start with the "never crashes" property test — it's fuzzing with better ergonomics
- Focus on code that processes untrusted input

**Decision**: Does the code process untrusted input where a crash = vulnerability? → Consider fuzzing.

---

## Decision Flowchart

```
START: New feature or bug fix
│
├─ Is this a bug fix?
│  └─ YES → Write regression test (Tier 1) ──→ then continue below
│
├─ Does it have non-trivial logic?
│  └─ YES → Write unit tests (Tier 1)
│     ├─ Does it accept arbitrary input?
│     │  └─ YES → Add property-based tests (Tier 2)
│     ├─ Do the unit tests use mocks?
│     │  └─ YES → Add contract tests (Tier 2)
│     └─ Continue
│
├─ Is it a user-facing endpoint/command?
│  └─ YES → Write smoke test (Tier 1)
│     └─ Is there a multi-step workflow?
│        └─ YES → Write E2E test (Tier 2)
│
├─ Does it produce structured output (JSON/HTML/file/trace)?
│  └─ YES → Choose snapshot dialect (Tier 2):
│     ├─ Input file → output file?         → Dialect A (golden file)
│     ├─ Returns structured value?          → Dialect B (Jest/syrupy/insta/Verify)
│     ├─ Multi-step trace matters?          → Dialect C (session/trace golden)
│     └─ HTTP boundary?                     → VCR cassettes (specialization)
│
├─ Is it documented?
│  └─ YES → Add doc-sync test (Tier 2)
│
├─ Is it security-critical?
│  └─ YES → Consider mutation testing + fuzzing (Tier 3)
│
├─ Is pixel layout critical?
│  └─ YES → Consider screenshot tests (Tier 3, local only)
│
└─ Is performance user-visible?
   └─ YES → Consider benchmark tests (Tier 3)
```

---

## Cost-Benefit Summary

| Test Type | Setup Cost | Maintenance | Run Time | Bug-Finding Power | Flakiness Risk |
|-----------|-----------|-------------|----------|-------------------|----------------|
| Unit tests | Low | Low | Fast | Medium | Very Low |
| Smoke tests | Very Low | Very Low | Fast | Low (but critical) | Low |
| Regression tests | Low | Low | Fast | High (targeted) | Very Low |
| Property-based | Medium | Low | Medium | Very High | Low |
| E2E tests | High | Medium | Slow | High | Medium |
| Doc-sync tests | Low | Low | Fast | Low (but embarrassment-saving) | Very Low |
| Contract tests | Medium | Medium | Medium | High | Low |
| Snapshot — golden file (A) | Low | Low | Fast | Medium | Very Low |
| Snapshot — structured (B) | Low | Medium | Fast | Medium | Low (rubber-stamp) |
| Snapshot — session/trace (C) | Medium | Medium | Medium | High | Low |
| VCR cassettes | Low | Low | Fast | Medium | Very Low |
| Visual regression | High | High | Slow | Medium | High |
| Mutation testing | High | Low | Very Slow | Very High | Very Low |
| Performance tests | Medium | Medium | Slow | Low | High |
| Fuzz testing | High | Low | Very Slow | High (security) | Low |

---

## The Minimum Viable Test Suite

For any project, start with these and add more based on the decision tree:

1. **One smoke test** — the app starts and responds
2. **Unit tests for business logic** — 3+ assertions each, happy + sad path
3. **Regression test for every bug fix** — written before the fix
4. **Property test for every parser/serializer** — "never crashes" at minimum

This gives you the highest bug-finding-power-per-hour-invested. Add Tier 2 and Tier 3 tests as the project matures and the trigger conditions apply.
