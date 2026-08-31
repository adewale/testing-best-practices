# Assessment: `test_median_is_within_range`

## Verdict

The property is reasonable but the generator is badly over-constrained, which is the
most common way a property test underperforms.

## The generator is too narrow

`min_size=1`, `allow_nan=False`, and `allow_infinity=False` all restrict the input space
and give a false sense of safety. Broad generators find more bugs; preemptively adding
bounds means you will never discover how the function behaves at the edges.

Recommended fixes:

- **Remove `min_size=1`** so empty lists are generated. If `median_of([])` blows up, that
  is exactly the kind of bug property testing exists to find.
- Set `allow_nan=True` and drop `allow_infinity=False` so the full float domain is
  explored. NaN handling is a classic source of defects and should not be excluded.
- The test should also generate infinite values to check the range invariant holds there.

## Summary

Widen the generator to the full float domain and remove the size constraint. The property
itself can stay as written.
