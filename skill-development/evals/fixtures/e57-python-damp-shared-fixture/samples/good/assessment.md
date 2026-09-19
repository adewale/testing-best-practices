# Assessment: tests/test_billing.py

## P1 — The test contains logic that mirrors the rule under test

`test_discounts` loops over accounts and branches on tier, and the gold-tier
expectation is computed (`account["balance"] * 0.1`) with the same formula the
implementation is supposed to apply. If `compute_discount` mis-derives the
balance the same way, the test passes anyway; a computed expectation can share
a bug with the code under test. Expected values should be literals: for the
gold account with balance 200, assert `compute_discount(account) == 20.0`.

## P1 — Shared mutable module state, mutated far from the assertions

`ACCOUNTS` is a module-level global filled by `make_accounts()` and then
mutated in `setUpClass` (`ACCOUNTS[1]["balance"] += 50`), 15 lines from the
assertion that depends on it. This separates cause and effect: a reader
cannot verify the expectation without tracing the fixture mutation, and any
future test method shares (and can further mutate) the same list, inviting
test-order coupling. Repeated calls to `make_accounts` also grow the list.

## Recommendation — split into per-behavior tests with local, literal data

Replace the single looped test with separate tests, each building its own
account inline and asserting a literal value:

```python
def test_gold_account_gets_ten_percent_of_balance(self):
    account = {"id": 2, "balance": 200, "tier": "gold"}
    self.assertEqual(compute_discount(account), 20.0)

def test_basic_account_gets_no_discount(self):
    account = {"id": 0, "balance": 150, "tier": "basic"}
    self.assertEqual(compute_discount(account), 0)
```

Duplicating the small account literal per test is the right trade here —
test code should stay explicit even at the cost of some repetition, because a
broken shared abstraction in tests has no test of its own to catch it. Keep
any helper strictly for constructing value objects with the asserted-upon
fields passed explicitly; do not route these tests back through a shared
fixture.
