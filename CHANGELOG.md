# Changelog

All notable changes to the testing-best-practices skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added (PBT/fuzzing execution audit)
- **Reachability-first assessment guidance** — distinguish a decorated test from one the configured runner collects, a fuzz target from active discovery, and a test-only helper from the production path it claims to cover.
- **Focused PBT and fuzzing references** — separate arbitrary-totality inputs, specification-valid generators, corpus mutation, independent semantic oracles, stateful accepted-transition depth, engine-managed replay, and target cost from campaign cost.
- **Minimal engine adapters** — Go seed replay versus per-target `-fuzz` discovery, Python collection and structured-valid strategies, and fast-check command preconditions/replay/accepted-transition accounting.
- **Durable-workflow model guidance** — derive no-loss, redelivery, recovery, and terminal-state properties from the contract; test lease/fencing, idempotency, or outbox repair only when the design exposes those mechanisms.
- **Executable eval regressions E64–E70** — three hidden restraint probes plus cue-free audits for collection/discovery/production reachability, valid-generator integrity, fast-check command models, durable queue protocols, and appropriate fuzz-campaign cadence.
- **Cue-free executable fixtures** — E64–E70 pair raw repository artifacts with conjunction oracles and curated good/pass plus bad/fail samples. Candidate review hardened the prose oracles and clarified the fast-check `replayPath` adapter; because those exploratory candidate outputs were not retained with reproducible run provenance, this release makes no measured-lift claim from them.

### Fixed (PBT/fuzzing execution audit)
- Corrected the generic fuzz harness advice: property-based testing is not “structured fuzzing,” unexpected failures must escape for minimization, replay is engine-specific, ordinary Go tests replay seeds but do not discover, and long campaigns—not small targets—are the expensive tier.
- Made Markdown assessment artifacts visible to the prompt-eval judge instead of silently omitting `assessment.md` candidates, and frame fenced Markdown with a dynamically longer delimiter so candidate code blocks cannot escape their section.

### Added
- **Variance measurement for the ablation matrix** (`scorecard.md`): n=5 repeats on the ten variance-riskiest cells (prose-sensitive base-arm evals E57/E60/E61 and both new-arm restraint probes E58/E63, each on two models) — 50/50 pass, Wilson 95% CI [0.93, 1.00], zero observed model variance; every raw failure was an E61 prose-oracle phrasing artifact, fixed across three hardening passes with fixture self-tests kept green. Caveats recorded: repeat-arm provenance (draft bundle vs. landed text) and one shared-workspace contamination incident.
- **Blind judge pass over all 44 matrix cells** (`scorecard.md`): cells re-scored on the rubric by six judges behind opaque hash codes (arm/model hidden), min-of-`rubric_focus`-dims scoring with the critical-failure override; two further judges on a second model double-judged the 16 new-arm cells. Zero critical failures, minimum cell score 3; judges recover a soft base→current→new quality gradient (3.67→3.83→3.92 like-for-like) that the binary oracles compress to all-pass. First measurement of `eval-health.md`'s judge-disagreement meta-signal: 97% exact per-dimension agreement, no eval-score disagreement >1, 16/16 critical-failure agreement (noted in `eval-health.md`).
- **Six new eval-methodology lessons** in `LESSONS_LEARNED.md` (oracle artifacts dwarf model variance at the frontier ceiling; negation-aware prose oracles vs. the judge layer; judges recover compressed gradients; completion-driven sub-agent queue draining and isolated repeat workspaces; validating against the real shared harness; feed-based corpus enumeration).
- **Google-Testing-Blog-derived guidance landed after a 44-run ablation study** (Sonnet+Opus sub-agents; arms base / current skill / skill+draft; every cell scored by deterministic fixture oracles — results in `skill-development/evals/scorecard.md`). The matrix showed the text safe (both hidden restraint probes held on both models) and frontier models at baseline ceiling, so the sections ship as research-grounded regression guards: narrow assertions with the whole-state-roundtrip boundary and actionable failure messages (SKILL.md), deliberate non-default test values and literal expectations (write mode + validation loop + language refs), DAMP test-code readability and suite-shape checks (assess mode), size-first flake triage (upgrade mode + antipatterns #8 + deterministic-time), antipattern #15 "Logic in tests / over-DRY test code" with its sanctioned-DRY restraint, builder-defaults rule (test-data-builders), fake-to-real contract-suite welding (vcr-cassettes), tier-as-resource-contract + SMURF axes + composed-workflow E2E trigger (test-types), and mutation-noise economics (mutation-testing).
- **Evals E59–E63** with self-testing fixture oracles (suite now 63 cases / 40 oracles / 14 hidden probes): E59 narrow-assertions upgrade, E60 fake-contract weld (three-run pytest oracle), E61 suite-shape assess, E62 hidden numeric-default hardened variant of E56, E63 hidden DAMP-keeps-builders restraint probe. `audit-best-practices.py` `section_probes` now maps the narrow-assertions marker → E58 and the logic-in-tests antipattern → E63.
- **Three oracles hardened against real model output** during the matrix (E55 parametrize-carried literals, E57 parametrize-as-split phrasing, E61 negation-aware doubling-down check), with good/bad sample self-tests kept green — the raw matrix "failures" were all oracle artifacts, confirmed by reading the candidates.
- **Shared benchmark**: 42 cases (six Google-derived mirrors wired through `evals/oracles/gtb_output_adapter.py`) and 10 ablations, all validated and materialized end-to-end with the installed `skill-benchmark` CLI (0.6.0); trigger cases carry explicit `should_trigger`, judge-only holdout/holdback cases promote their judge assertion to a gate, and two new `list_item` ablations remove the landed SKILL.md checklist items.
- **Research: `research/LESSONS_FROM_GOOGLE_TESTING_BLOG.md`** — complete crawl of all 404 Google Testing Blog posts (2007–2026) via the Blogger feed, read in full by ten parallel analyst passes with quotes re-verified against primary text. Corpus now 16 accounts + three engineering organizations, 25 research files. Covers enforceable test sizes, the pyramid's life cycle (70/20/10 → SMURF), fleet-scale flakiness data (size beats tool choice, r²=0.82), the Hevery testability campaign, the test-double/fidelity canon, DAMP test style, coverage bands, mutation testing at scale (~70% bug–mutant coupling, ~80%→15% noise suppression), and the corpus's negative results.
- **`skill-development/GOOGLE_TESTING_BLOG_GAP_ANALYSIS.md`** — identified skill changes (C1–C9, ranked; deliberately not yet applied pending with/without A/B probes), conflicts with the skill (assertion-density antipattern wording, whole-state golden vs. narrow assertions, builders vs. DAMP, Go table tests vs. Data-Driven Traps) and with the corpus (Dan Luu spend-the-compute vs. Efficacy skip-predicted-passes; Whittaker variation vs. determinism, reconciled by seeded PBT), plus the verification workflow for applying each change.
- **Research-derived evals E55–E58** with self-testing fixture oracles (dev suite now 58 cases, 35 oracles): `E55-python-no-logic-in-tests` (literal expectations; AST-scoped oracle validated against real model output), `E56-go-distinct-test-values` (the suite's first mutant-execution runtime oracle: candidate `go test` must pass the real impl and kill drop-value/swap-args mutants), `E57-python-damp-shared-fixture` (cue-free assess; fails answers that DRY test code harder), `E58-hidden-narrow-not-roundtrip` (hidden adversarial restraint probe guarding whole-state roundtrips against narrow-assertion over-application; register in `section_probes` when the narrow-assertions section lands).
- **Baseline probes recorded** (sonnet sub-agents, no-guidance vs. guided arms) for E55/E56: both at baseline ceiling under symptom-reporting prompts → regression guards; probe results stored in each eval's `validity.backing` and the E55 oracle hardened from a false positive the real candidate exposed.
- **Shared-benchmark mirrors** `pos-literal-expectations`, `pos-damp-assess-shared-fixture`, `neg-keep-roundtrip-whole` (39 cases total), wired to the same fixture oracles through the new `evals/oracles/gtb_output_adapter.py` (extracts fenced code from `output.md`, delegates to the dev fixture oracle).
- **Core principle: Examples are communication artifacts** — preserve product/domain language from user-supplied rows, examples, bug reports, or spreadsheets; run rule examples at the domain/service/API seam instead of forcing every row through browser automation; keep UI/E2E tests for wiring and golden paths. Derived from Ward Cunningham's Fit and Fit post-mortem.
- **Core principle: Calibrate test investment to asset lifetime and change kind** — distinguish throwaway probes from reusable libraries, behavior changes from structure/tidying, and debt repayment from feature work. Derived from Ward Cunningham's GitHub patterns and Kent Beck's Tidy First?/XP book updates.
- **Visible-state/fake guidance** — prefer real collaborators or purpose-built recording/logging fakes, assert emitted events or persisted state, and avoid brittle call-order choreography. Derived from Ward's wiki tests and GOOS mock-discipline updates.
- **Reference updates** in `test-types.md`, `test-data-builders.md`, and `correctness-by-construction.md` for customer-sourced examples, domain seams, action-specific validation, test DSL helpers, and logging fakes.
- **Research-derived evals** `pos-customer-examples-domain-seam`, `pos-test-investment-lifetime-fit`, `pos-visible-state-logging-fake`, `pos-go-test-seam-no-security-bypass`, `pos-tdd-microtactics-test-list`, `pos-walking-skeleton-inprogress-acceptance`, and `pos-fuzz-harness-reproducible` covering the new Ward/Kent/Pryce/Dan Luu lessons.
- **Go testability safety fix** — replaced unsafe `NewForTesting` guidance that disabled SSRF checks with dependency-injection seam guidance that preserves production security/business rules.
- **TDD micro-tactics** — test list, assert first, child test, learning test, crash-test-dummy fake, and Fake It/Triangulate/Obvious Implementation calibration.
- **Acceptance lifecycle guidance** — walking skeleton for first-feature system risk, in-progress acceptance tests tied to issues/stories, and no committed failing unit tests.
- **Fuzz harness discipline** — seed/replay/corpus logging, timeout/quarantine, production-shaped distributions, and nightly/opt-in placement for long fuzz runs.
- **Core principle: Test error-handling paths, not just invalid input** — inject the downstream failure (a fake/stub that raises, an injected I/O error, a `side_effect` exception) and assert the system degrades correctly. Backed by the empirical "most critical failures are shallow" finding. Includes a scope-control clause: assert the failure behavior the code *actually* has; do not invent a retry budget, error type, or rollback the contract never promised — characterize and flag the gap instead.
- **Research: `research/LESSONS_FROM_DANLUU.md`** — lessons from Dan Luu (danluu.com/testing + GitHub: Fuzz.jl harness mechanics, csv differential testing, fs-errors fault injection, kodkod-clj/secvisor formal-methods thread). Corpus now 15 accounts with antirez below.
- **Eval `E33-python-fault-injection-error-paths`** — runnable fixture oracle (good/bad samples) plus prompt-eval entry guarding the error-path principle.
- **Eval `E34-hidden-fault-injection-unprompted`** — adversarial hidden probe: the prompt fixes the contract (failures propagate, no retries), so inventing retry/wrapping is unambiguously scope creep. Now 6 hidden hard/adversarial probes.
- **`skill-development/scripts/run-prompt-evals.py`** — before/after prompt-eval runner with pluggable generation backends (sub-agent via `--candidate-dir`, shell via `--agent-cmd`) and a rubric judge backend (`--judge-cmd`, e.g. `claude -p`) that computes eval score = min(rubric_focus dims) with the critical-failure override.
- **Core principle: Test concurrent code under a race detector, and pin the concurrency contract** — drive shared state from many workers released together, run under `-race`/ThreadSanitizer, and assert the promised invariant (compute-at-most-once, no lost updates) instead of logging the observed count and tolerating the race. Found via an eval-driven probe where a capable base model detected a TOCTOU double-compute race but only `t.Logf`'d it.
- **Eval `E35-go-concurrency-contract`** — fixture-backed (good asserts compute-once under contention; bad only logs it). The oracle is scoped to the concurrent test function so asserting the contract only sequentially does not pass.
- **`references/differential-testing.md` — "When no reference exists: build a trivial shadow model"** — model-based fuzzing against an obviously-correct reference, seeded for reproducibility, compared on multiple observables, with an explicit do-not-over-apply clause (from antirez's rax/redis fuzzing).
- **`references/differential-testing.md` — "Approximate, probabilistic, or non-deterministic outputs"** — brute-force oracle with a recall/closeness threshold plus exact-on-overlap checks, and a clause forbidding statistical oracles on deterministic outputs (from antirez's Vector Sets recall testing).
- **6 eval fixtures** (E36–E41): E36/E38 dev (Python), E37/E39 isomorphic Go holdbacks, E40/E41 hidden adversarial restraint probes — each with a self-testing good/bad oracle.
- **`audit-best-practices.py` gate**: every new technique section must ship with a registered hidden adversarial probe (audit now 110/110).

### Added (iteration 9)
- **Seam guardrails in `references/deterministic-time.md`** — "When the seam isn't time: forced transitions, and guardrails": force background transitions or await completion signals instead of sleeping, keep introspection read-only, and never bypass security/business rules with test modes (from antirez's Redis `DEBUG` surface). Originally shipped as a standalone `design-for-testability.md`; folded after iteration-10's non-time isolation showed both ablation arms produce genuine seams from priors alone — only the guardrails (validated by the E46 restraint probe) are unique content.
- **Whole-state roundtrip digest section** in `references/golden-file-testing.md` — seeded rich state, canonicalize-then-compare, save→load identity parameterized across formats (from antirez's `DEBUG RELOAD` + dataset digest). Golden-file trigger now covers save/load and migration roundtrips.
- **8 more eval fixtures** (E42–E49): cue-free statistical pair (prompts name only the metric, never the technique), testability dev/holdback plus a no-security-bypass restraint probe, digest dev/holdback plus a canonicalization restraint probe. Audit gate maps both new sections to their hidden adversarial probes.

### Changed
- **Strengthened the Differential Testing "When NOT to use it" guidance** after an adversarial probe (E41) showed the section could induce a redundant reference reimplementation for a trivial pure function.

### Fixed
- **Repository coherence audit cleanup** — refreshed README counts/structure and corrected E36–E49 fixture prompt headings to match their manifest eval IDs after the v0.3 oracle and iteration 8–9 eval work.

### Added (iteration 11)
- **Antipattern #14 "Asserting through fault-masking code"** in `references/antipatterns.md` (from Voas & Miller's PIE/fault-hiding theory, via the design-for-testability literature review) — output-only assertions behind a clamp / swallow-to-default / recover-to-zero / high domain-to-range coercion can't catch faults, because the mask blocks propagation; fix is to assert the pre-mask/internal value. Ships with a restraint clause excluding spec'd clamps/graceful degradation.
- **PIE "Why it works" paragraph** in `references/mutation-testing.md` — grounds mutation testing in execution/infection/propagation; surviving mutants in masking code mark where the code hides faults from any output-only test.
- **Evals E52 (Python assess dev), E53 (Go assess holdback), E54 (hidden adversarial: a documented clamp must not be flagged as fault-masking)**; audit gate maps the new antipattern to E54.

### Eval Results (iteration 11, assess-mode ablation; sonnet, n=1 per cell)
- **Fault-masking detection is at ceiling**: with and without antipattern #14, both the Python and Go arms caught the masking from priors via the existing not-empty/tautological-assertion knowledge ("this test would pass even if compute_score crashed silently... the clamp structurally enforces the only invariant"). The restraint guard held in both arms (neither flagged the documented clamp).
- **Decision (consistent with the iter-10 fold)**: trimmed #14 ~50% to its non-redundant residue — the PIE framing, the assert-pre-mask-state fix (the one move the without-arm missed), and the restraint clause — and kept the cleanly-additive mutation-testing PIE paragraph. E52/E53 marked `saturated_public`.
- Oracle calibration bug #6 (false negative): the E52-without oracle wanted "passes even" but the prose said "would pass even if"; fixed by accepting the concept's phrasings. Six of six oracle bugs across four iterations have been false negatives on good work.

### Eval Results (iteration 10, non-time isolation; sonnet, n=1 per cell)
- **Fold decision executed per a pre-registered rule.** E50 (Python volume-triggered compactor) and E51 (Go channel-fed aggregator) removed the time seam entirely; both arms passed both fixtures (without-arms built Event/WaitGroup synchronization seams from priors). `design-for-testability.md` deleted; guardrails folded into `deterministic-time.md` (net ≈ −700 on-demand tokens); audit gate's probe mapping follows the guardrails to their new home.
- Oracle calibration bug #5: sleeps in comments/docstrings describing the old flaky test false-negatived 3 of 4 runs; oracles now strip comments first. All 28 self-tests green.

### Eval Results (iteration 9, cue-free ablation; sonnet, n=1 per cell)
- **Statistical-oracle section validated**, resolving iteration 7's open question: cue-free E42 discriminates cleanly (with: brute-force reference + recall ≥ 0.80 with headroom + exact-on-overlap; without: gap-gated exact set equality — the warned-against failure mode). E43 (Go holdback) discriminates weakly; its without-arm's tie-only tolerance is a defensible reading of underspecified prompt wording.
- **Digest-roundtrip section validated in the Go holdback** (E48: without-arm wrote single-key roundtrips + golden-bytes, no whole-state load identity); Python dev fixture at ceiling because existing snapshot guidance already teaches stable serialization.
- **Design-for-testability at ceiling against the strongest baseline**: with `deterministic-time.md` alone, both arms added genuine seams (public `flush()`, injectable clock+ticker). Marked unproven marginal value; its security guardrail is validated by the E46 restraint probe (clock injection, no env-var bypass).
- Both new restraint probes (E46, E49) pass. Four oracle calibration bugs — all false negatives on good work using unexpected identifiers — found by manually reading every FAIL, then fixed; 24/24 oracle self-tests green.

### Eval Results (iteration 8, ablation; sonnet, n=1 per cell)
- Shadow-model section **discriminates and generalizes**: E36 (Python dev) and E37 (Go holdback) pass with the section, fail without it.
- Statistical-oracle section **at ceiling / did not discriminate**: E38/E39 pass with and without, because the prompt names the brute-force helper and cues the behavior. Marked `saturated_public`; needs a cue-free fixture next iteration.
- Restraint: E40 (deterministic sort) restrained; E41 (trivial pure fn) over-applied first, then restrained after the guidance fix.
- Two fixture-oracle calibration bugs (E39 named-constant threshold false negative; E41 test-name false positive) found and fixed; all 16 oracle self-tests pass.

### Research
- Added **`research/DESIGN_FOR_TESTABILITY_LITERATURE.md`** — academic literature review (hardware DFT/SCOAP → Freedman 1991 → Voas & Miller's PIE → Binder 1994 → Bach/Pettichord heuristics → Meszaros/Feathers patterns → 2019 survey, flaky-test and LLM-era empirical work), compiled to pressure-test the iteration-10 fold. Outcome: the fold is corroborated (the canon's seam hierarchy prefers substitutable dependencies over test hooks; Luo et al.'s condition-based-synchronization fix is exactly what baseline arms build from priors), the E46 guardrail matches the canonical "Test Logic in Production" smell, and one genuinely new concept is flagged as a candidate delta pending the standard eval discipline: Voas's fault-hiding/PIE theory (fault-masking code passes tests while harboring faults).
- Added **Salvatore Sanfilippo / antirez** (`research/LESSONS_FROM_ANTIREZ.md`) — scanned his actual repos (rax, sds, redis, Vector Sets, ds4). Captures: differential fuzzing against a "tells the truth" reference oracle with a seeded platform-independent RNG (rax); content-digest persistence roundtrips and the `DEBUG` command surface as a deliberate testability affordance (redis); `assert_encoding`, `wait_for_condition` (poll, never sleep), fuzz-vs-Tcl-model across encodings, and replication-stream assertions; statistical recall testing of an approximate ANN index against a brute-force oracle plus SIMD-boundary/overflow fuzzing (Vector Sets); allocating test effort by reuse risk (libraries fuzzed hard, teaching code untested); and agent-as-QA-engineer driven by objective oracles instead of hardcoded baselines (ds4 `AGENT.md`).

## [0.3] - 2026-05-21

### Added
- **Core principle #10: Correctness by construction** — push invariants into types/schemas/contracts so the wrong state is unrepresentable; surviving test tactics are invariant-proof PBT and model-gap tests that try to construct each forbidden state.
- **`references/correctness-by-construction.md`** — on-demand reference with TypeScript branded types, Rust newtypes, Python smart constructors, Go unexported fields, right-when/still-necessary checks, and canonical sources.
- **Step Zero decision tree** — ask “can the type replace the test?” before writing another rejection test.
- **Trust-boundary lens** in `references/test-types.md` — untyped input → typed interior → untyped output, with test types matched to each boundary.
- **Antipattern #13: Logical defense-in-depth / shotgun validation** — repeated validation everywhere, loose strings through layers, duplicated status enums, runtime guards instead of state machines/types/schema constraints.
- **Eval development workspace** in `skill-development/` with rubrics, taxonomy, scorecards, version comparison, and non-LLM gates.
- **32 eval definitions** with claim/warrant/backing/rebuttal validity metadata and difficulty/saturation/discrimination health metadata.
- **5 hidden hard/adversarial eval probes** for assertion calibration, weak PBT oracles, in-process integration classification, correctness-by-construction deletion safety, and VCR/MSW distinction.
- **10 fixture-backed public oracles** covering Python, Go, TypeScript, and Rust.
- **3 mutation-backed mini-repos** that kill seeded JS/Python/Go mutants.
- **Best-practices audit gate** for installable-skill boundaries, generated artifact hygiene, schema coverage, eval metadata, hidden probes, and mutation-backed fixtures.
- **Token report** comparing first GitHub, previous GitHub, and current skill versions.

### Changed
- **`SKILL.md` router refactor** — cut the always-loaded entrypoint from ~5,572 estimated tokens in the previous GitHub version to ~2,745 estimated tokens while preserving reference breadth.
- **Reference calibration fixes** in TypeScript, Go, test-types, antipatterns, VCR cassettes, and correctness-by-construction guidance.
- **Red-Green TDD renamed to Red-Green-Refactor TDD** to match Beck’s canonical cycle.
- **Assertion guidance calibrated** — assertion density is a smell/heuristic, not a universal “3+ assertions per test” rule.
- **Integration-test guidance calibrated** — in-process component-boundary integration is valid; external dependencies are not required just to earn the label.
- **VCR guidance clarified** — hand-written MSW mocks are deterministic mocks, not recorded cassettes.
- **Correctness-by-construction deletion guidance hardened** — delete redundant same-invariant checks only after proving boundary/type enforcement; keep auth/security/output-escaping defense-in-depth.
- **Eval scoring split into layers**: artifact rubric, static audit, fixture oracles, mini-repo mutation checks, and best-practices audit.

### Removed
- Generated prompt-run outputs and Python caches from tracked source; raw `skill-development/eval-runs/` are now local/generated artifacts.
- Development/eval artifacts from the installable skill directory; installable contents are limited to `SKILL.md` and `references/*.md`.

### Eval Results
- Skill artifact rubric: first GitHub `28/100`, previous GitHub `69/100`, v0.3 `100/100`.
- Static audit: previous GitHub `6 P0 / 6 P1`, v0.3 `0 P0 / 0 P1`.
- Fixture prompt oracles: first/current/v0.3 all `10/10`, confirming public oracle saturation rather than release-quality discrimination.
- Mini-repo mutants killed: `3/3`.
- Best-practices audit: `100/100` after hygiene fixes.
- Final local gate: `python3 skill-development/scripts/check-all.py` passes.

### Token Impact
- `SKILL.md`: ~5,572 → ~2,745 estimated tokens vs previous GitHub main (**-50.7%**).
- Full installable skill: ~26,305 → ~23,948 estimated tokens (**-9.0%**).

## [0.2] - 2026-04-11

### Added
- **4 supported languages**: Python, TypeScript, Go, Rust (was Python + TypeScript only)
- **9 topic-specific reference files** with conditional loading (characterization testing, differential testing, golden file testing, VCR cassettes, doc-sync testing, mutation testing, exhaustive testing, mathematical properties, test data builders) — each loads only when its trigger condition matches
- **Kent Beck's Test Desiderata** integrated into quality assessment framing (12 properties of good tests that conflict with each other)
- **3 new PBT invariant patterns**: associativity, commutativity, distributivity — plus language integration tests (test `sum()`, `sorted()`, set membership with your domain objects)
- **Fixture-based golden file testing** pattern from kepano/defuddle (auto-discover, auto-baseline, zero-code test creation)
- **Characterization testing** pattern from Michael Feathers (capture current behavior before refactoring)
- **Pirate testing** pattern for language-neutral conformance suites
- **File tree builders** for filesystem tests (nested objects → directory structures)
- **Validation loop** in Write mode — agent self-checks assertion density and antipatterns before reporting done
- **Ordering dependency detection** in Detect mode
- **Go-specific patterns**: `testdata/` convention, `t.Helper()`, `t.Cleanup()`, `TestMain`, Example tests as documentation
- **10 eval cases** across all 4 languages (was 3, Python-only)
- **Weak test fixtures** for TypeScript (`weak_tests.ts`) and Go (`weak_tests.go`) for assess-mode evals
- **Rust eval fixture** (`config_parser.rs`) for write-mode eval

### Changed
- **Split `advanced-patterns.md`** (747 lines, 5,485 tokens) into 9 focused topic files (32-82 lines each) — typical task now loads ~7,200 tokens instead of ~12,000-16,000 (~50% reduction)
- **Conditional loading guidance** in SKILL.md — each topic file has a specific trigger ("Refactoring legacy code? → read characterization-testing.md") instead of generic "read advanced-patterns.md"
- **Validation loop is language-agnostic** — guidance-based, not script-based
- **README rewritten** to match actual skill structure (15 reference files, 10 evals, 13 research accounts)

### Removed
- `scripts/check_test_quality.py` — Python-only, replaced by language-agnostic validation loop guidance
- `advanced-patterns.md` — split into 9 topic files

### Research
- Added **Kent Beck** (Test Desiderata, TCR, MoneyPython mathematical property tests)
- Added **Mary Rose Cook** (gitlet test suite, file tree builders, pinned time)
- Added **Steph Ango / kepano** (defuddle fixture-based golden file testing)
- Split combined `LESSONS_FROM_PRACTITIONERS.md` into 7 individual files (one per practitioner)

### Eval Results
- Iteration 1: 96% (24/25) — 3 evals, Python + TypeScript
- Iteration 2: 100% (25/25) — 3 evals, same languages
- Iteration 3: 100% (49/49) — 7 evals, Python + TypeScript + Go + Rust

## [0.1] - 2026-04-11

### Added
- Initial release
- Core SKILL.md with 4 operational modes (Write, Assess, Upgrade, Detect)
- 10 core testing principles (Red-Green TDD, quality over quantity, real objects over mocks, PBT, E2E, doc-sync, characterization, differential, test data builders, sad path)
- Language-specific references for Python and TypeScript
- Go and Rust language references
- Antipatterns reference (12 anti-patterns with detection/fix/prevention)
- Test-type decision guide (3-tier hierarchy)
- Research corpus from 10 GitHub accounts
- 3 eval cases with iteration-1 results (96% with-skill vs 68% without-skill)
