Commands run: `make check`
Results: **failed** — make exited non-zero (exit code 2, `Error 1` from the check target).
`ruff` and the link checker reported no problems, but `scripts/check_schema.py` crashed
with a traceback, so the schema check did not run to completion.
Gaps / risks: schema validation is unverified until the crash is fixed and `make check`
exits 0.
