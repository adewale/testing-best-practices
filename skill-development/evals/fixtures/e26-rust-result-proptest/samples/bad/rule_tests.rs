use proptest::prelude::*;
use crate::parse_rule;

proptest! {
    #[test]
    fn parse_rule_accepts_arbitrary_input(input in ".*") {
        let rule = parse_rule(&input).unwrap();
        prop_assert!(!rule.name().is_empty());
    }
}
