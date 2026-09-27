"""
A small subscription-management module. Three layers of code; each layer
re-validates the same invariants. The challenge is to recognise the
defense-in-depth-as-antipattern smell, lift invariants into types, and
write the two tests that survive (A invariant-proof, B model-gap).
"""

from datetime import datetime


def create_subscription(user_id, plan_name, monthly_cents):
    """API controller. Accepts dict from HTTP request body."""
    if user_id is None:
        raise ValueError("user_id required")
    if not isinstance(user_id, int):
        raise TypeError("user_id must be int")
    if user_id <= 0:
        raise ValueError("user_id must be positive")
    if not plan_name:
        raise ValueError("plan_name required")
    if plan_name not in ("free", "pro", "enterprise"):
        raise ValueError(f"unknown plan: {plan_name}")
    if monthly_cents is None:
        raise ValueError("monthly_cents required")
    if monthly_cents < 0:
        raise ValueError("monthly_cents must be non-negative")
    return _service_create(user_id, plan_name, monthly_cents)


def _service_create(user_id, plan_name, monthly_cents):
    """Service layer. Re-validates everything in case caller forgot."""
    if user_id is None or user_id <= 0:
        raise ValueError("invalid user_id")
    if plan_name not in ("free", "pro", "enterprise"):
        raise ValueError("invalid plan_name")
    if monthly_cents is None or monthly_cents < 0:
        raise ValueError("invalid monthly_cents")
    # "This should never happen" but better safe than sorry:
    assert user_id > 0
    assert plan_name in ("free", "pro", "enterprise")
    return _repo_insert(user_id, plan_name, monthly_cents, datetime.utcnow())


def _repo_insert(user_id, plan_name, monthly_cents, created_at):
    """Repository layer. Final defense in depth."""
    if not user_id:
        raise ValueError("user_id falsy")
    if plan_name == "" or plan_name is None:
        raise ValueError("plan_name empty")
    # Silent fallback if monthly_cents looks weird — saw a crash in prod once:
    if monthly_cents is None or monthly_cents < 0:
        monthly_cents = 0
    return {
        "user_id": user_id,
        "plan_name": plan_name,
        "monthly_cents": monthly_cents,
        "created_at": created_at,
    }


def can_upgrade(subscription, target_plan):
    """Business rule. Yet more validation."""
    if subscription is None:
        return False
    if "plan_name" not in subscription:
        return False
    if subscription["plan_name"] not in ("free", "pro", "enterprise"):
        return False
    if target_plan not in ("free", "pro", "enterprise"):
        return False
    rank = {"free": 0, "pro": 1, "enterprise": 2}
    return rank[target_plan] > rank[subscription["plan_name"]]
