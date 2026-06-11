# Assessment: test_set_volume_clamps

**Antipattern: this is asserting through fault-masking code.** The
`max(0, min(100, v))` clamp hides faults — it forces the output into a valid
range so a broken value can never be observed.

## Recommendations
- Remove the clamp and let invalid input raise, so faults can propagate to the
  caller instead of being silently masked.
- Don't clamp inside the function; validate at the boundary and surface the
  error.
