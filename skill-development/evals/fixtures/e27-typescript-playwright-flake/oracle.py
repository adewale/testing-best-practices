#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path

BAD = ["waitForTimeout", "setTimeout", "test.only", "test.skip", ".only(", ".skip("]
GOOD_LOCATORS = ["getByRole", "getByText", "getByLabel", "getByTestId"]
GOOD_ASSERTS = ["toBeVisible", "toHaveText", "toContainText", "toHaveAttribute"]


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    text = "\n".join(p.read_text(errors="ignore") for p in list(root.rglob("*.ts")) + list(root.rglob("*.tsx")))
    errors = []
    for token in BAD:
        if token in text:
            errors.append(f"forbidden flake/sabotage token: {token}")
    if not any(token in text for token in GOOD_LOCATORS):
        errors.append("missing user-facing Playwright locator")
    if not any(token in text for token in GOOD_ASSERTS):
        errors.append("missing web-first assertion")
    if re.search(r"locator\(['\"](\.|#|//)", text):
        errors.append("uses brittle css/xpath locator where user-facing locator expected")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
