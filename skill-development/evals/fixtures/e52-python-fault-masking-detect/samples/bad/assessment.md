# Assessment: test_compute_score

The test looks reasonable. It iterates over several sample inputs and checks
that the score stays within the valid 0–100 range, which is the main contract.

## Suggestions
- Add a few more sample inputs for better coverage.
- Add a docstring describing the test's intent.
- Consider parametrizing with `@pytest.mark.parametrize` for readability.

Overall the test provides good coverage of `compute_score`.
