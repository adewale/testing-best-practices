from ledger import Account, apply_deposit

def test_assertions_before_the_behaviour():
    account = Account(id="a", owner="Dana", currency="EUR", balance=150)
    account.transactions = [{"kind": "deposit", "amount": 50, "memo": "salary"}]
    assert account.balance == 150
    assert account.transactions == [{"kind": "deposit", "amount": 50, "memo": "salary"}]
    apply_deposit(account, 50, "salary")
