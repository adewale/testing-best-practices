# Assessment: suite structure and health

## P0 — The suite is an inverted pyramid (ice-cream cone)

38 Selenium E2E files sit on top of only 4 unit files, with no integration
tier at all. The shape, not any individual test, is the root problem: nearly
all verification happens in the slowest, flakiest, least failure-isolating
tier. The 12% flake rate and the twice-weekly release blocks are the
predictable output of that distribution — a red run tells you almost nothing
about *where* the bug is, and 3 configured retries are currently masking real
signal rather than fixing it.

## What I would change first

1. **Move the business rules out of the browser.** Most specs assert VAT
   rates, coupon stacking, and currency rounding by driving checkout. Those
   are pure domain rules: rewrite them as unit/domain-level tests
   (table-driven rows per country/coupon case) that run in milliseconds
   without the browser. This alone likely converts 25+ of the 38 specs.
2. **Create the integration tier.** Add service-level integration tests for
   the seams the unit tests can't cover (cart service ↔ pricing ↔ payment
   API contract), using in-process wiring or a hermetic/local backend
   instead of the full deployed stack.
3. **Keep a small E2E core.** Retain a handful of end-to-end journeys — the
   golden-path checkout, login, and one coupon flow — as the wiring proof.
   Aim for well under ten E2E specs, each owned and budgeted for
   maintenance.
4. **Then remove the retries.** Once the suite is mostly fast tiers, drop
   the per-test retries so a red run means something again; treat any test
   that still needs a retry as a bug to root-cause (shared state, timing,
   external dependency), not a setting.

Sequenced this way, PR feedback drops from ~2h40m to minutes for most
changes, and release blocks stop being coin flips.
