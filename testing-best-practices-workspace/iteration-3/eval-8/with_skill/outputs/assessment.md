# Test Quality Assessment: weak_tests.go

## Source Under Test

`evals/files/go_cache.go` implements a thread-safe in-memory key-value cache with TTL support. Public API: `New()`, `Set(key, value, ttl)`, `Get(key)`, `Delete(key)`, `Len()`, `Clear()`.

## Verdict: Failing -- these tests provide almost no protection

The test file contains 5 test functions. Every single one has critical defects. A mutation testing tool would likely achieve a near-100% mutation survival rate against this suite, meaning the tests catch almost no bugs.

---

## Step 1: Sabotage Detection

### P0 -- Logging not asserting (every test)

All five tests use `t.Log()` or `t.Logf()` where they should use `t.Errorf()` or `t.Fatalf()`. In Go, `t.Log` prints a message but **never fails the test**. This means every test in this file passes unconditionally, regardless of what the code under test does.

| Test | Line | Problem |
|------|------|---------|
| `TestSetAndGet` | 14 | `t.Log("expected key to exist")` -- should be `t.Errorf` |
| `TestGetMissing` | 23 | `t.Log("expected key to not exist")` -- should be `t.Errorf` |
| `TestTTL` | 33 | `t.Log("expected key to be expired")` -- should be `t.Errorf` |
| `TestDelete` | 43 | `t.Log("expected nil after delete")` -- should be `t.Errorf` |
| `TestLen` | 51-52 | No assertion at all -- `if c.Len() > 0 { // good enough }` does nothing |

**Impact**: You could replace the entire cache implementation with `return nil, false` for every method and all 5 tests would still pass. The test suite is functionally inert.

### P0 -- Discarded return value (TestSetAndGet)

Line 16: `_ = val` explicitly discards the retrieved value. Even if the `t.Log` were changed to `t.Errorf`, the test would only verify the boolean `ok` flag -- it would never verify that the correct value was returned. A cache that always returns `("wrong", true)` would pass.

---

## Step 2: Assertion Density

| Test | Assertions (real) | Assessment |
|------|--------------------|------------|
| `TestSetAndGet` | 0 | No real assertions (t.Log does not fail) |
| `TestGetMissing` | 0 | No real assertions |
| `TestTTL` | 0 | No real assertions |
| `TestDelete` | 0 | No real assertions |
| `TestLen` | 0 | No real assertions, empty if-body |

**Aggregate assertion density: 0 assertions across 5 tests.**

The target is 3+ meaningful assertions per test. This file has zero.

---

## Step 3: Mock-Reality Drift

Not applicable -- no mocks are used. The tests operate on the real `Cache` object, which is appropriate for an in-memory data structure.

---

## Step 4: Test Tier Integrity

These are unit tests testing a single in-memory object. This is correct for the type of code under test. No misclassification issues.

---

## Step 5: Coverage Gaps

Even if the `t.Log` calls were fixed to `t.Errorf`, there are significant coverage gaps:

### Missing functionality tests
1. **`Clear()` is never tested** -- one of the five public API methods has zero test coverage
2. **Value correctness is never checked** -- no test verifies the *value* returned by `Get()` is what was stored by `Set()`
3. **Overwrite/update behavior** -- no test for calling `Set()` twice with the same key
4. **Different value types** -- only strings and ints are stored, no test for structs, nil values, etc.

### Missing sad-path tests
5. **Delete a non-existent key** -- does it panic?
6. **Get after Clear** -- does Get return false after Clear?
7. **Empty string key** -- edge case
8. **Nil value storage** -- can you store and retrieve nil?

### Missing property tests
9. **TTL zero means never expires** -- not explicitly tested (TestSetAndGet uses ttl=0 but never verifies value)
10. **Concurrent access** -- the cache uses sync.RWMutex but no test exercises concurrent reads/writes

### Flaky test risk
11. **TestTTL uses `time.Sleep(200ms)`** -- this is a time-dependent test. Under load (slow CI machines), the sleep duration might not be enough, or the timing might cause flaky results. Better to inject a clock.

---

## Step 6: Mutation Testing Recommendation

This suite would benefit enormously from mutation testing, but the prerequisite is having tests that actually fail. Currently, mutation testing would show 100% mutation survival because the tests never fail regardless of code changes.

---

## Summary of Issues by Priority

| Priority | Issue | Count |
|----------|-------|-------|
| P0 | Logging not asserting (`t.Log` instead of `t.Errorf`) | 4 tests |
| P0 | Discarded return value (value never checked) | 1 test |
| P0 | Empty assertion body (TestLen) | 1 test |
| P1 | Zero assertion density across entire file | All tests |
| P1 | `Clear()` method completely untested | 1 method |
| P2 | No sad-path tests (empty key, nil value, delete missing) | Multiple |
| P2 | No concurrent access tests despite mutex usage | 1 |
| P2 | Flaky time-based test using `time.Sleep` | 1 test |
| P3 | Not using table-driven test pattern (Go convention) | All tests |

## Bottom Line

This test suite is security-theater for code quality. Every test passes unconditionally because `t.Log` never fails a test. The suite would not catch a single bug introduced into the cache implementation. It needs a complete rewrite with real assertions (`t.Errorf`/`t.Fatalf`), value verification, table-driven patterns, sad-path coverage, and concurrency tests.
