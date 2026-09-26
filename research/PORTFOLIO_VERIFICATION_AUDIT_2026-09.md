# Portfolio Verification Audit: github.com/adewale, 2025-03-26 → 2026-09-26

> Audit of the testing and verification mechanisms in every repository `adewale` has worked on in the last 18 months. It asks what the portfolio teaches this skill, what works and what doesn't across projects, and how each project should change.
> Date: 2026-09-26. Supersedes the per-repo facts in `LESSONS_FROM_ADEWALE_REPOS.md` (2026-04-11) where they conflict; see [Corrections](#corrections-to-lessons_from_adewale_reposmd).

---

## Table of Contents

1. [Scope, method, limits](#scope-method-limits)
2. [Headline findings](#headline-findings)
3. [What the portfolio teaches this skill](#what-the-portfolio-teaches-this-skill)
4. [What is working well across projects](#what-is-working-well-across-projects)
5. [What is not working well across projects](#what-is-not-working-well-across-projects)
6. [How and why each project should change](#how-and-why-each-project-should-change)
7. [Corrections to LESSONS_FROM_ADEWALE_REPOS.md](#corrections-to-lessons_from_adewale_reposmd)
8. [Appendix: numbers](#appendix-numbers)

---

## Scope, method, limits

**What was audited.**
- 53 repositories with commits since 2025-03-26:
  - 46 owned public repositories (including this one);
  - `agentic-mermaid`, a fork where Ade and agents wrote 731 of 758 non-merge commits;
  - 6 private repositories, which were audited and reported privately; this document does not describe them.
- Excluded: 9 forks whose recent history is upstream work (e.g. `hallmark`, `small-app-gardener`, `who-to-bother-at-on-x`). The fork `livecore` has only 2 owner commits and is noted in one line.
- Each repository was cloned with history back to 2025-03-01.

**How evidence was gathered.**
- Eight review agents each took a group of repositories. For each repo they:
  - read the test code, runner configs, CI workflows, hooks, agent instruction files (CLAUDE.md/AGENTS.md) and testing docs;
  - read the git history since 2025-03-26;
  - **ran the fast suites from a fresh install**.
- A uniform history scan measured the following for every repo (script in the Appendix):
  - fix commits that touched a test;
  - flake, skip and revert commits;
  - agent co-authorship.
- High-impact claims were spot-checked by hand before inclusion. Examples: the skill passages quoted below; `agentic-mermaid`'s deploy skip; the `skill-eval-harness` runner; `planet_cf`'s secrets and migration steps; `olsen`'s `|| true`.

**Limits.**
- **GitHub Actions run history for public repos was not accessible** from the audit session. "Passes in CI" means the agents ran the same commands locally.
- **All suites ran on a shared 4-CPU machine at load average 15–31.** Absolute durations are inflated. Timeout failures were re-run alone before being classified: "passes alone, fails under load" is a finding about contention sensitivity, not a product bug.
- **Agent share is a lower bound.** Share of non-merge commits carrying Claude/Codex authorship or trailers is 62% for the public repos, and it is a lower bound because Codex-era commits usually carry no trailer.

---

## Headline findings

1. **The dominant failure is verification that stops running, or can never go red, while everyone believes it is green.** It is not missing tests. Examples:
   - `rogue_planet`'s network tests, praised in April, have not compiled since 2025-11-02.
   - `agentic-mermaid`'s deploy has ended "green but skipped" for about 8 weeks. The live site is 53 commits behind `main`.
   - `planet_cf`'s secrets scan and migration step cannot fail.
   - `skill_scanner`'s CI "security gate" scans 0 skills.
   - `olsen` ran CI tests behind `|| true` for about 8 months. Its first honest run found a `DeletePhoto` that had never worked.
   - `skill-eval-harness` CI never collects 56 of its own tests.
   - `demoscene`, `embed.oshineye.dev` and `sunrise` have good suites and no CI at all.
2. **Where the skill was applied, it visibly worked.**
   - `keyboardia`'s July 2026 audit, run explicitly against this skill, found 91 of ~189 E2E runs failing silently under `continue-on-error`. It reversed the Dec–Jan agent-era skips, retries and production-proxy E2E, and replaced them with executable, fixture-tested gates. Those gates still pass at HEAD.
   - `agentic-mermaid` (audit `6707615`, 2026-04-11) and `aha`, `garten`, `geist_fabrik`, `vaders` and `yaket` cite the skill.
   - Downstream repos now file skill issues (#20–#22 came from `agentic-mermaid`).
3. **The skill currently ships four pieces of guidance that the portfolio refuted** (verified in the current text; open PR #27 fixes only the mutation cadence):
   - `references/typescript.md:122` recommends `retries: process.env.CI ? 2 : 0`. `keyboardia`'s hard-won policy is `retries: 0` plus a `flaky == 0` reporter contract. The skill's own `antipatterns.md:94` also says retries mask races.
   - `references/typescript.md:148-149` and `references/test-types.md:245` say to skip visual tests in CI. Every visual suite in the portfolio that followed this ran zero times in CI: `atlas`, `flux-search`, `embed`, `demoscene`, `vaders`, and `keyboardia` until July. The repos that fixed it rendered baselines on the CI image.
   - `references/test-types.md:275` ("Unit tests for business logic (3+ assertions…)") and `antipatterns.md:108` ("Track assertion density") contradict SKILL.md's "Assertion count is a heuristic, not a law". Downstream, this became quotas: `planet_cf` Lesson 31 sets ≥3.0 per file, and was met with `isinstance` asserts plus a new flaky property test. `vaders` runs a density audit, and an in-repo `bobbin` audit used "≥3 per test".
   - The mock-contract pattern (`typescript.md`, and the April research) is now vestigial in its source repo. `atlas` deleted the mock in favour of a real engine (node-canvas), and the contract test guards nothing.
4. **The agent era produces a recognisable set of test smells the skill does not name yet:**
   - tests that assert source or config text (CSS, JS, YAML, docs);
   - hash-pinned goldens that churn on every change;
   - E2E through a test facade;
   - tests that import nothing from the code under test;
   - vacuous universal assertions over empty sets;
   - self-authored oracles (eval questions and golden approvals written by the same agent in the same change);
   - claims of "green" based on a narrower command than CI runs.
5. **The newest, most heavily verified repos are now limited by verification cost, not coverage.**
   - `keyboardia`: `ci.yml` grew from 141 to 915 lines. 15 of 317 unit files take 92% of unit CPU, mostly tests of the verification tooling. The global timeout was ratcheted 5 s → 20 s → 30 s.
   - `agentic-mermaid`: the unit suite is 31 min under load, and a 41-job mutation lane was retired after 26 straight failures.
   - The skill says a lot about under-testing and almost nothing about gate budgets, retirement, or cost-weighted suite shape.
6. **Testing LLM features and agent skills is the largest subject the shipped skill does not cover.** More than ten repos in the portfolio are skills or eval tooling, and this repo's own development process is eval-heavy. Yet `SKILL.md` and `references/` have no guidance on:
   - paired baselines;
   - saturation;
   - keyword oracles;
   - judge validity;
   - holdouts or leakage;
   - cost per unit of lift.

---

## What the portfolio teaches this skill

Ordered by expected impact. Each item names the skill location it affects and the evidence behind it.

### 1. Stop shipping guidance the portfolio refuted (small edits, highest leverage)

| Current text | Change | Evidence |
|---|---|---|
| `typescript.md:122` `retries: process.env.CI ? 2 : 0` | Required lanes: `retries: 0` plus a reporter contract (expected, skipped, `flaky == 0`, `unexpected == 0`). Retries only in explicitly non-gating discovery lanes. | `keyboardia` `e2e/lane-contracts.json`, `scripts/assert-playwright-stats.mjs`. Agent-era `fbe41bf` "Add retries for flaky E2E" was later reversed. `atlas` `retries: 1` always hides flakes locally too |
| `typescript.md:148-149` and `test-types.md:245` "Skip in CI" | Render baselines **on the CI image**, via a reviewed manual workflow that never auto-commits. Keep per-platform baselines. Gate exactly. Carry precision in structural or semantic assertions where pixels are noisy (`agentic-mermaid` pairs 5% pixel tolerance with structural SVG asserts). Otherwise golden the deterministic intermediate (text frames, draw lists), as `vaders` `3f08b6a` does. | `keyboardia` `visual-baselines.yml`. darwin-only baselines in `atlas`, `flux-search`, `embed` (7/7 fail on Linux), `demoscene`, `vaders` |
| `test-types.md:275` "3+ assertions" and `antipatterns.md:106-108` "Track assertion density" | Delete the number. Say "multiple meaningful assertions where the behaviour has multiple observable effects; never a per-file or per-test quota." Add "assertion quota" to antipattern #10 as a Goodhart failure. | `planet_cf` `8610054` and Lesson 31; `vaders` `audit-assertion-density.mjs`; `bobbin` audit |
| Mock-contract tests as the remedy for mock drift (`typescript.md`, `antipatterns.md` #3) | Prefer deleting the mock when a real engine can run in process. Contract-test only the doubles you must keep, with expected values **recorded from the real service**. Flag contract tests whose target double no longer exists. | `atlas` `9a16ad7`; `sunrise` `24c6d80`/`8ac4d46`. `tasche` `test_mock_fidelity.py:97-110` asserts the mock author's belief (`changes == 1` for a no-match DELETE), which production code contradicts |

Also publish a **retracted-guidance changelog**, a short list in `CHANGELOG.md` of rules the skill has withdrawn. Downstream repos keep enforcing retracted rules (`vaders`), and agents re-read stale project lessons that cite them (`keyboardia` Lesson 16 still says to add retries).

### 2. Add a first-class check: "Is the verification actually running, and can it go red?"

This is the single biggest gap. Assess check #10 already asks whether the configured runner reaches the production path, but only for generative tests. Generalise it into a **step 0 of Assess mode**, repeated in the Validation loop and the report contract.

- **Liveness**: for every tier (unit, integration, E2E, visual, mutation, coverage, evals, fuzz, perf), which job runs it, and when it last passed on the default branch.
  - A tier with no job is presumed broken.
  - Portfolio examples:
    - `tasche`'s 126 Playwright/axe tests and 35 staging E2E tests have no job; the last recorded run was February.
    - `planet_cf` vitest has no job and is 10/27 red.
    - `geist_fabrik` real-model tests and benchmarks run nowhere.
    - `atlas` iPhone projects are never invoked.
    - `keyboardia`'s `mobile-chrome` project is in no lane.
- **Gated-test reachability**: every build tag, `skipIf(resource)`, env gate, OS-suffixed baseline or optional leg needs three things:
  - (a) it must be compiled in CI;
  - (b) some lane must provide the resource and select the file;
  - (c) that lane must fail when the test skips.

  Portfolio examples:
  - `rogue_planet` `-tags=network`: compile error since `65d22f3`.
  - `yaket`: Python parity files are selected by no lane.
  - `aha`: 5 of 8 MCP conformance legs skip and still exit 0.
  - `olsen`: LibRaw tests never compiled; 18 tests skip from a fresh checkout.
  - `atlas`: perf budgets `skipIf(!dist)`.
  - Cheap detection: run the CI command verbosely in a fresh checkout and list the skips.
- **Gate integrity**: show every CI or hook step can go red. Detect signals to add to Detect mode and `antipatterns.md`:
  - `|| true`, `continue-on-error`, `2>/dev/null`;
  - baseline updaters used as checks (`detect-secrets scan --baseline` exits 0 and absorbs new secrets; `detect-secrets-hook` fails);
  - shell that swallows errors (`planet_cf` greps `$?` for "already exists");
  - "skip green when a secret is missing";
  - `::warning::Skipping…` that ends a deploy green (`agentic-mermaid`);
  - steps that iterate an empty set (`skill_scanner` self-scan finds 0 skills);
  - coverage thresholds that are configured but never invoked, or whose provider isn't installed (`skill_scanner` has 80% configured against 78% actual; `keyboardia` lacks `@vitest/coverage-v8`);
  - `thresholds.break: null` or dispatch-only mutation;
  - fail-open dynamic imports (`import(x).catch(() => null)` plus `skipIf`).
- **Runner collection parity**: CI's collector may not see every test. `skill-eval-harness` CI runs `unittest discover`, which cannot see 56 pytest-only cases (2 Hypothesis properties plus a 54-case exhaustive matrix). Compare collected counts between collectors.
- **Deploy freshness**: a post-deploy smoke proves only a deploy that happened. Compare the live build SHA or version with the deployable `main` (`agentic-mermaid`'s `capabilities.json` `gitSha` is 53 commits stale). Also require that E2E targets the artifact built from this commit: `planet_cf`'s `e2e.yml` never deploys what it tests, and `flux-search` PR CI tests production, not the PR.
- **Dead gate**: CI red or not executing for non-code reasons (quota, missing runner, uninstalled browser engine). It trains everyone to ignore red. The fix is to make the gate's execution visible (runner, duration, test counts), with a rule for how long a red lane may be ignored.

Proposed evals:
- A CI YAML with `detect-secrets scan --baseline` and `|| true`: the agent must flag both.
- A version-gated deploy that skips green.
- A repo whose `skipIf(!dist)` budgets never run in CI.
- A harness whose CI collector drops pytest-style functions.

### 3. Name the "vacuous pass" family ("the instrument measures something else")

Add to `antipatterns.md`, cross-linked from `property-based-testing.md` and `mutation-testing.md`:

- **Vacuous universal assertion**: "every X satisfies P" or `violations == []` without asserting that X is non-empty.
  - `demoscene` `app.spec.ts:62-98`.
  - `geist_fabrik` `test_example_geists.py`: 41 loops over possibly-empty output, 3 non-empty assertions.
  - `bobbin`'s layout spec audited 404 pages for two months.
  - Fix: a precondition assertion (non-empty, HTTP 200, font loaded, n > 0), and print the denominator.
- **Vacuous gate**: a scanner or check run against an empty target. Fix: a known-positive canary fixture, which is "verify both directions" at CI level.
- **Tautological re-implementation**: a test or script that imports nothing from the SUT and asserts on its own copy of the logic (`MaintainerBot` `scripts/test-rejections.mjs`).
- **Test linkage**: tests of code with no non-test importer, or tests of a reimplementation. In `keyboardia`, 64 tests of an unimported `validators.ts` masked a live NaN-persistence bug. `keyboardia/docs/upstream-issue-test-linkage.md` is a ready draft for this skill and was never filed.
- **Instrument drift**: measurement tools or tests that copy constants from the code instead of importing them. This is mock drift aimed at the test itself.
- **Assertions that pass when a precondition silently failed**: `test.skip()` inside the failure branch (`tasche` `immersive-and-settings.spec.js`); `page.goto(...).catch(() => {})` (`slide-maker`); imperative `pytest.xfail()` left in a resolved issue's test (`python-workers-issues`), which makes a regression report green.

### 4. Name the agent-era implementation-coupling smells

Extend antipattern #7 (coupled to implementation) and the Detect list:

- **Source-text assertions**: `readFileSync(src/…)` or `read_text()` followed by `toContain`/`assertIn`/`assert.match`. Examples:
  - `pythonbyexample` `tests/test_app.py` asserts literal CSS 17 times; 14 of those assertions came from agent commits.
  - `sunrise` asserted bundle text until `24c6d80`.
  - A private repo has 129 files of source-regex tests, including "mutants" that only test the regex.
  - Fix: assert computed or rendered behaviour, or extract a seam.
- **Config-text assertions**: literal YAML/workflow lines (`agentic-mermaid` `website-build.test.ts`, 525 string matches; `geist_fabrik` workflow string tests). They force an edit on every workflow change and still missed the deploy skip and the release-artifact bugs. Fix: parse the file and assert behavioural invariants ("every step after a precondition is gated on it"), or use actionlint plus a dry run.
- **Hash-only goldens**: exact render or op-stream hashes give no reviewable diff and need a table per backend. In a private repo, about 170 pins were touched by 90 commits. Prefer structural or perceptual goldens with a visible diff, and treat pin churn as a health metric (`golden-file-testing.md`).
- **E2E through a test facade or backdoor** is not user-journey evidence. Require at least the golden path via trusted input (`test-types.md` E2E, and Assess check #4).
- **Screenshots without an oracle**: `atlas` has 86 `page.screenshot({path})` calls into a gitignored directory that nothing compares or uploads.
- **Stale scaffold tests**: `web2kindle`'s "Hello World" test can neither start nor pass.

### 5. Oracle provenance rules

- **Fidelity expectations come from the real service**, recorded, never from the mock author's belief (`tasche`; `good-pr`'s path test asserts the consumer's belief about the harness; `skill-eval-harness`'s Jetty adapter showed 4 drifts on its first live run, 5 weeks after the mocks).
- **The author is not the oracle.** Goldens, approvals or eval cases produced in the same change by the same actor are characterizations, not oracles.
  - Examples: `agentic-mermaid` has 21 of 54 golden approvals agent-attributed. A private repo's retrieval eval is always N/N, and a title-overlap baseline already scores 85/103.
  - Remedy: report a trivial-baseline score next to the real one.
  - Where it goes: `golden-file-testing.md` review discipline and the new eval reference.
- **Test every custom oracle, gate, linter and fixer from both sides.** At least one passing and one failing example, checked in CI. The pattern exists in:
  - this repo's `run-fixture-oracles.py` and mini-repo mutants;
  - the harness's CF.1;
  - `good-pr` `test_eval_assertions.py`;
  - `slide-maker`'s two-sided gate-check;
  - `aha` `internal/testquality`;
  - `keyboardia`'s fixture-tested AST analyzer;
  - `geist_fabrik`'s gate meta-tests.

  It is missing from `atlas`'s `lint-*` scripts, a private repo's content fixers (3 wrong rewrites found by probing) and 7 skill repos. Promote it to a SKILL.md rule under "Quality beats coverage".
- **Detectors need near-miss controls.** Extend "verify both directions" from sanitizers to scanners, linters and detectors, and write fixtures from the failure, not from the regex (`cfdoctor` `forbidden_check_ids`, `max_findings: 0`).

### 6. Add a real-runtime rung and "test what ships"

- **The mock hierarchy is missing a rung.** In SKILL.md "Prefer real behavior over mocks", add **local emulation of the real runtime** between fakes and live deploys: workerd via `vitest-pool-workers`, Pyodide in Node, `pywrangler dev`, SQLite loaded from migrations. These rungs:
  - are cheap and need no credentials;
  - caught what fakes could not (`cfboundary`: under real Pyodide a `None` dict value becomes JS `undefined`, which the identity fake cannot show);
  - fixed yes-man doubles (`sunrise`'s fake D1 ignored `WHERE`; `bobbin`'s hand-built schema drifted).
- **Name the "permissive environment / yes-man double"**: a test environment that enforces fewer constraints or runs fewer branches than production. Signals: regex-dispatched SQL fakes, hand-written schemas, missing bindings (`bobbin` omits AI and Vectorize, so semantic search is never tested), fresh-only databases, tiny fixtures.
- **Production branches that exist only for test doubles** are test-induced damage. Example: `cfboundary`'s `except TypeError` retry never fires under real Pyodide.
- **"Is the artifact under test the artifact deployed?"** belongs in Assess check #4. Positive examples:
  - `pythonbyexample` lock parity: CI had tested Starlette 1.0.0 while deploys shipped 1.7.0;
  - `agentic-mermaid` tarball-consumer fuzz;
  - `geist_fabrik` publishes the exact bytes that passed smoke.

  Also test the declared compatibility floor: `xampler` declares `requires-python >=3.12` and cannot import on 3.12.

### 7. Timing, cost, and the lifecycle of gates

- **Wall-clock budgets in the unit tier**: `expect(elapsed).toBeLessThan(...)`, 30 s polling deadlines, and 5 s default timeouts on property or subprocess tests. All of these failed under contention in `agentic-mermaid`, `keyboardia`, `vaders`, `yaket`, `bobbin` and `atlas`, and passed alone.
  - The skill covers sleeps used for synchronisation, not deadline or performance assertions. Add to `deterministic-time.md`: assert bounded work (counters); put deadline contracts in an isolated lane with ~10× headroom (`garten`'s perf canaries survived) or an injected clock.
  - A **timeout ratchet** is a flakiness smell: `keyboardia` went 5 → 20 → 30 s, and `rogue_planet` widened jitter tolerance from ±10% to ±20%.
  - `isCI ? 15_000 : 5_000` runner budgets make a fresh local clone the flaky environment (`flux-search`).
- **PBT operational budget.** Size timeouts to `numRuns`. Watch generator cost: Hypothesis `from_regex(...{501,800})` trips `too_slow` under coverage and load (`planet_cf`). Use CI profiles, or a fast PR budget plus a deep scheduled budget.
- **Cost-weighted suite shape** (Assess check #12).
  - Count tests per tier, and also measure where the CPU goes. In `keyboardia`, E2E costs about 650× unit per test, and meta-verification dominates the unit tier.
- **An operating contract for every recurring lane**, not just mutation (generalise issue #20 / PR #27):
  - a baseline run before scheduling;
  - a runtime budget and an owner;
  - notify-or-block;
  - after 3 consecutive failures, fix, narrow, disable or delete (`agentic-mermaid`'s rule);
  - a removal criterion.

  Informational gates need an exit plan: `vaders`' density audit has been `continue-on-error` since April; `olsen`, `garten`, `yaket` and `aha` all have mutation lanes that cannot fail.
- **Prune discipline for agent-scale test volume.** Examples:
  - `keyboardia`'s knowledge-disposition audit for deleted tests (superseded / subsumed / re-expressed / evaporated) found a live bug.
  - A private repo deleted 1,222 lines of "ceremony" only after mutation showed it caught nothing.
  - Add to calibration and Upgrade mode.

### 8. Validation-loop and report-contract changes (agent discipline)

Add these rules to the Validation loop and the report contract.

- **Decide pass/fail from the exit status**, never by grepping output. A private repo's recurring bug was fixed by hand four times before this rule closed it. Proposed eval: a command that prints "0 errors" and exits 1.
- **Run the exact CI entrypoint**, not a sub-mode. `aha` was red for 4 days across 13 agent commits that ran `verify.sh mcp` instead of `verify.sh ci`.
- **Compile tag-gated files you touch.** `rogue_planet` `fa1dd44` said "All tests pass" after editing a file it never compiled.
- **Check the pushed commit's CI.** `atlas` `350bd65` said "268 pass locally", and the next day `ca06db0` fixed 123 CI failures, partly by loosening assertions.
- **Record which environment a green claim came from.**
- **When repairing CI, keep "update stale selector" separate from "weaken assertion / raise timeout"**, and justify each weakening.
- **Confirm a new guard goes red with the bug reintroduced.** This is the revert-control rule in `keyboardia`'s and `pythonbyexample`'s PR templates, and `sunrise` Lesson 36.
- **Prove a "pre-existing failure" on a clean base**, in an isolated checkout with its own server.
- **Receipts must be reviewable.** Commit a summary or attach it to CI, never cite a local path.
- **Add "CI status: ran / red / not running" to the final report contract.** When CI is dead, local runs are the only evidence, and the report must say so.

### 9. Make lessons durable

- **A lesson or postmortem is not a regression test.** It counts only when its check is committed and runs before deploy. Examples:
  - `slide-maker` Lesson 18 prescribes a navigation smoke that nothing implements, although the regression it describes escaped to production.
  - `geist_fabrik`'s "A Test That Cannot Fail" template has no enforcement, and its oracle helper has 0 callers.
  - Positive cases, where a mechanical guard ended a bug class: a private repo's layered exit-code gate; `agentic-mermaid`'s seed policy; `pythonbyexample`'s generated-drift hook.
- **No silent tier downgrade.** Upgrade mode must inventory deleted or replaced tests by tier. Example: `tasche` Lesson 82 praised SQLite-backed ranking tests (`887c8e3`), and 4 days later an agent's "Improve search test quality" PR (`45cc325`) replaced them with SQL-string asserts. Proposed eval: "clean up this file", where the file contains one real-SQLite test that the agent must keep.
- **Fix by bug family, not by symptom.** After the regression test, grep for the bug's shape. `keyboardia` turned 4 bugs into 13 this way.
- **Retract the guidance you replace**, in the project doc that recommended it.

### 10. New reference: `references/llm-and-skill-evals.md`

The portfolio has the material, and the skill has no page for it. Route to the new reference from the matrix and from `differential-testing.md` ("approximate/probabilistic output"). Contents:

- **Arms and statistics**
  - Paired with-skill / without-skill / previous-version arms; report lift, not pass rate. Templates: `cfdoctor` three-way with sign-flip p-values and bootstrap CIs; this repo's receipts.
  - Repeat runs: n=1 findings were refuted at n=5 in the harness's 10-skill study.
  - Tune, holdout and holdback splits; leakage lint.
- **Saturation**: saturation means the eval is broken, not green. Examples:
  - 25 of 63 of this repo's development evals are saturated;
  - `guardrails-skill` scored 1.0 in every arm;
  - `anti-slop-writing`'s holdout reads 15/15.
- **Oracle strength ladder**: executed or rendered-artifact oracles, then scoped regex, then keyword. Name these keyword-oracle antipatterns:
  - generic alternatives (`contains_any ["run","validation","assert"]`, `"do not"`, `"<!--"`);
  - enum-accepting checks (any severity label passes);
  - vocabulary echo (`swiss-poster`'s oracle rewards the skill's own hex codes);
  - duplicate-grep "second oracles";
  - coverage-by-declaration (`caught_by` never executed).
- **Judges**: judge-only cases kept small and labelled; judge agreement measured.
- **Cost**: cost per unit of lift. Skill arms run at about 5× the tokens (`swiss-poster` 28k vs 5.7k).
- **Harm and triggers**:
  - Over-application ("harm") probes. `anti-slop-writing`'s harm signal (0.2 with vs 1.0 without, n=5) got no follow-up.
  - Trigger evals must not be meta-prompts; use the harness's offline `stub` adapter.
- **LLM pipelines**
  - Replay recorded context bundles as cassettes (`MaintainerBot`).
  - Cap LLM-graded scores with a deterministic heuristic (`pythonbyexample` `--max-delta`).
  - Add grounding checks for generated prose: `oshineye-dev` shipped about 25 hallucinated project descriptions, fixed by hand with no check added.

### 11. Smaller reference additions

| Reference | Addition | Source |
|---|---|---|
| `typescript.md` / `property-based-testing.md` | fast-check global-seed pitfalls. A global seed makes bare `fc.sample` return one draw, and the seed must reach every Vitest project, including the Workers pool. Pair a fixed PR seed with a scheduled rotating seed that promotes counterexamples; a CI seed failure is a finding to pin. Use `fc.date({ noInvalidDate: true })`. Enumerate small finite domains instead of `fc.integer().map(i => arr[i])`. | `keyboardia` c74b19a; `flux-search` c902722; `vaders` cf659ad; `demoscene`; `atlas` samples ~70 of 118 elements per run |
| `typescript.md` / `deterministic-time.md` | Deferred-promise race tests (hold responses, release them in a chosen order) as the replacement for sleep-based async UI tests | `flux-search` `search-races.spec.ts` |
| `python.md` | Strict xfail; test the `requires-python` floor; Hypothesis `from_regex` cost | `python-workers-issues`, `xampler`, `planet_cf` |
| `go.md` | Compile tag-gated tests in CI (`go vet -tags=…`, `go test -tags=… -run '^$'`); `defer` before `os.Exit` in TestMain skips cleanup | `rogue_planet`, `olsen` |
| SKILL.md "Quality beats coverage" | Coverage denominator honesty: set `coverage.include`, or thresholds only see the files tests happen to load. Coverage is configured ≠ enforced. | `demoscene`, `skill_scanner` |
| `mutation-testing.md` | A sabotage kill matrix (neuter one central function; every importing test file must fail) as cheap targeted mutation. Change-witnesses for invariants a no-op satisfies. Committed, executable defect-replay probes. Equivalent-mutant triage (PR #27). | `keyboardia` §22 (6/12 → 0/12 importers surviving); `garten` 0/12 → 12/12; `keyboardia` Stryker: 7/7 survivors were equivalent |
| `exhaustive-testing.md` | Issue #22: per-cell cost is a feasibility criterion, and verify at the layer that decides the property. Still open, and not covered by PR #27. | `agentic-mermaid` 1,440 → 250 render calls, 75 s → 18 s |
| `test-types.md` Smoke | A smoke test must touch the core dependency (open the DB, run a query), not just `--help`. It must also check the live version is current. | `olsen`, `agentic-mermaid` |
| `test-types.md` | A realism ladder for platform-SDK wrappers (static → local runtime → realistic data → deployed); verification for content/data repos (the SUT is corpus plus gates, and the gate scripts get the unit tests); experiential quality (games, audio, visual taste) needs scheduled, receipted human review, not pinned numbers | `xampler`; two private repos |
| `doc-sync-testing.md` | Verification claims in project docs (test counts, script names, lane counts, `last_verified`, CLAUDE.md claims, SKILL.md frontmatter limits) | `pythonbyexample` 54 vs 31; `keyboardia` TESTING.md; `guardrails-skill` CLAUDE.md; `audit-skill` description is 1,064 characters |

### 12. This repository's own verification and research hygiene

The group review of skill repos ran this repo's gates: `check-all.py` passes, taking 513 s on the loaded machine. CI on `main` has passed 15/15 runs, with 0 re-runs. It is the only repo in the portfolio that tests its oracles from both sides and mutation-tests them. Its receipts are honest about limits. Remaining issues:

- **`evals/evals.json` is dead but advertised.** Every gate reads `skill-development/evals/evals.json` (63 cases). The 12-case top-level file, last touched 2026-05-19, is referenced only by `README.md:126`. Archive it, or delete it and fix the README.
- **Harness pins contradict each other.** `evals/shared-harness.md:12` installs `@v0.3.0`, while the manifest declares `>=0.4.0`. v0.3.0 validates these manifests but has no ablation materialization. Pin `==0.6.0`, and add the model-free gate the harness documents (`skill-benchmark validate --strict-leakage --check-ablations` + `audit-manifest --fail-on-blockers`) to `eval-integrity.yml`. cfdoctor and keyboardia already do this; this repo does not.
- **A generic keyword oracle in 8 shared cases**: `contains_any ["run","validation","assert"]`. Replace it with scoped checks.
- **Self-scores are at the ceiling.** `score-skill-version.py` is 100/100 and `audit-best-practices.py` is 110/110. Report them as regression guards, not quality scores. Record lift and token cost for new guidance: PR #25 shipped on a panel where both arms passed 23/24 cells, at about 5× the tokens.
- **Correct the April research doc** ([below](#corrections-to-lessons_from_adewale_reposmd)). Downstream agents read it as instructions: `planet_cf` codified its "measure assertion density" takeaway into a quota the day after it was published.
- **Help consumers.** Suggest that repos record which skill version they applied, and ship an audit-record template plus a starter set of checker rules. `keyboardia`'s `test-quality-analyzers.ts` (always-green patterns, vacuous property guards, empty tables, self-skips) is a ready-made rule set. Two keyboardia sessions could not reach this repo and had to work from an in-repo copy.
- **Open work to finish**: issue #22 (verify at the deciding layer) and `keyboardia`'s unfiled test-linkage draft.

---

## What is working well across projects

- **Fix discipline is real.** Of the ~1,191 fix-type commits in public repos since 2025-03, 66% touched a test file. Examples:
  - `demoscene` 15/15;
  - `agentic-mermaid` 89%;
  - `vaders` 89%;
  - `keyboardia`, rising from 57% in Dec–Jan to 82% in Jul–Sep.

  PR templates in `keyboardia`, `pythonbyexample` and `agentic-mermaid` require revert-control evidence.
- **Verifying the verifier is spreading.** Examples:
  - `geist_fabrik` meta-tests its coverage and acceptance gates; its verifier had silently dropped 41% of criteria.
  - This repo has oracle self-tests and mini-repo mutants.
  - `skill-eval-harness` has CF.1–CF.4.
  - `aha` has shrink-only test-quality ratchets.
  - `agentic-mermaid` has sabotage worktrees and a lint "teeth" self-test.
  - `keyboardia` has a sabotage kill matrix.
  - `garten` has defect replay, `cfdoctor` near-miss fixtures, and `slide-maker` a two-sided gate check.
- **Real runtimes where they exist.** Examples:
  - workerd via `vitest-pool-workers`: `keyboardia` 134 integration tests including a stateful fuzz with DO eviction; `yaket`, `demoscene`, `bobbin`.
  - `pywrangler dev` in CI: `pythonbyexample`, `python-workers-issues`.
  - Real SQLite from migrations: `sunrise`, `planet_cf` migrations.
  - `agentic-mermaid` tarball-consumer fuzz on Node 22/24.
  - `geist_fabrik` installed-wheel semantic smoke.
- **Property-based testing with independent oracles is mature.** Examples:
  - `geist_fabrik`'s stateful vault model, with a shadow model and a passive read-only commit oracle;
  - `pythonbyexample`'s valid-domain frontmatter generator;
  - `flux-search`'s state-machine invariants I1–I13;
  - `tasche`'s conservation, idempotence and monotonicity properties.
- **Honest verification documentation.** Examples:
  - `agentic-mermaid`'s per-gate "Runs / Does not prove" table and "Honest gaps" list;
  - `xampler`'s 0–5 realism ladder;
  - `cfdoctor`'s labelled proxies;
  - `claude-history-explorer`'s "record could-not-run" release rule;
  - this repo's evidence-limited receipts.
- **Evidence-based pruning.** Examples:
  - `agentic-mermaid` replaced a 4,500-render matrix with an independently checked 1,047-row portfolio, and retired broad mutation on run data;
  - issue #22 cut 1,440 render calls to 250;
  - `keyboardia` deleted a 980-line in-memory Durable Object double in favour of real workerd.
- **Audits turn into gates.** Examples:
  - `pythonbyexample` §5 decorative gates became tested failing checks;
  - `keyboardia` PR #68 added 5 blocking meta-gates;
  - `bobbin` `7aa6da3` made E2E blocking against a seeded local fixture, and the first real run found a mobile bug.
- **Result contracts beat retries.** `keyboardia` lanes assert exact expected, skipped and `flaky=0` counts plus test identities, so a dropped or renamed test cannot hide behind a stable count.

## What is not working well across projects

1. **Gates that don't run, and nobody notices** (see §2 above). This is the most frequent finding, in about 20 repos.
2. **Gates that cannot go red.**
   - `olsen` ran under `|| true` for about 8 months.
   - `planet_cf` has three: the secrets scan, the migration step and E2E.
   - `skill_scanner`'s self-scan and coverage gate.
   - `agentic-mermaid`'s deploy skip.
   - `keyboardia`'s fail-open audio lane and a receipt check that verifies 0 receipts.
   - Warning-only expiries get ignored: `cfdoctor` has been overdue since 2026-09-08, and `pythonbyexample` will fail every PR from 2026-12-01.
3. **Advisory-forever gates.**
   - `vaders` has kept its density audit as `continue-on-error` since April.
   - Of the four mutation setups (`olsen`, `garten`, `yaket`, `aha`), none can fail on its own.
   - `rogue_planet` runs gosec, Trivy and Codecov as `continue-on-error`.
4. **Production inside the test suite.**
   - `flux-search`'s `npm test` includes 9 files that call the production Worker.
   - `keyboardia` still has a CI-only Vite proxy to the production Worker.
   - `atlas` CI E2E depends on Google Fonts.
5. **Contention-sensitive suites and timeout ratchets** in 6 repos (see §7 above). Multi-agent development on shared machines makes this worse.
6. **Agent-era coupling smells** (§4): source-text tests, YAML-text tests, hash pins, facade E2E, and 259 `waitForTimeout` calls in `atlas`.
7. **Mock fidelity that encodes belief.** Seen in `tasche`, `good-pr`, harness Jetty, `cfboundary` identity fakes, `bobbin` missing bindings, and `sunrise-deploy`'s yes-man D1 (the upstream template fixed this; the fork has not).
8. **Lessons written and then undone or never enforced**: `tasche` 45cc325, `geist_fabrik` template, `slide-maker` Lesson 18, `keyboardia` Lesson 16, `yaket` audit's parity-lane recommendation.
9. **Copy-paste fleet scaffolding drifts.**
   - `check_install_boundary.py` is byte-identical in 11 repos.
   - One pin to a non-existent tag (`astral-sh/setup-uv@v9`) broke Ruff in 3 repos in the same minute on 2026-07-26; PR CI caught it each time.
   - Harness `main` would break all 8 consumer manifests in the skills group on its next release (unreleased `should_trigger` requirement). No job validates consumers.
10. **Eval suites that don't discriminate.**
    - Keyword oracles are rated "strong" by the harness.
    - Saturation is widespread: 5 of 10 skills in the harness study; 25 of 63 cases here.
    - Evals run manually only.
    - `good-pr`'s with-skill arm mounts a nonexistent path while `validate` says OK.
11. **Push-to-main or long-lived-branch workflows with no PR gate** let red land and stay red. Where CI data was available, PR-based repos kept every failure off `main`.

---

## How and why each project should change

Priorities: **P0** = the repo currently believes something false about its verification; **P1** = a high-value gap; **P2/P3** = hygiene. "Why" cites the evidence. Six private repositories are omitted here and were reported to the owner separately.

### Large applications and libraries

| Project | What verifies it today | Change (priority): why |
|---|---|---|
| **keyboardia** | 5,070 Vitest unit tests; 319 `fc.assert`; 134 workerd integration tests; 8 Playwright lanes with exact result contracts; CI-rendered visual baselines; blocking AST test-quality gates | **P0** Make the offline-audio lane fail closed (`import('node-web-audio-api').catch(()=>null)` + `skipIf` in 3 files) and make `verify-receipts.mjs` fail on 0 receipts: required lanes can be green while running nothing. **P1** Delete the CI-to-production proxy in `vite.config.ts`: any `CI=true` Playwright run would mutate production. **P1** Move meta-verification and heavy renders out of `test:unit`, then lower `testTimeout` from 30 s: at load 20–30 there were 14 timeouts, 0 alone. **P1** Make `createSessionWithRetry` (112 sites) retry only transport errors and 429, and retract Lesson 16: 5xx retries bypass `flaky: 0`. **P2** Install `@vitest/coverage-v8` or delete the thresholds; schedule Stryker with an equivalent-mutant allowlist. **P2** Add AGENTS.md; generate TESTING.md counts from `lane-contracts.json`. |
| **agentic-mermaid** | 7,553 tests, 0 mocks; differential, metamorphic and combinatorial conformance; sabotage worktrees; Stryker (break 90); MCP conformance; tarball fuzz; staged deploy with rollback | **P0** The deploy gate warns and skips green when the version isn't on npm. 0.4.2 was never published, so the live site has been stale since 07-31. Fail instead, and add a scheduled live `gitSha` freshness check. **P1** Move wall-clock `elapsedMs` budgets (89 uses) to a timing lane and lint them. **P1** Bun stdio MCP hang (3 of 8 manual runs): add a stress lane, report it upstream, document Node as the supported runtime. **P1** Replace the 525 literal YAML asserts with parsed invariants. **P2** Golden approvals should be independent of the authoring agent. **P3** Clean up 64 leaked temp dirs per run. |
| **geist_fabrik** | 1,538 unit + 185 integration tests on 3 OS/Python legs; branch gate 70% (at 71.1%); stateful Hypothesis; 147 AUTO acceptance criteria; release-the-tested-bytes | **P0** Enforce "a test that cannot fail" with an AST meta-test, and port the 41 loop-only geist tests to `assert_valid_suggestions` (0 callers): dead geists stayed green for months. **P1** Schedule the real-model, slow and benchmark tiers, which run nowhere. **P1** Replace workflow string tests with actionlint + a release dry-run; they missed two release bugs. **P2** Ratchet the MANUAL acceptance count (84, 36%). |
| **tasche** | 1,243 pytest (72 `@given`); 241 Vitest; mock-fidelity tests. 126 Playwright/axe and 35 staging E2E tests are manual | **P0** Record real D1 responses and fix MockD1: its "fidelity" test asserts `changes == 1` for a no-match DELETE, which production code contradicts, so the 409 path is unreachable. **P0** Restore the SQLite bm25 tests removed in `45cc325`. **P1** Put `agent-tools/check_*.py` in `make check`, and run `verify-staging` nightly. **P1** Fail the smoke test on `"error"` health. **P2** Replace `test.skip()`-on-failure with capability probes; add a CLAUDE.md Testing section. |
| **planet_cf** | 1,426 pytest; 159 `@given`; 87.7% branch coverage; migrations run against real SQLite | **P0** `e2e.yml` never deploys the commit it tests and is green without secrets. **P0** The migration step swallows every error. **P0** Use `detect-secrets-hook`: `scan --baseline` absorbs new secrets. **P1** Fix or delete the orphaned Vitest suite (10/27 red). **P1** Replace the `from_regex` property that fails `too_slow` under coverage. **P2** Amend Lesson 31 (no density quota); pin `ty`. |
| **bobbin** | 867 workers-pool tests + 68 node tests; 27 fast-check files; blocking E2E against a seeded local fixture (35/35) | **P1** Add interface-faithful AI and Vectorize bindings: semantic search has no test path (open since the June audit). **P1** Seed the scale tests and give them a slow project; they time out with unseeded `Math.random`. **P2** Schedule `alerts:production` and `health:production`. |
| **atlas** | 644 Vitest; fast-check; budgets; SEO checks; Playwright desktop + 1 mobile spec | **P1** Replace 259 `waitForTimeout` (~391 s of sleep) with condition waits. **P1** Keep one visual system, with Linux baselines in CI: 43 of 79 fixes are layout/visual bugs and that tier never runs in CI. **P1** Serve fonts locally in tests. **P2** Replace the vestigial mock-contract spec with a node-canvas vs Chromium parity check. **P2** Enumerate all 118 elements instead of sampling. **P2** Add planted-violation tests for the `lint-*` scripts. |
| **pythonbyexample** | 227 unittest; Hypothesis; 13 editorial gates; byte-exact verification of all 109 examples; `pywrangler dev` + Chrome in CI; lock parity | **P1** Replace CSS/JS source-substring tests (14 of 17 agent-added) with computed-style checks in the existing CDP test. **P1** Make `make deploy` run `smoke_deployment.py`. **P2** Warn 30 days before waiver expiry: CI fails on every PR from 2026-12-01. **P2** Fix stale doc claims (54 vs 31 tests; the deleted fixture script). |
| **aha** | Go tests; rapid + native fuzz; fault-injection sweep; `internal/testquality` ratchets; MCP conformance | **P1** Require all 8 conformance legs in CI (`AHA_MCP_REQUIRE_ALL_LEGS=1`): 5 skip and the step still exits 0. **P1** Make the fuzz drift guard bidirectional. **P2** Turn the corpus-missing skips into `t.Fatal`; run a nightly mutation baseline on the 5 critical packages. |
| **flux-search** | ~120 `fc.assert`; state-machine invariants; node:sqlite D1; deferred-promise race E2E (manual) | **P1** Move the 9 live-production files out of `npm test` into a post-deploy `live` project: PR CI tests production, not the PR. **P1** Use one timeout budget for CI and local runs: default local gives 9 timeouts, CI settings 0. **P2** Run Playwright in CI against `wrangler dev` with Linux baselines. **P2** `ngram-cases` logs instead of asserting. |
| **vaders** | 2,607 tests; fast-check; Playwright; density audit (advisory) | **P1** Add a `vitest-pool-workers` lane for DO alarms and hibernation: 5 fixes needed mock widening. **P1** Typecheck every workspace (client-core has 20 errors). **P2** Run a PR E2E smoke with state waits; size PBT timeouts to `numRuns`. **P3** Replace the density audit with a blocking weak-sole-assertion check. |
| **rogue_planet** | Go tests with `-race`; real-feed `testdata/` snapshots; network tests behind a build tag | **P1** Run `go vet -tags=network ./...` in CI and fix `crawler_live_test.go:70`, which has not compiled since 2025-11-02. **P2** Inject a clock instead of the ±20% jitter tolerance. **P2** Delete the fake `test-integration` target. |
| **olsen** | Go tests (CGO SQLite, DNG fixtures); Makefile; gremlins weekly | **P1** Seed facet, lifecycle and engine tests from `PhotoBuilder` fixtures, and fail CI if they skip (18 skip today). **P1** Compile and run the LibRaw-tagged tests in the existing `build-raw` job. **P2** Give gremlins thresholds; fix TestMain cleanup; make the smoke test open the DB. |
| **yaket** | 238 Vitest; `vitest-pool-workers` lane; Python differential parity | **P1** Run all Python parity files in CI, pin the upstream reference, and add parity to `release.yml` (the audit asked for it). **P2** Move package-smoke out of Vitest: it runs `tsc` inside a 5 s test. **P2** Schedule Stryker so `break: 85` means something. |
| **garten** | 981 tests; mock-contract tests against real Chromium; Stryker (`break: null`) | **P1** Commit the 12 defect-replay probes as an executable script. **P2** Set a Stryker `break`. **P3** Pin the browser revision. |
| **demoscene** | 114 unit + 56 workerd tests; fast-check; Playwright; **no CI** | **P0** Add CI running `test:fast` and gate `deploy` on it; nothing enforces a good suite. **P1** Add non-empty preconditions to the layout invariants; generate Linux baselines. **P2** Set `coverage.include: ["src/**"]`, since the 90% threshold ignores unloaded entrypoints. **P3** Exclude tests from jscpd. |
| **claude-history-explorer** | 348 pytest on 3 OSes; 47 Vitest; golden-URL bridge tests | **P1** Schedule `npm audit` and block only on production-high; bump hono. Blocking audit is red today with no code change. **P1** Make a missing golden fixture fail in CI. |
| **sunrise** / **sunrise-deploy** | workerd D1 from migrations; browser project; `verify` script; no CI | **P1 (sunrise)** Add a workflow: strangers fork and deploy this template. **P1 (sunrise-deploy)** Merge upstream 0.2.0 (21 commits behind, still on the yes-man fake D1) or mark it frozen. **P2** Add a doc-sync test for `sunrise.version.json` (0.1.0) vs `package.json` (0.2.0), which agents are told to read. |

### Smaller services and tools

| Project | Change (priority): why |
|---|---|
| **skill_scanner** | **P1** Point the CI self-scan at committed malicious and benign fixture skills; today it scans 0 skills and exits 0. Add a lower bound to the self-scan test. **P2** Run coverage in CI: the 80% floor is never measured, and branch coverage is 78%. |
| **cfboundary** | **P1** Add a real-Pyodide-in-Node tier (seconds, no credentials). 100% coverage is measured against identity fakes, and real Pyodide drops `None` dict keys from JSON. **P2** Remove the fake-only `except TypeError` branch. **P3** Exclude `testing/fakes.py` from coverage. |
| **xampler** | **P0** `requires-python >=3.12` is false (12 import errors on 3.12): fix the metadata or add a 3.12 leg. **P1** Run `verify_examples.py` for 3–5 examples in CI: the "realism 4" claims rest on manual runs. **P2** Move the CLI fuzz to Hypothesis. |
| **cfdoctor** | **P2** Make CI call `npm test` (the command lists have drifted) and drop the duplicate install-boundary workflow. **P2** Make an overdue evidence review fail; it has warned since 09-08. **P3** Commit only `latest.md` eval reports. |
| **python-workers-issues** | **P1** Use strict xfail, or remove the xfail for resolved issues: a regression reports green today. **P2** Give every directory the warm-up/timeout the `2-` directory gets (cold run: 2 errors). **P3** Run lint in CI. |
| **MaintainerBot** | **P1** Replace `scripts/test-rejections.mjs`, which imports nothing from `src/`, with a real test. **P1** Golden-test the deterministic pipeline from stored context bundles; 2 of 56 functions in `daily.ts` are tested. **P2** Let deep-verify run `uv`/`make` so it can verify the Python repos it audits. |
| **embed.oshineye.dev** | **P1** Add a ~10 s CI job (Vitest 136, Python 10, a fixed `tsc`); these embeds are live on third-party pages. **P2** Restore Playwright `webServer`; Linux baselines. **P3** Add the hooks the vendored guardrails skill promises, or remove it. |
| **oshineye-dev** | **P2** Run the existing `typecheck` in CI. **P2** Add a grounding check (or checklist) for generated project copy: about 25 hallucinated descriptions shipped. |
| **lempicka** | **P3** Scripts exit 0 on failure (`.catch(console.error)`); import the shipped prompt instead of copies. Otherwise proportionate. |
| **web2kindle** | **P3** Delete the scaffold test (it can't start and asserts "Hello World!"), or replace it if the fork is maintained. |
| **cf-workers-design-system** | **P2** Validate `manifest.json` against its own published JSON Schema before deploy; agents consume it. |
| **fibonacci_durable_object**, **pi-comfort**, **next-starter-template**, **wwwoshineye**, **adewale** | Proportionate as they are. Optional: a `check` script (types + `deploy --dry-run`) for the DO demo; make `pi-comfort`'s test portable (it hard-codes a Homebrew path). |
| **livecore** (fork) | The CI "Test" step runs 0 tests; don't read it as evidence. |

### Skills and eval tooling

| Project | Change (priority): why |
|---|---|
| **testing-best-practices** | See [§1](#1-stop-shipping-guidance-the-portfolio-refuted-small-edits-highest-leverage), [§12](#12-this-repositorys-own-verification-and-research-hygiene) and the [corrections](#corrections-to-lessons_from_adewale_reposmd). |
| **skill-eval-harness** | **P0** Collect every test in CI (pytest, or a parity guard): 56 cases have never gated a merge. **P0** Add a downstream-consumer job over `all-manifests.txt`. `main` fails `validate` on 8 of 8 consumer manifests because of an unannounced `should_trigger` requirement; put it in the CHANGELOG with a migration. **P1** Make `validate`, `prepare` and `audit-manifest` agree on `skill_paths`. **P1** Re-tier lexical oracles (not "strong"); add per-assertion pass/fail examples checked offline. **P2** Schedule the live smokes; repair `skill-pins.json` so it reproduces the evaluated trees. |
| **anti-slop-writing** | **P0** Turn the over-application finding (0.2 with vs 1.0 without) into a replicated case with checked-in pass/fail examples. **P1** Install `skills-ref` in CI or fail when it is absent (the validator silently skips); add the harness gate and `should_trigger`. |
| **swiss-poster-skill** | **P1** Oracle self-tests (known-good passes, defective fails), run in CI with Chromium. **P1** Separate compliance oracles (vocabulary echo) from outcome oracles and report lift on outcomes only. **P2** Infrastructure errors must not score as FAIL; add a token-budget case. |
| **slide-maker** | **P0** Implement Lesson 18's navigation smoke per PR, gate the Pages deploy on `verify`, and remove the `goto().catch(() => {})` calls: the Slidev regression escaped to production. **P1** Make gate-check run the declared catchers: per-PR recall is 0/4. Pin the theme versions. **P2** Unit tests for deck-lint rules; delete the tracked `.pyc`. |
| **good-pr** | **P0** Revert `skill_paths` to `skills/good-pr/SKILL.md`: the with-skill arm mounts a nonexistent file. Test it with the real harness `prepare`. **P1** Pin the harness `==0.6.0`, and run `validate --check-ablations` in CI. |
| **good-repo** | **P1** Add `should_trigger` and the harness gate; retire the duplicate grader. **P2** Reuse the harness's fence-aware link checker. |
| **good-readme** | **P1** Add the harness gate; use scoped regexes instead of generic keywords; make the fixture oracle execute the corrected commands. |
| **guardrails-skill** | **P1** Fix CLAUDE.md, which claims no tests or CI; enforce the line budget (SKILL.md is 260 lines against a stated ~250 limit); schema-check `hooks.json`. **P2** A headless hook-fires-and-blocks probe; "tests were run" enforced by an LLM reading the transcript is an attestation, not a test. |
| **audit-skill** | **P0** Delete or regenerate the committed `.skill` bundle, a stale full-repo snapshot outside the install-boundary check, and extend the boundary check to `*.skill`/`*.zip`. **P1** Shorten the 1,064-character description (the spec limit is 1,024); bind the severity oracle to the expected verdict. |
| **python-workers-skill** | **P1** Parse or compile the ~2,300 lines of code-bearing references in CI; enforce `last_verified` freshness. It predates all 5 upstream-expert corrections. |
| **cf-advisor-skill** | **P3** Archive it, or add a banner pointing to cfdoctor. |
| **Fleet-wide** | Package `check_install_boundary.py` (11 copies) as a harness subcommand or a reusable workflow. Let Dependabot/Renovate own action pins (`setup-uv@v9` broke 3 repos at once). Record the skill version each repo applied. |

---

## Corrections to LESSONS_FROM_ADEWALE_REPOS.md

Verified 2026-09-26 against the repositories' current state and history:

| April claim | Correction |
|---|---|
| tasche coverage "pytest-cov, branch=true" | Never configured in any version. |
| tasche mock-fidelity covers "R2 list pagination" and "MockQueue message storage" | No such tests exist. One fidelity test contradicts production (`changes == 1` for a no-match DELETE). |
| geist_fabrik PBT "--"; planet_cf PBT "--" and "Playwright" | Both had Hypothesis before April (geist_fabrik since 2026-03-14; planet_cf 117 `@given`). planet_cf's browser tier is agent-browser, not Playwright. |
| geist_fabrik conditional `sys.modules` stub injection keyed on `-m` | Replaced 2026-09-08 (`c163c34`) by a marker-driven session patch that refuses mixed sessions. |
| skill_scanner "Security tools should scan themselves"; `fail_under = 80` | The CI self-scan finds 0 skills; the coverage floor is never run in CI (branch coverage is 78%). |
| rogue_planet network tests behind build tags (praised) | They have not compiled since `65d22f3` (2025-11-02); gated tests must be compiled in CI. |
| atlas mock-contract tests (praised) | The mock was deleted on 2026-04-03 in favour of node-canvas; the contract now guards nothing. |
| Takeaway #7 "Visual regression tests belong in local dev, not CI" | Refuted by keyboardia: suites skipped in CI ran zero times. Render baselines on the CI image. |
| Takeaway #3 "Measure assertion density" | Became quotas downstream (planet_cf Lesson 31). Use it as a triage signal only. |
| tasche/planet_cf "E2E against real infrastructure" | tasche's is manual only; planet_cf's does not deploy the commit under test. |

---

## Appendix: numbers

**Portfolio history since 2025-03-26** (non-merge commits; 47 public repos). "Fix" means the subject matches fix/bug/regression/hotfix; "touched a test" means one or more changed paths match a test-file pattern.

| Metric | Value |
|---|---|
| Commits | 5,094 |
| Commits with agent authorship or trailer (lower bound) | 3,177 (62%) |
| Fix-type commits | 1,191 |
| …that touched a test file | ~789 (66%) |
| Commits touching `.github/workflows` | 361 |
| Flake-titled / skip-or-disable-titled / revert commits | 37 / 18 / 22 |

**Largest public repos**: commits (agent % / fix-with-test %):

| Repo | Commits | Agent % | Fix commits | Fix touched test % |
|---|---|---|---|---|
| keyboardia | 925 | 70 | 294 | 75 |
| agentic-mermaid | 758 | 42 (+ untrailered Codex) | 162 | 82 |
| geist_fabrik | 476 | 88 | 149 | 62 |
| bobbin | 248 | 76 | 60 | 57 |
| atlas | 241 | 95 | 97 | 46 |
| pythonbyexample | 188 | 47 | 19 | 68 |
| aha | 183 | 42 | 24 | 71 |
| flux-search | 183 | 73 | 35 | 77 |
| tasche | 168 | 99 | 54 | 74 |
| planet_cf | 150 | 97 | 47 | 55 |
| vaders | 138 | 99 | 64 | 89 |

**Fresh-clone suite runs** (loaded 4-CPU machine; "load" = timeout that passes alone):

| Repo | Result |
|---|---|
| keyboardia | unit 5,055/5,070 (14 load timeouts, 0 alone); workerd integration 134/134; static gates pass; coverage unrunnable |
| agentic-mermaid | 7,502 pass / 5 fail / 1 error in 31 min (3 load timeouts, 1 no-IPv6 sandbox, 1 Bun stdio hang) |
| geist_fabrik | 1,525 + 174 pass; branch 71.1%; 147/147 acceptance criteria |
| tasche | 1,243 pytest + 241 Vitest pass |
| planet_cf | 1,426 pass; the CI coverage step fails (Hypothesis `too_slow`); Vitest 10/27 fail |
| bobbin | 867 pass + 5 load timeouts; node 68/68; E2E 35/35 |
| atlas | 631 pass, 1 load timeout; drop-cap E2E needs live Google Fonts |
| flux-search | offline 810/819 with default config, 819/819 with `CI=true` |
| pythonbyexample | 227 + 13 gates + 109 examples pass |
| aha / olsen / rogue_planet | pass / pass (18 skip) / pass, but `-tags=network` does not compile |
| vaders / garten / yaket | 2,607 + 1 load timeout / 981 + 14 E2E / 238 + 1 timeout (fails alone too) |
| demoscene | 114 + 56 pass |
| cfdoctor / cfboundary / xampler | 93 + 30 fixtures / 24 + 5 skip at 100% / 66 on 3.13, import failure on 3.12 |
| skill-eval-harness | unittest 1,286 vs pytest 1,335 (56 never collected by CI) |
| testing-best-practices | `check-all.py` OK (513 s under load); CI on `main` 15/15 green |
| embed.oshineye.dev | Vitest 136/136; `tsc` 127 errors in a dependency's sources; Linux visual 7/7 fail (no baselines) |
| web2kindle | 0 tests (pool-workers cannot host the Workflow binding) |

The history metrics came from a single script over `git log --since=2025-03-26 --no-merges --name-only`. The full per-group review reports, with file:line evidence for every row above, are retained with the owner.
