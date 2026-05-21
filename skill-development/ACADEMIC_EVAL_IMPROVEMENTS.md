# Academic Literature: Better Rubrics, Evals, Testing, and Skill Assessment

Purpose: identify improvements to make `testing-best-practices` evals discriminate between early/current/local skill versions and remain useful as models change.

## Key literature signals

### Validity and rubric reliability
- **Messick (1995), “Validity of psychological assessment”**: validity is about the interpretation/use of scores, not just the instrument. Applied here: every eval score needs a claim it supports, e.g. “the skill prevents weak PBT oracles,” not a vague “quality” score.
- **Kane (2013), “Validating the interpretations and uses of test scores”**: use an argument-based validity framework: claim → warrant → backing → rebuttals. Applied here: each eval should state its claim, what evidence would support it, and what could invalidate it.
- **Cronbach et al. (1972), Generalizability Theory**: observed scores vary by task, rater, model, prompt wording, and environment. Applied here: run multiple prompt variants/models/judges and estimate where variance comes from.
- **Linacre (1989), Many-Facet Rasch Measurement**: account for item difficulty and judge severity. Applied here: calibrate eval items and judge rubrics; do not trust raw averages when one judge or easy item dominates.
- **Jonsson & Svingby (2007), scoring rubrics review** and **Moskal & Leydens (2000), rubric validity/reliability**: analytic rubrics with clear criteria and exemplars improve reliability. Applied here: add 0/1/2/3/4 anchor examples for each high-value eval.

### Benchmark design and obsolescence
- **Raji et al. (2021), “AI and the Everything in the Whole Wide World Benchmark”**: benchmarks encode assumptions and often overclaim. Applied here: label what each eval does *not* measure.
- **Bowman & Dahl (2021), “What Will it Take to Fix Benchmarking in NLP?”**: benchmarks get saturated and overfit. Applied here: maintain hidden/rotating probes and retire saturated public items.
- **Kiela et al. (2021), Dynabench**: dynamic/adversarial benchmarking finds failures after static sets saturate. Applied here: add new evals from real misses and have reviewers generate adversarial variants.
- **Ribeiro et al. (2020), CheckList**: test behavioral capabilities with minimum-functionality tests, invariance tests, and directional expectation tests. Applied here: convert evals into capability families, not one-off prompts.
- **Liang et al. (2022), HELM** and **Srivastava et al. (2022), BIG-bench**: report broad metrics and scenarios, not single aggregate scores. Applied here: keep per-dimension dashboards for language, technique, and failure mode.

### Code-generation and agent evals
- **Chen et al. (2021), HumanEval / Codex** and **Austin et al. (2021), MBPP**: executable tests are essential but can be narrow. Applied here: fixture oracles are necessary but not sufficient.
- **Liu et al. (2023), EvalPlus**: base tests miss many incorrect code generations; augment with stronger hidden tests. Applied here: add hidden bug/mutant tests to every code-writing fixture.
- **Jimenez et al. (2024), SWE-bench** and **Jain et al. (2024), LiveCodeBench**: use realistic, contamination-aware, time-aware tasks. Applied here: add full mini-repo fixtures and keep future-dated/rotating tasks.
- **Cassano et al. (2022), MultiPL-E**: translate/evaluate across languages. Applied here: keep Python/Go/TypeScript/Rust parity and compare language-specific failure rates.

### Software testing research
- **Inozemtseva & Holmes (2014), “Coverage is not strongly correlated with test suite effectiveness”**: coverage alone is a weak proxy. Applied here: score mutation/seeded-bug detection and oracle strength.
- **Jia & Harman (2011)** and **Papadakis et al. (2019)**, mutation testing surveys: mutation testing estimates fault-detection strength. Applied here: add seeded mutants to fixtures and measure killed mutants.
- **Claessen & Hughes (2000), QuickCheck**: properties test whole input spaces better than examples. Applied here: evaluate invariant quality, not just generator usage.
- **Chen et al. (2018), Metamorphic Testing survey**: when oracles are hard, check relations across transformed inputs. Applied here: prompt/eval metamorphic variants should preserve expected scores under wording/framework perturbations.

### LLM-as-judge and rubric scoring
- **Liu et al. (2023), G-Eval** and **Zheng et al. (2023), MT-Bench/Chatbot Arena**: LLM judges can correlate with humans but are biased and need calibration. Applied here: use blind pairwise comparison, multiple judges, and executable oracles where possible.
- **Prometheus / fine-grained evaluator work (Kim et al., 2023)**: explicit rubrics and reference feedback improve judging. Applied here: add reference rationales and counterexamples to evals.

### Skill acquisition / instruction design
- **Sweller (cognitive load / worked examples)**: instructions should reduce extraneous load and include worked examples. Applied here: keep `SKILL.md` as router; move detail to refs; add good/bad examples for hard traps.
- **Ericsson deliberate practice**: improvement needs targeted feedback on weak subskills. Applied here: eval categories should feed back to skill edits, e.g. “weak on Go zero values” or “weak on VCR drift.”
- **Cognitive task analysis / intelligent tutoring literature**: expert workflows should be decomposed into decision points and common errors. Applied here: make testing decisions explicit: tier choice, oracle choice, determinism, validation.

## Improvements we should add

### 1. Claim-based eval cards
For each eval, add:
- **Claim**: what skill capability this eval supports.
- **Warrant**: why passing this eval supports the claim.
- **Backing**: oracle/static/runtime evidence.
- **Rebuttals**: ways the eval can pass while the skill is still bad.

Example: E05 should not claim “PBT skill is good”; it should claim “the skill avoids weak sole truthy/defined assertions for arbitrary-input parser properties.”

### 2. Item difficulty and discrimination tracking
Add per-eval metadata:
- easy / medium / hard / adversarial,
- expected pass rate,
- discriminates which version(s),
- saturation status.

A good suite should include anchor items plus high-discrimination items that separate first/current/local.

### 3. Hidden and metamorphic variants
For each public fixture oracle, create hidden variants:
- same capability, different wording,
- different framework idiom,
- adversarial distractor from old skill guidance,
- changed file/function names.

Use metamorphic checks: score should remain stable when irrelevant wording changes, and should change when the underlying failure mode changes.

### 4. Mutation-backed runtime fixtures
For Python, Go, TypeScript, and Rust, add tiny runnable projects with seeded mutants:
- sanitizer lets `javascript:` through,
- parser returns malformed error shape,
- scheduler runs early/late,
- Go zero-value invalid state reaches send path,
- Rust parser panics or loses span.

Measure mutant kill rate, not just oracle pattern pass.

### 5. Pairwise blind version judging
For each hard eval, ask a judge to compare first/current/local outputs with version labels hidden. Use:
- pairwise preference matrix,
- reason categories,
- inter-judge agreement if multiple judges are available.

This catches improvements that simple pass/fail oracles miss.

### 6. Generalizability runs
Run each high-value eval across:
- at least 3 prompt variants,
- at least 2 model/settings if available,
- at least 2 judges or judge prompts for subjective dimensions.

Track variance by eval item, model, judge, and skill version. If version effect is small relative to prompt variance, the eval is weak.

### 7. Rubric anchors and counterexamples
For each rubric dimension, add concrete examples of score 0/1/2/3/4. Include:
- bad answer from first skill,
- acceptable answer from current GitHub,
- ideal answer from local,
- deceptively good answer that should fail.

### 8. Saturation dashboard
Extend `score-evals.py` or add `eval-health-report.py` to report:
- evals with 100% pass across all versions,
- evals with no discrimination,
- dimensions with no hard items,
- language imbalance,
- stale references by last-reviewed date.

### 9. Realistic mini-repos
Add SWE-bench-style mini tasks rather than just single-file candidates:
- package config,
- adjacent tests,
- production code with seeded bug,
- runner command,
- hidden tests.

The skill is supposed to make agents inspect context; mini-repos are the only reliable way to measure that.

### 10. Eval-to-skill feedback loop
Every failed or saturated eval should produce one of:
- skill edit,
- reference edit,
- rubric edit,
- oracle hardening,
- retired eval.

No eval should stay in the suite if it cannot influence a decision.

## Priority recommendations for this repo

1. **Add high-discrimination hidden evals** targeting current GitHub's static failures: assertion calibration, PBT weak example, integration external-only mistake, VCR/MSW confusion, unsafe correctness deletion.
2. **Add claim/warrant/backing/rebuttal fields** to `evals/evals.json`.
3. **Add difficulty/discrimination/saturation metadata** and a script to flag saturated evals.
4. **Convert 3–4 fixtures into full mini-repos with seeded mutants**.
5. **Add rubric anchors** for the 10 fixture-backed evals.
6. **Add pairwise blind comparison** over first/current/local outputs for hard evals.

These improvements directly address the observed problem: public fixture prompt oracles scored first/current/local as 10/10, while artifact quality differed sharply. The suite needs more discriminatory behavioral evals, not just more evals.
