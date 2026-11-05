This is an inverted pyramid and an hourglass because the integration tier is
absent. Relocate business-rule coverage below the browser, including VAT,
coupon stacking, and rounding. Keep 5–15 E2E golden journeys, add focused
integration tests, and triage flakes before adding retries or more E2E.

```json
{
  "business_rule_tier": "domain",
  "integration_contracts": true,
  "browser_role": "wiring_and_core_journeys",
  "retry_action": "diagnose_not_increase",
  "first_action": "move_rule_tests"
}
```
