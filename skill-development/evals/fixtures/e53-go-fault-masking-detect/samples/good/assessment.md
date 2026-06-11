# Assessment: TestParseAndScore

**Severity: P1 — the test cannot catch faults in parsing or scoring.**

`ParseAndScore` masks faults before the result is observed:
- The `defer`/`recover` converts *any* panic from `mustParseAndScore` into a
  silent `score = 0` (the named return's zero value).
- The `if s < 0 { s = 0 } else if s > 100 { s = 100 }` clamp forces the result
  into [0, 100].

The test only checks `got < 0`. That can never fire — the clamp guarantees a
non-negative result. `mustParseAndScore` could panic on every input or return
garbage and the test would still pass: the fault is executed but its infection
is recovered/clamped away before it can propagate to the assertion.

## Recommendations
- Assert **exact expected scores** for known inputs, not just `>= 0`.
- Test `mustParseAndScore` **directly** so a parsing/scoring fault fails a test.
- Remove the blanket `recover` (or re-panic after recording) so unexpected
  panics are visible rather than silently turned into 0.
- Use mutation testing (gremlins); surviving mutants mark exactly the faults the
  recover and clamp hide.
