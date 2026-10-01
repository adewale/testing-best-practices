from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, MutableMapping, Optional, Tuple, Type


REGISTRY: Dict[str, Type["OneWayMember"]] = {}


class OneWayMember:
    """Base class for automatically enrolled, idempotent normalizers."""

    member_id: str

    def __init_subclass__(
        cls,
        *,
        member_id: str,
        registry: Optional[MutableMapping[str, Type["OneWayMember"]]] = None,
        **kwargs: object,
    ) -> None:
        super().__init_subclass__(**kwargs)
        target = REGISTRY if registry is None else registry

        if not member_id:
            raise ValueError("member_id must not be empty")
        if member_id in target:
            raise ValueError(f"duplicate member_id: {member_id}")

        cls.member_id = member_id
        target[member_id] = cls

    @staticmethod
    def normalize(value: str) -> str:
        raise NotImplementedError


class StripWhitespace(OneWayMember, member_id="strip-whitespace"):
    @staticmethod
    def normalize(value: str) -> str:
        return value.strip()


class CollapseWhitespace(OneWayMember, member_id="collapse-whitespace"):
    @staticmethod
    def normalize(value: str) -> str:
        return " ".join(value.split())


@dataclass(frozen=True)
class OneWayCase:
    member_id: str
    member: Type[OneWayMember]
    samples: Tuple[str, ...] = (
        "",
        "plain",
        "  Alpha  BETA  ",
        "\tline\nbreak\t",
    )


def one_way_cases(
    registry: Mapping[str, Type[OneWayMember]],
) -> Tuple[OneWayCase, ...]:
    """Generate exactly one conformance case for every registry member."""
    return tuple(
        OneWayCase(member_id=member_id, member=registry[member_id])
        for member_id in sorted(registry)
    )


def contract_passes(case: OneWayCase) -> bool:
    """A one-way normalizer must return strings and be idempotent."""
    if case.member.member_id != case.member_id:
        return False

    try:
        for sample in case.samples:
            once = case.member.normalize(sample)
            if not isinstance(once, str):
                return False
            if case.member.normalize(once) != once:
                return False
    except Exception:
        return False

    return True
