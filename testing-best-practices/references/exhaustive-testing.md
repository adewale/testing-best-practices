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
2. **Derive the residue**: cells the upstream check cannot decide (e.g. a default
   that resolves to `undefined` by name but to a record explicitly) stay on the
   expensive path. Select them with the cheap check ("every member whose name
   resolves to undefined") rather than hard-coding names, so future members of the
   same shape are covered.
3. **Keep entry-path witnesses**: if the public API accepts the input in more than one
   form (a name or a value), keep a small expensive check per entry path, because
   upstream identity does not prove both paths reach it.

Do not apply this when the factors genuinely interact at the expensive layer (layout
× font metrics, where no upstream value determines the output); reduce those with a
covering-array portfolio instead. See also `references/correctness-by-construction.md`
(the same move for production checks) and antipattern #14 (assert the pre-mask value).
