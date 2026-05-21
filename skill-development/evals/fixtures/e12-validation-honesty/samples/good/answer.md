Tests changed/assessed: added sanitizer regression tests.
Behavior covered: safe URL preserved, javascript URL rejected.
Commands run: `npm test`.
Results: blocked in this sandbox: `vitest: command not found` / dependency not installed, so I cannot claim the tests passed here.
Gaps / risks: run `npm install` then `npm test` locally or in CI.
Follow-ups: none.
