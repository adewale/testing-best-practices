# PDA test audit

**1. The dollar cap masked a separate limit on unresolved calls.** PDA allows at most two unresolved demo calls per person per UTC day. The existing overlap test exhausts the $1 allowance before requesting a third call, so it still passes if the ledger admits three. The production agent gives its SQLite ledger to the router, which checks local admission before provider dispatch and records any smaller reservation granted by the shared domain. See `pda-spec.md:249`, `src/agent.ts:202`, `src/model-router.ts:387`, `src/model-router.ts:403` and `test/budget.test.ts:141`.

Added a workerd test at `test/budget.test.ts:166`. It supplies a $0.25 partial grant through the ledger API, admits a second call, evicts the Durable Object and verifies that the third call is refused with $0.25 still available. Settling the first call opens a slot, and the next UTC day has its own allowance. Existing checks cover competing shared reservations, replay after a lost settlement response, and charging a background summary (`test/budget.test.ts:42`, `test/budget.test.ts:74`, `test/compaction.test.ts:233`).

**2. The overlap test can stall on slow dispatch.** After 100 one-millisecond polls, its diagnostic awaits a stream that the test completes later. The dispatch promise in the sibling key-generation test shows how to wait for the event directly. This risk came from inspection. The overlap test passed locally. See `test/budget.test.ts:133`, `test/budget.test.ts:151` and `test/model-key-generation.test.ts:25`.

**Local validation** used Node 24.22.3 with Wrangler metrics disabled.

```sh
node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/budget.test.ts
node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config test/vitest.config.ts test/compaction.test.ts
npm run typecheck
git diff --check
```

Budget passed 8/8 before the patch and 9/9 after. In an isolated copy, changing `>= 2` to `> 2` at `src/budget.ts:108` passed all eight original tests. With the patch, only the new case failed (exit 1) because it received a $0.25 reservation where it expected `null`. Restoring the source byte-for-byte returned 9/9. The scratch copy was removed. Compaction passed 18/18. Typecheck and diff check exited 0.

**Scope.** The supplied CI job recorded a successful full-checkout `npm test` on main at `c0a9a85c`, before this patch (`.github/workflows/ci.yml:66`, `scripts/test-projects.mjs:2`, `ci/jobs-45800972889.json`). Local execution covered the two named Workers files. The inventory supplied 56 of 155 named modules and omitted both `test/model-access.test.ts` and `test/properties/budget.test.ts`.
