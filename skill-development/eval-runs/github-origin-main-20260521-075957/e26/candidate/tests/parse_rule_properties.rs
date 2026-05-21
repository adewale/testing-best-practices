use proptest::prelude::*;
use std::panic::{catch_unwind, AssertUnwindSafe};

use rule_parser::{parse_rule, Rule, RuleError};

fn rule_inputs() -> impl Strategy<Value = String> {
    prop_oneof![
        Just(String::new()),
        Just(" ".to_owned()),
        Just("\t\n".to_owned()),
        Just("\0".to_owned()),
        Just("rule".to_owned()),
        Just("rule {".to_owned()),
        any::<String>(),
    ]
}

proptest! {
    #![proptest_config(ProptestConfig {
        cases: 2048,
        .. ProptestConfig::default()
    })]

    #[test]
    fn parse_rule_is_total_and_returns_actionable_results(input in rule_inputs()) {
        let result = match catch_unwind(AssertUnwindSafe(|| parse_rule(&input))) {
            Ok(result) => result,
            Err(_) => return Err(TestCaseError::fail(format!(
                "parse_rule panicked for input {input:?}"
            ))),
        };

        match result {
            Ok(rule) => assert_rule_invariants(&rule, &input)?,
            Err(err) => assert_error_is_actionable(&err, &input)?,
        }
    }
}

#[test]
fn malformed_rules_report_a_specific_kind_and_in_bounds_span() {
    for input in ["", "   ", "\0", "rule {", "rule \"unterminated"] {
        match parse_rule(input) {
            Ok(_) => panic!("malformed input unexpectedly parsed as a valid rule: {input:?}"),
            Err(err) => assert_error_is_actionable(&err, input).unwrap(),
        }
    }
}

fn assert_rule_invariants(rule: &Rule, input: &str) -> Result<(), TestCaseError> {
    let span = rule.span();
    assert_span_in_input(span.start, span.end, input, "rule")?;

    prop_assert!(
        !rule.name().trim().is_empty(),
        "Ok Rule must have a non-empty name for input {input:?}"
    );
    prop_assert!(
        !rule.predicates().is_empty(),
        "Ok Rule must contain at least one predicate/condition for input {input:?}"
    );

    for predicate in rule.predicates() {
        prop_assert!(
            !predicate.to_string().trim().is_empty(),
            "Ok Rule contained an empty predicate for input {input:?}"
        );
        let span = predicate.span();
        assert_span_in_input(span.start, span.end, input, "predicate")?;
    }

    Ok(())
}

fn assert_error_is_actionable(err: &RuleError, input: &str) -> Result<(), TestCaseError> {
    let kind = format!("{:?}", err.kind());
    prop_assert!(
        !kind.trim().is_empty(),
        "RuleError kind must be present for input {input:?}"
    );
    prop_assert!(
        !matches!(kind.as_str(), "Unknown" | "Other" | "Unspecified" | "None"),
        "RuleError kind must be specific/actionable for input {input:?}: {kind}"
    );

    let span = err.span();
    assert_span_in_input(span.start, span.end, input, "error")
}

fn assert_span_in_input(
    start: usize,
    end: usize,
    input: &str,
    label: &str,
) -> Result<(), TestCaseError> {
    prop_assert!(
        start <= end,
        "{label} span start must be <= end for input {input:?}: {start}..{end}"
    );
    prop_assert!(
        end <= input.len(),
        "{label} span must be within input bounds for input {input:?}: {start}..{end}, len={}",
        input.len()
    );
    prop_assert!(
        input.is_char_boundary(start) && input.is_char_boundary(end),
        "{label} span must use UTF-8 character boundaries for input {input:?}: {start}..{end}"
    );
    if !input.is_empty() && label == "error" {
        prop_assert!(
            start < end || start == input.len(),
            "error span should cover the offending token or point at EOF for input {input:?}: {start}..{end}"
        );
    }
    Ok(())
}
