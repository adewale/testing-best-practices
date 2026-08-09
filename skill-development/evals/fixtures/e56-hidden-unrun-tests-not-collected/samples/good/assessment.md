# What the green suite actually guarantees

**Less than the 210 suggests. Two of your payment safety nets cannot fail.**

## 1. `test/staging/payment-failures.test.ts` never runs

`include: ['src/**/*.test.ts']` collects only files under `src/`. That file is
under `test/staging/`, so Vitest does not collect it. Its 31 tests — declined
card, gateway timeout, partial capture, idempotency key reuse — are not part of
the 210, and have not run for as long as that glob has been in place. Those are
exactly the failure paths a payment change puts at risk.

Confirm it in one command rather than trusting my reading of the glob:

```
npx vitest list        # what the runner actually collects
```

Diff that against the test files on disk. Anything on disk and not in the list
is a file that cannot fail.

## 2. The e2e job cannot fail the build

`continue-on-error: true` on the `e2e` job means those 18 Playwright tests are
advisory: they can be red for months and CI stays green. Check the last few
runs — if they are currently failing, you have been shipping past them.

## So the real coverage of the payment path is

`src/payment/capture.test.ts`, 12 tests, happy path plus whatever it covers.
The declined/timeout/partial/idempotency cases are unguarded.

## What to do before shipping

1. Widen the glob to `include: ['src/**/*.test.ts', 'test/**/*.test.ts']` and
   run it. Expect failures — those tests have not been maintained against a
   running suite, so treat the first red as information, not as a blocker.
2. Prove the 31 tests can now fail: break `capture.ts` (reject every card) and
   confirm the declined-card test goes red. A test that is merely collected is
   not yet a test that works.
3. Make the e2e job gating, or delete it. An advisory lane that nobody reads is
   worse than no lane, because it looks like coverage on the CI page.
4. Add a check that diffs collected-vs-on-disk so a file cannot silently fall
   out of the glob again. Land it advisory with today's known gaps allowlisted,
   then make it blocking once the list is empty.
