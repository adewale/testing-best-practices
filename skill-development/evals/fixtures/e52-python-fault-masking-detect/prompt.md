# E52 Assess a test behind fault-masking code

Assess the quality of this Python test. The function and its test:

```python
def compute_score(raw):
    try:
        score = heavy_calc(raw)   # complex scoring
    except Exception:
        score = 0
    return max(0, min(100, score))

def test_compute_score():
    for raw in SAMPLE_INPUTS:
        result = compute_score(raw)
        assert 0 <= result <= 100
```

Write an assessment (assessment.md) of how well this test verifies `compute_score`.
