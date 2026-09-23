# Cost-Aware, Variable-Strength Combinatorial Test Portfolios

> Primary-source synthesis for issue #21. Research date: 2026-07-22. This file
> records evidence and caveats; the installable decisions live in
> `testing-best-practices/references/combinatorial-testing.md`.

## Research question

How should a coding agent reduce a large interaction space without confusing
systematic tuple coverage with proof of correctness, and without replacing an
expensive Cartesian product with an opaque cost optimizer?

The answer supported by the literature is a layered portfolio:

1. preserve mandatory and repaired-fault regressions;
2. prove exact one-way registry enrollment independently;
3. exhaust cheap finite slices;
4. cover feasible low-order interactions with constrained arrays;
5. raise strength only for named risk groups;
6. prioritize optional rows using explicit cost/risk evidence;
7. validate any reduction against historical faults, mutation/sabotage, and a
   shadow/full-suite holdout before deletion.

## What covering arrays prove

A uniform `t`-way covering array contains every feasible value tuple for every
`t`-factor subset at least once. It proves a property of the **input model**. It
does not prove that:

- the model contains the real triggering factor or value;
- state, order, timing, or continuous input behavior is represented;
- setup reaches the faulty behavior;
- the fault propagates to an observable result;
- the oracle distinguishes correct from incorrect output;
- the generated row count is globally minimum;
- another system has the same interaction-fault distribution.

This distinction is essential when interpreting the historical NIST data.

## Qualification of the “60–90% / 90–99%” claim

`research/NOVEL_TESTING_TYPES.md` previously said “2-way catches 60–90% of
bugs; 3-way catches 90–99%.” No single primary study establishes those ranges
as universal detection probabilities.

NIST SP 800-142 synthesizes retrospective interaction-degree analyses from:

- Kuhn and Okun, “Pseudo-exhaustive Testing for Software” (2006);
- Kuhn and Reilly, “An Investigation of the Applicability of Design of
  Experiments to Software Testing” (2002);
- Kuhn, Wallace, and Gallo, “Software Fault Interactions and Implications for
  Software Testing” (2004);
- Wallace and Kuhn, “Failure Modes in Medical Device Software: an Analysis of
  15 Years of Recall Data” (2001).

Its Figure 2 plots cumulative interaction degree for medical-device, browser,
server, and NASA distributed-database fault corpora. The report gives one exact
example: in the NASA application, 67% of observed failures were triggered by a
single parameter value, 93% by interactions of at most two values, and 98% by
interactions of at most three. It says the studied curves reached 100% at four
to six factors, while explicitly calling the results “not conclusive.” Its
executive summary also says pairwise testing “may miss 10% to 40% or more of
system bugs.”

These are cumulative classifications of **observed historical failures in the
studied systems**. They are not controlled estimates that any generated
pairwise or 3-way suite will detect the same proportion of latent defects.

Defensible wording is therefore:

> Empirical studies of several historical fault corpora found that many
> observed failures involved relatively few factors, but distributions varied
> by system. Covering arrays guarantee specified modeled interactions, not a
> universal defect-detection percentage.

## Primary-source literature table

| Topic / source | Systems or material | Reported result | Caveat | Practical implication |
|---|---|---|---|---|
| Kuhn, Wallace & Gallo, “Software Fault Interactions and Implications for Software Testing,” IEEE TSE 30(6), 2004, [DOI 10.1109/TSE.2004.24](https://doi.org/10.1109/TSE.2004.24) | Historical failures from several domains, combined with related NIST corpora | Studied failures were triggered by relatively few conditions; maximum observed interaction degree was low enough to motivate pseudo-exhaustive `t`-way testing | Retrospective observed faults; reconstructed factor models; heterogeneous domains; not a generated-suite detection experiment | Use local fault history to choose strength; do not promise a portable catch rate |
| Kuhn, Kacker & Lei, *Practical Combinatorial Testing*, NIST SP 800-142, 2010, [DOI 10.6028/NIST.SP.800-142](https://doi.org/10.6028/NIST.SP.800-142) | Synthesis, tutorials, configuration/input/sequence examples | NASA example: cumulative 67% one-way, 93% two-way, 98% three-way; all studied curves reached 100% by four to six; pairwise may miss 10–40% or more | Secondary synthesis; report itself says evidence is not conclusive; abstracted factor values and oracle still matter | Cite for terminology and scoped historical evidence, not universal percentages |
| Cohen, Gibbons, Mugridge & Colbourn, “Constructing Test Suites for Interaction Testing,” ICSE 2003, [DOI 10.1109/ICSE.2003.1201186](https://doi.org/10.1109/ICSE.2003.1201186) | Covering-array construction problems | Defines mixed-level and variable-strength objects and evaluates heuristic construction approaches | Primarily construction size/cost, not real-fault yield; heuristics do not imply global minima | Practical generators produce smaller valid suites; report algorithm and resulting size honestly |
| Cohen et al., “A Variable Strength Interaction Testing of Components,” COMPSAC 2003, [DOI 10.1109/CMPSAC.2003.1245373](https://doi.org/10.1109/CMPSAC.2003.1245373) | Variable-strength covering-array benchmark objects | Defines arrays whose interaction strength differs within one suite and gives construction methods/initial bounds | Initial algorithmic evidence, not proof that every elevated group finds more real defects | Use a broad base strength and elevate only named risk groups |
| Bryce & Colbourn, “Prioritized Interaction Testing for Pair-wise Coverage with Seeding and Constraints,” Information and Software Technology 48, 2006, [DOI 10.1016/j.infsof.2006.03.004](https://doi.org/10.1016/j.infsof.2006.03.004) | Pairwise construction benchmarks with seeds and constraints | Develops prioritized coverage so important interactions can appear earlier while incorporating seeds/constraints | Priority assignments may be subjective; improved prefix coverage is not automatically improved real-fault detection | State what is prioritized and assess prefixes at equal execution budget |
| Huang et al., “Prioritizing Variable-Strength Covering Array,” COMPSAC 2013, [DOI 10.1109/COMPSAC.2013.84](https://doi.org/10.1109/COMPSAC.2013.84) | Variable-strength interaction suites and algorithmic comparison baselines | Proposes two heuristics specialized for ordering variable-strength suites; the reported experiments outperformed generation-order, random, and fixed-strength prioritizers on their coverage-oriented measures | Tests ordering/early coverage, not real-fault probability; benchmark transfer and assigned importance remain concerns | Variable-strength obligations and execution order are separate decisions; evaluate early coverage under the real budget |
| Zhang, Sui & Gong, “Large Scale Software Test Data Generation Based on Collective Constraint and Weighted Combination Method,” Tehnicki Vjesnik 24(6), 2017, [DOI 10.17559/TV-20170319045945](https://doi.org/10.17559/TV-20170319045945) | Four experiment groups using usage-model probabilities and Java Pathfinder coverage | Generates representative weighted input combinations; authors report better fit to modeled usage and better internal code coverage than compared data sets | Usage-frequency fit and code coverage are proxies, not interaction guarantees or fault detection; only four experiment groups | Usage weights may guide optional sampling/repetition, but must not erase mandatory feasible tuples |
| Cohen, Dwyer & Shi, “Constructing Interaction Test Suites for Highly-Configurable Systems in the Presence of Constraints,” IEEE TSE 34(5), 2008, [DOI 10.1109/TSE.2008.50](https://doi.org/10.1109/TSE.2008.50) | Four real highly configurable systems plus synthetic models | SAT-assisted greedy techniques reduced constrained generation cost to about 30% of widely used unconstrained methods in their evaluation without degrading solution quality | Result concerns generation cost/array quality for those models, not defect probability | Integrate constraints during generation; do not generate then delete invalid rows |
| Yılmaz, “Test Case-Aware Combinatorial Interaction Testing,” IEEE TSE, 2013, [DOI 10.1109/TSE.2012.65](https://doi.org/10.1109/TSE.2012.65) | Two widely used highly configurable systems | Test-specific constraints caused masking under traditional arrays; test-case-aware arrays avoided those invalid test/configuration assignments | Configuration validity and test applicability are separate; algorithms trade generation time, configurations, and test runs | Record which tests are valid in each configuration; tuple presence alone may not exercise behavior |
| Demiröz, “Cost-aware Combinatorial Interaction Testing,” ISSTA Doctoral Symposium 2015, [DOI 10.1145/2771783.2784775](https://doi.org/10.1145/2771783.2784775) | Early empirical work on configuration-dependent QA cost | Defines a cost-aware covering array that minimizes a supplied cost function; early studies suggested reductions over equal-cost assumptions | Doctoral/early evidence; simple scenarios; manual cost models were found impractical | Treat cost-aware generation as optional and locally validated, not settled universal guidance |
| Demiröz & Yılmaz, “Towards Automatic Cost Model Discovery for Combinatorial Interaction Testing,” ICSTW 2016, [DOI 10.1109/ICSTW.2016.7](https://doi.org/10.1109/ICSTW.2016.7) | Two widely used configurable systems | Samples configurations, measures a QA task, and fits a generalized linear model to predict unseen configuration cost | Cost depends on runner/environment and can drift; predictive fit does not prove safe test deletion | Build versioned local calibration from representative samples and retain uncertainty/fallbacks |
| Yoo & Harman, “Pareto Efficient Multi-objective Test Case Selection,” ISSTA 2007, [DOI 10.1145/1273463.1273483](https://doi.org/10.1145/1273463.1273483) | Empirical two- and three-objective formulations | Constructs non-dominated subsets over objectives such as coverage, past fault detection, and execution cost | Objectives/proxies can conflict and past detection can bias future selection | Expose a Pareto frontier instead of hiding policy inside one scalar score |
| Elbaum, Malishevsky & Rothermel, “Incorporating Varying Test Costs and Fault Severities into Test Case Prioritization,” ICSE 2001, [DOI 10.1109/ICSE.2001.919106](https://doi.org/10.1109/ICSE.2001.919106) | Case study extending test-prioritization metrics | Introduces a cost/severity-aware rate-of-fault-detection metric and illustrates it in a case study | Requires a known/estimated fault universe, costs, and severities; one metric cannot represent every operational concern | Track cost and impact separately; do not rely on ordinary APFD alone |
| Yoo & Harman, “Regression Testing Minimization, Selection and Prioritization: a Survey,” STVR 2012, [DOI 10.1002/stvr.430](https://doi.org/10.1002/stvr.430) | Survey of regression-testing research | Separates minimization (remove redundancy), selection (change relevance), and prioritization (order for early feedback) | Evidence and goals differ across the three tasks | Do not infer that evidence for ordering justifies permanent deletion |
| Spieker et al., “Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration,” ISSTA 2017, [DOI 10.1145/3092703.3092709](https://doi.org/10.1145/3092703.3092709) | Three industrial CI data sets | Retecs used duration and execution/failure history to adapt CI ordering/selection | Historical labels are policy-dependent and become missing for omitted tests; industrial subjects may not transfer | CI history can inform prioritization only with temporal replay, exploration/holdouts, and safe fallback |
| Yaraghi et al., “Scalable and Accurate Test Case Prioritization in Continuous Integration Contexts,” IEEE TSE 2022, [DOI 10.1109/TSE.2022.3184842](https://doi.org/10.1109/TSE.2022.3184842) | 25 open-source systems selected for meaningful regression time and failed builds | Defines a broad CI feature model and examines effectiveness, collection cost, feature impact, and model decay | Data collection has nontrivial cost; models decay; evaluation needs systems where prioritization matters | Version calibration snapshots and monitor temporal drift rather than reacting to one run |
| Luo et al., “An Empirical Analysis of Flaky Tests,” FSE 2014, [DOI 10.1145/2635868.2635920](https://doi.org/10.1145/2635868.2635920) | 201 likely flaky-test-fix commits across 51 open-source projects | Classifies common root causes and repair strategies | Fix-commit mining misses unknown/unfixed flakes and does not price local triage | Model valid-verdict/false-red burden separately from detection value |
| Just et al., “Are Mutants a Valid Substitute for Real Faults in Software Testing?”, FSE 2014, [DOI 10.1145/2635868.2635929](https://doi.org/10.1145/2635868.2635929) | 357 real faults in five Java projects, developer and generated suites | Mutant and real-fault detection were significantly correlated independently of coverage, but the study also found inherent operator limitations | Mutants represent only some fault classes; correlation is not equivalence | Use stratified mutation as one validation signal alongside repaired real faults |
| Papadakis et al., “Are Mutation Scores Correlated with Real Fault Detection?”, ICSE 2018, [DOI 10.1145/3180155.3180183](https://doi.org/10.1145/3180155.3180183) | CoreBench and Defects4J, C and Java programs | Mutation-score correlations with real-fault detection became weak after controlling for suite size; higher-scoring equal-size suites still improved detection | Predictive power remained low and depends on benchmark/operator design | Use mutants as guidance and sabotage evidence, not an absolute portfolio objective |

## Decision guide

### Exhaustive

Use when the complete feasible state space is cheap and the oracle is strong.
Exhaustive tests are also useful as a tiny-model oracle for a covering-array
generator and coverage checker.

### Uniform pairwise or t-way

Use when discrete factors interact, the Cartesian product is too large, and no
specific subset clearly deserves stronger treatment. Pairwise is a practical
base, not a universal default for safety-critical behavior.

### Variable strength

Use a base strength across all factors and elevated strength for groups selected
from:

- hazard/threat analysis;
- architectural coupling;
- repaired interaction faults;
- changed-file/component coupling;
- high consequence combined with uncertain behavior.

### Weighted/prioritized

The strongest primary evidence here concerns prioritized pairwise/variable-
strength ordering; Zhang et al. additionally study usage-probability-weighted
input combinations in four experiment groups. Generalizing weights to arbitrary
risk at the factor, value, tuple, or row level is an **engineering heuristic**,
not a proven covering-array fault-yield law.

Use explicit priorities/weights to determine early prefix coverage, repeated
coverage, or optional rows after hard obligations. State whether the input is
usage frequency, hazard impact, repaired-fault history, or judgment, and compare
against unweighted ordering at equal execution budgets.

### Property/fuzz

Use for the values *inside* factors, arbitrary strings/bytes/numbers, state
transitions, and sequences. A covering array over `input_size = small/large`
does not replace generating actual inputs within those classes.

### Regression

Every repaired fault remains a fixed test, including a known 4-way or 6-way
interaction. Portfolio generation must not erase historical evidence simply
because its interaction lies above the current base strength.

### E2E and periodic boundaries

Use a small number of rows to prove real packaging/wiring/platform behavior.
Measure setup and critical-path cost locally. A periodic lane needs a witnessed
baseline, owner, decision/notification path, budget, and stop rule; otherwise it
is a write-only log.

## Cost model: obligations plus a vector

Do not begin with a weighted sum. First declare hard constraints:

- mandatory incident/security/contract tests;
- exact registry enrollment;
- required feasible interaction tuples;
- maximum compute and critical-path budgets;
- required environments and capacity limits.

Then compare feasible portfolios across:

| Dimension | Measurement examples | Main caveat |
|---|---|---|
| Execution | CPU/runner minutes, service/device charges | Standalone duration is not marginal critical path |
| Setup | cold/warm environment startup, cache and fixture reuse | Shared setup makes row costs non-additive |
| Flake/rerun | false-red posterior, rerun compute/delay, valid-verdict rate | Flaky does not necessarily mean low bug-finding value |
| Maintenance | fixture/config churn, ownership changes, repair time | Sparse change history is not zero cost |
| Review | snapshot/golden baseline bytes and reviewer time | Automatic approval removes the oracle |
| Diagnosis | failures per row, localization ambiguity, triage minutes | Large mixed rows can be cheap to run but expensive to explain |
| Evidence | repaired faults, mutation/sabotage kills, risk/usage obligations | Coverage and kills are proxies, not correctness |

Where trade-offs cannot be monetized credibly, publish a Pareto frontier and let
policy choose. A useful implementation can greedily add the row with greatest
marginal uncovered obligation/evidence per limiting cost, recomputing overlap,
but the installable skill should not prescribe a solver or coefficients.

## CI-history calibration

### Three classes of input

**Stable policy inputs** may gate:

- canonical registries and factor constraints;
- known regressions and mandatory risk classes;
- environment requirements and budgets;
- owners, waivers, and expiry criteria.

**Versioned calibration snapshots** may inform periodic planning:

- robust duration and setup distributions by test/platform/runner;
- classified product-failure, test-flake, and infrastructure-failure history;
- retry/valid-verdict and human-triage estimates;
- repaired-fault and stratified mutation/sabotage evidence;
- change/hotspot models with temporal validation.

**Raw telemetry** is diagnostic only:

- the latest duration or queue wait;
- a single retry or failure;
- unclassified stack traces;
- one branch-local coverage delta.

### Promotion rules

- Use stable test and configuration IDs.
- Stratify by platform, runner class, and meaningful environment.
- Use robust quantiles/distributions, not one wall-clock sample.
- Retain timeouts as censored observations rather than ordinary completed runs.
- Classify infrastructure, test, and product failures separately; allow unknown.
- Record sample count, interval/uncertainty, collection window, policy version,
  and snapshot ID.
- Detect drift and fall back; do not automatically delete tests after decay.
- Use temporal train/replay splits. Randomly mixing future CI runs into training
  leaks information.
- Preserve randomized/full holdouts once selection starts, because omitted tests
  otherwise stop producing labels.

## Stable automatic registry enrollment

The conformance model must derive members from a canonical code registry rather
than a copied test list:

```text
registry.entries() -> one-way conformance cases
registry.entries() + factor model -> interaction rows

assert registry IDs == one-way case IDs
assert generated result IDs + owned expiring waivers == registry IDs
```

Exact one-way equality is deliberately independent of covering-array
interaction checking. This catches a new registry member omitted from the model
even if the old model retains perfect pairwise coverage.

### Sabotage test

In an isolated registry:

1. inject a fake member without changing the test case list;
2. assert it appears in generated one-way and applicable interaction cases;
3. make the fake violate one named contract;
4. assert that exact generated contract fails for the intended oracle;
5. restore registry/global state.

This is an engineering synthesis of the repository's doc-sync source-of-truth
pattern and mutation-backed oracle tests, not a claim that covering-array papers
established registry sabotage.

## Worked renderer example

Suppose the factors include:

- 15 diagram families;
- 16 Looks including default;
- 21 Palettes including default;
- SVG, PNG, ASCII, and Unicode output;
- library, CLI, browser, local MCP, and hosted MCP boundaries;
- Bun, Node variants, browser, and Worker runtimes;
- security, transparency, font, and input-complexity classes.

The raw product is enormous and contains invalid combinations. A defensible
portfolio is:

1. **Exact one-way conformance:** every family/Look/Palette/output/boundary/runtime
   has a cheap representative case derived from its canonical registry.
2. **Exhaustive cheap slices:** all values for pure schema/registry logic and
   bounded format semantics where the full feasible slice is cheap.
3. **Constrained pairwise base:** broad in-process rendering rows after encoding
   impossible output/runtime/boundary combinations.
4. **Variable strength:** 3-way `{family, Look, Palette}` for style interactions;
   3-way `{output, transparency, security}` if architecture/threat history
   supports it.
5. **Fixed regressions:** every known topology, font, security, transparency, or
   high-order failure remains explicit.
6. **Properties/fuzz:** arbitrary input complexity, roundtrips, renderer
   invariants, and crash resistance.
7. **Boundary rows:** representative browser/hosted/runtime cases on slower
   measured lanes with owners and budgets.

No row count should be promised until the real model and constraints are passed
to a named generator. Report both generated rows and independently verified
feasible-tuple coverage.

## Replacement validation protocol

### Offline temporal replay

Compare the proposed portfolio with:

- current/full suite;
- random within the same budget;
- fastest-first;
- recent-failure-first;
- uniform pairwise;
- the proposed constrained/variable-strength policy.

Use only information available at each historical decision. Evaluate repaired
faults first and supplement sparse classes with stratified mutation/sabotage.

### Shadow period

Run old and proposed portfolios together without changing gates. Record selected
and omitted tests, obligations, snapshot/policy IDs, result classifications, and
counterfactual late detections.

### Guarded rollout

Start with ordering, then optional noncritical omission. Keep mandatory tests and
a rotating randomized/full-suite holdout. Fall back on missing/stale calibration,
registry mismatch, coverage-check failure, or selector error.

### Measurements

Report before/after:

- generated and executed case count;
- feasible one-way/t-way obligations covered;
- CPU/runner use and p50/p90 wall/critical-path time;
- valid-verdict, flake, retry, and false-red rates;
- maintenance/config/baseline churn and review time;
- triage time and localization quality;
- repaired-fault replay and mutation/sabotage kills by risk/operator;
- escaped defects and severe-risk floor violations;
- selection stability and randomized-holdout misses.

Deletion requires preserved obligations and no material regression in severe
fault evidence during replay/shadowing. Pairwise coverage alone is never deletion
proof.

## Sources checked

- NIST SP 800-142 full text and bibliography (interaction evidence on report
  pp. 4–5; constraints/cost discussion on pp. 16–21):
  <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf>
- DOI/Crossref/OpenAlex metadata and abstracts for the primary papers linked in
  the table; findings derived only from abstracts are kept at abstract-level
  granularity rather than presented as full-paper replications.
- Current StrykerJS threshold configuration:
  <https://stryker-mutator.io/docs/stryker-js/configuration/>
- Repository resources: `research/NOVEL_TESTING_TYPES.md`,
  `research/DESIGN_FOR_TESTABILITY_LITERATURE.md`,
  `testing-best-practices/references/doc-sync-testing.md`, and the fixture/mutant
  eval harness under `skill-development/evals/`.

## Limits

- The cost-aware covering-array evidence is materially thinner than the basic
  construction/constraint literature; early and doctoral results stay
  research-only.
- Historical CI data is missing-not-at-random and changes after a selector is
  deployed.
- Rare catastrophic failures cannot be estimated safely from local frequency;
  mandatory policy remains necessary.
- Mutation operators and fault corpora are incomplete proxies.
- Registry sabotage proves enrollment and oracle bite for the seeded contract,
  not production correctness.
