from ledger import Account, apply_deposit

def test_checks_an_unrelated_balance():
    account = Account(id="a", owner="Dana", currency="EUR", balance=100)
    other = Account(id="b", owner="Lee", currency="EUR", balance=150)
    apply_deposit(account, 50, "salary")
    assert other.balance == 150
    assert account.transactions == [{"kind": "deposit", "amount": 50, "memo": "salary"}]
