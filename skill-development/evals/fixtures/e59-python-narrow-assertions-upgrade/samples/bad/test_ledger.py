# "Fixed" by adding the new field to the literal — the change-detector
# treadmill: the next field addition breaks it again.
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
        "schema_version": 3,
    }
