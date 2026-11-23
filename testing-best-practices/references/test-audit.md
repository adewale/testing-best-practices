# Audit and repair existing tests

Use this workflow for a bounded test-quality sweep, consolidation, or deletion.
It complements [anti-patterns](antipatterns.md) and [gate integrity](gate-integrity.md).
The output is a set of evidence-backed decisions about tests and their owners.
Search hits, test counts, coverage percentages, and deleted lines are not quality
verdicts or targets.

## 1. Establish scope and baseline

- Read repository instructions, CI configuration, nearby tests, and relevant open
  PRs. Pin the base SHA. Choose a coherent production owner or boundary and a time
  budget; do not start with a deletion quota.
- For each in-scope tier, record the actual command, CI job/trigger, last result
  on the default branch, and whether it selects any tests and can fail. Read job
  results rather than inferring them from the workflow's overall conclusion.
- Run each relevant tier once when feasible, or record why it was unavailable.
  A passing baseline does not establish oracle strength. A failing baseline may
  expose a product bug; keep it separate from cleanup candidates.
- Read the owner, entry points, callers, fixtures, and history of candidates.
  For external-system doubles, inspect the real API/types and exercise the real
  runtime where available. SQLite can validate SQL without validating D1's
  binding semantics, `exec`, `batch`, or limits.
- Check fixtures are obtainable from a fresh checkout. An orphan Git pin, a
  developer-specific absolute path, unavailable recording, or generated state
  with no maintained recipe makes historical proof difficult to reproduce. If replacing it with
  generated scenarios, verify their observable state and label old outputs as
  historical rather than claiming the original experiment was reproduced.

## 2. Discover candidates cheaply

Start with focused searches, then read each hit in context. With ripgrep, from
the target repository root:

```sh
rg -n -g '*test*' -g '*spec*' -g '!node_modules/**' -g '!vendor/**' \
  '(readFileSync|read_text|read_to_string|toBeDefined|toBeTruthy|assertIsNotNone|waitForTimeout|Thread\.Sleep|time\.sleep|test\.only|test\.skip|pytest\.mark\.skip)' .
rg -n -g '*.yml' -g '*.yaml' -g '!node_modules/**' -g '!vendor/**' \
  '(continue-on-error|\|\| true|--passWithNoTests|--updateSnapshot)' .github
```

These commands only collect candidates; exit 1 means no regex match, not a clean
bill of health. They miss nonstandard test paths, assertion-free tests, computed
oracles, custom helpers, and semantic duplication. Adapt paths/frameworks and
inspect at least the critical boundary's tests and helpers directly. Do not turn
these patterns into a CI failure rule without calibrated good/bad examples.

For every candidate, ask:

| Signal | What to inspect | Possible improvement | Reason to retain |
|---|---|---|---|
| Source/config/SQL strings, copied counts, hashes | Does it execute the owner or only recognize its spelling? | Run the executable, renderer, parser, migration, or real engine | Independent architecture, package, protocol, prompt-byte, or published config contract |
| Mock supplies the asserted answer | Where did the expected value and fixture come from? Does the real owner produce the effect? | Real local engine; externally grounded fixture; assert persisted/emitted state | A controlled dependency failure or a separately verified external contract |
| Truthy, not-null, no-crash | Which wrong outputs would still pass? | Assert relevant values, state transitions, and error semantics | Existence or totality is itself the complete contract |
| Assertions in loops, empty result lists, negative checks | Are inputs nonempty and is the intended branch reached? | Assert enrollment/reachability and check each required item | An empty violation set is valid when inspected inputs are independently nonempty |
| Same behavior at several layers | Which suite owns the contract? What distinct failure can each layer detect? | Consolidate shared behavior into a keeper; retain wiring/lifecycle checks | Transport, security, persistence, platform, or ordering risks differ |
| Sleep, retry, timeout increase | Who produces completion? Does the original shard order reproduce a leak? | Wait for produced state; virtual time; repair resource ownership | A measured performance or timeout contract, with justified bounds |
| Test-only export, flag, wrapper, injection hook | Are there non-test callers? Is this a useful owned interface or only access to internals? | Move proof to a real entry point; remove an obsolete seam within scope | A legitimate public API or stable dependency boundary |
| Name promises more than assertions prove | Do input, execution, and oracle reach the named condition? | Correct the test/fixture or narrow its name and claim | A narrower, honest contract still matters |
| Grader/checker self-tests all pass | Can plausible wrong answers pass a scored assertion? Are valid phrasings rejected? | Calibrate each independently scored assertion with both controls | Instrument validation proves checker behavior; product or model gains need their own experiment |

Static, slow, mocked, and single-assertion tests are not automatically bad.
Retain independently specified API, security, migration, storage, release,
cross-language, default, and observable-ordering contracts. Do not remove
behavioral proof merely because a type exists; check its runtime boundary and
hostile inputs using [correctness by construction](correctness-by-construction.md).

## 3. Decide before editing

For each candidate and relevant neighbour, record one decision. Start with the
highest-risk evidence, rather than cataloguing every obviously sound test in a
large repository. Expand to a full ledger when a broad layer removal makes
coverage ownership uncertain.

```md
Base SHA / owner / scope:
Tier command / CI job / baseline result:

| Test location and name | Observable contract / credible regression | Expected-value provenance | Decision | Remaining proof / keeper | Validation |
|---|---|---|---|---|---|
```

- **Retain**: name the independent contract and the regression it catches.
- **Repair**: preserve the contract; fix a weak oracle, unreachable fixture,
  unrealistic double, or synchronization problem.
- **Consolidate**: name the keeper test and migrate every distinct assertion
  before removing the redundant suite. A similar name or coverage line is not
  evidence that the keeper catches the same bug.
- **Delete**: name the remaining proof, or explain why no independent contract
  exists. No contract needs no artificial replacement. Missing evidence means
  retain pending investigation.

Before any deletion, record the old and new tier and inspect CI routing,
parameter rows, negative/error branches, callers, and the reason the test exists.
An internal duplicate can disappear while its boundary proof remains. An
independent real-engine contract must keep equal or stronger proof.

## 4. Repair and prove preservation

Work in small owner batches. Keep production fixes distinguishable from test
cleanup; respect tests-only scope and report any required production repair.

1. Replace source recognition and self-supplied answers with execution through
   the smallest honest production boundary. Expected values come from a spec,
   reviewed recording, independent model, or explicit example, not the SUT's
   constants or the double's implementation.
   A captured result can be a deliberate compatibility characterization; label
   and review it using [golden-file guidance](golden-file-testing.md). Comparing
   the SUT with its own fresh output establishes repeatability, not independent
   correctness.
2. Check negative controls reach the intended guard. Rejecting for unrelated
   missing configuration, fixture setup, or an earlier validation is no proof of
   the claimed rejection. A loop whose assertions never run supplies no evidence
   for its per-item claim; direct emptiness assertions can be valid contracts.
3. For a retained contract moved into a keeper, choose a plausible fault from
   what the old assertion could detect. Use isolated scratch copies/worktrees;
   do not mutate a checkout while tests are running. Run old and new tests
   against the **same** fault and record:

   | Fault / contract | Old tests | Keeper | Interpretation |
   |---|---|---|---|
   | Concrete production change | Fail/pass/unrun and reason | Fail/pass/unrun and reason | Preserved, stronger, lost, or unknown |

   Old fails/new passes is a possible lost check to resolve. Old passes/new
   fails shows additional sensitivity only if the failure is for the intended
   behavior. Both pass calls for investigation; equivalent or unreachable
   mutations are not automatically missing tests. Restore mutated source
   byte-for-byte. Do not pursue a mutation-score target or schedule a new lane
   by default; see [mutation testing](mutation-testing.md).
   For suspected implementation locks or custom checkers, also exercise a
   representative allowed change that must stay green: for example, JSON
   whitespace/key reordering when only parsed meaning is promised. Keep a real
   defect control alongside it. Preserve exact bytes, item order, or integrity
   checks when those are the independent contract. Catching more faults is not
   an improvement if harmless changes now fail.
4. A product bug needs an observed failing control and passing repaired run on
   the same harness where feasible. Report unavailable red/control evidence.
   A baseline failure is not permission to delete the failing test.
5. Run keeper/owner and relevant sibling tests, then required changed checks.
   Check deleted tests did not orphan support files, imports, exports, or CI
   entries. Search documentation for their descriptions as well as names.
   Delegate broad proof to the repository's normal CI when appropriate.

Choose checks in proportion to the change. Deleting a test with no independent
contract does not require inventing a mutation. When a compiler replaces a
type-level check, demonstrate that removing the relevant member fails the
actual typecheck, rather than building a mutation-testing program around it.

## 5. Review and hand off

For substantial removal, independently compare the deleted assertions against
the keepers, with special attention to error rows, persisted fields, ordering,
and external-system fidelity. Add production-correctness review when production
code or an external-system double changes. Review is useful when it checks
specific preservation risks; a fixed number of reviewers is not a requirement.

Report decisions, contracts retained/lost/restored, commands and actual results,
control/fault evidence, CI state at the pushed SHA, and unresolved gaps. Separate
test/support changes from production changes and any product defects discovered.
Do not claim quality from a lower test count or a green-only run.

## Reusable task brief

```text
Use testing-best-practices to audit and improve existing tests for <owner/boundary>.
Scope: <paths and allowed production changes>. Budget: <time/size>.
Read the skill's references/test-audit.md and relevant language/tier references.
Establish CI liveness and a pinned baseline; discover candidates, then inspect
their production owners, fixtures, callers, and history. Record retain/repair/
consolidate/delete decisions, independent expected-value sources, and remaining
proof before edits. Repair the highest-risk false-confidence cases through real
boundaries. For moved contracts, compare old and keeper tests against the same
credible faults; explain no-contract deletions. Treat baseline product failures
as defects. Validate focused proof and required gates, review lost coverage, and
report exact evidence and gaps. No deletion, assertion, or mutation-score quota.
```
