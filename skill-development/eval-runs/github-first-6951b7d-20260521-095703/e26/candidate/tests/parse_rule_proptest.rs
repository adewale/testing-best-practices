use proptest::prelude::*;
use proptest::test_runner::TestCaseError;
use std::panic::{catch_unwind, AssertUnwindSafe};

use crate::{parse_rule, Rule, RuleError};

fn arbitrary_rule_input() -> impl Strategy<Value = String> {
    let boundary_cases = prop_oneof![
        Just(String::new()),
        Just(" ".to_owned()),
        Just("\t\n".to_owned()),
        Just("\0".to_owned()),
        Just("=".to_owned()),
        Just(":".to_owned()),
        Just("rule".to_owned()),
        Just("rule = value".to_owned()),
        Just("rule -> value".to_owned()),
        Just("a".repeat(4096)),
    ];

    prop_oneof![
        4 => boundary_cases,
        6 => any::<String>(),
        3 => prop::collection::vec(any::<char>(), 0..512)
            .prop_map(|chars| chars.into_iter().collect()),
    ]
}

proptest! {
    #![proptest_config(ProptestConfig {
        cases: 2048,
        max_shrink_iters: 4096,
        .. ProptestConfig::default()
    })]

    #[test]
    fn parse_rule_never_panics_and_returns_well_formed_result(input in arbitrary_rule_input()) {
        let parsed = match catch_unwind(AssertUnwindSafe(|| parse_rule(&input))) {
            Ok(parsed) => parsed,
            Err(_) => return Err(TestCaseError::fail(format!(
                "parse_rule panicked for input {:?}", input
            ))),
        };

        match parsed {
            Ok(rule) => assert_ok_rule_invariants(&rule, &input)?,
            Err(err) => assert_error_kind_and_span_are_useful(&err, &input)?,
        }
    }
}

fn assert_ok_rule_invariants(rule: &Rule, input: &str) -> Result<(), TestCaseError> {
    prop_assert!(
        rule.validate().is_ok(),
        "parse_rule returned Ok for {:?}, but Rule::validate rejected {:?}",
        input,
        rule
    );

    let span = rule.span();
    let start = span.start;
    let end = span.end;

    prop_assert!(start <= end, "rule span must be ordered: {:?}", span);
    prop_assert!(end <= input.len(), "rule span {:?} must fit in input {:?}", span, input);
    prop_assert!(
        input.get(start..end).is_some(),
        "rule span {:?} must be on UTF-8 character boundaries for {:?}",
        span,
        input
    );

    Ok(())
}

fn assert_error_kind_and_span_are_useful(err: &RuleError, input: &str) -> Result<(), TestCaseError> {
    let kind = err.kind();
    let kind_debug = format!("{:?}", kind);
    prop_assert!(
        !kind_debug.trim().is_empty(),
        "RuleError kind must be present for input {:?}: {:?}",
        input,
        err
    );
    prop_assert!(
        !matches!(kind_debug.as_str(), "Unknown" | "None" | "Other"),
        "RuleError kind must be specific for input {:?}: {:?}",
        input,
        err
    );

    let span = err.span();
    let start = span.start;
    let end = span.end;

    prop_assert!(start <= end, "error span must be ordered: {:?}", span);
    prop_assert!(end <= input.len(), "error span {:?} must fit in input {:?}", span, input);
    prop_assert!(
        input.get(start..end).is_some(),
        "error span {:?} must be on UTF-8 character boundaries for {:?}",
        span,
        input
    );

    Ok(())
}
