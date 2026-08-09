# False Green: Tests That Pass for the Wrong Reason

The anti-patterns in `antipatterns.md` are about *weak* tests — they can fail,
just not often enough. This file is about tests that **cannot fail**, **do not
touch the code they name**, or **never run**. They are invisible to coverage
(the lines do execute), to test counts (they are counted), and to CI (they are
green).

**The rule: a green test is a claim, not evidence.** The only proof that a test
can fail is making it fail. Break the production code it names and confirm that
*specific* test goes red. Coverage, test names, docblocks, and grep are
hypotheses.

## A. Vacuous — the test runs but cannot fail

| Signal | Shape |
|---|---|
| Self-comparison | `assert canonicalEqual(x, x)`, `expect(v).toEqual(v)` — passes for any implementation, including 2,500 property runs asserting nothing |
| Constant assertion | `expect(true).toBe(true)`, `assert True` "documentation tests" |
| Swallowed assertion | assertion inside `try`, `catch` accepts any error (below) |
| Nullified assertion | `await act().catch(() => {})`; `except Exception: pass` wrapping the assert |
| Runtime self-skip | `test.skip(true, ...)`, unconditional `t.Skip()`, or a guard (`if (!el) return`) that is false on every run |
| Empty collection | cases built from `readdirSync`/glob/`testdata/`; on an empty directory the suite asserts `0 === 0` |
| Expired premise | a differential/equivalence test whose two sides now route through the *same* function after a refactor |
| Fixture at default | the mutation under test is a no-op against the fixture: setting tempo `120` on a session already at `120`, rotating an all-`false` pattern |
| Harness fault-masking | a crashing subprocess, a timeout, or a connection error reads as a pass |

The swallowed assertion is the one reviewers miss:

```ts
// Cannot fail. When connect() wrongly SUCCEEDS — the only thing this test
// exists to catch — the unreachable expect() throws, its own catch swallows
// that error, and expect(e).toBeDefined() passes on the assertion failure.
try { await connect(); expect(true).toBe(false); }
catch (e) { expect(e).toBeDefined(); }
```

**Fixes**

- Capture the outcome *outside* the `try`, then assert on it; distinguish a real
  refusal from the harness's own timeout.
- Require the operation to **change state**, not merely to agree: pair every
  equivalence check with `expect(after).not.toEqual(before)`.
- Assert a **floor** on collected cases (`expect(cases.length).toBeGreaterThan(20)`)
  so an empty or partial directory fails instead of vacuously passing.
- Make fixtures **off-default and asymmetric**, so a no-op implementation is
  distinguishable. Discard identity draws with `fc.pre` / `hypothesis.assume`
  rather than narrowing the generator.
- Assert the subprocess/connection *succeeded* before asserting on its output.

### Assert the precondition actually held

A postcondition proves nothing if the setup silently did nothing. A test
asserted that the last cell in a strip was reachable — it scrolled with
`scrollIntoViewIfNeeded`, then checked the cell cleared a sticky column. But
that API stops as soon as the element is inside the scrollport, which for a
sticky overlay is not the same as being clear of it; and if the strip already
fits, no scrolling happens at all and the reachability claim is vacuous. The
fix was to scroll to the container's maximum **and assert the scroll position
moved**.

Generalize: whenever setup can no-op, assert it took effect.

| Setup | Assert it happened |
|---|---|
| Scroll / resize / navigate | the position or viewport actually changed |
| Seed a database or cache | rows inserted > 0; the cache was cold before |
| Toggle a flag or feature | it was in the other state beforehand |
| Expire a TTL, advance a clock | the clock moved past the boundary |
| Apply a mutation to a fixture | the state differs from before (see "Fixture at default") |

## B. Disconnected — the test does not exercise what it names

| Kind | What |
|---|---|
| **REIMPL** | the test file **re-implements** the logic it names instead of importing it |
| **ORPHAN** | names a module it never imports |
| **DEAD** | the named module is reachable from nothing in production |

REIMPL is the dangerous one, and it is worse than a wrong test: **the test's
reach is bounded by its copy**, so the uncovered production branch is exactly
the shape of the divergence. A test that copies `isMelodicInstrument` as
`"sampled:" -> true` cannot exercise sampled *drums* at all — production's real
branch is invisible, and no coverage report shows a gap. Copies exist mostly
because the real function is module-private; export it or test it through its
caller instead.

Three more in this family:

- **Import-without-call** — `import { applyMutation as _applyMutation }` and
  never calling it. Defeats import-based linkage checks: the module *is*
  imported.
- **Double as second implementation** — a hand-written fake large enough to be a
  second implementation of the dependency. The suite then tests the double. See
  `antipatterns.md` #3/#5.
- **Hand-picked sample** — replacing an enumeration over a shared catalogue with
  "the nine I picked myself". Iterate the shared constant so new entries are
  covered automatically; a hardcoded list is the drift-prone form.

## C. Never ran — green because nothing executed it

- Test files **no runner collects**: stale globs, a moved directory, a spec whose
  only test was removed leaving a docblock behind. Ask the runners what they
  collect (`vitest list`, `go test -list`, `pytest --collect-only`) and diff
  that against disk.
- CI job set to `continue-on-error`, or the only real gate is a pre-push hook
  that `--no-verify` bypasses.
- A precondition that fails in `beforeEach` on **every** run — e.g. specs waiting
  for a WebSocket the mock backend never provides — sitting in an advisory lane
  where nobody reads the red.

Never-scheduled and always-green compound: each defect hides the other.

## D. Deleting a test deletes knowledge

Before removing a test, check what it is the **only** holder of: extract its
input literals and assertion targets and search the surviving suite for them.
Test *names* rarely reveal the loss; a specific input literal does. Note that a
file-level scan cannot see titles removed from files that still exist.

A negative assertion about a completed migration ("the old three-state enum no
longer exists") legitimately expires — retiring it is correct.

## Confirm before you flag

Every detector above over-reports on its first run. Measured on one 250-file /
85k-LOC suite audit:

| Detector | First pass | Real | The noise was |
|---|---|---|---|
| test/subject linkage | 34 | 17 | barrels, fixtures, `*.worker`/`*.worklet`, `await import()` |
| antipattern text scan | 17 | 5 | the audit's **own prose** describing the patterns |
| empty-collection suites | 5 | 2 | three built cases from a constant, not a directory |
| bug-family sweep | 9 | 4 | five families genuinely had no instances |

So:

1. **Strip comments and docstrings before pattern-matching.** Agents narrate
   their fixes; a raw-text scan punishes the outputs that explain themselves
   best.
2. **A grep is not evidence of coverage — and not evidence of its absence.** One
   audit reported a missing `MAX_PLAYERS` test after searching for the
   identifier; the test existed and spelled the limit `10` and `"eleventh"`.
   Establishing coverage means breaking production and watching a lane go red,
   **in both directions**.
3. **Report the sabotage, or mark the finding unconfirmed.** State what you broke
   and which test went red. A pattern match is a suspicion, not a defect.

### Look-alikes to leave alone

| Looks like | Leave it when |
|---|---|
| One assertion in a property test | the single oracle is strong (roundtrip, invariant). Count what a mutation would kill, not assertions |
| A clamp / fallback / `recover()` | it is the documented contract — see `antipatterns.md` #14 |
| "Integration" test with no network | it crosses a real in-process component boundary |
| Test naming a module it never imports | it is black-box: it drives the real system through its entry point. Rename it; do not rewrite it to import internals |
| A skipped test | the skip is conditional on a genuinely absent capability *and* the condition can be false |
| Duplicated-looking coverage | the layers defend **different** failure modes, or one is a boundary/security test — see `correctness-by-construction.md` |
| A slow, redundant E2E test | redundant and slow is a **placement** problem: move it down a tier, keep the assertion |

### Landing a new check

A gate that fails on day one gets disabled on day two. Land it **advisory** with
the known findings in an allowlist, clear the backlog, then make it **blocking**
— and make the allowlist fail when an entry stops being a finding, so it cannot
rot into a permanent exemption.
