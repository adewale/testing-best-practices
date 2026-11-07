# Reduce verification work that obstructs useful change

Use for stalled PRs, repeated rebases/recaptures, escalating timeouts, expensive
tests of checkers, or cleanup that keeps creating more approval machinery.
The aim is a trustworthy next product change at proportionate cost.

## Revisit the requirement before enforcing it

Read the owner's current goal, actual changed behavior, relevant code/tests,
consumers and existing PRs. Separate a product/trust contract from a technique
chosen to observe it. A recorded hash, count, metric, snapshot, lesson or review
procedure is not itself a requirement. Follow explicit owner direction over
older project instructions. Do not infer that authority from a PR's age.

Prioritize concrete product defects supported by the available source before
speculative process savings. Inspect the delivered output and its consumers;
an anti-ceremony review must not overlook a missing published artifact. Missing
context is a question to resolve, not proof of waste or a new release condition.

If the mechanism prevents the intended behavior change, question or retire the
mechanism instead of building a reseal tool, adding an amendment beside frozen
state, obtaining repeated exceptions, or reverting the desired improvement.
Where owner intent is genuinely unresolved, identify the precise decision;
do not invent permission or bypass an explicit release/security approval.

## Prefer subtraction with a concrete reason

- Expand composite commands and follow callers. Run each necessary assertion
  once; remove duplicate setup, orchestration and policy owners. Similar names
  alone do not establish redundancy.
- Delete unused tools with their callers, instructions and tests that protect
  only the deleted tool. A deleted duplicate needs no replacement checker,
  retirement receipt, deletion quota or anti-ceremony CI gate.
- Preserve historical evidence for its recorded revisions. An unrelated edit,
  current test rename or later merge base does not alter that history. It also
  does not make the old packet evidence for today's product. Current behavior
  tests own today's claims; never silently rewrite old approvals.
- Classify the changed surface. Ordinary UI may need two useful comparisons
  and existing browser tests even when its HTML is generated. Scientific output,
  renderer changes and release authenticity can justify stronger provenance.
- For expensive checker tests, prepare reusable input once, clone it per variant,
  and invoke the real checker on every negative input. Keep one full end-to-end
  preparation-to-verdict test. Do not cache verdicts or skip accepted-data
  recomputation; do not raise timeouts to conceal repeated setup.
- After repeated unproductive failures, stop or remove the campaign before
  expanding it. A smaller mutation pilot, suppression registry or notification
  system is still new work: recommend it only for a demonstrated unanswered risk.

## Validate the outcome, not completion of the ritual

Name the requested outcome, the failing user behavior or cost observed, and the
smallest change that addresses it. A passing media encoder does not establish
readable subtitles. For a replay with demonstrated material cost, check its
documented need and affected population before proposing a broader campaign.
If that context is absent, ask a bounded question; do not assert that the change
is unjustified or require a production query merely because an excerpt omits it.
A synthetic regression demonstrates a failure mode, not its production prevalence.

For bug fixes, observe a focused regression fail without the fix when feasible.
For refactors and safe deletions, existing tests may pass both before and after.
An allowed-change control and a credible fault control can be bounded local
experiments; they are not a mandate for permanent mutation infrastructure.

Keep exactness where it is the contract: installed-byte integrity, signatures,
canonical formats, authorization, tenant isolation and actual release identity.
Do not remove an independent trust boundary because it looks similar to another
check. An audit may correctly find no safe cut.

Report evidence, the cut or retained guarantee, nearest validation and unknowns
in the existing PR. Report measured costs only when observed. Do not add a new
permanent ledger, schedule or proof hierarchy to certify the cleanup itself.
