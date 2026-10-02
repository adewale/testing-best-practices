# Exhaustive Testing via Property-Based Testing

When the state space is small enough, don't sample — test *every* combination.
"Small enough" means few cells **and** cheap cells: 240 cells at 35 µs take about
8.4 ms; 240 cells at 35 ms take 8.4 seconds, before setup and runner overhead.

## When the space is bounded

- Boolean flags: 2^N combinations
- Small enums: product of all enum sizes
- Permutations: N! for N elements
- Subsets: 2^N

For 5 elements: 120 permutations, 32 subsets — easily exhaustible.

## Pattern: Graydon Hoare's exhaustigen

```rust
let mut gen = Gen::new();
let items = vec![1, 2, 3, 4, 5];
while !gen.done() {
    let perm: Vec<_> = gen.gen_perm(&items).collect();
    assert!(is_sorted_after_our_sort(&perm));
}
// Tests all 120 permutations
```

## Pattern: Parametrize for small finite sets

```python
@pytest.mark.parametrize("scheme", ["http", "https", "ftp", "ws", "wss"])
@pytest.mark.parametrize("has_port", [True, False])
@pytest.mark.parametrize("has_path", [True, False])
@pytest.mark.parametrize("has_query", [True, False])
def test_all_url_combinations(scheme, has_port, has_path, has_query):
    url = build_url(scheme, has_port, has_path, has_query)
    result = parse_url(url)
    assert result["scheme"] == scheme
    # 5 × 2 × 2 × 2 = 40 combinations, all tested
```

## Check the layer that decides the property first

Before enumerating a cross-product of expensive operations (renders, requests,
browser runs), ask what actually determines the property. If it is fixed by a
resolver, a parsed IR, a config projection, or a schema upstream of the expensive
operation, assert it there: the downstream sweep proves the same theorem by
enumeration, more slowly and often less sensitively, because it only sees
divergences that survive all the way to the output. Example: 1,440 render calls
(75 s) became 250 (18 s) by comparing resolved style records instead of rendering
every theme × diagram family; the resolver check caught a seeded divergence in 6 ms
where the render sweep took about 20 s.

Three safety rules for the swap:

1. **Validate before deleting**: run both checks over the full cross-product once
   and confirm the cheap check never says "equal" where the expensive one says
   "differ".
2. **Derive the residue**: every member the upstream check cannot prove equivalent
   stays on the **full** expensive cross-product, not one sampled cell. This
   includes an undefined projection on either side and, when projection equality
   is only sufficient, unequal projections. Select by that condition rather than
   hard-coding names: a second implicit default must be covered automatically.
   Unequal projections do not alone prove unequal output; do not invent the
   converse of the implication.
3. **Keep entry-path witnesses per member**: when the public API accepts a name or
   a value, exercise both forms for **every cheaply proven member**. A witness for
   an implicit default does not exercise the non-default branch. One downstream
   context per member suffices only if dispatch is independent of those factors;
   otherwise retain the interacting contexts too. Residue sweeps already provide
   their members' witnesses.

### Worked pattern: proof, witnesses, complete residue

Suppose a validated contract says equal, defined resolved **values** produce equal
outputs for every context, and input-form dispatch does not depend on context.
Compare records structurally (or with the resolver's documented semantic equality),
not `Object.is`/`===`: two freshly allocated records can denote the same value.
Do not normalize away meaningful fields just to obtain equality.

```javascript
const assert = require('node:assert/strict');
const { isDeepStrictEqual } = require('node:util');

function verify({ members, contexts, resolve, produce, maxCalls }) {
  assert.ok(Object.keys(members).length > 0 && contexts.length > 0);
  const proven = [], residue = [];
  for (const [name, record] of Object.entries(members)) {
    const byName = resolve(name), byValue = resolve(record);
    const decided = byName !== undefined && byValue !== undefined &&
      isDeepStrictEqual(byName, byValue);
    (decided ? proven : residue).push([name, record]);
  }

  // Both public forms cost a call. No extra witness is needed for swept members.
  const calls = 2 * (proven.length + residue.length * contexts.length);
  assert.ok(calls <= maxCalls, `Complete verification needs ${calls} calls`);
  const compare = ([name, record], context) => {
    // Here the output contract is exact structural equality.
    assert.deepStrictEqual(produce(name, context), produce(record, context));
  };
  for (const member of proven) compare(member, contexts[0]);
  for (const member of residue) {
    for (const context of contexts) compare(member, context);
  }
}
```

`contexts` is the complete required downstream product, not a sample. Enumerate
members from the authoritative registry. If complete proof plus witnesses plus
residue exceeds the budget, report that conflict; do not drop witnesses, cap a
loop, or sample the residue and still claim complete equivalence. Calibrate the
replacement by seeding a resolver divergence, a public-input-form divergence, and
a residue divergence away from the first context, while accepting fresh-but-equal
records and multiple implicit defaults. These are targeted checks of the swap,
not a requirement to introduce recurring mutation infrastructure.

Do not apply this when the factors genuinely interact at the expensive layer (layout
× font metrics, where no upstream value determines the output); reduce those with a
covering-array portfolio instead. See also `references/correctness-by-construction.md`
(the same move for production checks) and antipattern #14 (assert the pre-mask value).
