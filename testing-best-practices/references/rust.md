# Rust Testing Reference

## Framework: built-in (`#[test]`, `#[cfg(test)]`)

### Test conventions

```rust
// Unit tests: inline module in the same file
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_operation() {
        let result = add(2, 3);
        assert_eq!(result, 5);
    }

    #[test]
    #[should_panic(expected = "division by zero")]
    fn test_division_by_zero() {
        divide(1, 0);
    }
}

// Integration tests: separate files in tests/
// tests/integration_tests.rs
use my_crate::Calculator;

#[test]
fn test_full_workflow() { ... }
```

### Running tests

```bash
cargo test                         # All tests
cargo test --workspace             # All crates in workspace
cargo test -- --nocapture          # Show stdout
cargo test -- test_name            # Specific test
cargo test --release               # Release mode (for perf tests)
```

### Test organization

```
src/
  lib.rs          # #[cfg(test)] mod tests { ... }
  module.rs       # Inline unit tests
tests/
  integration_tests.rs   # Integration tests
  fixtures/              # Test data files
```

## Assertion Macros

```rust
assert!(condition);                           // Boolean
assert_eq!(left, right);                      // Equality
assert_ne!(left, right);                      // Inequality
assert!(result.is_ok());                      // Result
assert!(result.is_err());                     // Error case
assert_eq!(result.unwrap(), expected);        // Unwrap + compare
assert!(matches!(value, Pattern::Variant));   // Pattern match
```

## CLI Binary Integration Tests

Test the compiled binary as a subprocess:

```rust
use std::process::Command;

fn binary_path() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("target/release/my-tool")
}

#[test]
fn test_json_output() {
    let output = Command::new(binary_path())
        .args(&["search", "--output", "json", "pattern", &fixtures_dir()])
        .output()
        .expect("Failed to execute");

    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(output.status.success());
    assert!(stdout.contains("\"total_matches\""));
}
```

## Test Fixtures

```rust
fn setup_test_files() {
    let fixtures = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures");
    fs::create_dir_all(&fixtures).unwrap();
    fs::write(fixtures.join("test.py"), "def hello(): pass\n").unwrap();
}
```

## Property-Based Testing: proptest

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn roundtrip_encode_decode(input in ".*") {
        let encoded = encode(&input);
        let decoded = decode(&encoded);
        prop_assert_eq!(decoded, input);
    }

    #[test]
    fn never_crashes(input in prop::string::string_regex(".*").unwrap()) {
        let _ = parse(&input);  // Should not panic
    }
}
```

## Exhaustive Testing: exhaustigen

For small state spaces, test every combination:

```rust
use exhaustigen::Gen;

#[test]
fn test_all_permutations() {
    let mut gen = Gen::new();
    let items = vec![1, 2, 3];
    while !gen.done() {
        let perm: Vec<_> = gen.gen_perm(&items).collect();
        // Verify invariant holds for EVERY permutation
        assert!(is_valid_ordering(&perm));
    }
}
```

## Workspace CI

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    include:
      - os: macos-latest, rust: stable
      - os: macos-latest, rust: "1.90"  # MSRV
      - os: ubuntu-latest, rust: stable
steps:
  - run: cargo build --workspace --all-targets
  - run: cargo test --workspace
```

### Separate lint and test workflows

```yaml
# ci.yml (lint) — fast
- cargo fmt --all -- --check
- cargo clippy --workspace --all-targets -- -D warnings
- cargo audit

# test.yml (test) — matrix
- cargo test --workspace
```

## Fuzz Testing

```bash
cargo install cargo-fuzz
cargo fuzz init
cargo fuzz run my_target
```

```rust
// fuzz/fuzz_targets/my_target.rs
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    let _ = my_crate::parse(data);
});
```

## proptest + arbitrary interop

If you implement `arbitrary::Arbitrary` for fuzzing, reuse it for proptest:

```rust
use proptest_arbitrary_interop::arb;

proptest! {
    #[test]
    fn property_holds(value in arb::<MyType>()) {
        prop_assert!(value.is_valid());
    }
}
```
