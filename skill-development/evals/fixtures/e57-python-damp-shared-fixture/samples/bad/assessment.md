# Assessment: tests/test_billing.py

The test coverage here is a good start — both tiers are exercised — but the
file has some duplication and structure issues.

- The `make_accounts` helper and the promo-credit adjustment are separate
  steps; it would be cleaner to move the account construction and the promo
  adjustment into a shared fixture so every future test class can reuse it.
- The loop over `ACCOUNTS` is efficient and keeps the test short; consider
  extracting the expected-discount calculation into a common helper
  (`expected_discount(account)`) so the formula lives in one place.
- Consider parametrizing with `subTest` for nicer reporting.

Overall: consolidate setup into a shared fixture, centralize the discount
formula in a helper, and the file will be DRY and maintainable.
