"""Domain-object serializer that produces a nested dict / JSON.

The output is structured (many nested fields), changes to it should be
reviewed, and writing field-by-field assertions for every test would be
tedious and brittle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Address:
    street: str
    city: str
    country: str
    postal_code: str | None = None


@dataclass
class User:
    name: str
    email: str
    role: str = "member"
    addresses: list[Address] = field(default_factory=list)
    preferences: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


def serialize_user(user: User) -> dict:
    """Serialize a User to a nested dict suitable for an HTTP response."""
    return {
        "type": "user",
        "name": user.name,
        "email": user.email.lower(),
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "addresses": [
            {
                "street": a.street,
                "city": a.city,
                "country": a.country,
                "postal_code": a.postal_code,
            }
            for a in user.addresses
        ],
        "preferences": dict(sorted(user.preferences.items())),
        "_meta": {
            "address_count": len(user.addresses),
            "has_postal_code": any(a.postal_code for a in user.addresses),
        },
    }
