# E27 TypeScript Playwright Flake Fixture

A Playwright test uses `page.waitForTimeout(2000)` before checking a toast. It flakes under slow CI. Upgrade it using project conventions.
