# Sample larger suites and choose useful witnesses

Use with [the audit workflow](test-audit.md). The aim is useful proof within the
chosen scope, not a required number of findings, files, faults or assertions.

## Establish a coverage denominator

1. Inventory test entry points, parameter tables, fixtures, shared helpers and
   CI/manual tiers at a pinned revision. Distinguish declarations, generated
   cases, fixture assets and files; these are different counts.
2. Select coherent production owners by consequence and uncertainty. Supplement
   these with a reproducible sample across relevant tiers/owners so searches do
   not inspect only familiar suspicious spellings. State the selection recipe.
3. Record inventory size, selected files and files actually read in full, plus
   any partial reads and unrun tiers. A matching source hash proves which input
   was available, not that someone inspected it or that its tests are strong.
4. Read each candidate and its owner, callers, helpers, relevant parameter rows,
   routing and history. Expand only where a claimed contract needs that context.
5. For a whole-layer retirement, stop sampling that layer: account for every
   affected declaration/row and assign its distinct assertions to keepers.
   Reconcile source changes since the base and independently review preservation
   at each affected boundary. A similar test name is not a coverage map.

Do not call a partial audit a completed subsystem campaign. A source-only review,
focused execution, hosted suite result and end-to-end result support different
claims. Existing CI can supply the expensive baseline when its actual revision,
selection, prerequisites and job results are known.

## Pick a witness from the contract

| Suspected weakness | Small fixture and observed effect | Preserve or allow |
|---|---|---|
| Failed write/handoff loses work | Seed existing state; fail after meaningful progress; inspect durable state and run a healthy retry | Genuine intentional deletion and the normal accepted handoff |
| Partial refresh treated as complete | One source changes while another is unchanged or unavailable; inspect named retained and updated records | Valid empty results and supported caching, independently of failures |
| Fresh database hides upgrade loss | Apply the actual old schema, seed distinguishable records, then migrate and use the normal query | Fresh installation and new writes after upgrade |
| A mock supplies its own answer | Use the real local engine/runtime or a separately verified adapter shape; change a meaningful argument/result | Controlled dependency failures; owned seams with real adapter proof |
| Count/status stands for data | Reassemble bytes, reopen persisted state, or identify exactly which of two records changed | Independent API, privacy, authentication and ordering contracts |
| Async lifecycle never reached | Hold a real completion boundary with a controlled deferred result; observe acknowledgment, retry and cleanup | Supported callback order and intentionally independent subscriptions |
| Public artifact bypassed | Install/build as documented in a clean consumer and exercise the declared command/import | Source imports remaining side-effect free and supported package variants |
| UI selector or visual proxy is weak | Establish the named element/state exists; measure its relevant rendered result | Permitted styling, layout and encoding changes outside the contract |
| Checker matches vocabulary | Use a credible wrong decision and a correct alternative through the public scoring command | Valid paraphrases, explicit unavailable results and optional case routes |

These are choices, not a matrix to run for every owner. For a boundary with a
single clear defect, one discriminating fault and one relevant permitted change
can be sufficient. Deleting a test with no independent contract needs no invented
mutation. Keep costs and claims proportional to the actual decision.

## Avoid manufacturing a failure

- Provider fixtures must obey the supported API/version and ordering semantics.
  SQLite alone does not prove D1 bindings; a mocked array does not prove R2
  pagination; copied metadata does not prove a real runtime's buffer conversion.
- Separate required input/state from incidental spelling. A correct geometry
  assertion need not mention screenshots; a valid JSON object need not retain
  member order. Exact bytes or order remain necessary when independently promised.
- If failure behavior or identity policy is unspecified, document the question
  rather than designing a new product rule in a test. User-authorized replacement
  can have different semantics from failed-write rollback.
- Distinguish an absent file in a sparse audit copy from a fixture unavailable in
  a fresh checkout. Do not label an environment/setup failure a product defect.
- Keep old, candidate and fault runs isolated. Restore the source and record
  which assertions were exercised. Re-run beyond the focused proof only for a
  change, failure, preservation risk or required gate that warrants it.
