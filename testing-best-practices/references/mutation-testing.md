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

## Practical guidance

- Don't run on every commit — too slow. Run nightly or weekly.
- Focus on critical modules, not the whole codebase.
- Surviving mutants in security code are P0 issues.
- 80% mutation score with 70% coverage > 95% coverage with 50% mutation score.
