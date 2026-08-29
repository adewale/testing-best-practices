# E61 — Assess: test-suite structure and health

Here is the current test inventory for a mid-sized web shop repository, taken
from the CI config and the tree. Assess this suite's structure and health,
and say what you would change first. Write your assessment as Markdown.

```
tests/e2e/          38 files (Selenium; avg runtime ~4 min each;
                    30-day flake rate 12%)
  checkout_flow_spec.py, login_spec.py, search_filters_spec.py,
  coupon_codes_spec.py, gift_card_spec.py, currency_display_spec.py,
  address_validation_spec.py, vat_rules_spec.py, ... (30 more)

tests/unit/         4 files (pytest; < 2s total)
  test_price_math.py, test_slug.py, test_dates.py, test_csv_export.py

tests/integration/  (directory does not exist)
```

CI notes:
- The full e2e suite runs on every PR (~2h40m wall clock, 3 retries
  configured per test).
- A release is blocked roughly twice a week by a red e2e run that passes on
  retry.
- Most e2e specs assert business rules (VAT rates by country, coupon
  stacking, currency rounding) by driving the browser through checkout.
```
