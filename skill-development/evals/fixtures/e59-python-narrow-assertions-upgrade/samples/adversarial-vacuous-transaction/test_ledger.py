from ledger import Account, apply_deposit


def test_deposit():
    account = Account(id="acc-9", owner="Dana", currency="EUR", balance=100)
    apply_deposit(account, 50, "salary")
    assert account.balance == 150
    # A non-None list says nothing about whether a deposit was recorded.
    assert account.transactions is not None
