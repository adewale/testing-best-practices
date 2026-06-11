# Assessment: `TestParseAndScore`

## Summary

The test is weak. It contains two overlapping anti-patterns that together make it nearly useless as a correctness signal.

---

## Anti-Pattern 1 — Asserting Through Fault-Masking Code (P1)

`ParseAndScore` contains two independent fault masks:

1. **Recover-to-zero**: The `defer recover()` absorbs any panic from `mustParseAndScore` and returns `0`.
2. **Clamping**: The `if s < 0 { s = 0 } else if s > 100 { s = 100 }` clamps the raw score into `[0, 100]`.

The sole assertion is:

```go
if got := ParseAndScore(raw); got < 0 {
    t.Errorf("negative score %d", got)
}
```

This checks `got < 0`. The clamp already guarantees `got` is never negative — the assertion is therefore **tautologically true regardless of what `mustParseAndScore` does**. If `mustParseAndScore` panics on every input, `got` is `0` and the test passes. If `mustParseAndScore` returns garbage values like `-9999` or `99999`, the clamp normalizes them and the test passes. A fault in the parsing or scoring logic can be fully executed, infect the internal data state, and still never propagate to the asserted output — exactly the Voas & Miller testability failure described in anti-pattern #14.

**What the test cannot catch:**
- `mustParseAndScore` always panicking (silenced by `recover`)
- `mustParseAndScore` returning completely wrong scores (silenced by clamp)
- Off-by-one errors near the 0 or 100 boundary
- Any semantic error in the scoring logic

---

## Anti-Pattern 2 — Missing Sad Path / No Exact-Value Assertions (P2)

Even setting aside the masking problem, the test only checks a range bound (`< 0`), not expected values. For every input in `samples`, there is presumably a known correct score. The test never checks whether `ParseAndScore` returns the *right* answer — only that the answer is non-negative. This is the "not-empty assertion" pattern applied to a numeric range: `return 0` for all inputs satisfies every assertion.

There are also no sad-path cases:
- No test for malformed/unparseable input (to verify the `recover` path produces a documented result)
- No test for inputs that should produce a score near 0 or near 100 to probe boundary behavior
- No test for the exact clamping boundaries (e.g., raw score of -1 should become 0; raw score of 101 should become 100)

---

## What Good Tests Would Look Like

1. **Test `mustParseAndScore` directly** (bypassing the masks) with exact expected values for each fixture, so a broken computation fails immediately without the clamp or recover absorbing the error.

2. **Test the clamp boundaries explicitly**: verify that a known input producing a raw score just below 0 yields `0`, and one just above 100 yields `100`. This tests that the mask *is* the specified behavior for those inputs, not that it hides other faults.

3. **Test the panic/recovery path explicitly**: provide an input known to cause `mustParseAndScore` to panic and assert the result is `0` (documenting the fallback as the contract, not leaving it untested).

4. **Use exact expected values** in the happy-path loop, not just range checks:

```go
for _, tc := range testCases {
    got := ParseAndScore(tc.raw)
    if got != tc.want {
        t.Errorf("ParseAndScore(%q) = %d, want %d", tc.raw, got, tc.want)
    }
}
```

---

## Verdict

The test provides near-zero defect-detection value. The two fault masks (`recover` and clamp) guarantee the assertion `got < 0` is always false, making the test permanently green independent of the correctness of `mustParseAndScore`. This is a textbook instance of asserting through fault-masking code (anti-pattern #14), compounded by the absence of exact expected values and any sad-path coverage.
