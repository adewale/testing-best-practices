# Eval 4 (post-rebase): Write Go cache tests

## Criteria

| # | Criterion | Pre | Post | Evidence |
|---|-----------|-----|------|----------|
| 1 | Uses Go stdlib testing (not testify) | PASS | PASS | Imports only `fmt sync testing time` |
| 2 | Table-driven with t.Run | PARTIAL | PASS | Both TestSetGet_RoundtripsValues AND TestDelete now use tables with t.Run |
| 3 | TTL expiry tested | PASS | PASS | TestGet_AfterTTLExpiry_ReturnsAbsent (with before+after assertions) |
| 4 | Concurrent access | PASS | PASS | Two concurrency tests: stress test + writers-vs-readers |
| 5 | Boundary cases (empty key, nil, zero TTL) | PARTIAL | PASS | All three now covered (empty key in table) |
| 6 | Acknowledges deterministic-time / clock injection | PASS | PASS | Comment on TestGet_AfterTTLExpiry references deterministic-time.md |
| 7 | 3+ assertions per test | PASS | PASS | Uses assertGet/assertLen helpers with t.Helper() |
| 8 | Tests Clear method | PASS | PASS | Two tests including reuse-after-clear |

**Score: 8/8** (up from 7/8)

References loaded by agent: SKILL.md, go.md, deterministic-time.md, test-types.md, antipatterns.md, correctness-by-construction.md (partial)

Key qualitative changes:
- Agent loaded correctness-by-construction.md and explicitly did a Step-Zero check: noted that the cache's `interface{}` value type makes type-level constraints inapplicable
- Added empty-key case (missing pre-rebase)
- Added 2nd concurrency test (writers-vs-readers)
- Introduced assertion helpers `assertGet` and `assertLen` with `t.Helper()`
