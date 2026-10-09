from ledger import Account, apply_deposit

def test_unused_assertion_helper():
    account = Account(id="a", owner="Dana", currency="EUR", balance=100)
    apply_deposit(account, 50, "salary")
    def never_called():
        assert account.balance == 150
        assert account.transactions == [{"kind": "deposit", "amount": 50, "memo": "salary"}]
