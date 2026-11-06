import pytest
@pytest.mark.skip(reason="candidate skipped behavior")
def test_missing():
    assert False
