# Tests that lock in an implementation: hashes, pins and byte-exact oracles (2026-09-30)

The owner's repositories use hashes, pins and byte- or pixel-exact comparisons to lock in one implementation rather than check what the code is for. This document checks that claim against the repositories' history, traces where the pattern comes from, summarises what the literature knows about it, and identifies where this skill contributes and what it should say instead.

**Method.** Three agents surveyed 44 of the owner's repositories at `origin/HEAD` on 2026-09-30:
- a classifier over the test files;
- hand classification of samples;
- `git log` churn over tests and pinned artifacts;
- samples of pin failures traced through history;
- Actions logs where CI ran.

A fourth agent reviewed the literature and checked quotes against primary sources where it could. Private repositories are anonymised here: "private repo A" is a canvas game with about 4,400 unit tests, and "private repo B" is a generated wiki.

## Summary

- **The claim holds, and the cost is mostly false alarms and churn, not bugs caught.**
  - In the two hardest-hit repositories, 37% (`agentic-mermaid`) and 43% (private repo A) of non-merge commits touched a pinned artifact or a source-text test.
  - Sampled pin failures were overwhelmingly false alarms: 10 of 14 in private repo A, and at least 7 kinds in `agentic-mermaid`.
  - Across all the samples, 2 true catches turned up: one geometry snapshot and one tooling port collision.
  - In private repo A, all 61 red CI runs that ran came from source-text, copied-count or governance tests. None caught a product regression.
- **Pins also let real bugs through.**
  - `agentic-mermaid` shipped 10 defects "inside freshly regenerated goldens".
  - YAML-text tests sat beside a deploy that skipped "green" for 8 weeks.
  - `geist_fabrik`'s workflow-text tests pinned the text of a release bug.
  - Observed output pinned a wrong label as correct.
- **The dominant form differs by repository.**
  - `agentic-mermaid` and private repo A used output hashes and receipts (T1) and exact goldens (T2): 7,858 committed hashes in one repo and 462 render-hash literals in the other.
  - Most other repos assert on source, CSS, workflow, docs or SQL text (T3), or copy counts from the code (T5).
- **Agents built most of it, through recognisable moves:**
  - a fix followed by a "regression test" that greps for the fix's text;
  - running the code and pasting its output as the expected value;
  - regeneration switches (`UPDATE_*`, `-u`) run by the same agent that changed the code, and approved on an unprotected branch;
  - lessons that ratchet towards binding more;
  - untestable architecture pushing tests into source text.

  The literature names every one of these, and generated tests are a documented source [37][38][42][43][45].
- **This skill contributes:**
  - `characterization-testing.md` says "Record the actual outputs as assertions — even if they look wrong", and never says to retire those tests. `agentic-mermaid` cites the skill for "pin what the code does today".
  - `golden-file-testing.md` and `test-types.md` teach auto-baselining on first run, "Catches drift" as a benefit, and snapshots whenever a value has more than ~5 fields.
  - The v1 "skip visual tests in CI" idiom was copied into `vaders` the day after it shipped.
  - There is no guidance on where an expected value should come from, on numeric tolerance, or on when byte-exactness is legitimate.
- **The owner's own remediations already show the fix.** `agentic-mermaid` #357/#361 replaced hashes with readable geometry and properties and added the rule "no expected values produced by the code under test". Private repo A replaced about 117k lines of seals and source-regex tests with properties, import-graph rules and replay equality. Elsewhere, real SQLite, computed styles and geometry checks replaced text pins.

## 1. What the problem is

| Type | Shape | Portfolio examples |
|---|---|---|
| **T1** Output hashes as oracles | A digest of rendered output asserted equal to a pinned value, or a receipt whose hashes must be regenerated | `agentic-mermaid`: 7,858 committed hashes, including a 4,346-hash upstream manifest and 375 styled-output hashes. Private repo A: 462 render/op-hash literals per backend, plus per-DPR SHA-256s "recorded on the author's Chrome". `atlas`: SHA-256 of 119 social-card PNGs. |
| **T2** Byte- or pixel-exact goldens of large output | Whole SVG/JSON/command-stream equality, zero-tolerance pixels, snapshots of everything | `agentic-mermaid`'s `layout-geometry-baseline.json` (~258 diagrams, exact rounded pixels, 43 commits) and styled-SVG goldens. Private repo A: 6.3 MB of sealed fixtures and exact canvas command streams. Darwin-only screenshot baselines that never run in CI in 5 repos. |
| **T3** Source- or config-text assertions | Read `src/`, CSS, YAML, docs or SQL as text and assert substrings or regexes; "sabotage proofs" of those regexes; fakes that route on SQL text | Private repo A: 165 files and 4,054 `assert.match` calls at peak (one file had 2,488 regexes). `pythonbyexample`: 180 of 962 assertions. `tasche`: 405 `if "…" in sql` fake-routing lines. `agentic-mermaid`: 486 substring asserts on built HTML/CSS. `planet_cf`, `atlas`, `bobbin`, `geist_fabrik`, `vaders`, `skill-eval-harness` (`inspect.getsource`). |
| **T4** Pinned incidental numbers | Coefficients, float artefacts, tie-breaks and exact paths copied from the implementation | Private repo A: 263 literals with 12+ decimals, including `0.2600000000000001` and duplicated load coefficients. `agentic-mermaid`: A* heuristic `toBe(6)` and tie-break `path[1]`. `tasche`: bm25 weights. |
| **T5** Copied enumerations and counts | Expected counts, lists or orders copied from the code or docs | `geist_fabrik`'s geist count, rewritten 15 times (once to a wrong value). `keyboardia`'s 11 exact lane counts plus an 834-line identity file. `atlas`'s 391 routes (×3). `garten`'s `toBe(147)`. |
| **T6** Legitimate exactness (control) | The bytes are the product or the protocol | Release tarball SHA and SRI; font and model file hashes; content-addressed stores; canonical sync-state hashes; crypto test vectors; ASCII terminal goldens that are the published output; Python-port float parity in `yaket`; replay A == replay B. |

**T3-eval** is the eval analogue of T3: keyword or regex oracles over model output, making up 41–83% of eval assertions in 9 skill repositories. It was covered in the September audit and is not repeated here.

## 2. Prevalence and cost

| Repo | Dominant types | Commits touching pins | Sampled failures: false alarm / neutral / catch |
|---|---|---|---|
| `agentic-mermaid` | T1, T2, T3 | 301 of 823 (36.6%), including 31 pin-only commits (22k lines) | ≥7 kinds of false alarm / 45 approvals alongside intended changes / 1 catch; 0 catches in 59 golden approvals |
| private repo A | T3, T1, T4, T5 | 795 of 1,856 (43%) touched a T3 file | 10 / 3 / 1 (of 14); CI: 61 of 61 red unit runs came from T3/T5/governance tests, with 0 product regressions caught |
| `pythonbyexample` | T3, T2 | 45 of 192 (23%) | 4 / 6 / 0 (of 10) |
| `tasche` | T3 (SQL text) | 25 of 83 test-touching commits (all agent) | 0 catches; the real-SQLite ranking tests were *deleted* in favour of SQL substrings |
| `planet_cf` | T3 (SQL, workflow text) | 17 of 64 test-touching commits (all agent) | 0 catches; an error-swallowing migration step sat beside workflow-text tests that did not see it |
| `geist_fabrik` | T5, T3 | 15 count rewrites (13 agent) | 0 catches; one pin was itself wrong (43 vs 42); workflow text pinned a bug |
| `keyboardia` | T1 (evidence), T5 | 94 of 926 (10%) | ≥5 kinds of false alarm / 0 catches |
| `atlas`, `vaders`, `flux-search`, `demoscene`, `embed` | T2 (never run), T3 | small | 0 catches; baselines stale or never compared |

**Costs the owners recorded themselves:**
- **Merges.** 84 of 88 conflicts in one `agentic-mermaid` merge were in generated or hash files, and one merge took 56 minutes.
- **Churn.** 41 of 68 commits in one PR were bookkeeping. About 150k lines of golden churn came from a baseline flipping between two formats in 7 agent commits in a single day.
- **False alarms.**
  - A one-line comment edit tripped 13 checks (`agentic-mermaid` #357).
  - A comment rename broke a source-slice boundary (private repo A).
  - A sealed-fixture diff "sent a whole wave hunting a rendering bug that was never there".
  - A real pacing fix was reverted because it moved a pinned fixture's RNG draws.
- **Removals.** Private repo A's clean-up deleted about 117k lines of ceremony. `agentic-mermaid` #361 removed about 100k lines of derived files.

**The pattern also let bugs through:**
- regenerated goldens absorbed 10 defects (`agentic-mermaid` #136);
- snapshot drift missed 3 geometry bugs;
- output harvested from the code pinned a wrong ellipse label;
- workflow-text tests pinned the text of the release bug they were meant to prevent (`geist_fabrik`).

## 3. Where it comes from

1. **Fix, then a test that greps for the fix.** An audit or incident fix gets a "regression test" asserting that the fix's text exists: `planet_cf` b80a8d0 (+40 assertions for "20 mitigations"), `atlas` 560117f ("22 tests guarding the 5 audit fixes"), `tasche` f24cc91, `geist_fabrik`'s release contracts, and private repo A's `sourceBetween(...)` checks. These pass at once with no red step, cannot fail on the pre-fix *behaviour*, and break on any rename. This is the dominant agent pattern.
2. **Observe and paste (the regression-oracle problem):**
   - `pythonbyexample` 5cbc4f0: "Regenerated the fixture from the current examples. Parity check now reports 100%".
   - `atlas` bfd1915: "budget to match current build".
   - `geist_fabrik` 1acbc1e: "test count to 41".
   - `agentic-mermaid` 41a4468e: "re-pinned to live values".
   - Private repo A 6f97ba64: replaced parity oracles with 75 "frozen outcomes captured from the legacy law", written *during* its test audit.
   - Six `UPDATE_*` regeneration switches in one repo.
3. **Self-approval.** `[approve-goldens]` tokens: at least 54 of 59 were agent-authored, 3 were empty commits that existed only to carry the token, and `main` was unprotected.
4. **Untestable architecture.** Private repo A's `main.js` grew from 23k to 31k lines, and its own history notes: "Many tests parse source text because state cannot be imported." Source-text tests then needed tests of their own ("sabotage proofs").
5. **Lessons and quotas that ratchet towards exactness:**
   - "bind row/source/dimension/output hashes" (`agentic-mermaid` lessons);
   - "bind repeated counts to the authoritative collector" (`keyboardia`);
   - assertion-density quotas (`planet_cf`: +600 assertions, 141 of them substring checks);
   - a lint banning `toBeTruthy` that pushed tests to exact literals.
6. **Evidence ceremony.** Receipts, seals and rebind tools that demanded written review notes made every visual change a process, not a judgement. The re-pin tooling was later deleted as "a stub that refused every request".
7. **Hashes as workarounds.** 6,919 lines of Bun snapshots were replaced by 57 hashes "to avoid Bun's concurrent snapshot-writer race".
8. **Sweeps and copied scaffolding.** One-day "apply testing-best-practices" sweeps (2026-06-10: `garten`, `olsen`, `aha`, `geist_fabrik`) and an identical fixture oracle landed in 9 repos on 2026-06-11.
9. **This skill** (§6). `agentic-mermaid`'s characterisation suite (1e94e8a5) cites it for "pin what the code does today". `skill-eval-harness`'s source scans cite `doc-sync-testing`. `vaders` copied v1's `test.skip(!!process.env.CI…)` the next day. `garten`'s sweep produced `toBe(147)` doc pins.

## 4. What the literature says

- **Named and condemned for decades.**
  - *Change-detector tests*: "a transformation of the same information in the code under test… provide negative value… should be re-written or deleted" [1]. The canonical example reads the production source file.
  - *Fragile Test*, *Overspecified Software* and *Sensitive Equality* [2][3].
  - *Brittle assertions*, which depend on values derived from uncontrolled inputs [4].
  - "Test behaviour, not implementation": "The ideal test is unchanging… unless the requirements… change" [5][7].
  - Structure-insensitive: "Tests should not change their result if the structure of the code changes" [8].
  - Resistance to refactoring [10] [secondary].
  - Hyrum's law [11]. Protobuf deliberately destabilises non-canonical output "to avoid giving the illusion that the output is stable" [12].
- **Characterisation and approval tests are legitimate as scaffolds.** Feathers: "descriptions of what we have rather than statements of correctness", to "revisit… periodically to tighten up" [14]. Approval testing *chooses what to print*, scrubs it and reviews it; Falco still uses asserts for small values [15][16]. Beck: snapshotting is "copy the actual result, & paste it in as the expected results"; he prefers computing expected values independently [9].
- **Snapshots are fragile, and people rubber-stamp them.**
  - Fragility is the top reported drawback [32].
  - 8.2% of commits in snapshot-using projects update snapshots [33].
  - Jest's advice: small snapshots, property matchers, never write snapshots in CI, and "fix the bug before re-generating snapshots" [17].
  - "Most developers… will sooner just nuke the snapshot" [18] [secondary].
  - In a controlled study, testers kept wrong generated assertions [35].
- **Hash oracles are Sensitive Equality with the diff thrown away.** Chromium's Gold moved away from hash-only baselines because "the only thing the user had to go on was a hash" [23]. Protobuf forbids "comparing serialized payloads as a way of checking message equality" [12].
- **Generated tests capture the implemented behaviour, not the intended one.**
  - "A regression harness can automatically check that a result has not changed, but this information serves no purpose unless the result is known to be correct" [37].
  - Randoop's "Regression assertion (captures the current behavior…)" [38]; Fraser & Zeller [39]; TOGA and its replication, which found over 47% false positives [40][41].
  - LLMs "capture the actual program behaviour rather than the expected one" [42]. TestPilot updates an assertion's expected value from the failure message [43]. Meta keeps only passing tests "for regression testing" [45].
  - Magic numbers are among the most frequent smells in LLM tests [46][47]. Agent tests are denser in assertions and more mocked [48][49] [preprints].
- **Costs.** 26% of non-flaky CI failures in 61 projects came from incorrect or obsolete tests [26]. Refactoring *rarely* breaks tests in general [28], so brittleness comes from particular assertion styles and is avoidable. Test-smell detector counts are unreliable as a metric [31].
- **Remedies**, each with the conditions under which it fits:
  - assert only specified fields [2][6];
  - parse then compare semantically, and canonicalise [12][13][55];
  - scrubbers and redactions [16][56];
  - justified tolerances: relative/ULP for floats, perceptual thresholds for images [20]–[25];
  - small, reviewed snapshots [17][18];
  - properties, which in practice are most often differential [57];
  - metamorphic relations [58];
  - reference or differential oracles, such as reftests and `check_figures_equal` [22][59];
  - consumer-driven contracts [53];
  - spec-derived vectors [61].
- **When byte-exactness is legitimate:** formatter output, canonical encodings, crypto known-answer vectors, reproducible builds, and published wire or file formats [55][61][62][63]. "Deterministic serialization is not canonical" [12].

## 5. What worked in this portfolio

- **`agentic-mermaid` #357/#361:**
  - 44 hashes became readable geometry;
  - linkrank hashes became a property ("gap ≥ 223.5px");
  - source greps became executed scripts and workflow steps;
  - 375 styled hashes became 16 readable SVG goldens;
  - payload baselines became ceilings with headroom plus a delta against the base branch;
  - it added a red-green job and upstream differentials.

  Its new rules: "no expected values produced by the code under test" and "Hashes belong only on bytes we ship or fetch". The same PR found a real bug (a stroke width of `2.0999999999999996`).
- **Private repo A** replaced its 11.4k-line source-regex architecture file with import-graph and cycle checks. It replaced sealed fixtures with fast-check properties, replay equality, a trusted-input golden path and a seeded base-vs-head equivalence probe. Its lesson: exactness works when it is short-lived and differential, not when it is committed.
- **Real engines instead of text:** `sunrise`'s real SQLite loaded from migrations found 5 bugs; `pythonbyexample` checks computed styles in a real browser; `atlas` measures geometry; `garten` uses pixel probes plus Linux goldens in CI.
- **Relational characterisation** (`bobbin`: tuned ≤ baseline), docs-sync derived from the CLI's own help (`olsen`), and required/forbidden ID sets instead of full outputs (`cfdoctor`).
- **Input hashes for provenance** (`pythonbyexample`'s social cards) instead of output hashes as oracles.

## 6. Where this skill contributes

| Location | Text | Problem | Change |
|---|---|---|---|
| `references/characterization-testing.md:11,20,29` | "Record the actual outputs as assertions — even if they look wrong"; "not about correctness — they're about change detection" | Observe-and-paste with no exit; cited for permanent refactor gates and frozen outcomes | Scope it to changing existing code. Label each test as a characterization. Prefer relational or invariant characterisation. After the change, convert each pin to a specified assertion or delete it. Never use it as the oracle for new code |
| `references/test-types.md:211` | "Call the code and record actual outputs as assertions" | Same | Same, plus a retirement step |
| `references/golden-file-testing.md:11,21,36` | "don't hand-write the expected output"; "If no expected file exists, create a baseline automatically"; `saveExpected(...); return;` | A missing golden passes vacuously; the oracle is whatever the code emits | A missing golden fails in CI. Decide the contract first; generate the candidate, then review it against the contract |
| `references/golden-file-testing.md:61`; `test-types.md:234` | "Drift detection: any change to transformation logic is caught"; "Catches drift" | Sells change detection as the benefit | Say the goal is catching *behaviour* changes; incidental drift is noise to normalise away |
| `references/golden-file-testing.md:140–144`; `test-types.md:228` | Snapshot when "more than ~5 fields"; "a single change should cascade through the snapshots"; golden when output is "hard to assert on field-by-field" | Overspecification by default | First ask which fields the behaviour specifies; parse and compare those; snapshot only a small, normalised projection |
| `references/golden-file-testing.md` "Hash-only goldens" | "If you must keep hashes, re-pin through a tool that records a written review" | This is the rebind ceremony private repo A deleted | Hashes only for T6; otherwise keep the artifact and a semantic diff; if a pin changes more often than it catches bugs, replace it |
| `references/test-types.md:310,312` | Characterization maintenance "Medium"; Golden maintenance "Low", flake risk "Very Low" | Contradicted by 23–43% commit churn | Maintenance High unless normalised and small; bug power depends on review |
| `SKILL.md:176` | "For transformations or complex generated output, use golden files" | Golden as the default oracle | Oracle ladder (below); golden is one rung |
| `SKILL.md:173` | Forbids recomputing expectations with the SUT's logic | Silent on the equally dependent move: pasting the SUT's *output* | Add the provenance rule: every expected value comes from a spec, a hand derivation, a reference or a property; pasted output is a characterization |
| `SKILL.md:109`; `gate-integrity.md` §5 | Every oracle needs known-good and known-bad inputs | Read as "prove the regex catches its own text", which produced sabotage proofs | Say it applies to checkers of *behaviour*; a text-grep test is not an oracle to prove, it is a test to replace |
| `references/antipatterns.md:165` (#12) | "Delete and re-record periodically" | Institutionalises re-recording | For snapshots: reduce and normalise, don't re-record. Keep re-recording for cassettes only |
| `references/doc-sync-testing.md:41–42` | Counts in docs "(generate them, or assert them)" (added in this PR) | Drives T5 count pins that change with every addition | Don't quote volatile counts; generate them or omit them. Derive doc checks from the registry or CLI (`olsen`), not from copied literals |
| v1 `typescript.md` / `test-types.md` (retracted 2026-09-27) | `test.skip(!!process.env.CI…)` | Baselines that never run | Already retracted; the CI-image workflow stays |
| missing | — | No numeric tolerance guidance; no statement of when exactness is legitimate; no guidance on SQL-text fakes versus real engines beyond the mock ladder | Add the tolerance, T6 and real-engine rules |

This repository's own tooling pins text too. `audit-best-practices.py` keys probes on exact headings ("Restraint: don't over-apply"), and the static audit and prose oracles match wording. These are cheap lints over prose, and their failure mode is missing a paraphrase rather than raising false alarms. Keep them, but don't hold them up as examples.

## 7. What the skill should say (proposed)

1. **Where does the expected value come from?** Before writing an assertion, name its source: a spec or contract, a hand derivation, a reference implementation, a known-answer vector, or a property. A value obtained by running the code under test is a *characterization*. Allow it only to protect a change to existing code, label it, and retire it afterwards. Never make it the only oracle for new code.
2. **Assert the contract, not the serialization.** Use this oracle ladder, cheapest and most robust first:
   1. specified fields;
   2. parse then compare (DOM, AST, parsed YAML/JSON, rows from a real engine);
   3. properties, metamorphic relations or a differential against a reference;
   4. a tolerance justified by the spec (relative/ULP for floats; perceptual for pixels);
   5. a small, normalised, reviewed golden;
   6. a hash, only when the bytes themselves are the product (T6), with the artifact kept and a readable diff printed.
3. **A regression test must fail on the pre-fix behaviour.** Grepping for the fix's text is not a regression test: it cannot fail on the old behaviour, and it breaks on renames. If behaviour cannot be reached, create a seam. Don't read source text.
4. **No source- or config-text assertions.** Check config on parsed values. Enforce structural rules with AST lints or import-graph checks, never with regexes over source.
5. **Check tests from both sides.** A good test survives a behaviour-preserving refactor (structure-insensitive) and fails on an injected behaviour change [8][39]. Use both as the acceptance check for new tests; the two new evals below encode this.
6. **Goldens.** A missing golden fails in CI, and CI never writes goldens. Keep them small and normalised, reviewed as diffs, and never regenerated by the actor who changed the code. Measure pin churn against catches, and replace pins that only churn.
7. **Tolerances are spec decisions.** State them, justify them, and don't loosen them to go green.
8. **Real engines over text-routing fakes.** SQL-substring fakes are permissive environments. Load an in-memory engine from the migrations.
9. **Retire, don't ratchet.** When a pin keeps firing on refactors, replace it with a behavioural check. Don't add process (review notes, approval tokens, rebind tools) around it.

**Cheaper alternatives to recommend by situation:**
- rendered output → geometry or structure assertions, plus a few images reviewed as images;
- CSS → computed styles in a browser;
- workflows → parsed step graph plus actionlint;
- SQL → a real in-memory engine;
- floats → tolerances or properties;
- counts → derived from the registry;
- determinism → replay A == replay B, or base vs head;
- provenance → hash the *inputs*, not the outputs.

**Evals to add**, two-sided runtime oracles in the style of E78:
- "Add a regression test for this fix". The test must fail on the pre-fix build and pass on a behaviour-preserving refactor that renames the fixed code.
- "Add tests for this SVG/JSON renderer". The tests must pass on a variant with reordered attributes and changed whitespace, and fail on a semantic change.
- "Test this numeric routine". The tests must pass on an implementation that sums in a different order (differences around 1e-15) and fail on a real error.
- A hidden restraint probe: a crypto or serialization task where byte-exact is correct, and the answer must keep it.

## 8. Per-repository next steps (highest value first)

- **`agentic-mermaid`:**
  - make `layout-geometry-baseline` an opt-in refactor gate and rely on the layout and route-contract invariants;
  - replace the 486 substring asserts in `website-build` with DOM and computed-style checks;
  - replace the A* path pins with length, endpoints and determinism checks;
  - protect `main` (#331).
- **Private repo A:**
  - render chapter counts from the registry instead of linting prose;
  - replace the static clock-reach call graph with an injected clock;
  - replace the growing float pins with bounds and properties;
  - drop the stale source-text ratchet from the open audit PR.
- **`tasche`:** restore real SQLite with FTS5 loaded from the migrations; replace SQL-routing fakes and bm25 weight pins with ranking properties.
- **`planet_cf`:** real SQLite from the migrations instead of the regex MockD1; run the deploy script against a stub instead of pinning its text.
- **`pythonbyexample`:** merge the computed-style browser check (open PR) and delete the remaining CSS/workflow text asserts.
- **`geist_fabrik`, `atlas`, `garten`, `bobbin`, `skill-eval-harness`:** derive counts from registries; replace text asserts with rendered or parsed checks. `atlas`: hash social-card *inputs*.
- **`vaders`, `flux-search`, `demoscene`, `embed`, `atlas`:** render baselines on the CI image or delete them in favour of geometry checks.
- **`keyboardia`:** drop the evaluator source hash (rerun and compare with a tolerance); bind waivers to IDs rather than file hashes; replace exact lane counts with "no unexpected skips, no empty lane".

## References

Numbering follows the literature review. Quotes were checked against the primary text unless marked [secondary]; [preprint] marks 2026 arXiv papers that have not been peer reviewed.

1. Eagle, A. "Testing on the Toilet: Change-Detector Tests Considered Harmful." Google Testing Blog, 2015. https://testing.googleblog.com/2015/01/testing-on-toilet-change-detector-tests.html
2. Meszaros, G. *xUnit Test Patterns: Refactoring Test Code*. Addison-Wesley, 2007 (Fragile Test, p. 239). Draft: http://xunitpatterns.com/Fragile%20Test.html
3. van Deursen, A., Moonen, L., van den Bergh, A., Kok, G. "Refactoring Test Code." XP2001; CWI SEN-R0119, 2001. https://ir.cwi.nl/pub/4324
4. Huo, C., Clause, J. "Improving Oracle Quality by Detecting Brittle Assertions and Unused Inputs in Tests." FSE 2014. doi:10.1145/2635868.2635917
5. Kuefler, E. "Unit Testing," ch. 12 in Winters, Manshreck, Wright (eds.), *Software Engineering at Google*, O'Reilly, 2020. https://abseil.io/resources/swe-book/html/ch12.html
6. Trenk, A., Bly, D. "Test Doubles," ch. 13, ibid. https://abseil.io/resources/swe-book/html/ch13.html
7. Trenk, A. "Testing on the Toilet: Test Behavior, Not Implementation." 2013. https://testing.googleblog.com/2013/08/testing-on-toilet-test-behavior-not.html
8. Beck, K. "Test Desiderata." 2019. https://testdesiderata.com/ (the site carries no byline; kentbeck.github.io/TestDesiderata redirects here)
9. Beck, K. "Snapshot Testing." 2023. https://newsletter.kentbeck.com/p/snapshot-testing
10. Khorikov, V. *Unit Testing Principles, Practices, and Patterns*. Manning, 2020. Quote via https://khorikov.org/files/infographic.pdf [secondary]
11. Wright, H. "Hyrum's Law." https://www.hyrumslaw.com/
12. Protocol Buffers docs: "Proto Serialization Is Not Canonical," https://protobuf.dev/programming-guides/serialization-not-canonical/ ; Go FAQ (unstable errors/JSON/text), https://protobuf.dev/reference/go/faq/ ; `protobuf-go/internal/detrand`.
13. Google Go Style Guide, "Decisions" (Compare stable results; Test error semantics; Print diffs). https://google.github.io/styleguide/go/decisions
14. Feathers, M. *Working Effectively with Legacy Code*. Prentice Hall, 2004; "Characterization Testing," 2016. https://michaelfeathers.silvrback.com/characterization-testing
15. Falco, L., interviewed on SE Radio 595, 2023. https://se-radio.net/2023/12/se-radio-595-llewelyn-falco-on-approval-testing/
16. ApprovalTests.Java docs, "Scrubbers." https://github.com/approvals/ApprovalTests.Java/blob/master/approvaltests/docs/Scrubbers.md
17. Jest docs, "Snapshot Testing." https://jestjs.io/docs/snapshot-testing
18. Dodds, K.C. "Effective Snapshot Testing." 2017 (transcribes Justin Searls). https://kentcdodds.com/blog/effective-snapshot-testing
19. Yee, H. "A Perceptual Metric for Production Testing." J. Graphics Tools 9(4), 2004. doi:10.1080/10867651.2004.10504900
20. mapbox/pixelmatch README. https://github.com/mapbox/pixelmatch
21. Playwright docs, "Visual comparisons." https://playwright.dev/docs/test-snapshots
22. web-platform-tests docs, "Reftests." https://web-platform-tests.org/writing-tests/reftests.html
23. Chromium docs, "GPU Pixel Testing With Gold." https://chromium.googlesource.com/chromium/src/+/HEAD/docs/gpu/gpu_pixel_testing_with_gold.md
24. Dawson, B. "Comparing Floating Point Numbers, 2012 Edition." https://randomascii.wordpress.com/2012/02/25/comparing-floating-point-numbers-2012-edition/
25. Barker, C. PEP 485, 2015. https://peps.python.org/pep-0485/ ; NumPy `assert_allclose` (rtol=1e-7), `assert_array_max_ulp`.
26. Labuschagne, A., Inozemtseva, L., Holmes, R. "Measuring the Cost of Regression Testing in Practice." ESEC/FSE 2017. doi:10.1145/3106237.3106288
27. Vahabzadeh, A., Milani Fard, A., Mesbah, A. "An Empirical Study of Bugs in Test Code." ICSME 2015. doi:10.1109/ICSM.2015.7332456 (abstract only)
28. Kashiwa, Y., Shimizu, K., Lin, B., Bavota, G., Lanza, M., Kamei, Y., Ubayashi, N. "Does Refactoring Break Tests and to What Extent?" ICSME 2021. doi:10.1109/ICSME52107.2021.00022 (abstract only)
29. Bavota, G. et al. "An Empirical Analysis of the Distribution of Unit Test Smells and Their Impact on Software Maintenance." ICSM 2012. doi:10.1109/ICSM.2012.6405253 (EMSE 2015 extension, doi:10.1007/s10664-014-9313-0, [unverified])
30. Spadini, D., Palomba, F., Zaidman, A., Bruntink, M., Bacchelli, A. "On the Relation of Test Smells to Software Code Quality." ICSME 2018. doi:10.1109/ICSME.2018.00010 (abstract only)
31. Panichella, A., Panichella, S., Fraser, G., Sawant, A.A., Hellendoorn, V.J. "Test Smells 20 Years Later: Detectability, Validity, and Reliability." EMSE 27, 2022. doi:10.1007/s10664-022-10207-5 (abstract only)
32. Cruz, V.P.G., Rocha, H., Valente, M.T. "Snapshot Testing in Practice: Benefits and Drawbacks." JSS 204, 2023. doi:10.1016/j.jss.2023.111797
33. Fujita, S., Kashiwa, Y., Lin, B., Iida, H. "An Empirical Study on the Use of Snapshot Testing." ICSME 2023 (NIER). doi:10.1109/ICSME58846.2023.00041
34. Watanabe, M., Horikawa, K., Reid, B., Kashiwa, Y., Iida, H. "What Are Developers Actually Discussing When Visual Regression Tests Fail?" arXiv:2608.07020, 2026 [preprint]
35. Fraser, G., Staats, M., McMinn, P., Arcuri, A., Padberg, F. "Does Automated Unit Test Generation Really Help Software Testers? A Controlled Empirical Study." TOSEM 24(4), 2015. doi:10.1145/2699688 (checked against the submitted version)
36. Barr, E.T., Harman, M., McMinn, P., Shahbaz, M., Yoo, S. "The Oracle Problem in Software Testing: A Survey." IEEE TSE 41(5), 2015. doi:10.1109/TSE.2014.2372785
37. McKeeman, W.M. "Differential Testing for Software." Digital Technical Journal 10(1):100–107, 1998.
38. Randoop Manual, "Regression tests" / "Regression test failures." https://randoop.github.io/randoop/manual/
39. Fraser, G., Zeller, A. "Mutation-Driven Generation of Unit Tests and Oracles." IEEE TSE 38(2), 2012. doi:10.1109/TSE.2011.93
40. Dinella, E., Ryan, G., Mytkowicz, T., Lahiri, S.K. "TOGA: A Neural Method for Test Oracle Generation." ICSE 2022. doi:10.1145/3510003.3510141
41. Hossain, S.B., Filieri, A., Dwyer, M.B., Elbaum, S., Visser, W. "Neural-Based Test Oracle Generation: A Large-Scale Evaluation and Lessons Learned." ESEC/FSE 2023. doi:10.1145/3611643.3616265
42. Konstantinou, M., Degiovanni, R., Papadakis, M. "Do LLMs Generate Test Oracles that Capture the Actual or the Expected Program Behaviour?" arXiv:2410.21136, 2024.
43. Schäfer, M., Nadi, S., Eghbali, A., Tip, F. "An Empirical Evaluation of Using Large Language Models for Automated Unit Test Generation." IEEE TSE, 2024. doi:10.1109/TSE.2023.3334955
44. Yuan, Z. et al. "Evaluating and Improving ChatGPT for Unit Test Generation" (arXiv title: "No More Manual Tests?"). FSE 2024. doi:10.1145/3660783
45. Alshahwan, N. et al. "Automated Unit Test Improvement using Large Language Models at Meta." FSE Companion 2024. doi:10.1145/3663529.3663839
46. Siddiq, M.L. et al. "Using Large Language Models to Generate JUnit Tests: An Empirical Study." EASE 2024. doi:10.1145/3661167.3661216
47. Ouédraogo, W.C. et al. "On the Diffusion of Test Smells in LLM-Generated Unit Tests." TOSEM, 2026. doi:10.1145/3838597 (arXiv:2410.10628)
48. Hora, A., Robbes, R. "Are Coding Agents Generating Over-Mocked Tests? An Empirical Study." arXiv:2602.00409, 2026 [preprint]
49. Yoshimoto, S. et al. "Testing with AI Agents: An Empirical Study of Test Generation Frequency, Quality, and Coverage." arXiv:2603.13724, 2026 [preprint]
50. Canedo, A. "Oracles That Cannot Fail: Anchoring and the Expectation That Moves With the Fault." arXiv:2608.17214, 2026 [preprint]
51. Leith, D.J. "The Quality of Claude AI-authored Python Tests Is Not Weaker Than Human-authored Tests." arXiv:2608.15188, 2026 [preprint]
52. Foster, C. et al. "Mutation-Guided LLM-based Test Generation at Meta." arXiv:2501.12862, 2025.
53. Robinson, I. "Consumer-Driven Contracts: A Service Evolution Pattern." 2006. https://martinfowler.com/articles/consumerDrivenContracts.html
54. Fowler, M. "Tolerant Reader." 2011. https://martinfowler.com/bliki/TolerantReader.html
55. Rundgren, A., Jordan, B., Erdtman, S. RFC 8785, "JSON Canonicalization Scheme (JCS)." 2020. https://www.rfc-editor.org/rfc/rfc8785
56. insta docs, "Redactions." https://insta.rs/docs/redactions/
57. Goldstein, H., Cutler, J.W., Dickstein, D., Pierce, B.C., Head, A. "Property-Based Testing in Practice." ICSE 2024. doi:10.1145/3597503.3639581
58. Chen, T.Y., Kuo, F.-C., Liu, H., Poon, P.-L., Towey, D., Tse, T.H., Zhou, Z.Q. "Metamorphic Testing: A Review of Challenges and Opportunities." ACM CSUR 51(1), 2018. doi:10.1145/3143561
59. Matplotlib developer docs, "Testing" (`image_comparison`, `check_figures_equal`, `tol`). https://matplotlib.org/devdocs/devel/testing.html
60. Graves, J. "Larger Testing," ch. 14, *Software Engineering at Google*, 2020. https://abseil.io/resources/swe-book/html/ch14.html
61. Project Wycheproof (crypto test vectors). https://github.com/C2SP/wycheproof
62. Go source, `src/go/printer/printer_test.go` (golden files, `-update`, idempotence check). https://github.com/golang/go/blob/master/src/go/printer/printer_test.go
63. Reproducible Builds, "Definitions." https://reproducible-builds.org/docs/definition/
64. TNG, ArchUnit. https://github.com/TNG/ArchUnit
65. Kuefler, E. "Testing on the Toilet: Don't Put Logic in Tests." 2014. https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html
