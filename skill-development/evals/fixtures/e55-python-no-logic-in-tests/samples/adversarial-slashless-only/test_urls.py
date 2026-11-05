from urls import avatar_url, profile_url


def test_profile_with_bare_host():
    assert profile_url("https://example.com", "bob") == "https://example.com/users/bob"


def test_avatar_with_bare_host():
    assert avatar_url("https://example.com", "bob", 64) == "https://example.com/users/bob/avatar?size=64"
