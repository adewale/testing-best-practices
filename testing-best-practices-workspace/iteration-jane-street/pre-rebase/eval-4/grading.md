# Eval 4 (pre-rebase): Write Go cache tests

## Criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Uses Go stdlib testing (not testify) | PASS | Imports only `fmt sync testing time` |
| 2 | Table-driven with t.Run | PARTIAL | `TestSet_StoresVariousValueTypes` uses table+t.Run; other tests are individual functions |
| 3 | TTL expiry tested | PASS | `TestGet_ExpiredKeyReturnsFalse` |
| 4 | Concurrent access | PASS | `TestConcurrent_ReadersWritersAreSafe` (50 goroutines × 200 ops, 4 roles) |
| 5 | Boundary cases (empty key, nil, zero TTL) | PARTIAL | zero TTL: yes; nil value: yes (table); empty key: NOT tested |
| 6 | Acknowledges deterministic-time / clock injection | PASS | Explicit comment on `TestGet_ExpiredKeyReturnsFalse` noting missing clock seam |
| 7 | 3+ assertions per test | PASS | Most tests have 3 (ok, value, Len) |
| 8 | Tests Clear method | PASS | `TestClear_*` (RemovesAllItems, EmptyCacheIsNoop, AllowsReuse) |

**Score: 7/8** (6 PASS + 2 PARTIAL counted as 0.5 each = 7.0)

References loaded by agent: SKILL.md, go.md, deterministic-time.md, antipatterns.md, test-types.md
