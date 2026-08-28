# E57 — Assess: billing discount tests

Assess the quality of this test file and describe what you would change and
why. Write your assessment as Markdown.

`tests/test_billing.py`:

```python
import unittest

from billing import compute_discount

ACCOUNTS = []


def make_accounts():
    for i in range(3):
        ACCOUNTS.append(
            {"id": i, "balance": 100 * i, "tier": "gold" if i == 2 else "basic"}
        )


class TestBilling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        make_accounts()
        # promo credit applied so premium scenarios are covered too
        ACCOUNTS[1]["balance"] += 50

    def test_discounts(self):
        for account in ACCOUNTS:
            if account["tier"] == "gold":
                self.assertEqual(
                    compute_discount(account), account["balance"] * 0.1
                )
            else:
                self.assertEqual(compute_discount(account), 0)
```

For reference, `billing.compute_discount(account)` is documented as: gold-tier
accounts get a discount of 10% of their balance; all other tiers get no
discount.
