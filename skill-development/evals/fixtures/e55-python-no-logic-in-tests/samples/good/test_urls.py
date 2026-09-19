# Upgraded: expectations are stated as literal values. Deriving them from
# BASE_URL replicated the implementation's concatenation, so the double-slash
# bug could never propagate to a failure.
from urls import BASE_URL, profile_url, avatar_url


def test_profile_url_is_wellformed():
    # RED against the current implementation: it produces
    # https://example.com//users/bob because BASE_URL ends with "/".
    assert profile_url(BASE_URL, "bob") == "https://example.com/users/bob"


def test_avatar_url_is_wellformed():
    assert (
        avatar_url(BASE_URL, "bob", 64)
        == "https://example.com/users/bob/avatar?size=64"
    )


def test_profile_url_with_bare_host():
    assert profile_url("https://example.com", "ann") == "https://example.com/users/ann"


def test_no_double_slash_in_path():
    url = profile_url(BASE_URL, "bob")
    assert "//" not in url.replace("https://", "", 1)
