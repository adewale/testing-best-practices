# Exhaustive Testing via Property-Based Testing

When the state space is small enough, don't sample — test *every* combination.

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
