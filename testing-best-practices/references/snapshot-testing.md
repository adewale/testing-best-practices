# Snapshot Testing (umbrella)

The general idiom: **run the system, serialize what it produced, store it as a
baseline, diff against the baseline on every subsequent run.** Also called
golden testing, approval testing, golden-master testing, or characterization
testing depending on context.

This file covers three dialects of the same idea. Pick the one whose
*recorded artifact* matches your system:

| Dialect | What gets recorded | Best for |
|---|---|---|
| **A. Golden-file (transformation)** | Output file produced from an input file | HTML→Markdown, compilers, formatters, code generators |
| **B. Structured-output snapshots** | Serialized in-memory value (JSON/YAML, rendered DOM, console output) | API responses, CLI output, rendered components, complex objects |
| **C. Session/trace goldens** | Full execution trace: args, env, HTTP, DB, LLM calls, tool calls, side effects | Multi-step agents, LLM apps, pipelines, orchestrators |

VCR cassette tests (`vcr-cassettes.md`) are a fourth dialect specialized to the
network boundary — they record HTTP responses and *replay* them as inputs.
Cross-reference that file when the snapshot is HTTP traffic.

## Shared rules (all dialects)

1. **Auto-baseline on first run, diff thereafter.** Store baselines in the
   repo as plain text. Update workflow: delete the baseline file (or pass
   `--update`) and re-run.
2. **Normalize unstable fields at write time.** Timestamps, generated IDs,
   random values, absolute paths, line numbers, and addresses get filtered or
   replaced with placeholders *before* serialization. Otherwise tests are
   flaky.
3. **Mark every field as stable or unstable** in your serializer. Stable
   fields require exact matches; unstable fields are normalized.
4. **Review baseline diffs with code-review rigor.** A snapshot is a behavioral
   spec — not a thing to rubber-stamp with `--update`.
5. **Keep snapshots focused.** Shard by scenario; don't dump everything into
   one giant artifact. Big monolithic snapshots get rubber-stamped.
6. **Both directions.** If the snapshot covers a security-sensitive
   transformation, also assert programmatically that dangerous content is
   absent — don't rely on the diff alone.

## Dialect A: Golden-file (transformation pipelines)

Input file → output file. The most common dialect.

### Pattern (from kepano/defuddle)

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

function getFixtures() {
  const dir = join(__dirname, 'fixtures');
  return readdirSync(dir)
    .filter(f => f.endsWith('.html'))
    .map(f => ({ name: basename(f, '.html'), path: join(dir, f) }));
}
```

### Naming convention

Use `category--source-description.extension`:

```
codeblocks--stripe.html
comments--news.ycombinator.com.html
```

### When to use

- HTML → Markdown extraction
- Code formatting / pretty-printing
- Template rendering, compiler output
- Data migration / transformation pipelines

### Why this dialect is strong

- Zero-code test creation: add a fixture file = add a test case
- Human-readable expected output (Markdown/text, not binary)
- Real-world inputs (actual web pages, documents, source files)

## Dialect B: Structured-output snapshots

Serialize an in-memory value to a stable text format, diff against a stored
baseline. The recorded artifact is *not* a transformation of an input file —
it's the result of calling code with arbitrary setup.

### Pattern (Python with syrupy)

```python
def test_user_serialization(snapshot):
    user = User(name="Alice", age=30, role="admin")
    assert user.to_dict() == snapshot
    # First run: writes __snapshots__/test_user.json
    # Subsequent runs: diffs against it
    # To update: pytest --snapshot-update
```

### Pattern (TypeScript with Vitest)

```typescript
test('renders user card', () => {
  const html = renderUserCard({ name: 'Alice', role: 'admin' });
  expect(html).toMatchSnapshot();
});
```

### Tools by language

| Language | Tool | Notes |
|---|---|---|
| Python | `syrupy` | pytest plugin, multiple serializers |
| TypeScript/JS | Jest `.toMatchSnapshot()` / Vitest | Built-in, inline variant available |
| Rust | `insta` | `cargo insta review` for interactive approval |
| .NET | `Verify` | Strong support for "scrubbers" (unstable-field normalization) |
| Multi-language | `ApprovalTests` (Falco) | Original approval-testing library |
| Go | `testdata/` convention | No framework — write helper that reads/writes files |

### Anti-patterns specific to this dialect

- **Rubber-stamping**: blindly running `--update` without reviewing the diff.
  Treat the snapshot as code.
- **Snapshotting whole pages** when a component would do. Keep snapshots
  narrow enough that a diff is meaningful at a glance.
- **Snapshotting non-deterministic output** without scrubbers. A timestamp
  field will flap on every run — normalize it before serializing.

## Dialect C: Session / trace goldens

For multi-step systems where the *trace* is the thing under test: which
operations ran, in what order, with what arguments, producing what side
effects. This generalizes snapshot testing to "everything observable about a
run."

### What to capture

- Full command args, env vars, working directory, complete stdout/stderr
- HTTP requests/responses (method, headers, body, status)
- Database queries, cache operations
- LLM calls with complete requests/responses
- Tool calls with arguments, intermediate reasoning
- Files read/written (contents or checksums)

### Stable vs unstable field classification

Every field in the trace must be tagged at schema definition time:

| Stable (exact match required) | Unstable (normalize before write) |
|---|---|
| Action / event type | Timestamps |
| Operation name, arguments | Generated IDs (UUIDs, request IDs) |
| HTTP status, method, path | Random values, nonces |
| Counts, quantities, totals | Absolute paths, hostnames |
| Tool selection, ordering | Latency / duration measurements |

Use type-safe schemas (Zod, Pydantic) and serialize to YAML for diff
readability.

### Switchable mock modes

The same test code runs in two modes via a `MOCK_MODE` env toggle:

- **live**: hits real services — used for debugging, generating new traces
- **mocked**: replays recorded responses — used in CI, target <100ms per scenario

All non-deterministic dependencies (clock, randomness, network, LLM, DB)
must be mockable.

### Layered assertions

Snapshot diff catches *unanticipated* changes. Layer programmatic assertions
on top for *known* invariants:

- Event ordering (login event precedes any user-data event)
- Aggregate constraints (sum of debits == sum of credits)
- Cross-event relationships (every tool_call has a matching tool_result)

### When to use

- LLM agents, multi-step pipelines, orchestrators
- Systems with many interacting components and non-deterministic outputs
- Where writing hundreds of unit tests would be burdensome and you need broad
  visibility instead of narrow assertions

### Anti-patterns specific to this dialect

- **Regex-matching stable fields.** Patterns should match only genuinely
  unstable values (IDs, timestamps). A regex on a priority field will silently
  pass when P2 unexpectedly becomes P1.
- **Surgical extraction with grep/jq/awk.** Reverts session testing to
  unit-test mentality and silently passes when unanticipated fields change.
  Show complete content; let the diff reveal what actually changed.
- **Forking logic between test and production code paths.** Mock at the
  dependency boundary, not by branching inside the SUT.

## Choosing between dialects

```
Is the system a pure transformation (input file → output file)?
  YES → Dialect A (golden-file)
  NO  ↓

Is the system a single function returning a structured value?
  YES → Dialect B (structured-output snapshot)
  NO  ↓

Is the system a multi-step process where the sequence of operations matters?
  YES → Dialect C (session/trace golden)

Does the snapshot include HTTP traffic?
  YES → also see vcr-cassettes.md (record-replay)
```

## Relationship to other test types

- **Characterization testing** (`characterization-testing.md`) is the *use
  case* — capture current behavior to enable safe refactoring. Snapshot
  testing is the typical *technique* used to do it.
- **VCR cassettes** (`vcr-cassettes.md`) are a snapshot of the network
  boundary, with replay semantics added. Cassettes are both stub *and*
  snapshot.
- **Differential testing** is the *inverse*: compare two live implementations
  to each other instead of comparing today's run to a stored baseline.
- **Mutation testing** is the *meta-check*: verify that snapshots are
  sensitive enough to fail when the code changes meaningfully.
- **Doc-sync testing** is structurally similar (compare X to a stored Y) but
  the oracle is a live code registry, not a stored file.

## Lineage and references

- Mitchell Hashimoto, "Testing with Golden Files":
  <https://mitchellh.com/writing/golden-files>
- Llewellyn Falco, Approval Testing: <https://approvaltests.com/>
- Michael Feathers, *Working Effectively with Legacy Code* (characterization
  testing as the pattern that motivated the genre)
- Pryce & Freeman, *Growing Object-Oriented Software, Guided by Tests*
- Wikipedia, Characterization Test:
  <https://en.wikipedia.org/wiki/Characterization_test>
- Go `testdata/` convention:
  <https://pkg.go.dev/cmd/go#hdr-Test_packages>
