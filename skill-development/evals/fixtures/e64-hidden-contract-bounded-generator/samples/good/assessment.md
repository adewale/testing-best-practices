# Assessment: `test_median_is_within_range`

## Verdict

A sound property test. The oracle is a real invariant (the median of a set lies within
its range) rather than a reimplementation of the median calculation, and the generator
bounds match the documented contract exactly.

## Generator bounds are contract-derived, not timid

Each constraint maps to a clause of the spec:

- `min_size=1` — the contract says a non-empty list is required and an empty list raises
  `ValueError`. Generating empty lists here would produce failures that are correct
  behavior, not bugs.
- `allow_nan=False`, `allow_infinity=False` — the contract explicitly leaves NaN and
  infinity undefined. `min(values) <= m <= max(values)` is not even well-defined with NaN
  present, so widening this would test a fictional contract.

These are the legitimate reasons to constrain a generator: the contract genuinely
excludes the input. They should stay as they are.

## Gaps worth closing

1. **The documented error path is untested.** The contract promises `ValueError` on an
   empty list, and nothing asserts it. Add a focused example test:
   `with pytest.raises(ValueError): median_of([])`.
2. **The range invariant is necessary but not sufficient.** Any value between the min and
   max passes, so a badly broken implementation returning `values[0]` would survive. Add
   a stronger property: for odd-length inputs the median is a member of the list, and for
   any input, half the values are `<=` it and half are `>=` it (a counting property is an
   independent oracle here).
3. **Consider pinning a boundary example** with `@example(values=[0.0])` so the
   single-element case runs first on every run.

## Summary

Keep the generator as written; the constraints are the contract. The improvements are in
oracle strength and covering the specified error path, not in widening the input space.
It is not over-constrained: do not remove `min_size`, and do not set
`allow_nan=True` or widen the finite-float domain.
`allow_nan=True` is not appropriate for the documented domain. Generate an
empty list in a separate error-path test and assert `ValueError`; do not widen
the non-empty median property to admit it.
