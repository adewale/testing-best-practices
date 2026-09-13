# Upgraded: assert the fields the deposit behavior is about, not the whole
# object. Whole-object equality implicitly tested every unrelated field, so
# any field addition broke this test without any behavior change.
from ledger import Account, apply_deposit


def make_account(**overrides):
    defaults = dict(id="acc-9", owner="Dana", currency="EUR", balance=100)
    defaults.update(overrides)
    return Account(**defaults)


def test_apply_deposit_increases_balance():
    account = make_account()
    apply_deposit(account, 50, "salary")
    assert account.balance == 150


def test_apply_deposit_records_transaction():
    account = make_account()
    apply_deposit(account, 50, "salary")
    assert account.transactions == [
        {"kind": "deposit", "amount": 50, "memo": "salary"}
    ]


def test_apply_deposit_returns_same_account():
    account = make_account()
    assert apply_deposit(account, 50, "salary") is account

# If a whole-state check is ever needed (e.g. serialization), it belongs in a
# deliberate save/load roundtrip test, not in this behavior test.
