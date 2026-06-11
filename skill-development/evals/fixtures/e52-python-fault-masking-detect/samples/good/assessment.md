# Assessment: test_compute_score

**Severity: P1 — the test cannot catch faults in the scoring logic.**

`compute_score` masks faults twice before any output is observed:
1. The blanket `except Exception: score = 0` swallows *any* failure in
   `heavy_calc` and substitutes a valid-looking 0.
2. `max(0, min(100, score))` clamps any out-of-range result into [0, 100].

The test asserts only `0 <= result <= 100`. That assertion is true *by
construction* — the clamp guarantees it. `heavy_calc` could be completely
broken (raise on every input, or return 9999) and every test would still pass:
the fault is executed but its infection never propagates to the asserted output.
This is "asserting through fault-masking code" — weak evidence dressed as a
green suite.

## Recommendations
- Assert **exact expected scores** for known inputs, not the output range.
- Test `heavy_calc` **directly** so a fault there fails a test, and assert the
  value **before** it is clamped.
- Narrow or remove the blanket `except` — let an unexpected exception propagate
  (or catch a specific, expected one) so failures are visible.
- Run mutation testing on this module; surviving mutants are exactly the faults
  the clamp and the swallow are hiding.
