# Eval 8 (post-rebase): Assess Go weak tests

## Criteria

| # | Criterion | Pre | Post | Evidence |
|---|-----------|-----|------|----------|
| 1 | Identifies t.Log instead of t.Error | PASS | PASS | P0, all 5 tests by line |
| 2 | Identifies sleep-based TTL as flaky | PASS | PASS | P0.3 cites deterministic-time.md explicitly |
| 3 | Recommends clock seam / virtualization | PASS | PASS | P0.3 + P2 architectural finding: "clockwork.Clock" injected |
| 4 | Identifies missing concurrency tests | PASS | PASS | P2: "central invariant... completely unverified" |
| 5 | Identifies no table-driven tests | PASS | PASS | P3 |
| 6 | Identifies unused return values | PASS | PASS | P0.1 "value `val` is explicitly discarded" |
| 7 | Output is structured | PASS | PASS | P0/P1/P2/P3 sections |
| 8 | Identifies missing Clear method coverage | PASS | PASS | P1 missing sad-path/boundary |

**Score: 8/8** (unchanged)

References loaded by agent: SKILL.md, go.md, antipatterns.md, deterministic-time.md

Key qualitative changes:
- Post-rebase adds a NEW finding under P2: "No property-based / invariant tests" referencing SKILL.md §4 and §10 (correctness by construction tactic A)
- Adds an explicit Kent Beck scorecard table at the end
- Otherwise substantively the same depth and structure
