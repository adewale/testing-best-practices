from urls import BASE_URL, profile_url, avatar_url


def test_unused_nested_helper():
    def never_called():
        assert profile_url(BASE_URL, "bob") == "https://example.com/users/bob"
        assert avatar_url(BASE_URL, "bob", 64) == "https://example.com/users/bob/avatar?size=64"
    assert True
