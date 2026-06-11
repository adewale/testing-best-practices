# Assessment: `test_compute_score`

## Verdict: Weak — anti-pattern P1 "Asserting through fault-masking code"

The test passes even if `compute_score` is entirely broken.

---

## What the test checks

```python
assert 0 <= result <= 100
```

This is a range check on the final output.

---

## Why the test provides almost no coverage of the actual computation

`compute_score` contains two fault masks stacked on top of each other:

### Mask 1 — swallow-to-default

```python
try:
    score = heavy_calc(raw)
except Exception:
    score = 0
```

If `heavy_calc` raises for every input — including inputs where it should
succeed — `score` is silently set to `0`. A value of `0` then passes the
subsequent clamp and the test assertion unchanged. Every exception, whether
expected or catastrophic, is invisible to the test.

### Mask 2 — clamping

```python
return max(0, min(100, score))
```

Even if `heavy_calc` returns a wildly wrong numeric value (e.g., `99999`,
`-500`, or `NaN` coerced to `0`), the clamp forces the result into `[0, 100]`.
The final `assert 0 <= result <= 100` therefore always passes regardless of what
`heavy_calc` actually computed.

### Combined effect

A fault must be **Executed**, **Infect** program state, and **Propagate** to an
observable output to be caught (Voas & Miller). Here:

- Execution: the call to `heavy_calc` does run.
- Infection: a wrong value in `score` is produced.
- Propagation: **blocked** — the swallow-to-default replaces the infected
  `score` with `0`; the clamp then absorbs any remaining wrong numeric values.
  The infection never reaches the observable output in a form the test can
  distinguish from a correct result.

Mutants such as "replace `heavy_calc` body with `return -9999`" or "replace
entire body with `raise RuntimeError`" survive this test suite.

---

## Additional weaknesses

| Weakness | Detail |
|---|---|
| No exact expected values | Range assertions are documented as a weak oracle; a specific correct result for each `SAMPLE_INPUTS` element would catch regressions the range check cannot. |
| No sad-path coverage | There are no tests for inputs that *should* trigger the exception path vs. inputs that should succeed, so the silent `except` branch is never intentionally exercised or verified. |
| `SAMPLE_INPUTS` is opaque | Without knowing the inputs or their expected outputs, it is impossible to tell whether any interesting or boundary cases are included. |

---

## How to fix

1. **Test `heavy_calc` directly** (before either mask) with specific expected
   values, so a wrong computation fails immediately without being absorbed.

2. **Test the exception path explicitly**: use a test double that raises a known
   exception and assert that `compute_score` returns `0` — making the fallback
   behavior a deliberate contract rather than an invisible escape hatch.

3. **Assert exact expected values** for each sample input, not just the range:

   ```python
   assert compute_score(known_input) == expected_score
   ```

4. **Run mutation testing** on `heavy_calc` and `compute_score`; surviving
   mutants will map directly to the faults the two masks are hiding.

If clamping and the fallback-to-zero are the *specified contract* (i.e., the
function is documented to return a clamped, never-raising score), test those
behaviors directly with dedicated cases — but also test the underlying
`heavy_calc` separately so the computation behind the mask has its own coverage.
