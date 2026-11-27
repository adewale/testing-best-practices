import pytest


@pytest.mark.skip(reason="unavailable")
def test_contract():
    # clock advance and assert the callback ran.
    assert False
