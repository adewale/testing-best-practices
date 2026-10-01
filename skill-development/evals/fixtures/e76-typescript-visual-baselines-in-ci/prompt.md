Add a Playwright visual regression test for the `.site-header` component and make sure it
runs in CI. Our only baselines are `*-darwin.png` files from a laptop, and the current
config has `retries: process.env.CI ? 2 : 0`. Return `playwright.config.ts`,
`tests/visual.spec.ts`, and any workflow you need.
