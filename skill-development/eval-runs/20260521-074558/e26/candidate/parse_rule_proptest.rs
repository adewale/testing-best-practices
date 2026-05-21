// Candidate tests for parse_rule(input: &str) -> Result<Rule, RuleError>.
// Place this module next to parse_rule (or change `super::*` to the crate path).
// Assumes Rule exposes public accessors such as span/name/action/conditions and
// RuleError exposes kind/span; keep the assertions if the exact names differ.

#[cfg(test)]
mod parse_rule_property_tests {
    use super::*;
    use proptest::prelude::*;
    use std::ops::Range;
    use std::panic::{catch_unwind, AssertUnwindSafe};

    proptest! {
        #[test]
        fn arbitrary_strings_never_panic_and_return_well_formed_results(input in any::<String>()) {
            let parsed = catch_unwind(AssertUnwindSafe(|| parse_rule(&input)));
            prop_assert!(parsed.is_ok(), "parse_rule panicked for input {input:?}");

            match parsed.unwrap() {
                Ok(rule) => assert_rule_invariants(&rule, &input)?,
                Err(err) => assert_error_has_useful_kind_and_span(&err, &input)?,
            }
        }
    }

    fn assert_rule_invariants(rule: &Rule, input: &str) -> Result<(), TestCaseError> {
        let rule_span = rule.span();
        assert_valid_span("rule", rule_span.clone(), input)?;

        prop_assert!(
            !rule.name().trim().is_empty(),
            "accepted rule must have a non-empty name: {rule:?}"
        );
        prop_assert!(
            !rule.action().trim().is_empty(),
            "accepted rule must have a non-empty action: {rule:?}"
        );

        for condition in rule.conditions() {
            let condition_span = condition.span();
            assert_valid_span("condition", condition_span.clone(), input)?;
            prop_assert!(
                rule_span.start <= condition_span.start && condition_span.end <= rule_span.end,
                "condition span {condition_span:?} must be inside rule span {rule_span:?}"
            );
            prop_assert!(
                !condition.field().trim().is_empty(),
                "condition field must be non-empty: {condition:?}"
            );
            prop_assert!(
                !condition.operator().trim().is_empty(),
                "condition operator must be non-empty: {condition:?}"
            );
            prop_assert!(
                !condition.value().trim().is_empty(),
                "condition value must be non-empty: {condition:?}"
            );
        }

        Ok(())
    }

    fn assert_error_has_useful_kind_and_span(err: &RuleError, input: &str) -> Result<(), TestCaseError> {
        let kind_debug = format!("{:?}", err.kind());
        prop_assert!(!kind_debug.trim().is_empty(), "error kind must be printable: {err:?}");
        prop_assert_ne!(kind_debug, "Unknown", "error kind should be specific: {err:?}");

        assert_valid_span("error", err.span(), input)?;

        let message = err.to_string();
        prop_assert!(
            !message.trim().is_empty(),
            "error Display message should help diagnose parse failures: {err:?}"
        );

        Ok(())
    }

    fn assert_valid_span(label: &str, span: Range<usize>, input: &str) -> Result<(), TestCaseError> {
        prop_assert!(
            span.start <= span.end,
            "{label} span start must be <= end: {span:?}"
        );
        prop_assert!(
            span.end <= input.len(),
            "{label} span {span:?} must fit within input byte length {}",
            input.len()
        );
        prop_assert!(
            input.is_char_boundary(span.start) && input.is_char_boundary(span.end),
            "{label} span {span:?} must align to UTF-8 character boundaries in {input:?}"
        );
        Ok(())
    }
}
