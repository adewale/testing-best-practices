# Google Testing Blog research → skill: gap, conflict, and eval plan

> What the `research/LESSONS_FROM_GOOGLE_TESTING_BLOG.md` corpus (all 404
> posts, 2007–2026) should change in the skill, how each change is verified
> with the Skill Eval Harness, and where the research conflicts with the
> skill or with the rest of the research corpus.
> Date: 2026-08-28. Status: **complete** — research, evals, the 44-run
> ablation matrix (§5), and the C1–C9 skill text are all landed. The matrix
> showed the draft text safe (no over-application on either restraint probe,
> either model) and 2026 frontier models at baseline ceiling on these
> fixtures, so the sections shipped as research-grounded regression guards
> with their boundaries probe-enforced, not as measured-lift claims.

---

## 1. What the research confirms (no skill change needed)

The largest bucket. Google independently converges on positions the skill
already holds, which raises confidence but requires no edits:

| Google finding | Existing skill feature | Existing guard |
|---|---|---|
| Sleep → signal/injected clock, 18 years of posts | `references/deterministic-time.md`, antipattern #8, upgrade P2 | E08, E44–E46 |
| Real > fake > mock ("fidelity" ranking, 2024) | SKILL "Prefer real behavior over mocks" hierarchy | E07, E21, E30, E32 |
| State over interactions; verify only commands | SKILL "allow queries and expect commands" (GOOS, via npryce research) | E21 |
| Don't mock types you don't own; wrap + contract-check | SKILL: "Mock roles you own… wrap provider SDKs behind an owned interface" | E22, E32 |
| Change-detector tests have negative value | Antipattern #7 (implementation coupling) | E21 |
| Coverage is a gap-finder, not proof | SKILL "Quality beats coverage" | E10 |
| Error-handling paths are where failures live | SKILL core principle (Dan Luu / Yuan et al.) | E33, E34 |
| Race detector always-on; races are never benign | SKILL concurrency-contract principle | E35 |
| Fuzz harness discipline (seed/replay/denylist) | test-types.md fuzz harness list (Dan Luu) | pos-fuzz-harness-reproducible |
| Risk-first test planning; cheapest strategy per risk | SKILL "Calibrate test investment"; risk-boundary step | E14 shape |
| E2E capped at golden path + wiring; 5–15 tests | test-types.md E2E rules | E11 |
| TDD red-green with honest evidence | SKILL core + validation loop | E01, E12, neg-no-red-claim |
| Mutation testing targeted at critical modules, nightly | `references/mutation-testing.md` | E10, mini-repos |

Google's fleet data (flakiness/size r²=0.82, 84%-of-red-is-flaky, mutant–bug
coupling ~70%, +10% coverage from in-review surfacing) is the strongest
*empirical backing* the skill's existing positions have ever had; the research
doc is now the citation source for them.

## 2. Identified skill changes (ranked)

Priorities are calibrated by the baseline probes in §5: capable models
already exhibit some of these behaviors in **write** mode when a symptom is
described, so the highest-leverage changes are on the **assess/detect** side
(recognizing the smells in existing suites) and at **boundaries** (knowing
when *not* to apply a rule).

### C1 (P1) — DAMP counterweight: logic-in-tests + cause-effect locality as named antipatterns

- **Source**: Don't Put Logic in Tests (2014), Tests Too DRY? Make Them DAMP!
  (2019), Keep Cause and Effect Clear (2017), Include Only Relevant Details
  (2023).
- **Gap**: the skill pushes builders/helpers to cut fixture noise (upgrade P4,
  test-data-builders.md) but has *no counterweight*: nothing flags a computed
  expected value that shares the SUT's bug, a loop/branch inside a test body,
  or shared fixtures mutated far from the assertion. An agent following only
  the current text can "improve" a suite by DRY-ing it into opacity.
- **Proposed change**: new antipattern in `references/antipatterns.md`
  ("Logic in tests / over-DRY test code": detection signals — expected values
  built by concatenation/arithmetic, `for`/`if` in test bodies, assertions
  depending on fixture state mutated in `setUp*`), plus one SKILL.md assess
  checklist item and a boundary sentence in `test-data-builders.md`
  (helpers construct *values*; every field an assertion depends on stays
  visible in the test — the existing "keep behavior-specific fields explicit"
  line, strengthened to Google's "never rely on builder defaults for
  asserted-upon fields").
- **Eval**: **landed** — `E55-python-no-logic-in-tests` (upgrade,
  fixture-backed: literal single-slash expectations required, BASE_URL-derived
  expectations rejected, AST-scoped oracle) and `E57-python-damp-shared-fixture`
  (assess, cue-free: must flag computed expectation + shared mutated fixture,
  must NOT recommend DRY-ing harder). Over-application guard: E57's oracle
  fails any answer that consolidates more setup into shared fixtures.

### C2 (P1) — Narrow assertions + actionable failure messages, with the whole-state boundary stated

- **Source**: Prefer Narrow Assertions (2024), Test Failures Should Be
  Actionable (2024), Choosing Values for Robust Tests (2026).
- **Gap**: the skill fights *weak* assertions everywhere but never names the
  opposite failure — full-object equality asserting unrelated fields (breaks
  on any unrelated change), and assertions whose failure output
  (`true != false`) cannot start a debugging session.
- **Proposed change**: extend SKILL.md "Quality beats coverage" with two
  sentences: assert the fields the behavior is about (reserve whole-object
  equality for deliberate whole-state tests: golden files, save/load
  roundtrips); prefer assertion forms whose failure message carries the
  actual values (matchers, `EXPECT_OK`-style, fluent asserts). Add the
  brittleness→missing-matcher reframe (unordered-collection matchers) to the
  language refs.
- **Conflict this creates, and its resolution**: `golden-file-testing.md`'s
  whole-state digest roundtrips are *deliberately* maximally broad. The rule
  must be scoped: narrow assertions for behavior tests; whole-state
  comparison where breadth **is** the contract. 
- **Eval**: **landed** — `E58-hidden-narrow-not-roundtrip`, an adversarial
  hidden restraint probe: a reviewer asks to narrow a `canonical_dump`
  roundtrip to the PR's fields; passing requires defending the whole-state
  comparison. When the narrow-assertions text lands, register E58 in
  `audit-best-practices.py` `section_probes` (mirroring E40/E41/E46/E49/E54)
  so the section cannot ship unguarded. A write-side narrow-assertion eval
  (upgrade a full-struct-equality test that broke on an unrelated field) is
  specified in §5 as E59-candidate.

### C3 (P2) — Deliberate test values (non-default, distinct per parameter)

- **Source**: Choosing Values for Robust Tests (2026); Voas's
  Execute-Infect-Propagate (already in mutation-testing.md).
- **Gap**: boundary values are covered; the *default-value blindness* trap
  (a dropped store passes when expected == zero value; swapped args pass when
  key == value) is not stated anywhere.
- **Proposed change**: one line in each language reference's test-writing
  checklist plus one validation-loop bullet ("do any tests assert only
  default/zero values or reuse one value for two parameters?").
- **Eval**: **landed** — `E56-go-distinct-test-values`, a runtime oracle that
  executes candidate tests against the real implementation and two seeded
  `Put` mutants (drop-value, swap-args). Baseline probe hit ceiling (§5), so
  this is a **regression guard**; keep the skill text minimal (a checklist
  line, not a section).

### C4 (P2) — Weld fakes to reality: one contract suite against both implementations

- **Source**: Fake Your Way to Better Tests (2013), Exercise Service Call
  Contracts (2018), Discomfort as a Tool for Change (2017), the E2E→
  unit+replay pair (2016: 30min→3min, equal bug-catching, 0% flake).
- **Gap**: the skill says wrap unowned SDKs and add "a contract/VCR check for
  the real provider shape", and test-types.md says "validate mock return
  values against reality" — but the strongest known mechanism is missing:
  **one shared behavioral suite executed against both the fake and the real
  implementation** (the fake is *provably* equivalent, not assumed), with the
  fake faked at the lowest level (the database, not each caller) and owned
  by the real implementation's owner where org structure allows.
- **Proposed change**: a short pattern block in `references/vcr-cassettes.md`
  or test-types.md Contract Tests: parameterize the contract suite over
  `[fake, real]` with the real arm gated (env var), citing the replay-pair
  variant for RPC-shaped seams.
- **Eval**: proposed **E60-candidate** (write mode, fixture: an in-memory
  fake + a "real" local implementation; oracle checks the same test
  functions run against both via parametrization/env gate, and that the fake
  arm fails when the oracle swaps in a drifted fake). Shared-benchmark mirror
  after the dev eval discriminates.

### C5 (P2) — Suite-shape diagnostics in Assess mode

- **Source**: Just Say No to More End-to-End Tests (2015: ice-cream cone,
  hourglass), Fixing a Test Hourglass (2020), SMURF (2024).
- **Gap**: Assess mode audits individual tests but never the suite's *shape*:
  tier counts/ratios, the hourglass (unit+E2E with no integration middle),
  the inverted pyramid — despite the skill's own cost table having the axes.
- **Proposed change**: one assess-mode checklist item ("tier balance: count
  tests per tier; name ice-cream-cone/hourglass shapes; recommend the
  smallest-tier home for each E2E case that has one"), optionally naming
  SMURF's five axes as the vocabulary for trade-off arguments (the existing
  cost table already encodes them — add the Fidelity column name).
- **Eval**: proposed **E61-candidate** (assess, fixture: a listed inventory —
  38 Selenium specs, 4 unit files, 0 integration — with flake stats; oracle:
  names the shape problem and pushes specific cases down-tier without
  recommending deleting coverage outright).

### C6 (P2) — Flake triage: size first, and quarantine-masks-races caution

- **Source**: Flaky Tests at Google (2016), Where do our flaky tests come
  from? (2017), the four-layer taxonomy (2020–21).
- **Gap**: antipattern #8's cause→fix table starts at time/state/network. The
  research adds the strongest predictor — test *size* (binary/RAM footprint,
  r²=0.82/0.76) — so "shrink the SUT" belongs *above* the per-cause fixes,
  and tool-blame ("Playwright is flaky") is usually a size confound. Also:
  auto-retry/quarantine as *masking debt* (84% of red transitions are flaky;
  quarantine "could easily mask a real race condition").
- **Proposed change**: two rows/sentences in antipattern #8 and
  deterministic-time.md's triage order; upgrade-mode P2 wording: "first ask
  whether a smaller SUT can host this test."
- **Eval**: judge-level addition to E08/E27 rubric focus (does the answer
  consider SUT size before patching waits?); a dedicated fixture is possible
  but low priority — the behavior is advisory, not structural.

### C7 (P3) — Mutation-testing noise economics

- **Source**: Mutation Testing (2021): initial Not-Useful ~80%; arid-node
  suppression + one-mutant-per-line + in-review delivery → ~15%; bug–mutant
  coupling ~70%.
- **Proposed change**: 3 sentences in `references/mutation-testing.md`
  practical guidance: expect most raw mutants to be noise; suppress
  arid/unproductive mutants (logging, mocked-out branches); cap per line;
  surface findings on the diff under review, not as a global score. The ~70%
  coupling number becomes the "why it works" citation.
- **Eval**: covered by existing E10 + mini-repos; add a judge check ("does
  the answer warn about mutant noise / prioritize the diff?") when text lands.

### C8 (P3) — Changelist (incremental) coverage gating

- **Source**: Code Coverage Best Practices (2020); Measuring Coverage at
  Google (2014).
- **Proposed change**: one sentence in SKILL.md "Quality beats coverage":
  prefer gating *new/changed code* coverage over repo-wide targets (bands
  60/75/90 as expectations, not mandates); "what's not covered is more
  meaningful than what is covered" as the review lens.
- **Eval**: fold into E10's judge checks; no new fixture needed.

### C9 (P3) — Tier names as resource contracts; cross-feature workflow trigger

- **Source**: Test Sizes (2010); A Tale of Two Features (2022).
- **Proposed change**: (a) test-types.md tier rules get the framing sentence
  "a tier is a resource contract (network/db/fs/threads/sleep/time); treat a
  violation as misclassification, and enforce mechanically where the runner
  allows"; (b) E2E trigger list gains: "a new feature changes the meaning of
  an existing action (redirects, overrides, new defaults) → test the composed
  workflow, not each feature alone".
- **Eval**: (a) is enforced already by E06/E30 tier-integrity checks; (b) add
  a judge check to E11.

## 3. Conflicts

### 3.1 Google research vs. this skill

1. **Assertion-count heuristics vs. narrow, focused assertions.**
   Antipattern #10 says "100% coverage with 1 assertion per test catches
   fewer bugs than 80% with 5 assertions per test" and recommends tracking
   assertion *density*. Google's canon (one behavior per test; narrow
   assertions; a test making a second SUT call after asserting is scope
   creep) treats high per-test assertion counts as a smell, not a virtue.
   The skill already hedges ("assertion count is a heuristic, not a law"),
   but #10's framing invites padding. **Resolution**: reword #10 toward
   assertion *strength on the behavior under test* (kill-power per mutant,
   not asserts per test). Guarded by E03 (density calibration) + E57.
2. **Whole-state golden/digest comparisons vs. narrow assertions.** Direct
   collision, resolved by scoping (see C2): breadth is correct when identity
   is the contract (roundtrips, golden files with review discipline), wrong
   when smuggled into behavior tests. **E58 is the tripwire in both
   directions.**
3. **Builders/DRY helpers vs. DAMP.** test-data-builders.md optimizes for
   intent-revealing abstraction; Google warns test abstraction hides bugs
   (no test tests the tests). Not a contradiction — a missing boundary:
   helpers for *value construction* with asserted-upon fields explicit
   (both sources agree), never helpers that compute expectations or hide
   cause-effect (only Google says this today). C1 adds the boundary.
4. **Go table-driven tests vs. "Data Driven Traps!" (2008).** go.md
   recommends table tests; Google's 2008 TotT warned against data-driven
   loops (failure localization, hidden intent) while its 2026 post uses
   parameterized tests approvingly. **Resolution**: the good form is named
   rows + `t.Run(tt.name, …)` + no branching in the loop body — which go.md
   already shows. Add the "no logic in the loop body; name every row" caveat
   when C1 lands; no retraction needed.
5. **Retry-until-green tooling.** Google's own quarantine/3-strikes tooling
   is reported *with* its masking cost; the skill's rubric F already treats
   retries as paper-over. No change — but C6 imports Google's own caution
   against Google's own mechanism, which is the strongest available citation
   when an agent is asked to "just add retries."

### 3.2 Google research vs. the rest of the research corpus

1. **Dan Luu ("spend the compute", run the dumb fuzzer overnight) vs.
   Efficacy Presubmit ("the only important results come from tests which
   deterministically fail" — skip predicted-passing tests).** Real tension
   in budget philosophy. Reconciliation the skill should keep: they answer
   different questions — *exploration* (fuzzing/PBT hunting new bugs:
   spend compute) vs. *regression confirmation* (CI on a diff: spend
   selectively, backed by a full-run safety net). The skill's existing
   "keep long fuzz runs out of the default fast suite" already encodes the
   split; no change, recorded here as deliberate.
2. **Whittaker's pesticide paradox / "inject variation" (2009–10) vs. the
   corpus-wide determinism doctrine** (TigerBeetle, Jane Street, the skill's
   "pin nondeterminism"). Resolved by seeded generation: property-based
   tests are principled variation *with* reproducibility. The skill already
   lands there; the research doc records the tension so nobody re-imports
   "randomize your test order" as advice.
3. **Hevery's anti-defensive-asserts stance vs. correctness-by-construction.**
   Superficially opposed to defense-in-depth language, actually the same
   position as the skill's antipattern #13 (shotgun validation) reached from
   the testability side: null-checks at every internal layer force tests to
   build irrelevant graphs. Strengthens CbC's citation base; no change. The
   1-in-corpus counterpoint (Harty: add guard conditions in *acceptance*
   tests) maps onto the skill's boundary-vs-interior lens, not against it.
4. **Google's 70/20/10 + anti-E2E vs. chrischabot's five-tier/API-scenario
   emphasis and Google's own WebRTC interop investment.** The skill's
   trigger-based (not ratio-based) tier selection already absorbs both: heavy
   integration investment is justified *when the risk is at that boundary*
   (WebRTC's explicitly-argued tradeoff), and the ratios are a shape check,
   not a quota (C5).
5. **Beck/TCR-adjacent "leave a failing test as re-entry marker" (Seshadri
   2009 agrees) vs. "do not commit failing tests" —** already reconciled in
   SKILL.md ("not pushed as green proof"); Google's corpus contains both
   halves, confirming the synthesis.

### 3.3 Conflicts internal to the Google corpus (recorded, not actionable)

Documented in the research doc: system-tests-undervalued (2007) vs.
automate-at-lowest-interface (2007); "Test is Dead" vs. its rebuttal;
mandates-are-ineffective vs. Test Certified's celebrated push; zero-tolerance
flakes vs. pragmatic quarantine. Skill takeaway: where Google argued with
itself, the skill should expose *triggers and trade-offs* (as it does), not
pick a slogan.

## 4. What was landed in the Skill Eval Harness now

- **Dev suite** (`skill-development/evals/evals.json`): 54 → **58** evals.
  - `E55-python-no-logic-in-tests` — upgrade; AST-scoped fixture oracle.
  - `E56-go-distinct-test-values` — write; *runtime* oracle (go test vs. real
    impl + two seeded mutants), the suite's first mutant-execution fixture
    oracle.
  - `E57-python-damp-shared-fixture` — assess; cue-free; over-DRY
    over-application guard built in.
  - `E58-hidden-narrow-not-roundtrip` — hidden adversarial restraint probe
    guarding C2's boundary with golden/digest guidance.
- All four fixtures ship `manifest.json` + `oracle.py` + good/bad samples;
  `run-fixture-oracles.py` self-tests pass (35 oracles).
- **Shared benchmark** (`evals/shared-benchmark.json`): three mirror cases
  (`pos-literal-expectations`, `pos-damp-assess-shared-fixture`,
  `neg-keep-roundtrip-whole`) wired to the same oracles via `script`
  assertions. The E56 mirror is deliberately dev-only (needs a Go toolchain
  in the grading environment).
- `python3 skill-development/scripts/check-all.py` passes end-to-end after
  the additions (static audit, eval shape, 35 oracle self-tests, mini-repos,
  eval health, best-practices audit 110/110, version score 100/100).

## 5. The ablation study (44 runs, sonnet + opus)

Two rounds of harness use, both with sub-agents as the eval backend and
deterministic fixture oracles as the metric.

**Round 1 — pre-text probes** (one sonnet sub-agent per arm, fixture prompt
only vs. prompt + one-paragraph guidance draft): E55 and E56 both passed in
both arms — baseline ceiling under symptom-reporting prompts; the E55 run
also exposed a docstring false positive that forced the oracle onto AST
segments.

**Round 2 — the full matrix** (after building E59–E63): evals E55, E57,
E59, E60, E61, E62 × arms {base, current-skill, skill+draft-text} × models
{sonnet, opus}, plus restraint probes E58 and E63 × {current, new} × both
models = **44 candidate runs**, every one scored by its fixture oracle.
Result table and the oracle-fix log live in `evals/scorecard.md`; summary:

- **44/44 cells pass** after oracle hardening. The three raw fails
  (e55/current-opus, e57/current-sonnet, e61/base-opus) were all oracle
  artifacts — parametrize-carried literals, parametrize-as-split phrasing,
  and negated "what not to do" phrasing — confirmed by reading the
  candidates, then fixed with sample self-tests kept green.
- **The draft text is safe**: 16/16 new-arm cells pass, including E58
  (didn't narrow the whole-state roundtrip) and E63 (didn't inline the
  value builder) on both models. This was the landing gate for C1/C2.
- **No with/without oracle delta on frontier models** — the new evals
  are regression guards; `known_discriminates_versions` stays empty, public
  cases are marked `saturated_public`, and the discrimination claim the
  suite *can* make is about oracles and future drift, not current models.
  Two follow-up rounds firmed this up (both in `evals/scorecard.md`):
  n=5 variance repeats on the ten riskiest cells came back 50/50 with all
  raw failures traced to prose-oracle phrasing, and a blind rubric judge
  pass over all 44 cells found zero critical failures while recovering a
  soft base→current→new quality gradient (3.67→3.83→3.92 like-for-like)
  invisible to the binary oracles — suggestive of marginal skill value,
  not oracle-level proof.

## 6. What was executed (the §2 changes are now landed)

1. C1–C9 text landed across `SKILL.md`, `antipatterns.md` (antipattern #15
   with its sanctioned-DRY restraint), `test-data-builders.md`,
   `test-types.md` (tier resource contract, SMURF axes, composed-workflow
   E2E trigger), `vcr-cassettes.md` (fake-weld contract suite),
   `mutation-testing.md` (noise economics), `deterministic-time.md`
   (size-first flake triage), and all four language references
   (deliberate values + order-insensitive matchers).
2. `audit-best-practices.py` `section_probes` now maps the narrow-assertions
   marker (SKILL.md) → E58 and the logic-in-tests antipattern → E63, so
   neither section can ship unguarded.
3. `check-all.py` green end-to-end after landing (static audit, eval shape,
   40 oracle self-tests, mini-repos, health, audit 110/110, version score
   100/100); scorecard and eval metadata updated as above.
4. Shared benchmark: manifest validates under the installed
   `skill-benchmark` CLI (0.6.0) and all 10 ablations materialize. Six
   mirror cases are wired to the fixture oracles via
   `evals/oracles/gtb_output_adapter.py`; two new ablations
   (`no-gtb-damp-and-value-choice`, `no-gtb-suite-shape-checklist`) remove
   the landed SKILL.md checklist items via the `list_item` mechanism.
   Reference-file *sections* (antipatterns #15, the vcr-cassettes weld) are
   not harness-ablatable — every content mechanism edits the root's main
   file — so those are guarded repo-side instead: hidden probes E63/E58
   registered in `audit-best-practices.py` `section_probes`, plus the dev
   fixture oracles.
