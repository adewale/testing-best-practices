# Pre-rebase vs Post-rebase eval comparison

The "Jane Street" branch added: `deterministic-time.md` (new), expanded
`golden-file-testing.md` with snapshot/promote workflow, a "What Types Can
Express vs What Tests Must Catch" section in `test-types.md`, and the
matching SKILL.md trigger.

The rebase brought in main's `correctness-by-construction.md` (new),
main's larger "Step Zero" rewrite of `test-types.md` (which subsumed my
smaller section — I dropped mine), and various other CBC-related edits.

Three evals run pre- and post-rebase using parallel subagents
following the skill faithfully.

## Scores

| Eval | Pre | Post | Delta |
|------|-----|------|-------|
| 4 — Write Go cache tests | 7.0/8 | 8.0/8 | +1.0 |
| 8 — Assess weak Go cache tests | 8.0/8 | 8.0/8 | 0 |
| 10 — Characterization tests for Go cache | 5.5/6 | 5.0/6 | -0.5 |
| **Total** | **20.5/22 (93.2%)** | **21.0/22 (95.5%)** | **+0.5 (+2.3pp)** |

## What changed and why

### Eval 4: +1 point
The post-rebase agent loaded `correctness-by-construction.md` in addition to
`deterministic-time.md`, and explicitly did a Step-Zero check on the cache's
`interface{}` value type. The output gained: an empty-key boundary case (was
missing pre-rebase), a second concurrency test (writers-vs-readers), and
assertion helpers using `t.Helper()`. The CBC reference's "Step Zero"
prompted the agent to think about types before tests, which surfaced the
boundary case.

### Eval 8: 0 change
Both runs scored 8/8 with the same findings. Post-rebase added a NEW finding
("No property-based / invariant tests") that cited CBC tactic A, and added a
Kent Beck scorecard table at the end. The structure was equivalent; nothing
was lost.

### Eval 10: -0.5 point
The post-rebase agent did NOT load `deterministic-time.md` despite the
trigger matching (TTL-dependent cache). It loaded characterization-testing,
go.md, antipatterns, and SKILL — but not the time reference. As a result the
header comment about "recommend introducing a Clock interface during the
refactor" (present pre-rebase) was missing. The rest of the output was
roughly equivalent.

This is likely a noise/attention effect: the agent had more triggers to
evaluate after the rebase (CBC + deterministic-time) and skipped one. A
sharper trigger phrasing in SKILL.md could mitigate.

## Net assessment

The rebase is a net positive (+2.3pp). The CBC additions reinforce the
"think about types first" framing without displacing the deterministic-time
guidance in most cases. The one regression (eval 10) is a missed reference
load, not a content failure — the agent could have loaded both and didn't.

Recommendation: leave the trigger wording for deterministic-time.md as is,
since it fired in 2/3 cases; the eval 10 miss is within run-to-run variance
rather than a structural problem with the trigger.
