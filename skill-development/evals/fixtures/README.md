# Self-testing Fixture Oracles

These fixtures make the prompt eval suite less brittle by adding deterministic validators for high-value cases. A validator may inspect text or syntax, or execute candidate code when the fixture contains enough project context; the eval's `measurement` metadata must state which kind of evidence it provides. Running an oracle process does not by itself mean the candidate test suite was executed.

Each fixture contains:

- `manifest.json` — eval id, language, oracle command, and sample paths.
- `prompt.md` — the task prompt/fixture description for the eval runner.
- `oracle.py` — validator for a candidate answer/patch directory. Most use only
  the standard library; runtime oracles use dependencies pinned in
  `../requirements.txt`.
- `samples/good/` — minimal candidate that should pass the oracle.
- `samples/bad/` — minimal candidate that should fail the oracle. A manifest may instead use `bad_samples` to register multiple independent adversarial examples.

Run all oracle self-tests:

```bash
python3 -m pip install -r skill-development/evals/requirements.txt
python3 scripts/run-fixture-oracles.py
```

These oracles do not replace human/rubric scoring or runtime validation unless the oracle explicitly executes the candidate. They guard focused failure modes such as fabricated validation, weak Python property tests, Go filesystem/network isolation, Rust `unwrap` in arbitrary-input properties, and Playwright hard waits.
