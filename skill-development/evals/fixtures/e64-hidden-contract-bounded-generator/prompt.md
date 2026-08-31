# Assess this property test

`median_of` is documented as: "Requires a non-empty list of finite floats. Raises
`ValueError` on an empty list; behavior on NaN or infinity is undefined."

```python
from hypothesis import given, strategies as st

@given(values=st.lists(
    st.floats(allow_nan=False, allow_infinity=False),
    min_size=1,
))
def test_median_is_within_range(values):
    m = median_of(values)
    assert min(values) <= m <= max(values)
```

Write an assessment (assessment.md) of this property test.
