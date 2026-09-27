# Gate Integrity: Is the Check Running, and Can It Fail?

Read this when assessing a suite, changing CI/hooks/test configuration, adding a
gated or scheduled test, asking why bugs escape a green pipeline, or before
claiming "tests pass". The most common failure in real repositories is not a
missing test. It is a check that silently stopped running, or one that cannot go
red, while everyone believes it is green.

## 1. Liveness: which job runs each tier, and when did it last pass?

For every tier (unit, integration, E2E, visual, perf/budgets, coverage, mutation,
fuzz, evals, post-deploy smoke, lint/types) record:

- the exact command, the CI job that runs it, and its trigger (PR, push, schedule,
  dispatch);
- the last run on the default branch: status, duration, and test count.

A tier with no job is presumed broken until run. A test that exists but no job
runs is documentation, not verification.

Check that runs executed, not just that they are green or red: a runner was
assigned, the duration is plausible, and counts are non-zero. CI that is red or
not starting for non-code reasons (quota, billing, missing runner, uninstalled
browser engine) is a **dead gate**: surface it before anything else. While it is
dead, local runs are the only evidence, and the report must say so.

**Collection parity.** The CI collector may not see every test: `unittest
discover` ignores pytest-style module functions; Playwright projects that no lane
invokes never run; runner `include` globs miss files. Compare counts against an
alternate collector (`pytest --collect-only -q` vs the CI runner; the JSON
reporter's per-project totals).

## 2. Gated-test reachability

For every build tag, env gate, `skipIf(resource)`, OS-suffixed baseline, optional
conformance leg, or `if:` condition, all three must hold:

1. **Compiled in CI**: `go vet -tags=network ./...` or `go test -tags=… -run '^$'`;
   a type-check that includes the file.
2. **Selected with the resource present**: some lane provides the capability and
   selects the file.
3. **Fails when it skips**: a skip ledger, a reporter contract
   (`skipped == expected`), or a `REQUIRE_*` flag that turns a skip into a failure.

Cheap detection: run the CI command verbosely in a fresh checkout and list what
was skipped or not collected. Honest gating is fine; gating that no lane
satisfies is a dead test.

## 3. Gate integrity: show every check can go red

| Signal | Why it cannot fail | Fix |
|---|---|---|
| `\|\| true`, `continue-on-error: true`, `2>/dev/null` on a test or check step | Failure is discarded | Remove; if genuinely advisory, see §6 |
| Baseline updater used as a check (`detect-secrets scan --baseline`) | Rewrites the baseline and exits 0 | Use the checking form (`detect-secrets-hook --baseline`) or fail on a diff |
| Error-swallowing shell (`if echo "$?" \| grep …`) | Every error becomes a warning | Capture stderr; tolerate only the specific benign message |
| Skip-green when secrets or tokens are missing | The owner's own repo can lose its gate silently | Fail in the owner's repo; skip explicitly only for forks |
| `::warning::` + skip that ends a deploy green | Nothing shipped, and the badge is green | Fail on the normal path; alert on live-version drift (§5) |
| Step iterating an empty set (scanner over a directory with no targets) | Zero findings from zero inputs | Scan committed canary fixtures: one that must fire, one that must not |
| Coverage threshold configured but never invoked, or its provider not installed | The number is never computed | Run it in CI, or delete the dead threshold |
| Mutation `break: null`, no threshold, a threshold the tool ignores, or dispatch-only | Cannot fail on its own | Threshold from a measured baseline, shown to fail when set above the score; or keep it explicitly diagnostic |
| Fail-open imports (`import(x).catch(() => null)` + `skipIf`) | A required lane passes when its dependency fails to load | Fail when CI is set; assert the skip count is zero |
| Warning-only expiry or review dates | Warnings nobody reads | Fail after a grace period; warn ahead of time |
| E2E against production or a deployment not built from this commit | Tests someone else's code | Target a local server or a deploy of this SHA |

Prove a gate works by planting a violation in a scratch copy (a failing test, a
fake secret, an empty target) and watching it go red, then revert.

## 4. Vacuous passes: the instrument measures something else

- A universal assertion over a possibly-empty set ("every row fits", `violations
  == []`) needs a non-empty precondition; print the denominator.
- Zero-sample aggregates (`Math.min(...[])` is `Infinity`) must refuse n = 0.
- A test or script that reimplements the logic and imports nothing from the SUT
  tests its own copy.
- **Test linkage**: a subject with no non-test importer (dead code, or a
  reimplementation) can carry many green tests while the live path is untested.
  Check linkage at symbol level.
- Precondition failures converted to green: `test.skip()` in the failure branch,
  `page.goto(...).catch(() => {})`, an imperative `pytest.xfail()` left after the
  fix.
- **Instrument drift**: measurement tools or tests that copy constants from the
  code instead of importing them agree with the code by construction.
- **Quiescent harness**: pausing or stubbing can flip which branch the SUT takes;
  ask what the harness changed to get its quiet.

## 5. Test the tester, and trust the artifact

- **Both sides**: every custom oracle, linter, validator, auto-fixer, scanner, and
  eval grader needs at least one known-good input that passes and one known-bad
  input that fails, checked in CI. Detectors also need near-miss controls that
  must not fire. Write fixtures from the failure, not from the regex.
- **Cheap targeted mutation**:
  - A sabotage kill matrix: neuter one central function in a scratch copy; every
    test file that imports it should fail; count survivors.
  - Committed defect-replay probes: reintroduce each past bug; the suite must fail.
  - Invariants that a no-op satisfies (determinism, count preservation) need a
    change-witness assertion that state actually changed.
- **The author is not the oracle**: goldens, approvals, and eval cases produced in
  the same change by the same actor are characterizations until independently
  reviewed. Report a trivial baseline next to any eval score.
- **Deploy truth**:
  - A smoke test touches the core dependency.
  - The live version or SHA must match the deployable default branch; alert on
    drift.
  - The artifact under test must be the artifact deployed: lockfile parity,
    installed-package or tarball tests, publishing the bytes that passed.
  - Test declared compatibility floors (`requires-python`, `engines`).

## 6. Recurring lanes and advisory gates: an operating contract

Before scheduling a nightly E2E, fuzz, perf, eval, or mutation lane:

- run the exact configuration once to completion on the target infrastructure and
  keep the report;
- set a runtime budget and name an owner;
- decide notify-or-block: a red schedule that does neither is a write-only log;
- set a stop rule: after 3 consecutive failures, fix, narrow, disable, or delete
  before growing scope;
- state a removal criterion.

Gates cost minutes and attention. Weigh suite shape by where CI time goes, not
just test counts, and retire gates that never fire. Mutation specifics are in
`references/mutation-testing.md`.

## 7. Restraint: don't over-apply

- A capability-gated test is fine when a lane provides the capability and fails
  on skip.
- An advisory job with an owner, a schedule, and a notification is not a dead
  gate.
- Post-merge or nightly lanes are legitimate if someone is notified and acts; not
  every tier must run on every PR.
- Never turn a legitimately red lane green by deleting it or weakening it.
- Do not demand network, production, or paid resources in CI to satisfy this
  checklist; say what cannot be verified instead.

## Audit record (Assess mode)

```md
| Tier | Command | CI job / trigger | Last run (status, count, date) | Can it fail? (evidence) | Gap |
```

## Starter mechanical checks for a repository

Encode recurring findings as a static test with a shrink-only allowlist. Give
each rule a teeth test: a planted violation it must catch.

- focused or unconditional skip markers; assertion-free tests; weak sole assertions
- `sleep`/`waitForTimeout` synchronization; new retries
- `|| true` or `continue-on-error` on test steps in workflows
- `readFileSync(src…)` or `read_text()` of source followed by string assertions
- assertions only inside loops over results
- test files that import nothing from the source tree
- `Math.random`/unseeded randomness inside property bodies
