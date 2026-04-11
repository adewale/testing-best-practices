# Lessons from github.com/kepano (Steph Ango)

> Creator of Obsidian Minimal theme (4.9k stars), Flexoki color scheme, defuddle (6.6k stars), and Obsidian Skills.
> Date: 2026-04-11

---

## Testing Ecosystem Overview

| Repo | Language | Test Framework | Test Pattern | Notable |
|------|----------|---------------|-------------|---------|
| defuddle | TypeScript | Vitest | Fixture-based golden file tests | 40+ HTML fixtures with expected Markdown output |
| obsidian-skills | -- | -- | Agent skill specs | Skills for Obsidian agents |
| obsidian-minimal-settings | TypeScript | -- | No tests | Obsidian plugin |

---

## Fixture-Based Golden File Testing (defuddle)

defuddle (extract main content from web pages as Markdown) uses the most thorough fixture-based testing pattern found across all scanned repos.

### How It Works

1. HTML fixtures in `tests/fixtures/` (40+ real-world web pages)
2. Expected Markdown output in `tests/expected/` (auto-generated baselines)
3. Test runner processes each fixture and compares against expected output
4. If no expected file exists, the test creates a baseline automatically
5. If results differ from expected, the test fails

### The Test File

```typescript
// tests/fixtures.test.ts
describe('Fixtures Tests', () => {
  const fixtures = getFixtures();  // Auto-discovers all .html files

  test('should have fixtures to test', () => {
    expect(fixtures.length).toBeGreaterThan(0);
  });

  test.each(fixtures)('should process fixture: $name', async ({ name, path }) => {
    const html = readFileSync(path, 'utf-8');
    const doc = parseDocument(html, url);
    const response = await Defuddle(doc, url, { separateMarkdown: true });
    const result = createComparableResult(response);
    const expected = loadExpectedResult(name);

    expect(response.content.length).toBeGreaterThan(0);
    expect(response.contentMarkdown?.length).toBeGreaterThan(0);

    if (!expected) {
      // No baseline exists — create one automatically
      console.log(`Creating baseline expected result for ${name}`);
      saveExpectedResult(name, result);
    }

    if (expected) {
      expect(result.trim()).toEqual(expected.trim());
    }
  });
});
```

### Key Design Decisions

**Auto-discovery**: Tests find fixtures via `getFixtures()` which reads the `tests/fixtures/` directory. Adding a new test case = adding an HTML file. No code changes needed.

**Auto-baseline**: If no expected output exists, the first run creates it. This means:
- New fixtures are automatically baselined
- To update expectations: delete the expected file and re-run
- CI fails on drift because expected files are committed

**Comparable output format**: Expected files are Markdown with a JSON metadata preamble:

```typescript
function createComparableResult(response: DefuddleResponse): string {
  const metadataOnly = {
    title: response.title,
    author: response.author,
    site: response.site,
    published: response.published,
  };
  return '```json\n' + JSON.stringify(metadataOnly, null, 2) + '\n```\n\n'
    + response.contentMarkdown;
}
```

This captures both metadata and content in a single reviewable file.

**URL extraction from fixtures**: HTML fixtures can embed their source URL:
```html
<!-- {"url": "https://example.com/article"} -->
```
If absent, the URL is derived from the filename.

**Multi-environment support**: Tests can run against different DOM implementations:
```typescript
const USE_JSDOM = process.env.DOM === 'jsdom';
export const parseDocument = USE_JSDOM ? parseWithJSDOM : parseLinkedomHTML;
```

### Fixture Naming Convention

Fixtures use a `category--source-description.html` naming pattern:
- `codeblocks--chatgpt-codemirror.html`
- `codeblocks--stripe.html`
- `comments--news.ycombinator.com-item-id=12345678.html`
- `author-contact-block.html`

This groups related fixtures and makes the test output scannable.

### What Makes This Pattern Strong

1. **Zero-code test creation**: Add an HTML file, run tests, review the baseline
2. **Reviewable baselines**: Expected output is human-readable Markdown, not binary or opaque JSON
3. **Drift detection**: Any change to extraction logic that alters output is caught
4. **Real-world fixtures**: Tests use actual HTML from real websites, not synthetic examples
5. **Metadata + content**: Both are captured and compared, catching extraction regressions in either

### Comparison to Other Fixture Patterns

| Pattern | defuddle | atlas (visual regression) | simonw (VCR) |
|---------|----------|--------------------------|-------------|
| Format | HTML → Markdown | Browser → Screenshot PNG | HTTP → YAML cassette |
| Auto-baseline | Yes (creates .md on first run) | Yes (creates .png on first run) | Yes (records on first run) |
| Update method | Delete expected file, re-run | `--update-snapshots` | Delete cassette, re-run |
| Reviewable | Yes (Markdown) | Partially (pixel diff) | Yes (YAML) |
| CI-safe | Yes | No (font rendering) | Yes |

---

## Obsidian Skills

kepano created the Obsidian Skills repo — agent skills that teach agents how to use Obsidian's Markdown, Bases (databases), JSON Canvas, and CLI. This is relevant as a skill design reference rather than a testing reference.

---

## Key Insights

1. **Fixture-based golden file tests** are the ideal pattern for transformation pipelines (HTML→Markdown, parsing, rendering): add input files, auto-generate baselines, detect drift
2. **Auto-discovery + auto-baseline** means adding a test case is just adding a file — no code changes
3. **Human-readable expected output** (Markdown, not binary) makes review practical
4. **Real-world fixtures** (actual web pages) catch edge cases that synthetic HTML never would
5. **Multi-environment testing** (JSDOM vs linkedom) via environment variable toggle catches DOM implementation differences
6. **Fixture naming conventions** (`category--source.html`) make test output scannable
