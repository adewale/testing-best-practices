# Audit this mixed-language test setup

Write an `assessment.md` for this repository snapshot. Prioritize concrete
changes to the test setup.

`.github/workflows/test.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements-dev.txt
      - run: python -m unittest discover -s tests -p 'test_*.py' -v
      - uses: actions/setup-go@v5
      - run: go test ./...
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm test
```

`tests/test_slug_properties.py`:

```python
from hypothesis import given, strategies as st
from slug import slugify


@given(st.text())
def test_slugify_is_idempotent(value):
    assert slugify(slugify(value)) == slugify(value)
```

`wire/fuzz_test.go`:

```go
package wire

import "testing"

func FuzzDecodeFrame(f *testing.F) {
    f.Add([]byte{0, 0, 0, 0})
    f.Fuzz(func(t *testing.T, data []byte) { _, _ = DecodeFrame(data) })
}

func FuzzParseHeader(f *testing.F) {
    f.Add("Content-Type: text/plain")
    f.Fuzz(func(t *testing.T, line string) { _, _ = ParseHeader(line) })
}
```

`src/normalizeSlug.ts`:

```ts
export function normalizeSlug(value: string): string {
  return value.trim().toLocaleLowerCase("en-US").replaceAll(/\s+/g, "-");
}
```

`test/normalizeSlug.property.test.ts`:

```ts
import { describe, expect, test } from "vitest";
import fc from "fast-check";

// Kept here so this test has no application imports.
function normalizeCandidate(value: string): string {
  return value.trim().toLowerCase().replaceAll(/\s+/g, "-");
}

describe("slug normalization", () => {
  test("is idempotent", () => {
    fc.assert(fc.property(fc.string(), value => {
      expect(normalizeCandidate(normalizeCandidate(value)))
        .toBe(normalizeCandidate(value));
    }));
  });
});
```

`package.json` contains `"test": "vitest run"`.
