Audit this CI for dead or always-green gates and list findings by severity.

```yaml
name: CI
on:
  pull_request:
  schedule: [{cron: '0 3 * * *'}]
jobs:
  unit:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -e '.[test]' && pytest -q -m "not live"
  live:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    env: {RUN_LIVE: '1', STAGING_URL: '${{ secrets.STAGING_URL }}'}
    steps:
      - uses: actions/checkout@v4
      - run: test -n "$STAGING_URL" || { echo "STAGING_URL missing"; exit 1; }
      - run: pip install -e '.[test]' && pytest -q -m live -rs --junitxml=live.xml
      - run: python scripts/assert_no_skips.py live.xml   # fails if any live test skipped
  dependency-audit:   # owner: @platform-team; advisory by design
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - run: pip install pip-audit && pip-audit
      - if: failure()
        run: gh issue create --title "pip-audit found vulnerabilities" --label security
```

`tests/test_live.py` starts with
`pytestmark = pytest.mark.skipif(not os.environ.get("RUN_LIVE"), reason="needs staging")`.
