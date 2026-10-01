Our CI is always green but bugs keep escaping. Make every gate in `ci.yml` able to fail,
without removing any gate. `pyproject.toml` already sets `[tool.coverage.report] fail_under = 80`.
Return the corrected `ci.yml`.

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install -e '.[test]'
      - name: Unit tests
        run: pytest -q || true
      - name: Secrets scan
        run: detect-secrets scan --baseline .secrets.baseline
  e2e:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e '.[test]' && pytest -q tests/e2e
```
