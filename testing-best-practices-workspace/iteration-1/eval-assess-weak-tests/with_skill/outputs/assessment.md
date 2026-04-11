# Test Quality Assessment: weak_tests.py

## Summary

The test suite for `url_parser.py` is **severely deficient**. It contains 7 test functions but would catch almost no real bugs due to pervasive weak assertions, a sabotaged test, a logging-not-asserting antipattern, and a mock-only "integration" test that tests the mock rather than real behavior. The suite has zero sad-path tests, zero property-based tests, and misses most of the parser's functionality.

**Overall Grade: F (1/10)**

---

## Step 1: Sabotage Detection

### P0 -- Logging not asserting

**`TestEdgeCases.test_unicode_url`** (line 30-32): Uses `print()` inside a conditional instead of `assert`. This test will **never fail** regardless of what `parse_url` returns. The `if` check detects a wrong result but only logs a warning -- the test still passes.

```python
if result["host"] != "xn--r8jz45g.jp":
    print(f"Warning: got {result['host']}")  # should be assert!
```

### P1 -- Unconditional skip without tracking issue

**`test_parse_empty`** (line 22-24): Skipped with `@pytest.mark.skip("broken after refactor")`. No issue link, no `skipif` condition, no expiry. This is silently accumulating tech debt -- the empty-string edge case is completely untested.

---

## Step 2: Assertion Density

| Test | Assertions | Quality | Verdict |
|------|-----------|---------|---------|
| `test_parse_basic` | 1 | `is not None` -- any dict passes | Weak (P1) |
| `test_parse_with_port` | 1 | `!= {}` -- any non-empty dict passes | Weak (P1) |
| `test_normalize` | 1 | truthiness -- any non-empty string passes | Weak (P1) |
| `test_parse_empty` | 1 (skipped) | checks host but test is skipped | Sabotaged (P1) |
| `test_unicode_url` | 0 | logs instead of asserting | Sabotaged (P0) |
| `test_very_long_url` | 1 | `is not None` -- weak | Weak (P1) |
| `test_normalize_integration` | 1 | tests mock return, not real behavior | Tautological (P3) |

**Average assertion density: 0.86 per test** (target: 3+)

Every test with an assertion uses a "not empty" check as its sole assertion. A function returning `{"garbage": True}` for all inputs would pass every non-skipped test. None of the tests verify specific field values (scheme, host, port, path, query, fragment).

---

## Step 3: Mock-Reality Drift

**`test_normalize_integration`** (line 44-50): Patches `url_parser.parse_url` and provides a hardcoded return value. The test then asserts `normalize_url` returns a specific string. Problems:

1. **Testing the mock**: The asserted output (`"https://example.com/"`) is a direct reconstruction of the mock's return value. If `parse_url` were broken, this test would still pass.
2. **Mock-reality drift**: The mock returns `{"port": None}`, but the real `parse_url` might return a different structure. Nothing validates the mock matches reality.
3. **Mislabeled**: Called an "integration test" but mocks its only dependency -- it is a unit test in disguise.

---

## Step 4: Test Tier Integrity

- The `test_normalize_integration` function claims to be an integration test but mocks everything. It belongs in `tests/unit/` if it exists at all (P2).
- No actual integration test exercises `normalize_url` calling real `parse_url`.

---

## Step 5: Missing Test Coverage

### Untested functionality in `parse_url`:

- Query string parsing (`?key=value`)
- Fragment parsing (`#section`)
- Port extraction (`localhost:8080` -> port 8080)
- URLs without a path (`https://example.com`)
- URLs with only a host (no scheme)
- Empty string input
- Non-string input
- URLs with all components present simultaneously

### Untested functionality in `normalize_url`:

- Scheme lowercasing (`HTTP` -> `http`)
- Host lowercasing (`EXAMPLE.COM` -> `example.com`)
- Default port removal (port 80 for HTTP, port 443 for HTTPS)
- Non-default port preservation
- Query and fragment passthrough during normalization

### Missing test types:

| Test Type | Status | Priority |
|-----------|--------|----------|
| Sad-path / error handling | Missing | P1 |
| Property-based "never crashes" | Missing | P1 |
| Idempotency for `normalize_url` | Missing | P2 |
| Roundtrip property tests | Missing | P2 |
| Boundary value tests | Missing | P2 |

---

## Prioritized Fix List

### P0 (Fix immediately)
1. **Replace print-not-assert in `test_unicode_url`**: Change `print()` to `assert` so the test can actually fail.

### P1 (Fix before next release)
2. **Upgrade all "not empty" assertions**: Replace `is not None`, `!= {}`, and truthiness checks with specific field-value assertions (check scheme, host, port, path individually).
3. **Fix or delete the skipped test**: Either fix `test_parse_empty` to work with the current API or delete it. Add a proper empty-input test.
4. **Add sad-path tests**: Empty input, non-string input, malformed URLs, missing scheme, missing host.
5. **Add a property-based "never crashes" test**: `parse_url(arbitrary_string)` must always return a dict with the expected keys, never raise.

### P2 (Fix soon)
6. **Remove the mock from `test_normalize_integration`**: Test `normalize_url` against the real `parse_url` -- it is a pure function with no external dependencies.
7. **Add idempotency property test**: `normalize_url(normalize_url(x)) == normalize_url(x)`.
8. **Add tests for query strings, fragments, and ports**: These are core parser features with zero coverage.
9. **Add tests for default port removal**: Verify HTTP:80 and HTTPS:443 are stripped.

### P3 (Improve when convenient)
10. **Add conservation property test**: Output characters of `parse_url` components should be a subset of the input URL characters.
11. **Add boundary tests**: Very long URLs, URLs with special characters, URLs with empty components.
