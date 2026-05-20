# Iteration 1: Types vs tests section as principle §10

## Section added to SKILL.md (12 lines):

```markdown
### 10. Types vs tests

Types and tests answer different questions:

- **Types** answer *can this bug exist?* — invariants enforced at compile
  or parse time, free at runtime
- **Tests** answer *does observable behavior match the spec?* — invariants
  enforced at runtime, every run

A type and a test that assert the same invariant are redundant — pick one.
Types are cheaper when the language enforces them. Tests are mandatory for
what types can't reach: behavior, integration, liveness, performance,
concurrency, and the external world.

When you tighten a type, delete the now-redundant tests in the same commit.
When the language can't carry the invariant in the type system, the test
is the only option — see §11 for the deep treatment and the caveats for
weakly-enforced languages.
```

Renumbered: §10 (Types vs tests, new), §11 (Correctness by construction, was §10), §12 (sad path, was §11). Internal §10/§11 cross-references updated.

## Eval results

| Eval | Prior best | Iter 1 | Δ |
|------|-----------|--------|---|
| 4 — Go cache TTL tests | 8/8 (post-rebase) | **8/8** | 0 |
| 11 — Python subscription (CBC) | 8/8 (iteration-cbc) | **8/8** | 0 |
| 12 — Go order state machine (CBC) | 8/8 (iteration-cbc) | **8/8** | 0 |
| **Total** | **24/24** | **24/24** | **0** |

## Per-eval observations

### Eval 4 (Go cache write — 8/8)
Agent loaded SKILL.md, go.md, deterministic-time.md, antipatterns.md. Did NOT load
correctness-by-construction.md — correctly, since the cache uses `interface{}`
values where types can't carry an invariant. The §10 framing seems to have
guided the agent away from a misplaced CBC check.

Coverage matches post-rebase best: empty key boundary, multiple concurrency
tests, explicit time-seam note recommending `clockwork.Clock`.

### Eval 11 (Python subscription — 8/8)
Agent loaded SKILL.md, python.md, correctness-by-construction.md (correctly
triggered), antipatterns.md. Output matches all 8 iteration-cbc criteria
including bonus findings (bool-as-int model gap, math properties for
can_upgrade).

The §10 abstract framing reinforced the agent's recognition that this module
is "a textbook case of logical defense-in-depth as antipattern."

### Eval 12 (Go order state machine — 8/8)
Agent loaded SKILL.md, go.md, correctness-by-construction.md (correctly
triggered), exhaustive-testing.md (correctly triggered for the 4×3 state×method
matrix). Output matches all iteration-cbc criteria including the bonus catches
(unknown Status accepted by Cancel, Total's silent-fallback on negative
quantity).

Used `t.Errorf` rather than `t.Logf` for documented-gap tests — different from
iteration-cbc but consistent with "pin current behavior so a fix is deliberate."

## Verdict

The new `§10. Types vs tests` works on the first iteration:
- Short (12 lines)
- Abstract (no specific languages, no code examples)
- Explicit (named section in core principles)
- Holds eval 4 at 8/8 (matches post-rebase best)
- Holds evals 11 and 12 at 8/8 (matches iteration-cbc best)
- No regressions; the agent's reference-loading behavior is well-targeted

No further iteration needed.
