# E26 Rust Result/proptest Fixture

Add Rust tests for `parse_rule(input: &str) -> Result<Rule, RuleError>`. Arbitrary strings must not panic; `Ok` rules must satisfy invariants and `Err` values must expose a useful kind/span.
