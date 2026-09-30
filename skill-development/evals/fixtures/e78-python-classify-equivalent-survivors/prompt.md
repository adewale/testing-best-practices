A mutation run on `keyphrase.py` left three survivors:

1. `_before`: `return a[0] < b[0]` became `return a[0] <= b[0]`
2. `_score`: `if phrase in _CACHE:` became `if False:`
3. `top_phrases`: `if score >= MIN_SCORE:` became `if score > MIN_SCORE:`

Write `test_keyphrase.py` so that the tests kill all three survivors.
