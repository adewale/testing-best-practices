# Lessons from github.com/graydon (Graydon Hoare)

> Created the Rust programming language.
> Date: 2026-04-11

---

## Who He Is

Graydon Hoare created Rust. His testing repos focus on two problems: exhaustive enumeration of small state spaces, and bridging the gap between fuzzing and property testing.

## exhaustigen-rs — Exhaustive Testing

Not random testing, but testing *every possible combination* within bounds.

```rust
let mut gen = Gen::new();
while !gen.done() {
    let elts = gen.gen_elts(3, 4).collect::<Vec<_>>();
    // Tests EVERY combination: 0-3 elements, each 0-4
    // Total: (5^3) + (5^2) + 5 + 1 = 156 combinations
}
```

The key insight: **the generator tracks its progress through the state space and lazily extends it**. Nested value-dependent generation works correctly (generate K, then generate J in 0..K), and the state space is enumerated automatically.

**Available generators**:
- `gen(bound)` — scalar in 0..bound
- `flip()` — boolean
- `pick(slice)` — element from array
- `gen_elts(len, val)` — variable-length sequences
- `gen_comb(input)` — combinations
- `gen_perm(input)` — permutations (all N!)
- `gen_subset(input)` — all 2^N subsets

**Lesson**: Exhaustive testing is the gold standard when the state space is small enough. For a 5-element array, `gen_perm` tests all 120 permutations — no sampling bias, no missed cases.

## proptest-arbitrary-interop

Bridges `arbitrary::Arbitrary` (used for fuzzing) and `proptest::Strategy` (used for property testing):

```rust
use proptest_arbitrary_interop::arb;

proptest! {
    #[test]
    fn always_red(color in arb::<Rgb>()) {
        prop_assert!(color.g == 0 || color.r > color.g);
    }
}
```

**Lesson**: Write the data generator once, use it for both fuzzing and property testing. If you implement `Arbitrary` for cargo-fuzz, you get proptest for free.

## Key Insights

1. **Exhaustive testing > random testing** when the space is small enough
2. **Bridge fuzzing and property testing**: write the generator once, reuse everywhere
3. **Enumeration is lazy and demand-driven**: the generator tracks and extends the state space as needed
