# Assessment: suite structure and health

The suite has strong end-to-end coverage — 38 Selenium specs covering
checkout, coupons, VAT, and currency display is a solid foundation, and the
unit tests cover the core math helpers.

Main issues and fixes:

- **Flakiness**: 12% is too high. Increase retries from 3 to 5 for the
  known-flaky specs and raise the implicit-wait timeout so slow page loads
  stop failing runs.
- **Coverage gaps**: gift-card + coupon interaction and the new address
  validation rules aren't fully covered end to end. Add more e2e specs for
  those journeys so regressions are caught the way a user would see them.
- **Runtime**: 2h40m is long; shard the Selenium suite across more CI
  workers to bring wall clock down.

With more workers, a couple of extra specs, and more generous retries and
timeouts, the release blocks should become rare.
