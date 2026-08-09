# Mutation Testing

Measures whether tests actually *catch bugs*, not just execute code. Introduces
small faults ("mutants") and checks whether tests detect them.

## When to recommend

- Coverage is high (80%+) but you suspect tests are weak
- Security-critical code (XSS sanitization, auth, crypto)
- Financial calculations where off-by-one = real money
- After a quality audit reveals low assertion density

## Why it works: the fault model

Mutation testing is the empirical form of Voas & Miller's testability model. For
a seeded fault (mutant) to be caught, three things must happen: it must be
**Executed**, it must **Infect** the data state, and the infection must
**Propagate** to an observable output the test asserts on. A *surviving* mutant
means one of those links broke — most often propagation: the code masks the
infected state before it reaches the assertion (see "Asserting through
fault-masking code" in `references/antipatterns.md`). So surviving mutants in
clamping / swallow-to-default / high domain-to-range code aren't just test gaps;
they pinpoint *where the code is hiding faults from any possible output-only
test*. That's the signal to assert on internal/pre-mask state, not to add more
end-to-end cases.

## How it works

1. Tool modifies source: `>=` becomes `>`, `True` becomes `False`, etc.
2. Test suite runs against each mutant
3. If a test fails → mutant "killed" (good)
4. If all tests pass → mutant "survived" (test gap found)
5. Mutation score = killed / total

## Tools by language

| Language | Tool | Notes |
|----------|------|-------|
| Python | mutmut | Pragmatic defaults, caches between runs |
| JavaScript/TypeScript | Stryker | Most mature, incremental support |
| Java/JVM | PIT (pitest) | Fast, IDE integration |
| Go | gremlins | Mutation testing for Go |
| Rust | cargo-mutants | Mutation testing for Rust |

## Bug families: sweep the class, not the symptom

Mutation testing asks "what could break that no test catches?" from the tool's
side. After a real bug escapes, you can ask it from the bug's side, more cheaply:
**treat the fix as one instance of a family and search for the family.**

A worked example. A tempo handler used `clamp(v)` implemented as
`Math.max(MIN, Math.min(MAX, v))` — range control mistaken for type control,
because a non-numeric value arrives as `NaN` and sails through both
comparisons. Searching for the *family* rather than the symptom found the same
shape in a swing handler in the same factory, and an effects handler that
type-checked four of its nine numeric fields. Its mirror image lived in the
validator meant to be the second opinion: `v < MIN || v > MAX` is `false` for
`NaN`, so the guard passes exactly the value it exists to reject.

How to run one:

1. Name the family, not the bug. "Unvalidated numeric input reaches storage"
   generalizes; "tempo accepts NaN" does not.
2. Search for the *shape* — the helper, the comparison form, the coercion — not
   the identifier you just fixed.
3. Write the regression test as a **table over every member of the family**
   (every numeric field on that handler), so the next field added fails here.
4. **Record the families that came up empty.** Five of nine in that sweep had no
   instances; that is the half of the result that bounds the search and stops
   the next person redoing it.

The languages differ but the trap does not: `NaN` comparisons in JS/Python/Go
floats, `None` in Python comparisons, zero-values in Go, `null` coercion in
TypeScript. Any guard written as a range check inherits the type check it never
made.

## Practical guidance

- Don't run on every commit — too slow. Run nightly or weekly.
- Focus on critical modules, not the whole codebase.
- Surviving mutants in security code are P0 issues.
- 80% mutation score with 70% coverage > 95% coverage with 50% mutation score.
