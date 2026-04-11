# Fixture-Based Golden File Testing

For transformation pipelines (HTML→Markdown, compilers, template engines, code
generators), the most effective test pattern.

## How it works

1. Put input files in `tests/fixtures/`
2. Run the transformation and save output to `tests/expected/`
3. On subsequent runs, compare output against expected files
4. If no expected file exists, create a baseline automatically
5. To update: delete the expected file and re-run

## The pattern (from kepano/defuddle)

```typescript
describe('Fixtures Tests', () => {
  const fixtures = getFixtures();  // Auto-discovers all .html files

  test.each(fixtures)('should process: $name', async ({ name, path }) => {
    const input = readFileSync(path, 'utf-8');
    const result = transform(input);
    const expected = loadExpected(name);

    if (!expected) {
      saveExpected(name, result);  // Auto-baseline
      return;
    }

    expect(result.trim()).toEqual(expected.trim());
  });
});
```

## Auto-discovery helper

```typescript
function getFixtures() {
  const dir = join(__dirname, 'fixtures');
  return readdirSync(dir)
    .filter(f => f.endsWith('.html'))
    .map(f => ({ name: basename(f, '.html'), path: join(dir, f) }));
}
```

## Why this pattern is strong

- **Zero-code test creation**: add a fixture file = add a test case
- **Human-readable expected output**: Markdown/text, not binary
- **Real-world inputs**: actual web pages, documents, source files
- **Drift detection**: any change to transformation logic is caught

## When to use

- HTML → Markdown extraction
- Code formatting / pretty-printing
- Template rendering, compiler output
- Data migration / transformation pipelines

## Naming convention

Use `category--source-description.extension`:
```
codeblocks--stripe.html
comments--news.ycombinator.com.html
```

## Multi-environment testing

```typescript
const USE_JSDOM = process.env.DOM === 'jsdom';
export const parseDocument = USE_JSDOM ? parseWithJSDOM : parseLinkedomHTML;
```
