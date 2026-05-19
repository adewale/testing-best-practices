# Eval 10 (post-rebase): Characterization tests for Go cache

## Criteria

| # | Criterion | Pre | Post | Evidence |
|---|-----------|-----|------|----------|
| 1 | Uses Go stdlib testing | PASS | PASS | Imports only `sync testing time` |
| 2 | Records observed behavior, not opinions | PASS | PASS | Comments: "Surprising-but-current behavior", "Lock that in", "current behavior" |
| 3 | Documents surprising/edge-case behaviors | PASS | PASS | Negative TTL never expires; Len includes expired (no lazy eviction); nil-value storable; empty key valid; overwrite resets TTL |
| 4 | Covers Set, Get, Delete, Len, Clear | PASS | PASS | All five tested explicitly |
| 5 | Acknowledges time-dependence + strategy | PASS | PARTIAL | Uses short real sleeps; no explicit comment recommending Clock interface during refactor (pre-rebase had this) |
| 6 | 3+ assertions per test (mostly) | PARTIAL | PARTIAL | Similar density to pre-rebase; concurrency test has 1 meaningful assertion |

**Score: 5/6** (down from 5.5/6 — slight regression on time-acknowledgment)

References loaded by agent: SKILL.md, go.md, characterization-testing.md, antipatterns.md (NOT deterministic-time.md, NOT correctness-by-construction.md)

Key qualitative changes:
- Post-rebase agent did NOT load deterministic-time.md (pre-rebase did). The trigger ("Code depends on time, timers, scheduling") should have fired but the agent skipped it.
- Pre-rebase had a header comment recommending introducing a Clock interface during the refactor; post-rebase has no such recommendation
- Both versions cover similar surprising behaviors. Pre-rebase additionally tested "stored slice by reference" (mutation visible through cache); post-rebase covered heterogeneous types more broadly
- Net: a small regression on the deterministic-time signal, offset by slightly more consistent style
