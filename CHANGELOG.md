# Changelog

All notable changes to the testing-best-practices skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
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
