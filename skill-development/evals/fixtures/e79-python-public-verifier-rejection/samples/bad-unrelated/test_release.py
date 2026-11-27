def test_prepared_bytes_can_be_reused():
    assert b"abc" + b"!" == b"abc!"
