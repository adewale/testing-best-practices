"""
A small user service. Two operations with primitive-typed parameters and
heavy runtime validation that could be lifted into the type system.
"""


def create_user(email: str, age: int, role: str) -> dict:
    """Create a user. All validation done at runtime here."""
    if not email or "@" not in email:
        raise ValueError("invalid email")
    if email.count("@") > 1:
        raise ValueError("multiple @ in email")
    if not isinstance(age, int):
        raise TypeError("age must be int")
    if age < 0 or age > 150:
        raise ValueError("age out of range")
    if role not in ("admin", "user", "guest"):
        raise ValueError("invalid role")
    return {"email": email.lower(), "age": age, "role": role}


def upgrade_role(user: dict, new_role: str) -> dict:
    """Upgrade a user's role. Re-validates the dict shape and the new role."""
    if user is None:
        raise ValueError("user required")
    if "role" not in user:
        raise ValueError("user missing role")
    if user["role"] not in ("admin", "user", "guest"):
        raise ValueError("user has invalid role")
    if new_role not in ("admin", "user", "guest"):
        raise ValueError("invalid new_role")
    ranks = {"guest": 0, "user": 1, "admin": 2}
    if ranks[new_role] <= ranks[user["role"]]:
        raise ValueError("cannot downgrade or stay at same level")
    return {**user, "role": new_role}


def can_send_email(user: dict) -> bool:
    """Yet another consumer that re-checks the dict shape."""
    if user is None:
        return False
    if "email" not in user or "@" not in user["email"]:
        return False
    return True
