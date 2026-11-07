#!/usr/bin/env python3
"""Check six explicit inventory decisions; never execute model-supplied code.

This is a bounded plan oracle, not evidence of a working cleanup or honest prose.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
MAX_BYTES = 65536


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def grade(root: Path) -> list[str]:
    source = root / "answers.json"
    if not source.exists():
        source = root / "output.md"
    if not source.is_file() or source.stat().st_size > MAX_BYTES:
        return ["missing or oversized candidate answers"]
    text = source.read_text()
    if source.suffix == ".md":
        fences = re.findall(r"```json\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if fences:
            if len(fences) != 1:
                return ["expected exactly one JSON answer fence"]
            text = fences[0]
    try:
        answers = json.loads(text, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as exc:
        return [f"invalid candidate JSON: {exc}"]
    expected = json.loads((FIXTURE / "expected.json").read_text())
    if not isinstance(answers, list) or len(answers) != len(expected):
        return ["expected one inventory decision for each of six cases"]
    seen = set()
    errors = []
    for answer in answers:
        if not isinstance(answer, dict):
            errors.append("answer must be an object")
            continue
        ident = answer.get("id")
        if not isinstance(ident, str) or ident not in expected or ident in seen:
            errors.append("unknown or duplicate case ID")
            continue
        seen.add(ident)
        wanted = expected[ident]
        if answer.get("decision") != wanted["decision"]:
            errors.append(f"{ident}: unsupported next action")
        for field in ("retire", "retain", "introduce"):
            values = answer.get(field)
            if (not isinstance(values, list)
                    or any(not isinstance(value, str) for value in values)
                    or len(values) != len(set(values))
                    or set(values) != set(wanted[field])):
                errors.append(f"{ident}: incorrect {field} inventory")
        for field in ("rationale", "validation"):
            if not isinstance(answer.get(field), str) or not answer[field].strip():
                errors.append(f"{ident}: missing {field}")
    if seen != set(expected):
        errors.append("case inventory incomplete")
    return errors


def main() -> int:
    errors = grade(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    for error in errors:
        print(error, file=sys.stderr)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
