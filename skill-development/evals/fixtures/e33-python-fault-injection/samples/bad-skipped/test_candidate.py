import pytest


@pytest.mark.skip(reason="unavailable")
def test_contract():
    # raise ConnectionError; retry and assert recovery.
    assert False
