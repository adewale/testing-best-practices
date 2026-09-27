**P0 — the fidelity test pins the mock author's belief, not D1.** The test is named
`changes_0` but asserts `changes == 1` for a DELETE that matches nothing. SQLite (and
therefore D1) reports 0 rows changed for a no-match DELETE, and `routes.py` relies on
`changes == 0` to return 409. With this MockD1 default the 409 branch is unreachable in
tests.

Fix: derive the expected value from the real engine — run the statement against
`sqlite3` or a local D1 (`wrangler d1 execute --local --json`), record the `meta`
response as a fixture, and make the fidelity test compare MockD1 against that
recording. Then add a test that the duplicate-tag path returns 409.
