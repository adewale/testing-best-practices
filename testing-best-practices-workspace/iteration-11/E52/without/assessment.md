# Assessment: `test_compute_score`

## Summary

The test provides very weak verification of `compute_score`. It catches almost nothing beyond Python's ability to return a number.

---

## Anti-Patterns Present

### 1. Not-Empty / Trivial Bound Assertion (P1)

The sole assertion is:

```python
assert 0 <= result <= 100
```

This is equivalent to a "not-empty" assertion — it only checks that the result falls within a range that `compute_score` *structurally guarantees* via `max(0, min(100, score))`. The clamp is unconditional; any numeric return from `heavy_calc` (or the fallback `0`) will always satisfy this bound. A completely broken implementation that always returns `42` would pass every iteration of this loop.

**Fix**: Assert specific expected output values for known inputs — e.g., `assert compute_score(known_input) == expected_value`.

---

### 2. Logical Defense-in-Depth / Silent Fallback Behavior (P2)

`compute_score` silently swallows all exceptions from `heavy_calc` and substitutes `0`. The test never verifies this fallback:

- It does not confirm that error-path inputs produce `0`.
- It does not confirm that valid inputs do *not* silently trigger the fallback (i.e., the test cannot distinguish a correct result from a silently suppressed crash).

The bare `except Exception: score = 0` is a "silent fallback behavior" signal from the antipatterns catalogue. The test actively conceals this hazard by checking only the final clamped range.

**Fix**: Test the error path explicitly — inject an input or mock that causes `heavy_calc` to raise, and assert the result is `0`. Also assert that normal inputs yield non-zero scores (or exact values), proving the fallback was not triggered silently.

---

### 3. Missing Sad Path (P2)

The loop iterates over `SAMPLE_INPUTS` with no indication that those inputs include:

- Invalid / malformed inputs
- Boundary values (e.g., inputs that should yield exactly `0` or `100`)
- Inputs that exercise the exception branch

Only happy-path coverage is implied. There are no tests for error conditions.

**Fix**: Add explicit test cases for: invalid input types, inputs expected to trigger the exception handler, boundary-producing inputs, and empty/null inputs.

---

### 4. Quantity Over Quality / Weak Assertion Density (P3)

The loop runs multiple inputs but each iteration carries only one weak assertion. High iteration count with a trivially satisfiable bound gives an illusion of thoroughness while catching no meaningful defects.

**Fix**: For at least a representative subset of `SAMPLE_INPUTS`, assert the exact expected score, not just range membership.

---

## What the Test Does NOT Verify

| Concern | Tested? |
|---|---|
| Correct score for any specific input | No |
| That `heavy_calc` is called at all | No |
| That exceptions are handled (fallback to 0) | No |
| That the clamp correctly caps values above 100 | No |
| That the clamp correctly floors values below 0 | No |
| Behavior on invalid / unexpected input types | No |

---

## Verdict

The test is almost entirely tautological. Because `max(0, min(100, score))` structurally enforces the only invariant being checked, this test would pass even if `compute_score` returned a constant, crashed silently on every input, or lost all its business logic. It provides negligible regression protection.
