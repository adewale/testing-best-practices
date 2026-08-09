# E56 Assess what a green suite actually guarantees

We are about to ship a change to payment capture. `npm test` reports
**210 passed, 0 failed** and CI is green. Before I ship, tell me what this
suite actually guarantees about the payment path.

`vitest.config.ts`:

```ts
export default defineConfig({
  test: {
    include: ['src/**/*.test.ts'],
    exclude: ['**/node_modules/**'],
  },
})
```

Repository layout (abridged):

```
src/payment/capture.ts
src/payment/capture.test.ts          12 tests
src/cart/…                           198 tests across src/**
test/staging/payment-failures.test.ts   31 tests  ("declined card", "gateway timeout",
                                                   "partial capture", "idempotency key reuse")
e2e/checkout.spec.ts                    18 Playwright tests
```

`.github/workflows/ci.yml`:

```yaml
  unit:
    run: npm test
  e2e:
    continue-on-error: true
    run: npx playwright test
```

`package.json` scripts: `"test": "vitest run"`.
