# Test Quality Assessment: `evals/files/weak_tests.ts`

## Summary

This test suite for the HTML sanitizer is **critically flawed**. It provides zero real coverage of the sanitizer because the entire module is mocked, every assertion is weak or missing, and security-critical tests are either skipped or use logging instead of assertions. A malicious actor could introduce an XSS vulnerability in the sanitizer and every test would still pass.

## Issues Found (by priority)

### P0 -- Critical (Security)

#### 1. Entire module is mocked -- no real code is ever tested

**Lines 7-11:**
```typescript
vi.mock('../../src/sanitizer', () => ({
  sanitize: vi.fn().mockReturnValue('<p>safe</p>'),
  stripAllTags: vi.fn().mockReturnValue('text only'),
  escapeHtml: vi.fn().mockReturnValue('&lt;script&gt;'),
}));
```

**Problem:** Every call to `sanitize()`, `stripAllTags()`, and `escapeHtml()` returns a hardcoded string regardless of input. The real sanitizer code is never executed. This is the "testing the mock" antipattern -- the tests are tautological. If the real sanitizer had a critical XSS bypass, these tests would still pass.

**Fix:** Remove the `vi.mock()` block entirely. Import the real module and test its actual behavior.

#### 2. Logging not asserting in security-critical test

**Lines 37-40:**
```typescript
it('should escape HTML entities', () => {
  const result = escapeHtml('<script>alert("xss")</script>');
  console.log('Escaped result:', result);
  // No assertion -- just logging
});
```

**Problem:** This test logs output but never asserts anything. It will always pass, even if `escapeHtml` returns the raw unescaped HTML. This is a P0 antipattern (logging not asserting) on security-critical code.

**Fix:** Replace `console.log` with specific assertions checking that angle brackets, quotes, and ampersands are properly escaped.

#### 3. XSS test uses only `toBeTruthy()`

**Line 45:**
```typescript
expect(sanitize('<img onerror="alert(1)" src="x">')).toBeTruthy();
```

**Problem:** `toBeTruthy()` passes for any non-empty string, including one that still contains `onerror="alert(1)"`. This test provides a false sense of security -- it would pass even if the sanitizer returned the dangerous input unchanged.

**Fix:** Assert that `onerror` is removed AND that the benign parts of the tag survive where appropriate.

### P1 -- High

#### 4. Unconditional `it.skip` on security test

**Line 26:**
```typescript
it.skip('should handle nested script tags', () => { ... });
```

**Problem:** This is the only test that actually checks for `<script>` removal (via `not.toContain`), and it is unconditionally skipped. There is no reason, no tracking issue, and no `skipIf` condition.

**Fix:** Remove the `.skip` and enable this test. If there is a known issue, use a conditional skip with a linked issue.

#### 5. Not-empty assertions as sole checks (3 instances)

- **Line 19:** `expect(result).toBeDefined()` for sanitize
- **Line 24:** `expect(result).toBeTruthy()` for empty input handling
- **Line 33:** `expect(result).toBeDefined()` for stripAllTags

**Problem:** `toBeDefined()` passes for any non-undefined value, including error objects. `toBeTruthy()` passes for any truthy value. A sanitizer that returned `"<script>alert('xss')</script>"` unchanged would pass all these checks.

**Fix:** Replace with specific value assertions. Check that dangerous content is absent AND safe content is preserved.

### P2 -- Medium

#### 6. Fake integration test

**Lines 43-47:**
```typescript
describe('Integration', () => {
  it('should handle XSS', () => {
    expect(sanitize('<img onerror="alert(1)" src="x">')).toBeTruthy();
  });
});
```

**Problem:** This is labeled "Integration" but uses the same mocked module. It tests nothing that the unit tests do not (and even the unit tests test nothing). This is an "integration test mocking everything" antipattern.

**Fix:** Either remove the "Integration" label or write genuine integration tests that exercise the real sanitizer with realistic payloads.

#### 7. No sad-path tests

**Problem:** There are no tests for edge cases such as:
- Null/undefined input
- Nested malicious tags (`<scr<script>ipt>`)
- Mixed-case tags (`<ScRiPt>`)
- Malformed HTML
- Extremely long input
- `javascript:` URLs in href/src attributes
- `data:` URLs
- Dangerous attributes beyond `onerror` (e.g., `onclick`, `onload`, `onmouseover`, `onfocus`)

#### 8. No property-based tests

**Problem:** An HTML sanitizer processes arbitrary input. Per the testing best practices, every parser/normalizer should have at minimum a "never crashes on arbitrary input" property test, plus an idempotency test (`sanitize(sanitize(x)) === sanitize(x)`).

## Assertion Density

| Test | Meaningful Assertions | Verdict |
|------|----------------------|---------|
| should sanitize HTML | 0 (only `toBeDefined`) | Failing |
| should handle empty input | 0 (only `toBeTruthy`) | Failing |
| should handle nested script tags | N/A (skipped) | Skipped |
| should strip all tags | 0 (only `toBeDefined`) | Failing |
| should escape HTML entities | 0 (only `console.log`) | Failing |
| should handle XSS | 0 (only `toBeTruthy`) | Failing |

**Overall assertion density: 0 meaningful assertions across 5 active tests.**

## Recommendations

1. **Remove the `vi.mock()` block** -- test the real sanitizer, not a fake
2. **Replace all weak assertions** with specific positive and negative checks
3. **Enable the skipped test** for nested script tags
4. **Add `console.log` cleanup** and replace with real assertions
5. **Add sad-path tests** for edge cases (null input, nested tags, mixed case, `javascript:` URLs, all dangerous attributes)
6. **Add property-based tests** using fast-check for crash resistance and idempotency
7. **Test both directions** -- verify safe content survives AND dangerous content is removed in every test
8. **Target 3+ meaningful assertions per test** as a minimum for security-critical code
