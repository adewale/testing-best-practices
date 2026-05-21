use proptest::prelude::*;
use crate::parse_rule;

proptest! {
    #[test]
    fn parse_rule_returns_valid_rule_or_structured_error(input in ".*") {
        let parsed = parse_rule(&input);
        match parsed {
            Ok(rule) => {
                prop_assert!(!rule.name().trim().is_empty());
                prop_assert!(rule.span().start <= rule.span().end);
            }
            Err(err) => {
                prop_assert!(err.span.start <= err.span.end);
                prop_assert!(matches!(err.kind, RuleErrorKind::Syntax | RuleErrorKind::EmptyName));
            }
        }
    }
}
