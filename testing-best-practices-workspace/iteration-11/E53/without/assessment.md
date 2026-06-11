# Assessment: `TestParseAndScore`

## Summary

The test is severely under-specified. It exercises `ParseAndScore` only for a vague non-negativity invariant, leaving the vast majority of the function's behavior completely unverified.

---

## Anti-patterns present

### 1. Not-empty / not-negative assertion (P1)

The sole assertion is:

```go
if got := ParseAndScore(raw); got < 0 {
    t.Errorf("negative score %d", got)
}
```

This checks only that the result is not negative. The function clamps output to `[0, 100]` and recovers panics by returning `0`. Any implementation that always returns `42` — or always returns `0` — would pass every assertion here. The test cannot distinguish correct behavior from a stub.

**What is not verified:**
- The upper bound: values above `100` are never checked, so a bug that fails to clamp at the top is invisible.
- The actual numeric content: no test case checks that a known input produces a known score.
- The clamping logic: the `s < 0 → 0` and `s > 100 → 100` branches are never exercised with inputs that trigger them.
- The panic-recovery path: no test passes data that causes `mustParseAndScore` to panic, so the `recover()` branch is dead in the test suite.

### 2. Missing sad path (P2)

All tests run over `samples`, which appears to be a set of presumably valid inputs. There are no tests for:
- Malformed / invalid input (which would trigger the panic-recovery path).
- Empty string.
- Inputs that produce scores at the boundary values (`0` and `100`).
- Inputs that produce raw scores below `0` or above `100` (to exercise the clamp).

The anti-pattern: **no tests for invalid input, errors, or edge cases** — only a soft sweep over an uncharacterised happy-path corpus.

### 3. Opaque test corpus (`samples`) (P2 — quantity over quality)

The loop runs over `samples`, but the test provides no visibility into what those samples are or what scores they should produce. Even if the corpus is large, every test reduces to the same single weak assertion. This is a coverage illusion: many inputs, one invariant, zero specificity.

---

## What a good test suite would include

| Scenario | Why it matters |
|---|---|
| Known input → exact expected score | Verifies actual parsing and scoring logic |
| Input producing raw score < 0 | Exercises lower-clamp branch |
| Input producing raw score > 100 | Exercises upper-clamp branch |
| Malformed / panic-inducing input | Exercises `recover()` branch; asserts result is `0` |
| Empty string | Boundary / edge case |
| Score exactly at `0` and `100` | Boundary values |

---

## Verdict

The test provides a false sense of coverage. It will pass even if the implementation is completely wrong, as long as it never returns a negative number. The three primary failures are:

1. **Assertion is too weak** — only checks `>= 0`, not correct values.
2. **No sad-path tests** — the panic-recovery branch is entirely untested.
3. **No expected-value tests** — no input is paired with the score it should produce, so no regression can ever be caught.
