# Eval 8 (pre-rebase): Assess Go weak tests

## Criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Identifies t.Log instead of t.Error | PASS | P0 finding, called out all 5 tests by line |
| 2 | Identifies sleep-based TTL test as flaky | PASS | P1 finding on TestTTL with explicit citation to deterministic-time.md |
| 3 | Recommends clock seam / virtualization for TTL fix | PASS | Recommends adding `nowFunc func() time.Time` field, references Strategy 2 |
| 4 | Identifies missing concurrency tests | PASS | P2 finding mentions `sync.RWMutex` and `-race` |
| 5 | Identifies no table-driven tests | PASS | P1 finding |
| 6 | Identifies unused return values / discarded value | PASS | P0 not-empty/throwaway: "value is explicitly discarded" |
| 7 | Output is structured (severity-prioritized) | PASS | P0/P1/P2/P3 sections with findings within each |
| 8 | Identifies missing Clear method coverage | PASS | P2 finding: "Clear is entirely untested" |

**Score: 8/8**

References loaded by agent: SKILL.md, go.md, antipatterns.md, deterministic-time.md
