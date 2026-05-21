# Leading Testing/TDD Skills Comparison

Searches run on 2026-05-20:
- <https://www.skills.sh/?q=tdd>
- <https://www.skills.sh/?q=testing>
- skills.sh sitemaps filtered for `tdd`, `testing`, `test-driven`, `pytest`, `vitest`, `playwright`, `coverage`, `property-based-testing`, and `mutation-testing`.

Install counts are parsed from skills.sh page metadata at search time and should be treated as directional, not permanent rankings.

## Leading software-testing skills found

| Rank | Skill | Installs | Focus | What it teaches us |
|---:|---|---:|---|---|
| 1 | [`mattpocock/skills/tdd`](https://www.skills.sh/mattpocock/skills/tdd) | 135,860 | TDD workflow | Behavior through public interfaces; avoid “horizontal slicing”; one behavior/test slice at a time. Measure red/green evidence and public-contract testing. |
| 2 | [`obra/superpowers/test-driven-development`](https://www.skills.sh/obra/superpowers/test-driven-development) | 91,030 | Strict TDD | “If you did not watch it fail, you do not know it tests the right thing.” Measure command evidence, not claims. |
| 3 | [`anthropics/skills/webapp-testing`](https://www.skills.sh/anthropics/skills/webapp-testing) | 74,855 | Playwright/webapp interaction | Narrow decision tree, helper scripts, recon-then-action. Measure whether agents inspect rendered state and use tools rather than over-reading. |
| 4 | [`currents-dev/playwright-best-practices`](https://www.skills.sh/currents-dev/playwright-best-practices-skill/playwright-best-practices) | 41,187 | Playwright breadth | Activity-based reference matrix, quick decision tree, validation loop. Measure locators, auto-waiting, no hard sleeps, artifacts, CI/flaky handling. |
| 5 | [`microsoft/playwright-cli`](https://www.skills.sh/microsoft/playwright-cli/playwright-cli) | 37,884 | Browser automation/Playwright CLI | Tool-first automation. Measure whether tests use actual browser/tool evidence when relevant. |
| 6 | [`wshobson/python-testing-patterns`](https://www.skills.sh/wshobson/agents/python-testing-patterns) | 20,841 | Python testing | Language-specific depth: pytest, fixtures, mocking, TDD. Measure Python idiom separately from generic testing quality. |
| 7 | [`antfu/skills/vitest`](https://www.skills.sh/antfu/skills/vitest) | 19,349 | Vitest docs/reference | Compact generated/versioned framework reference. Measure framework freshness and API correctness. |
| 8 | [`wshobson/e2e-testing-patterns`](https://www.skills.sh/wshobson/agents/e2e-testing-patterns) | 16,010 | E2E with Playwright/Cypress | E2E-specific reliability practices. Measure scope discipline: few high-value journeys, not every endpoint. |
| 9 | [`wshobson/javascript-testing-patterns`](https://www.skills.sh/wshobson/agents/javascript-testing-patterns) | 13,264 | JS/TS testing | Jest/Vitest/Testing Library integration. Measure framework mismatch and component/user-observable behavior. |
| 10 | [`github/awesome-copilot/playwright-generate-test`](https://www.skills.sh/github/awesome-copilot/playwright-generate-test) | 12,455 | Playwright generation via MCP | Scenario-to-test generation. Measure whether generated tests are maintainable, deterministic, and not just recorder output. |
| 11 | [`supercent-io/backend-testing`](https://www.skills.sh/supercent-io/skills-template/backend-testing) | 11,814 | Backend testing | API/database/auth/business logic tiers. Measure unit/integration/API tier choice and database isolation. |
| 12 | [`supercent-io/testing-strategies`](https://www.skills.sh/supercent-io/skills-template/testing-strategies) | 11,234 | Strategy/test pyramid | Planning and infrastructure. Measure test strategy quality, not just test code generation. |
| 13 | [`github/awesome-copilot/pytest-coverage`](https://www.skills.sh/github/awesome-copilot/pytest-coverage) | 10,397 | Pytest coverage | Cautionary contrast: “increase coverage to 100%” is a proxy risk. Measure mutation/oracle strength so coverage does not dominate. |
| 14 | [`affaan-m/golang-testing`](https://www.skills.sh/affaan-m/everything-claude-code/golang-testing) | 6,832 | Go testing | Go table tests, fuzzing, benchmarks, idioms. Measure Go-specific behavior: `t.TempDir`, fakes, subtests, fuzz, zero values. |
| 15 | [`affaan-m/rust-testing`](https://www.skills.sh/affaan-m/everything-claude-code/rust-testing) | 3,777 | Rust testing | Rust unit/integration/async/property testing. Measure `Result` handling, no arbitrary `unwrap`, proptest, cargo conventions. |
| 16 | [`trailofbits/property-based-testing`](https://www.skills.sh/trailofbits/skills/property-based-testing) | sitemap hit | PBT/security mindset | Measure invariant quality and counterexample discovery, not just generator usage. |
| 17 | [`trailofbits/mutation-testing`](https://www.skills.sh/trailofbits/skills/mutation-testing) | sitemap hit | Mutation testing | Measure whether tests kill mutants/seeded bugs. |
| 18 | [`dotnet` testing skills](https://www.skills.sh/dotnet/skills/code-testing-agent) | sitemap hit | Code generation/assertion/gap analysis | Strong separation of generation, assertion quality, anti-patterns, gap analysis. Measure modes separately. |

Excluded from “software testing leaders” despite high search rank: marketing A/B testing skills, app-store review, finance coverage, and unrelated domain “testing” pages.

## Comparison to our skill

| Dimension | Leading skills | Current `testing-best-practices` |
|---|---|---|
| Scope | Most leaders are narrow: TDD, Playwright, Vitest, Python, Go, E2E. | Broader cross-language meta-skill. Stronger breadth, higher risk of generic advice. |
| Routing | Impeccable/Currents/Vitest-style skills use routing tables and activity references. | Now has a compact router + reference matrix. Comparable structure. |
| TDD evidence | Matt/Obra are stronger and stricter. | Calibrated default with evidence requirement; less dogmatic, better for broad use, weaker for pure TDD enforcement. |
| Framework depth | Vitest/Playwright/Python/Go/Rust-specific skills go deeper. | Covers Python/Go/TS/Rust via references and evals, but less detailed than specialists. |
| Anti-pattern detection | Dotnet and Impeccable provide concrete signals/severity. | Now has static audit + anti-pattern mode, but fewer deterministic detectors than Impeccable/dotnet. |
| Measurement | Most public skills have little visible eval infrastructure. Dotnet skills are strongest on metrics/report shapes. | Stronger than most: 27 evals, taxonomy, static audit, core-language coverage, fixture oracles, eval-health plan. |
| Runtime fixtures | Public skills often include scripts/helpers, especially webapp-testing. | Started: 7 fixture oracles self-test good/bad samples. Needs full candidate-project prompt runner. |
| Eval obsolescence | Rarely explicit in public skills. | Added `evals/eval-health.md` inspired by Wang: saturation/drift/rotating probes. |

## What we should measure because of this comparison

### Core outcome metrics
1. **Red/green evidence**: did the new regression test fail before the fix and pass after?
2. **Bug sensitivity**: does the test kill seeded mutants or hidden bug variants?
3. **Oracle strength**: are assertions behavior-specific, structural/stateful/negative where needed, not merely truthy/not-empty?
4. **Determinism**: no hard sleeps, live network, unseeded randomness, order coupling, or shared global state leaks.
5. **Framework idiom**: pytest/Hypothesis, Go `testing`/`t.TempDir`, Vitest/fast-check/Playwright, Rust/proptest/cargo conventions.
6. **Scope discipline**: no unapproved production architecture/type changes for tests-only tasks.
7. **Tier choice**: unit vs in-process integration vs contract/VCR vs E2E chosen by risk boundary.
8. **Validation honesty**: final answer reports exact commands, results, blockers, and gaps.

### Language-specific metrics
- **Python**: pytest idioms, fixtures, Hypothesis invariants, VCR/recorded fixtures, monkeypatch cleanup, no swallowed exceptions.
- **Go**: table/subtest calibration, `t.TempDir`, purpose-built fakes, zero-value caveats, fuzzing when appropriate, no real network.
- **TypeScript**: Vitest vs Jest API correctness, fast-check invariant assertions, Playwright locators/web-first assertions, MSW vs recorded fixtures distinction.
- **Rust**: `Result` branch assertions, no arbitrary `unwrap`, proptest/cargo idioms, differential/conformance tests for ports.

### Eval-health metrics, per Wang
- Score saturation: if >80% of evals score 4, add harder hidden variants.
- Static/runtime correlation: if static oracles pass but prompt/runtime quality drops, add runtime checks.
- Real-world miss mapping: every escaped failure must map to an eval or create one.
- Framework freshness: source/version review dates for pytest, Hypothesis, Go, Vitest, Playwright, fast-check, Rust/proptest.
- Probe rotation: add/remove rotating evals after model/tool capability shifts.

## Current gap against leaders

We are ahead of most public testing skills on **measurement infrastructure**. We are still behind the strongest specialist skills on **framework depth** and behind webapp-testing/Playwright-style skills on **tool-backed execution workflows**. The next competitive step is not more prose; it is a prompt runner that applies candidate outputs to fixture projects and records command logs in `evals/scorecard.md`.
