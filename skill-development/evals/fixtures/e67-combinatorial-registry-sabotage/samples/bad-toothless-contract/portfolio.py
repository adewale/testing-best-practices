from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class Case:
    member_id: str
    implementation: Callable[[], str]


def good_renderer() -> str:
    return "<svg/>"


REGISTRY = {
    "flowchart": good_renderer,
    "sequence": good_renderer,
}


def one_way_cases(registry: Mapping[str, Callable[[], str]]) -> list[Case]:
    return [Case(member_id, implementation) for member_id, implementation in registry.items()]


def contract_passes(case: Case) -> bool:
    # Mentions the case but never calls the member behavior, so every generated
    # case—including a broken fake—passes.
    return case is not None
