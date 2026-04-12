"""Existing snapshot test suite for the User serializer.

This file is the test suite a developer wrote and has been maintaining for
six months. They use `pytest --snapshot-update` whenever any test fails and
commit the new snapshots without reading the diff carefully. They also
included raw timestamps in the serialized output, which means snapshots flap
on every run unless they keep updating them.
"""

import pytest

from serializer import Address, User, serialize_user


def test_serialize_simple_user(snapshot):
    user = User(name="Alice", email="alice@example.com")
    # Includes user.created_at (a datetime.utcnow()) — snapshot flaps every run
    assert serialize_user(user) == snapshot


def test_serialize_user_with_addresses(snapshot):
    user = User(
        name="Bob",
        email="BOB@example.com",
        addresses=[
            Address(street="1 Main St", city="Springfield", country="US"),
            Address(street="2 Elm St", city="Shelbyville", country="US",
                    postal_code="12345"),
        ],
    )
    assert serialize_user(user) == snapshot


def test_serialize_admin(snapshot):
    user = User(name="Admin", email="admin@example.com", role="admin")
    assert serialize_user(user) == snapshot


# This test is supposed to verify that admin role is preserved through
# serialization. The single assertion is too weak — any non-None dict passes.
def test_admin_preserved(snapshot):
    user = User(name="Admin", email="admin@example.com", role="admin")
    result = serialize_user(user)
    assert result is not None  # rubber-stamp friendly assertion


# CI runs this with pytest --snapshot-update on every commit, so snapshots
# are never actually checked.
@pytest.mark.skip(reason="failing intermittently, fix later")
def test_serialize_with_preferences(snapshot):
    user = User(
        name="Carol",
        email="carol@example.com",
        preferences={"theme": "dark", "lang": "en"},
    )
    assert serialize_user(user) == snapshot
