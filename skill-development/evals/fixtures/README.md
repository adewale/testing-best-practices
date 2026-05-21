# Runnable Fixture Oracles

These fixtures make the prompt eval suite less brittle by adding executable oracles for high-value cases. Each fixture contains:

- `manifest.json` — eval id, language, oracle command, and sample paths.
- `prompt.md` — the task prompt/fixture description for the eval runner.
- `oracle.py` — stdlib-only validator for a candidate answer/patch directory.
- `samples/good/` — minimal candidate that should pass the oracle.
- `samples/bad/` — minimal candidate that should fail the oracle.

Run all oracle self-tests:

```bash
python3 scripts/run-fixture-oracles.py
```

These oracles do not replace human/rubric scoring. They guard against proxy gaming and eval drift by checking concrete failure modes: fabricated validation, weak Python property tests, Go filesystem/network isolation, Rust `unwrap` in arbitrary-input properties, and Playwright hard waits.
