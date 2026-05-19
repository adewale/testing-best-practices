# Types vs Tests section: iter 2 evaluation

## The experiment

Test whether SKILL.md §10 "Types vs tests" changes agent behavior on
loose-typed code (where stronger types could replace runtime validation).

**Three eval fixtures** with the same shape across Python/TS/Go: a service
with primitive-typed parameters (str/int/string/number/int64) and heavy
runtime validation that could be lifted into types.

**Three conditions** (all 3 evals × 3 conditions = 9 runs):
- Without §10 (control)
- With §10 v1 (12-line abstract framing)
- With §10 v2 (added "probe forbidden states, mark deletable" sentence)

## Scoring rubric (5 criteria, +1 Go bonus)

1. Identifies types-can-replace-tests opportunity
2. Recommends specific types/refactor
3. Tactic-A invariant proofs (PBT)
4. Tactic-B model-gap probes for forbidden states
5. Marks redundant tests as deletable / explicitly avoids per-layer duplication
6. (Go only) Notes the weakly-enforced caveat (Go zero value)

## Results

| Eval | Without §10 | With §10 v1 | With §10 v2 |
|------|-------------|-------------|-------------|
| Python user_service | 4.5/5 | 4.5/5 | **5/5** |
| TypeScript order_service | 4.5/5 | 5/5 | **5/5** |
| Go payment_service | 4/6 | 5.5/6 | **6/6** |
| **Total** | **13/16 (81%)** | **15/16 (94%)** | **16/16 (100%)** |

## v2 §10 (final, 17 lines)

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

When the type is too loose for an invariant it should carry, the test
surface explodes. Probe each forbidden state the model still permits, and
mark those tests as deletable when the type tightens (with `xfail`,
`@deprecated`, or an inline comment). When you tighten a type, delete the
now-redundant tests in the same commit. See §11 for the deep treatment.
```

## What v2 changed in agent behavior

The "probe forbidden states and mark deletable" sentence is the key. In
v2 runs, agents consistently:

1. **Wrote explicit deletable-on-refactor markers** in their test files:
   - Python: `TODO[CBC]: every test in this class collapses to a single EmailAddress.parse PBT once email is parsed at the boundary`
   - TypeScript: `When the type tightens (CustomerId branded type, NonEmpty<string[]>, MoneyCents newtype), most of these tests should be DELETED`
   - Go: `If/when the API switches to UserID, Money, Currency newtypes with smart constructors, these tests become deletable: the compiler will enforce the invariant.`

2. **Increased tactic-B depth**: Go v2 probes 5 model gaps (vs 4 in v1, 1 in
   without). Python v2 maintains its model-gap finding (bool-as-int) and
   explicitly frames the rejected-by-shape tests as "deletable after type
   tightening."

3. **Sharpened the weakly-enforced caveat** (Go-only):
   - v2 Go cites both `go.md` AND `correctness-by-construction.md` for the
     zero-value caveat
   - Explicitly says: "A pure tactic-B test ('invalid Payment cannot exist')
     would pass vacuously and lie"

## Per-language delta (without → with v2)

- **Python**: +0.5 — added explicit `TODO[CBC]` deletable markers
- **TypeScript**: +0.5 — moved from documenting silent-fallback to explicit
  "should be DELETED" framing for malformed-input tests
- **Go**: +2.0 — gained the weakly-enforced caveat (clear reference to CBC
  doc) AND increased model-gap coverage from 1 test to 5 tests

## Verdict

**v2 §10 produces improvements in Python, TypeScript, and Go.** The single
17-line section, abstract and language-neutral, shifts agent behavior on
loose-typed code toward (a) deeper model-gap probing and (b) explicit
deletable-when-refactored markers.
