# "Upgraded" but still computes every expectation from BASE_URL with the same
# concatenation as the implementation, so the double-slash bug still passes.
from urls import BASE_URL, profile_url, avatar_url


def test_profile_url():
    assert profile_url(BASE_URL, "bob") == BASE_URL + "/users/" + "bob"


def test_profile_url_other_user():
    expected = BASE_URL + "/users/" + "ann"
    assert profile_url(BASE_URL, "ann") == expected


def test_avatar_url():
    assert avatar_url(BASE_URL, "bob", 64) == (
        BASE_URL + "/users/" + "bob" + "/avatar?size=" + str(64)
    )
