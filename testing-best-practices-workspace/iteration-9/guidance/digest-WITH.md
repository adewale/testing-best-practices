# Golden File and Snapshot Testing

Two closely related patterns for asserting on complex output:

- **Golden files**: input file → output file, both on disk. Auto-discovered.
  Best for transformation pipelines (HTML→Markdown, compilers, code generators).
- **Snapshot tests**: any expression → stored string. Lives in or beside the
  test file. Best when an assertion would otherwise be a long, brittle
  field-by-field comparison.

Both share the **promote workflow**: don't hand-write the expected output.
The framework writes it the first time, you review the diff, then commit.

## Golden Files

### How it works

1. Put input files in `tests/fixtures/`
2. Run the transformation and save output to `tests/expected/`
3. On subsequent runs, compare output against expected files
4. If no expected file exists, create a baseline automatically
5. To update: delete the expected file and re-run (or set an env var)

### The pattern (from kepano/defuddle)

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

### Auto-discovery helper

```typescript
function getFixtures() {
  const dir = join(__dirname, 'fixtures');
  return readdirSync(dir)
    .filter(f => f.endsWith('.html'))
    .map(f => ({ name: basename(f, '.html'), path: join(dir, f) }));
}
```

### Why golden files work

- **Zero-code test creation**: add a fixture file = add a test case
- **Human-readable expected output**: Markdown/text, not binary
- **Real-world inputs**: actual web pages, documents, source files
- **Drift detection**: any change to transformation logic is caught

### When to use
- HTML → Markdown extraction
- Code formatting / pretty-printing
- Template rendering, compiler output
- Data migration / transformation pipelines

### Naming convention

Use `category--source-description.extension`:
```
codeblocks--stripe.html
comments--news.ycombinator.com.html
```

## Snapshot Tests (the promote workflow)

Snapshot tests generalize the golden-file idea: any string-renderable output
becomes the expected value, captured on first run, asserted on subsequent
runs. The expected output lives **inside** the test file (inline) or in a
sidecar (`__snapshots__/`), not in a separate fixtures tree.

### The promote workflow

1. Write the test with an empty expected slot
2. Run tests — framework writes the actual output as the expected
3. Subsequent runs: framework compares actual vs expected, fails with a diff
4. When the change is intentional: run with `--update` (or interactive review)
5. **Commit the snapshot file with the code change** — the snapshot diff in
   your PR is the record of what observable behavior changed

### Tools per language

| Language | Tool | Update command |
|----------|------|----------------|
| Python | `syrupy` | `pytest --snapshot-update` |
| JS/TS | Jest, Vitest | `jest -u`, `vitest -u`, or interactive `u` in watch mode |
| Rust | `insta` | `cargo insta review` (interactive), `cargo insta accept` |
| Go | `cupaloy` | `UPDATE_SNAPSHOTS=true go test` |
| Multi-language | `approvaltests` | `*.received.txt` → rename to `*.approved.txt` |

### Python (syrupy) example

```python
def test_render_invoice(snapshot):
    invoice = Invoice(items=[Item("Widget", 9.99, 2)], tax_rate=0.08)
    assert invoice.render() == snapshot
```

First run creates `__snapshots__/test_invoice.ambr` with the rendered output.
Subsequent runs compare. On legitimate change: `pytest --snapshot-update`.

### Rust (insta) — the inline form

```rust
#[test]
fn test_invoice() {
    let invoice = Invoice::new(...);
    insta::assert_yaml_snapshot!(invoice, @"");
    // After first `cargo insta accept`, the macro contains the snapshot inline:
    // insta::assert_yaml_snapshot!(invoice, @r###"
    //   items:
    //     - name: Widget
    //       price: 9.99
    //       quantity: 2
    //   subtotal: 19.98
    //   tax: 1.60
    //   total: 21.58
    // "###);
}
```

The snapshot lives in the source file — you read the test and see the
assertion together. This is closer to Jane Street's `ppx_expect` than the
sidecar `__snapshots__/` style.

## When to use snapshot tests instead of field-by-field assertions

- The output has more than ~5 fields you'd otherwise assert on individually
- The output is a tree, AST, rendered DOM, log sequence, or formatted text
- The same shape is asserted on across many tests (a single change should
  cascade through the snapshots, not require editing 50 assertions)
- The structure is part of the contract, not just the values

## When NOT to use snapshot tests

- The output has one or two meaningful fields — write specific assertions
- The "contract" is a single boolean or numeric value
- The output contains unredacted timestamps, UUIDs, or other non-determinism
  you haven't normalized (you'll get noise on every run)
- The test is exercising a security property — write the explicit assertion
  so a reviewer can't miss it among unrelated output

## Failure modes to defend against

Snapshot tests fail predictably when discipline slips:

### Rubber-stamping
The most common failure. Engineers run `--update` without reading the diff.
The test becomes a change detector, not a behavior test. Mitigations:

- Make snapshot diffs mandatory reading in code review
- Require a one-line explanation in the PR description for every snapshot
  diff: "Updated 3 invoice snapshots because we now include the tax line"
- For interactive review tools (`cargo insta review`), prefer them over
  blanket-accept

### Coupling to incidental detail
Timestamps, UUIDs, map iteration order, whitespace make tests fail on noise.
Fix at write-time:

```python
# syrupy custom serializer
class StableSerializer(SnapshotSerializer):
    def serialize(self, data):
        data = redact_uuids(data)
        data = freeze_timestamps(data, to="2024-01-01T00:00:00Z")
        data = sort_keys(data)
        return super().serialize(data)
```

### Cascade updates that hide intent
One logic change updates 50 snapshots. The reviewer can't tell which were
intended. Mitigations:

- Keep snapshots small and focused (one snapshot per behavior, not per test)
- Don't snapshot the entire program state — snapshot the part this test
  exercises
- When a refactor cascades through snapshots, split into two commits:
  "refactor (no behavior change, regenerated snapshots)" + "feature
  (intentional behavior change)"

### Loss of intent
A snapshot like `"hello Bob"` doesn't tell you what's important. The test
name has to carry the intent:

```typescript
// Bad: snapshot reveals nothing about why
test('renders correctly', () => { expect(view).toMatchSnapshot(); })

// Good: name carries the intent, snapshot verifies the form
test('greeting includes the user name after first interaction', () => {
  expect(view).toMatchSnapshot();
})
```

## Design pressure: make your output tell a story

The single biggest determinant of snapshot test quality is whether the
output itself is readable. Invest in:

- Custom `__repr__` / `Display` / `toString` for domain types
- Pretty-printers that surface what matters and elide what doesn't
- Stable serialization (sorted keys, normalized whitespace, fixed precision)
- Helper functions to format multi-object state into one cohesive trace

This is the principle behind Jane Street's `ppx_expect`: when stringification
is trivial and stable, tests get written. From "The Joy of Expect Tests":
*"The real art lies in producing output that tells a concise story, capturing
the state you care about."*

## Whole-state roundtrip digests (save/load, migration)

For persistence layers — save/load, serialization formats, schema migrations —
the highest-value characterization test is an **identity check over the whole
state**, not field assertions on one record. (Pattern source: Redis's
`DEBUG RELOAD` + dataset digest: snapshot a fingerprint, reload, assert the
fingerprint is unchanged.)

1. **Generate rich state with a seeded RNG** — many keys, every supported
   value type, the awkward ones especially (empty collections, TTLs, unicode,
   nesting). Hand-picked single-record tests miss exactly the types that break.
2. **Canonicalize, then fingerprint.** Produce a canonical dump of the entire
   state — **sort anything unordered** (sets, map iteration) before comparing
   or hashing. Digesting a non-canonical dump turns legitimate passes into
   flaky failures; structural equality on canonical forms is often better than
   a hash because failures show a diff instead of two checksums.
3. **Assert save→load is the identity**, comparing full canonical state.
4. **Parameterize the reload step across every format/path** — JSON and
   binary, snapshot and incremental, migration v1→v2→v1 — same state, same
   identity assertion, one parameterized test.
5. **On mismatch, emit both canonical dumps** so the failure is a reviewable
   diff, not "digests differ."

```python
@pytest.mark.parametrize("fmt", ["json", "binary"])
def test_save_load_roundtrip_identity(tmp_path, fmt):
    store = build_seeded_store(random.Random(1234), keys=500)  # all value types
    before = canonical_dump(store)                # sorted, normalized
    save(store, tmp_path / "db", format=fmt)
    reloaded = load(tmp_path / "db", format=fmt)
    assert canonical_dump(reloaded) == before     # whole-state identity
```

Two failure modes to defend against:
- **A digest that ignores fields gives false confidence** — if `canonical_dump`
  skips TTLs, TTL persistence bugs are invisible. The dump must cover every
  field the format claims to persist.
- **A digest over nondeterministic ordering gives false failures** — hashing
  `str(a_set)` fails randomly. Canonicalize first, always.

## Multi-environment testing

```typescript
const USE_JSDOM = process.env.DOM === 'jsdom';
export const parseDocument = USE_JSDOM ? parseWithJSDOM : parseLinkedomHTML;
```

Run the same fixtures through different backends; expected output should
agree.
