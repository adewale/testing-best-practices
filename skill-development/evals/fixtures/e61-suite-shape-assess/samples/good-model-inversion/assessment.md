The suite has a test-pyramid inversion: many slow E2E tests, no integration
tests, and very few unit tests. Move VAT, coupon, and rounding rules close to their implementation in self-contained unit tests. Add an integration layer
and keep a smaller E2E suite for critical user journeys. The first priority is
not adding more Selenium tests or retries.
