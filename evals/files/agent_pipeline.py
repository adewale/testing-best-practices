"""Multi-step LLM agent pipeline that calls tools in sequence.

Given a user query, the agent:
  1. Calls the LLM to plan tool usage
  2. Calls one or more tools (search, fetch, summarize) in some order
  3. Calls the LLM again to synthesize a final answer

The interesting behavior is the *trace*: which tools the agent picked,
in what order, with what arguments, and what the final synthesized answer
referenced. A bug here looks like "the agent stopped calling search before
fetch" or "the agent now calls summarize twice" — neither of which a
single-call assertion would catch.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Event:
    kind: str  # "llm_call" | "tool_call" | "tool_result" | "final_answer"
    timestamp: float
    request_id: str
    payload: dict[str, Any]


@dataclass
class Session:
    query: str
    events: list[Event] = field(default_factory=list)

    def record(self, kind: str, payload: dict[str, Any]) -> None:
        self.events.append(
            Event(
                kind=kind,
                timestamp=time.time(),
                request_id=str(uuid.uuid4()),
                payload=payload,
            )
        )


def run_agent(
    query: str,
    llm: Callable[[str], dict[str, Any]],
    tools: dict[str, Callable[..., Any]],
) -> Session:
    """Run a single agent session against the supplied LLM and tools.

    `llm(prompt)` returns either {"tool": name, "args": {...}} to invoke a
    tool, or {"final": "answer"} to stop.
    """
    session = Session(query=query)
    prompt = f"User query: {query}\nDecide the next action."

    for _ in range(8):  # max 8 steps
        session.record("llm_call", {"prompt": prompt})
        decision = llm(prompt)
        if "final" in decision:
            session.record("final_answer", {"answer": decision["final"]})
            return session

        tool_name = decision["tool"]
        args = decision.get("args", {})
        session.record("tool_call", {"tool": tool_name, "args": args})

        result = tools[tool_name](**args)
        session.record("tool_result", {"tool": tool_name, "result": result})

        prompt = (
            f"User query: {query}\n"
            f"Last tool {tool_name} returned: {result!r}\n"
            "Decide the next action."
        )

    session.record("final_answer", {"answer": "[step limit reached]"})
    return session
