from urls import BASE_URL, profile_url, avatar_url


def test_unrelated_expected_value():
    assert profile_url(BASE_URL, "bob") == avatar_url(BASE_URL, "bob", 64)
    assert "https://example.com/users/bob" == "https://example.com/users/bob"
