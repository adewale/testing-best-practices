# Assessment: tests/test_checkout_api.py

**Antipattern: orphan test. This file is disconnected from the code it claims to
test.**

`test_checkout_api.py` names the checkout module but never imports
`app.checkout`. The pricing logic in `price_basket()` therefore has no real
coverage — the suite is green for the wrong reason, and a change to the discount
rules would not be caught here.

## Recommendations

1. Rewrite these tests to import `app.checkout` and call `price_basket()`
   directly, so the test is linked to the module it names.
2. Delete the two route tests once the unit tests exist; they duplicate what the
   direct tests will cover and only add runtime.
3. Add a CI gate that fails on any test file which does not import its named
   module, so orphan tests cannot reappear.
