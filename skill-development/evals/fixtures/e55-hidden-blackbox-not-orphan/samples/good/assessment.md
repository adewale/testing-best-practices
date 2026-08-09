# Assessment: tests/test_checkout_api.py

**The audit finding is a false positive. These tests are fine — keep them.**

The tool checks whether a test file imports the module its filename names. This
file does not import `app.checkout`, but that is because it is a **black-box
test**: it drives the real application through its HTTP entry point, and the
route calls `checkout.price_basket()` for it. The code is exercised; only the
import is absent.

Import-based linkage checks cannot see this, which is exactly the noise class
they produce — alongside barrel files, fixtures, and modules reached through a
dynamic import.

## The assertions are strong

Both tests assert specific values rather than shape:
- `subtotal == 1000`, `discount == 100`, `total == 900` pins the bulk-discount
  rule at an exact figure, so a change to the discount arithmetic fails here.
- The sad path pins both the `422` status and the error text.

## Confirm it rather than trusting either verdict

A grep is not evidence of coverage, and it is not evidence of its absence
either. To settle it, break the pricing rule and watch these go red:

```
# temporarily change the bulk discount rate in app/checkout.py
pytest tests/test_checkout_api.py
```

If `test_basket_totals_apply_bulk_discount` fails, the linkage is real and the
finding is closed. Revert the sabotage afterwards.

## Optional, low priority

- Rename to `test_checkout_route.py`, or add a one-line docblock saying it
  covers `checkout.price_basket` through the API, so the next reader — and the
  audit tool — is not misled.
- If the tool supports it, add black-box tests of this shape to its allowlist so
  the finding does not recur.

Do **not** rewrite these to call `price_basket()` directly. That would trade an
end-to-end contract test — which also covers the route, serialization, and the
422 mapping — for a narrower unit test, losing coverage to satisfy a linter.
