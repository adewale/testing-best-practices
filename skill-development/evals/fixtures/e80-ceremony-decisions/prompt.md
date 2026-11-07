# Review the next development action

For each case, follow its task. Return a JSON array with all six decisions in one json code fence. Inventory IDs are local to each case. Do not execute project code.

## S1

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

The owner asks to make three game riders distinguishable and explicitly permits changing or removing obstructing seals. A reviewed historical capture records the old rider shapes. The new shapes pass foot-contact and continuity tests but change 144 alpha hashes. The proposed reseal tool is used only to update those hashes and requires a four-section review. Downloaded font integrity is a separate contract.

- `alpha_gate`: current render must equal historical alpha hashes
- `reseal_tool`: updates alpha gate after a four-section review
- `capture`: immutable old reviewed capture
- `contact`: current foot-contact and continuity behavior tests
- `font_sha`: checksum of downloaded font

## S2

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

An agent must resume an abandoned nightly mutation campaign before delivering a label fix. All 26 scheduled runs failed or were cancelled; attempted repairs grew the matrix to 41 jobs. No actionable product defect was found. A source-patching sabotage helper and a second revert helper duplicate an existing focused label regression that fails before its bug fix. The owner asks to stop paying for redundant verification, retaining the product regression and release security checks.

- `nightly`: 41-job scheduled mutation campaign
- `sabotage`: source-patching duplicate helper
- `revert`: second duplicate helper
- `label_regression`: focused executed label regression
- `release_security`: independent release security checks

## S3

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

Review a PR changing ordinary UI button colors. Two captioned before/after screenshots show the result. Existing browser tests cover both themes, keyboard focus, and forced colors, with a demonstrated regression control. An evidence linter classifies all programmatically built HTML as generated scientific output and asks for 30 screenshot permutations, per-image hashes, a receipt, and a regeneration command. These extra artifacts answer no additional review question. The owner asks for the smallest trustworthy PR.

- `comparisons`: two captioned before/after comparisons
- `browser`: existing focus/theme/forced-color regressions
- `matrix`: 30 generated screenshot permutations
- `receipt`: per-image hash receipt
- `regenerator`: tool used only to regenerate the matrix/receipt

## S4

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

Evidence-verifier tests repeatedly prepare an expensive audio matrix for every one-field tamper case. This costs 175 seconds and drove 15→30→60-second timeout increases. Structural rejection is cheap, but accepted PCM must still be recomputed from bytes. A proposed optimization would cache the final verdict. The owner wants less test setup cost without weakening detection. One full preparation→recompute→verdict integration already exists; prepared matrix input can be cloned safely between cases.

- `repeat_setup`: fresh full matrix preparation per tamper case
- `timeout_raise`: another proposed timeout increase
- `end_to_end`: one full preparation-to-verdict integration
- `each_rejection`: real verifier invocation for each tampered input
- `pcm_recompute`: accepted PCM checked against raw bytes

## S5

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

A behavior-preserving module move passes the existing product suite on base and head. CI nevertheless requires every PR to have a failing-base test; refactors must obtain an opt-out label. A docs check also freezes current test titles and counts, so a test rename demands an appendix rewrite. Public documented CLI commands are separately checked by executing their examples. The owner asks to simplify these requirements, while keeping bug-fix regressions and working documentation.

- `universal_red`: every PR must fail a test on base
- `optout`: refactor opt-out label machinery
- `test_roster`: copied test titles/counts in current docs
- `preservation`: existing product preservation suite
- `bug_regressions`: focused red-green evidence for actual bug fixes
- `cli_examples`: executed public CLI examples

## S6

Recommend the smallest supported next action. Return a JSON object with id, decision (change/defer/keep), retire (inventory IDs), retain (inventory IDs), introduce (new permanent machinery; empty if none), rationale, and validation. Review only; do not claim tests or production checks ran.

Review a release change. A tarball signature and checksum identify the actual installed bytes. An authorization regression rejects a request from another tenant, and a browser test proves the exported document is displayed. All run once in the existing release path. A previous cross-tenant bug was caught by the authorization test. No unnecessary execution or incidental implementation pin is demonstrated. The owner asks whether any verification can safely be cut; an empty finding list is acceptable.

- `signature`: signed installed tarball identity
- `checksum`: tarball byte integrity
- `tenant`: real cross-tenant authorization regression
- `browser`: exported-document display wiring
