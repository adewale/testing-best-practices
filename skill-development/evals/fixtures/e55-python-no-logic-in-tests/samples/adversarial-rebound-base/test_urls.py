from urls import BASE_URL, avatar_url, profile_url

BASE_URL = "https://example.com"


def test_profile():
    assert profile_url(BASE_URL, "bob") == "https://example.com/users/bob"


def test_avatar():
    assert avatar_url(BASE_URL, "bob", 64) == "https://example.com/users/bob/avatar?size=64"
