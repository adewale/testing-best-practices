# E59 — Upgrade: a deposit test that breaks whenever anything else changes

This test failed this week when an unrelated `schema_version` field was added
to `Account`. The deposit behavior it tests is unchanged, and this is the
third time an unrelated field addition has broken it.

`ledger.py`:

```python
from dataclasses import dataclass, field, asdict


@dataclass
class Account:
    id: str
    owner: str
    currency: str
    balance: int
    transactions: list = field(default_factory=list)
    overdraft_limit: int = 0
    status: str = "active"
    region: str = "us"
    schema_version: int = 3  # added this week for the migration tooling


def apply_deposit(account, amount, memo):
    account.balance += amount
    account.transactions.append({"kind": "deposit", "amount": amount, "memo": memo})
    return account
```

`tests/test_ledger.py` (currently failing):

```python
from dataclasses import asdict

from ledger import Account, apply_deposit


def test_apply_deposit():
    account = Account(id="acc-9", owner="Dana", currency="EUR", balance=100)
    apply_deposit(account, 50, "salary")
    assert asdict(account) == {
        "id": "acc-9",
        "owner": "Dana",
        "currency": "EUR",
        "balance": 150,
        "transactions": [{"kind": "deposit", "amount": 50, "memo": "salary"}],
        "overdraft_limit": 0,
        "status": "active",
        "region": "us",
    }
```

Task: upgrade `tests/test_ledger.py` (write the revised `.py` file) so it
verifies the deposit behavior and stops breaking when unrelated fields are
added. Brief notes are welcome as comments or a short `.md`.
