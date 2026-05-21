#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    py = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.py"))
    low = py.lower()
    fixture_files = list(root.rglob("*.json")) + list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
    errors = []
    if not fixture_files and "@pytest.mark.vcr" not in low and "vcr" not in low:
        errors.append("missing recorded fixture/cassette")
    if "monkeypatch.setattr" in low and not fixture_files and "schema" not in low and "contract" not in low:
        errors.append("hand-written monkeypatch remains sole oracle")
    if re.search(r"requests\.(get|post|put|delete)\(", low) and "record" not in low and "fixture" not in low and "vcr" not in low:
        errors.append("appears to call live requests directly in normal test")
    if not any(token in low for token in ["statuscode", "status_code", "schema", "contract", "fixture", "required_fields", "legacy_fields"]):
        errors.append("missing provider shape/contract assertion")
    # If JSON fixtures exist, require at least one to contain a realistic provider
    # shape: either envelope status+data or a body with multiple domain fields.
    has_shape = False
    for path in fixture_files:
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if isinstance(data, dict) and ("statusCode" in data or "status_code" in data) and ("data" in data or "body" in data):
            has_shape = True
            break
        if isinstance(data, dict) and isinstance(data.get("response"), dict):
            response = data["response"]
            body = response.get("json") or response.get("body") or {}
            if ("status_code" in response or "statusCode" in response) and isinstance(body, dict) and len(body.keys()) >= 3:
                has_shape = True
                break
        if isinstance(data, dict) and len(data.keys()) >= 3 and any(k in data for k in ["id", "email", "display_name", "account_status"]):
            has_shape = True
            break
    if fixture_files and not has_shape:
        errors.append("recorded fixture lacks realistic provider shape")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
