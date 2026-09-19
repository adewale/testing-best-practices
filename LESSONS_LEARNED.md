# Lessons Learned

What we discovered while building this skill. These are meta-lessons about building testing skills for agents, not about testing itself.

Latest capture: 2026-09-19, covering `c5d017d..3eb3bdc` — PR 26's eval-integrity work and PR 25's guidance, oracle, harness, and current-model verification changes.

---

## Skill Design

### Progressive disclosure saves tokens but requires sharp triggers

Splitting `advanced-patterns.md` (747 lines) into 9 topic files cut typical token load by ~50%. But the triggers must be specific: "read references/advanced-patterns.md" loads everything; "read references/characterization-testing.md IF you're refactoring legacy code" loads only what's needed. Generic pointers waste context.

### Language-specific scripts don't belong in polyglot skills

We shipped a `scripts/check_test_quality.py` that only worked for Python. A Go or Rust project got no validation benefit. We replaced it with language-agnostic guidance in SKILL.md that tells the agent *what to scan for* rather than giving it a single-language tool. The agent can grep for `t.Log` in Go, `toBeDefined()` in TypeScript, `assert result is not None` in Python — it doesn't need a script for that.

### The validation loop is the highest-ROI addition

Telling the agent to self-check its work before reporting done (scan for weak assertions, run the tests, verify density) eliminated the one failing assertion from iteration 1 (assertion density 2.53 vs 3.0 target). The agent catches its own mistakes when told to look.

### Don't explain what the agent already knows

Early versions of the language references explained what pytest is, what Vitest is, basic `describe`/`it` syntax. The agent knows this. Keep only the non-obvious parts: boundary-first Hypothesis strategies, `@cloudflare/vitest-pool-workers`, `t.Helper()` in Go.

### Abstract framings can sit beside detailed references without being redundant

§10 "Types vs tests" (17 lines, abstract — the mental model) sits next to §11 "Correctness by construction" (45+ lines, detailed — the techniques). Both load by default. The short principle gives the question each tool answers; the deep reference gives the tactics. Without §10, agents reach §11 but use only its tactical machinery; with §10, they frame their work around *which question this test answers* before reaching for tactics.

### Naming concrete mechanisms in an abstract section is what moves behavior across languages

§10 v1 said "delete the now-redundant tests in the same commit" — abstract and language-neutral. It moved TS and Go agents but left Python tied. §10 v2 added "(with `xfail`, `@deprecated`, or an inline comment)" — naming the mechanism. Naming mechanisms moved every language: Python agents reached for `xfail` and `TODO[CBC]`, TS for `should be DELETED`, Go for `deletable`. The conceptual instruction alone is not enough; each language needs a concrete anchor to translate the principle into its idiom.

### Teach the failure mode without banning valid techniques

PR 25's blanket rules for literal expectations and non-default, distinct
values were stronger than the research justified. The real requirements are an
oracle independent of the SUT and at least one case that exposes dropped,
defaulted, or swapped inputs. Properties and independent reference models
are valid oracles; zero, empty, and equal values can be essential boundaries.
Express the invariant and its scope in the router, validation loop, and each
language reference together — otherwise an absolute rule survives in the
file the agent actually loads. A memorable slogan is useful only while it
preserves the counterexamples that make the advice correct.

## Research

### Scan real repos, not documentation

The most valuable insights came from reading actual test files in production repos, not from testing documentation. The `t.Log` antipattern (logging instead of asserting) was found by reading rogue_planet's XSS tests. The mock contract test pattern came from reading atlas's Playwright tests. The fixture-based golden file pattern came from reading defuddle's test infrastructure. None of these appear in testing guides.

### Every practitioner has one big idea

- Kent Beck: tests have 12 properties that *conflict* — testing is a design space, not a checklist
- Nat Pryce: boundary-first generators, mutation-based fuzzing, test lifecycle tied to issue trackers
- Graydon Hoare: when the space is small enough, test *everything* exhaustively
- Andrej Karpathy: the reference implementation IS the test oracle
- Brad Fitzpatrick: write a protocol-faithful fake and run the same tests against fake and real
- Joe Walnes: a test framework needs exactly 4 things and nothing more
- Steph Ango: add a fixture file = add a test (zero-code test creation)
- Mary Rose Cook: test at the user-facing level, pin non-deterministic inputs

### One combined file per batch was a mistake

We initially lumped 7 practitioners into one `LESSONS_FROM_PRACTITIONERS.md`. Individual contributions got buried. Splitting into one file per person made each practitioner's key idea stand out and made the research navigable.

### Cross-source synthesis produces better skill content than any single source

§10 "Types vs tests" emerged from combining Jane Street's "make illegal states unrepresentable" (Minsky) + Alexis King's "parse, don't validate" + the team's existing defense-in-depth-as-antipattern work + the practical observation that agents over-write per-function rejection tests. No single source produced the 17-line framing; the combination did. The lesson: research artifacts compound. A new practitioner's contribution may not be a new principle — it may be the missing piece that finally fits an existing one into a usable form.

### Verbatim source beats fetched summaries

The first Dan Luu research pass used fetched-page summaries; the second used GitHub API search that returns raw file content. The API pass surfaced what the summaries flattened: the actual harness mechanics that make a "dumb" fuzzer productive (seed-from-arg reproducibility, try/catch + input logging for crash replay, a `banned.txt` denylist), two repos the profile-page summary missed entirely (kodkod-clj, secvisor-formal-verification), and grounds to drop an unverifiable "10+ bugs" claim in favor of what the repo actually shows. Research with tools that return artifacts, not paraphrases — the interesting details live below summary resolution. Corollary: global search endpoints (code/issue search) often work even when direct per-repo reads are access-restricted.

### A confirming research pass is still valuable — but the deliverable is the delta

Most of Dan Luu's testing thesis was already in the skill (property-based testing, fuzzing, differential testing, coverage skepticism, mutation). The temptation was to restate it all; the discipline was to add only the one genuine gap (error-handling paths exercised by injected dependency failure) and let the research file carry the confirmations. A new practitioner who mostly validates the existing skill is evidence the skill is right — not an invitation to bloat it.

### A literature pass after an engineering decision is cheap corroboration — and a gap detector

After iteration 10 folded design-for-testability on ablation evidence, a literature review found the canon had already reached the same hierarchy (substitutable dependencies over test hooks; Meszaros's "Test Logic in Production"; Feathers's enabling points outside production text), and the flaky-test literature's recommended fix (condition-based synchronization, Luo et al. FSE 2014) is exactly the seam shape our baseline arms built from priors — explaining *why* the teaching didn't discriminate: it's already in the models. The same pass surfaced precisely one concept the corpus lacked (Voas's fault-hiding/PIE theory of testability) and quantified honesty backing (Sharma et al. 2023: developer-plausible testability smells don't survive measurement). The pattern: make the decision on your own evidence, then check it against the literature — agreement converts a local result into a corroborated one, and the residue is a focused list of what you actually don't know.

### Enumerate a corpus from the platform's structured feed, not by link-following

The Google Testing Blog analysis used Blogger's
paginated JSON feed (`/feeds/posts/default?alt=json&max-results=100`) that
enumerates the archive deterministically, with a reported total of 404 posts
to reconcile against — no sitemap guessing or reliance on "older posts"
links. The historical analysis reports ten analyst batches over 216K words;
the retained metadata supports the archive count, but the raw batches were
not retained. For any platform-hosted corpus, find the machine-readable
enumeration first, then retain evidence of the coverage actually achieved.

### A receipt proves only the evidence it preserves

The [Google corpus receipt](research/GOOGLE_TESTING_BLOG_CORPUS_RECEIPT.md)
records the feed URL, verification date, count, date range, and latest-entry
metadata. It does not recreate the missing plain-text download, ten analyst
outputs, or per-post assessments, so it cannot substantiate the 216K-word
count or full-reading claim independently. Keep enumeration, retrieval, and
analysis coverage as separate claims. Preserve a source manifest and curated
analysis evidence while the work is happening; a later metadata check can
corroborate the archive but cannot recover the analysis. Apply the same rule
to eval receipts: an output digest identifies an artifact if it is available,
but is not a substitute for the artifact or a reproducible stochastic run.

### Keep a quantitative claim attached to its original scope

The Google research summary turned Hevery's two-week, single-project log
into "testability costs ~10%, not 2x." The corrected note retains the useful
counterexample to "tests always double development time" while naming its
duration, project scope, and what was measured: time spent writing tests.
Carry those qualifiers into both the research synthesis and the short
takeaways. A precise number becomes less reliable, not more, when its
denominator and setting disappear during compression.

### Infrastructure-specific patterns can still generalize if you extract the underlying invariant

Jane Street's library-level simulation testing — `Time_source` parameterization, the compiler-enforced `Require_explicit_time_source` — is uniquely OCaml. But the underlying idea ("make every source of non-determinism an explicit parameter") generalizes. The skill captures the pattern in `deterministic-time.md` (clock injection vs virtualization) without requiring OCaml. The cross-language lesson is "what would this look like in Java, Go, Python, TS" applied to every practitioner's contribution.

## Evals

### Without-skill baselines are essential

The with-skill runs always look reasonable on their own. The baselines reveal what the skill actually adds: property-based tests (appeared in 100% of with-skill runs, 0% of without-skill), structured severity-prioritized assessments (with-skill only), explicit assertion density measurement (with-skill only).

### Balance evals across languages early

Our first 6 evals were 4 Python + 1 TypeScript + 1 Go + 0 Rust. This made us confident in Python behavior but blind to Go and Rust. When we added Go assess and Rust write evals, they passed — but we didn't know that until we tested.

### Eval fixtures should contain realistic antipatterns

Our `weak_tests.py` fixture was effective because it contained real antipatterns observed in production repos: `t.Log` instead of `t.Error`, `print` instead of `assert`, `@skip` without conditions, mocking the system under test. Synthetic bad tests would have been less useful.

### The eval viewer was unusable

The skill-creator's `generate_review.py --static` produced an HTML file with JavaScript alerts on every interaction. We abandoned it and presented results inline in conversation. For future iterations: present results directly rather than depending on external viewer tools.

### Ceiling effects mask signal — purpose-build fixtures when testing a specific contribution

The first attempt to evaluate §10 reused existing CBC evals (subscription, order_state). Both scored 8/8 *without* §10 and 8/8 *with* §10 — proving non-regression but not improvement. The signal that §10 was working came only after building three new fixtures (`user_service.py`, `order_service.ts`, `payment_service.go`) deliberately shaped to test loose-types-could-replace-runtime-validation reasoning. Those fixtures scored 13/16 without §10 and 16/16 with v2 — a +18.75pp delta visible only because the fixtures weren't already at ceiling.

### A/B with language-isomorphic fixtures isolates language-specific gaps

Building the same shape across Python, TypeScript, and Go (each a small service with primitive params + runtime validation) let us see that §10 v1 helped TS and Go (+0.5, +1.5) but left Python tied. Without per-language fixtures we'd have averaged the aggregate and missed Python entirely. The fixtures must be *isomorphic* — same number of functions, same kind of invariants, same complexity — so the only variable is the language.

### Iterate on the section, never the rubric

When v1 of §10 didn't help Python, the temptation was to widen the rubric until v1 looked good. Instead we left the rubric fixed and changed §10 to v2. Result: a clean signal that the change to §10 (not the grader's generosity) moved Python from 4.5/5 to 5/5. Rubrics drift when iterated alongside the code being graded; freeze them before running A/B.

### Parallel agents make A/B affordable inside one session

6 agent runs (3 fixtures × 2 conditions) ran in parallel in ~2 minutes. Without parallelism the same experiment would take 10-15 minutes serially. For iteration cycles that need to converge in a single session, parallel dispatch is essential — and the parent agent doesn't need to do anything during the wait beyond commit hygiene.

### Public prompt oracles can saturate across genuinely different skill versions

The 10 fixture-backed prompt oracles passed for the first working GitHub version, the previous GitHub main version, and the improved local version. That does not mean the versions are equally good; it means the public prompt/oracle setup measured a narrower claim than intended. Treat saturated prompt oracles as smoke tests, not release-quality discrimination.

### Score the artifact when behavior evals stop discriminating

The version rubric separated first GitHub (28/100), previous GitHub (69/100), and the local skill (100/100) while the prompt fixtures stayed at 10/10. Artifact rubrics are not a replacement for runtime evals, but they catch stale contradictions, bad router structure, unsafe universal rules, and token bloat that single-prompt outputs can route around.

### Evals need validity metadata, not just prompts

Adding claim/warrant/backing/rebuttal fields forced each eval to say what interpretation it supports and how it could still be misleading. This turned “does the model pass?” into “what decision can this score justify?” That distinction matters once evals are used for release decisions.

### Probe with a capable baseline before writing skill text

The concurrency principle started as an eval, not as writing: a no-skill baseline run against a cache with a TOCTOU double-compute race. The baseline *detected* the race (it added a compute counter) but then `t.Logf`'d the count and "allowed" the contract violation — proving the gap was real and unsaturated before any skill text existed. This is the inverse of "without-skill baselines are essential": don't just use baselines to validate a change after the fact, use them first to find what's worth changing. A gap a frontier model already handles isn't worth tokens.

### Eval the over-application failure mode, not just the under-application one

"Test error-handling paths" worked — and then E34 showed it pushed the model to *invent* a retry budget and custom error type the contract never specified, tripping scope control (D: 4→2). Any "do more X" instruction has a sharp edge where X becomes over-engineering; the fix was a paired scope clause ("assert the failure behavior the code actually has, not one you wish it had"), verified by an isolation re-run. When adding a behavioral push, build the eval for its over-application before shipping it.

### Validate oracles against real model output, not just hand-built samples

The e35 oracle passed its good/bad self-tests, then falsely passed the real baseline candidate — which asserted compute-once in a *sequential* test while only logging it in the *concurrent* one. Hand-authored bad samples encode the failure you imagined; real candidates produce failures you didn't. The fix (scope the check to the function containing `go func`) only became visible by running the oracle against actual model output. Self-tests are necessary, not sufficient.

### Change one variable per re-run, or you can't attribute the result

Fixing the E34 scope-creep finding involved tightening the principle *and* hardening the prompt. Both arms then scored 4/4 — pleasant, but unattributable. The result only became evidence after an isolation run that held the original soft prompt constant and changed nothing but the principle (D: 2→3, invented contract gone). When a fix touches both the skill and the eval, re-run the original eval with only the skill changed before claiming the skill change worked.

### Sub-agents are a complete eval backend; keep the harness deterministic

The prompt-eval runner never calls a model: its core is fixture-oracle execution plus rubric arithmetic (score = min of focused dimensions, critical-failure override). Candidate generation and judging are pluggable backends — parallel sub-agents for A/B arms, `claude -p` headless as the judge. This made paired with/without-skill runs affordable inside one session with zero API setup. One sharp edge: parsing judge JSON by brace-counting breaks on braces inside string values; use `json.raw_decode`.

### Hardened probes stop discriminating but keep guarding

After hardening E34 (contract stated as fixed) both the baseline and with-skill arms scored 4/4 — the probe no longer separates skill from no-skill on a frontier model. That's not failure; its job changed from *discriminator* to *regression guard* for the specific over-engineering it originally caught. Track the distinction in eval health metadata rather than deleting saturated probes that still pin a real failure mode.

### Two eval mechanisms have distinct jobs; mirror cases deliberately

The repo ended up with an internal development suite (fixture oracles, deterministic gates — fast find-and-fix) and the shared benchmark (paired protocol, tune/holdout/holdback splits — slow prove-and-compare). That's a feature, not duplication, but it creates a sync obligation: when the dev suite finds a gap (error paths, concurrency), check whether the shared benchmark covers it and mirror a case if not — minding its keyword-leakage trap (assertion values must be terms a good answer produces but the prompt doesn't contain).

### Generated eval runs are evidence, not source

Committing raw `eval-runs/` directories and `__pycache__` files made the repo look more reproducible while actually mixing generated artifacts with maintained source. The better pattern is to track fixtures, oracles, scorecards, summaries, and scripts; keep raw run outputs ignored unless they are deliberately curated as fixtures.

### Cue leakage puts a fixture at ceiling before you even run it

Iteration 8's statistical-oracle fixtures (E38/E39) named the `brute_force_topk`
helper right in the prompt. Both with-section and without-section runs then
produced recall-vs-brute-force tests — the prompt did the teaching, not the
skill. The ablation measured nothing about the section. The fix for next time:
the prompt must describe the *situation* ("an approximate index, no single
correct answer") without naming the technique's machinery. A fixture that
mentions the oracle is testing the model's reading comprehension, not the skill.

### Adversarial probes earn their keep, and oracles need their own scrutiny

The E41 restraint probe (trivial pure function) immediately caught the
shadow-model guidance inducing a redundant `_reference_slugify` reimplementation
— a real over-application we then fixed in the guidance. But grading also
exposed two bugs in the probe oracles themselves: a false negative (a recall
threshold held in a named constant slipped past a literal-only regex) and a
false positive (`def \w*slug` matched the test function names). An oracle that
hasn't been adversarially checked against realistic-but-different outputs will
both miss real failures and punish good work. Self-tests (good/pass + bad/fail)
catch the crude cases; realistic agent output catches the rest.

### Cue-free fixtures answer what cue-leaked ones can't

Iteration 9 rebuilt the statistical-oracle fixtures with prompts that name only
the documented metric — no "brute force", "recall", "oracle", or "threshold".
The result reversed iteration 8's non-finding: with the section, agents derived
the reference-ranking-plus-recall-threshold design themselves; without it, they
pinned exact set equality against their own reference — the exact failure mode
the section exists to prevent. Same section, same model; the only change was
removing the teaching from the prompt. A fixture that names the technique's
machinery measures reading comprehension, not the skill.

### Specify the degree of nondeterminism, or agents will model exactly what you said

The Go cue-free prompt said results "may differ on near-ties." The
without-section agent took that literally and built a tie-only-tolerant exact
oracle — defensible given the wording, but not the taught shape, which made the
FAIL ambiguous evidence. Fixture prompts for approximate systems must state the
*kind and degree* of allowed variation ("may return slightly less similar
items"), or the ablation conflates guidance effects with prompt interpretation.

### Keyword oracles false-negative good work; read every FAIL before believing it

Iteration 9's grading hit four oracle calibration bugs — all false negatives on
high-quality outputs that used different identifiers than the oracle expected:
`.sort(key=...)` for `sorted(`, `random.Random(seed)` via variable for a
literal seed, a hand-rolled `canonicalDump` for `DeepEqual`, and a public
`flush()` seam for `flush_now`. One of them initially flipped a verdict from
"ceiling" to "discriminates"; manually reading the artifact caught it. Oracles
should encode behavioral shapes, not identifier spellings — and an ablation
verdict is not real until each FAIL has been verified against the artifact.

### A strong adjacent reference can absorb a new section's contribution

Design-for-testability did not discriminate because the ablation baseline
included `deterministic-time.md` — and that, plus priors, already produced
seam-in-the-SUT behavior in both languages. That is the right way to fail: a
win against an empty baseline would have been claimable but meaningless. Test
new sections against the strongest adjacent guidance, and when the baseline
absorbs the contribution, say "unproven marginal value," not "validated".

### Frontier priors keep moving the ceiling — re-test inherited "best practices" before shipping them

Two consecutive iterations took canonical, literature-backed testability ideas (design-for-testability seams; Voas's fault-masking detection) through the pipeline, and both came back at ceiling: the without-arms produced the taught behavior from priors alone. The lesson isn't that the ideas are wrong — they're correct and have decades of pedigree — it's that a capable base model has already absorbed them, so *teaching* them changes nothing measurable. What survives ablation is the residue priors *don't* reliably produce: explanatory framing that sharpens judgment (the PIE vocabulary; why mutants survive), a non-obvious tactic (assert the pre-mask value, not the clamped output), and restraint guards. Ship the residue, not the textbook. Before adding any well-known practice, ablate it against bare priors — the ceiling has risen.

### Pre-register the decision rule, and unproven sections become cheap to remove

design-for-testability.md survived iteration 9 as "shipped but unproven." Iteration 10 committed a decision rule *before* any runs: discriminate on non-time fixtures (where the strong baseline is irrelevant) → keep; both arms pass → fold into deterministic-time.md. Both arms passed — the without-arms built genuine Event/WaitGroup seams from priors alone — and the fold executed without debate, keeping only the guardrails the E46 probe had validated. Without the pre-registered rule, the temptation is to keep re-testing until some fixture flatters the section; with it, deletion is just the rule firing. Sections should be cheap to remove, and the way to make them cheap is to decide the removal criterion before the evidence arrives.

### Oracles must grade code, not prose about code

Iteration 10's first grading pass failed three of four runs for "real sleep still present" — every flagged sleep was in a comment or docstring *describing the old flaky test*. Agents narrate their fixes; an oracle that greps raw text will punish exactly the outputs that explain themselves best. Strip comments and docstrings before pattern checks. (Oracle bug #5; all five across three iterations were false negatives on good work.)

### Ship-but-flag is an honest state for an unproven section

The statistical-oracle section is plausibly useful and passes every gate, but
the ablation did not prove it changes behavior. Rather than delete it or
overclaim, we shipped it and marked its fixtures `saturated_public` with a
rebuttal noting the cue leak. "Validated" (shadow-model) and "shipped but
unproven" (statistical-oracle) are different claims, and the eval metadata
should say which one each section has earned.

### Schema and audit gates must evolve with eval design

After adding `validity`, `eval_health`, hidden probes, and mini-repos, the JSON schema still validated only the older prompt fields. The best-practices audit caught that mismatch. Every new eval concept needs a gate, or it becomes convention instead of infrastructure.

### Optimize the always-loaded router first

The installable package shrank only ~9%, but `SKILL.md` dropped from ~5,572 to ~2,745 estimated tokens. That matters more operationally because the router is always loaded while references are conditional. Progressive disclosure pays off most when the entrypoint is short and the triggers are sharp.

### At the frontier ceiling, oracle artifacts dwarf model variance

The Google-blog round produced 84 scored transcripts (44-cell ablation
matrix + 40 variance repeats at n=5/cell), and after verification the
score was 84/84 — every raw FAIL across both rounds was an oracle
phrasing artifact, zero were model failures, and repeated runs showed
zero variance (Wilson 95% CI [0.93, 1.00] on the repeats). The practical
inversion: at this ceiling, "measure the model" quietly becomes "debug
the oracle," and the round's real yield was ~13 oracle fixes across 8
fixtures. Budget accordingly — reading every FAIL against its artifact
is not a spot-check step, it is most of the work.

### Prose oracles need negation-awareness, or the judgment belongs to the judge layer

E61's assess-mode oracle regex-matched recommendations in free prose and
kept false-negating good work in new ways: candidates *named* the wrong
move in order to reject it ("adding more E2E … is the wrong one"), put
the down-tier recommendation in a migration table (`| unit |`) with no
verb the regex knew, or phrased it as "push the rules down." Three
hardening passes (negation windows around forbid-matches, phrasing
branches, table-cell patterns) got it stable — but the trajectory says
regex over prose asymptotes to a judge. Reserve deterministic oracles
for code-shaped claims (AST checks, runnable mutants) and route
free-prose judgments to the rubric/judge layer, where E61-style verdicts
were uncontroversial.

### Blind judges recover the gradient binary oracles compress — and agreement makes one judge enough

The 44 all-pass matrix cells, re-scored by rubric judges blinded to
arm/model, showed a consistent quality gradient (base 3.67 → current
3.83 → new 3.92 like-for-like, with score-3 cells falling 4 → 2 → 1)
that pass/fail oracles cannot see — suggestive, within overlapping
stddevs, but the only instrument in the stack that registered the skill
at all at the frontier ceiling. Double-judging 16 cells with a second
model measured the eval-health "judge disagreement rate" meta-signal:
97% exact per-dimension agreement, no eval-score disagreement >1, 16/16
on critical-failure calls — which licenses single-judge passes on these
fixtures. The layers divide labor: oracles gate hard behaviors,
judges grade the margin above the floor.

### Drain the sub-agent queue by completions, not by batch

The runtime caps concurrent sub-agents (20 here), and launching the full
matrix at once bounced two runs off the limit. The pattern that worked:
fill to the cap, then launch exactly one replacement per completion
notification — never retry a rejected launch immediately, never sleep-
poll. Throughput stays at the cap and nothing is lost. Corollary for
repeat runs: give each run an isolated workspace — one variance repeat
found a sibling run's finished solution in the shared scratchpad, which
can only inflate pass rates (the affected cells were already 5/5 from
clean runs, but the protocol hole is real).

### Validate against the real harness, not your mental model of it

Wiring the shared benchmark to the actual `skill-benchmark` CLI caught
three things a hand-check missed: trigger cases require explicit
`should_trigger`, judge-only assertions default to soft (need
`gate: true` to fail a run), and reference-file section ablations are
structurally impossible (all ablation mechanisms edit the root's main
file; overlapping skill roots are rejected by the materializer) — which
forced the honest redesign of two ablations as SKILL.md `list_item`
removals with repo-side hidden probes guarding the reference files. A
thin adapter (extract fenced code from `output.md`, delegate to the repo
fixture's oracle) let shared-benchmark mirror cases reuse the
deterministic oracles instead of duplicating them as prose assertions.

### Make vacuous candidates fail before trusting a green oracle

The September audit found the opposite of the earlier false-negative trend:
E23 accepted an `assert True` test with the required vocabulary in a
docstring; E55 accepted a literal URL assigned to `expected_url` with no
assertion; E59 accepted assignments mentioning balance and transactions
without checking a deposit. A candidate can contain every expected token and
test nothing. The fixes tied E23's checks to the Hypothesis property and
E55/E59's checks to assertions in test functions exercising the relevant
operation. Add explicit no-op and assignment-only bad samples, and ask what
failure could change each assertion's outcome. Structural checks improve
that connection but still do not prove execution or semantic correctness.

### Oracle calibration needs a growing corpus of both valid and invalid answers

Negated recommendations passed E57/E58/E61/E63 because they contained the
right words while rejecting the required behavior. Conversely, good answers
such as "self-contained tests," "a canonical comparison is appropriate," and
"relocate business-rule coverage below the browser" failed narrow phrasing
checks. The manifests now support multiple `good_samples` and `bad_samples`,
retaining each discovered case instead of replacing the original exemplar.
Check both directions after every oracle change. Keep the behavioral rubric
fixed, save the rejected or falsely accepted artifact, and regrade existing
candidates under the corrected oracle before interpreting a model delta.

### Candidate transport is part of the measurement

The prompt-eval runner originally omitted assessment Markdown, so a judge
could miss the actual answer. A fixed triple-backtick wrapper also allowed
fenced code inside the answer to close the candidate's framing early. PR 26
added Markdown ingestion, a fence longer than any backtick run in the
candidate, and regression checks that supported answer files reach the judge
intact.
Verify the judge's input as well as its output: an excellent rubric cannot
grade evidence that was dropped or ambiguously framed in transit.

### Missing evidence must not become a passing result

PR 26 made failed generation, empty judge inputs, missing required judges, and
malformed judge results fail closed. Required rubric dimensions must be
present, scores must be numeric and within 0–4 (a JSON boolean is not a
score), and `critical_failure` must be an explicit boolean. Distinguish a
staged run awaiting a candidate from a completed evaluation; the former may
exit successfully as a preparation step without having passed anything. A
fixture-only pass is valid when no judge was requested, but cannot stand in
for a missing requested judge. Test these state transitions independently
of any model so an infrastructure failure cannot inflate the scorecard.

### Running an oracle is not the same as running the candidate tests

E23 launches an executable Python oracle, but that oracle inspects the
candidate's AST; it does not execute the Hypothesis suite. Its metadata and
scorecard previously suggested runtime coverage they did not provide. E60,
by contrast, runs pytest against pristine implementations and separately
drifted fake and real stores. Label text, structural, runtime, and mutation
evidence explicitly in measurement metadata and reports. A green validator
supports its stated checks, not an implied claim that candidate tests ran
or caught a real defect.

### Prompts, output format, and test discovery form one contract

The six shared Google cases initially used one-line summaries while their
oracles assumed the full fixture source and behavior. Reusing the complete
fixture through `prompt_ref` closed that gap. E60 also needed an explicit
request for a complete fenced Python answer, and the adapter had to name the
extracted file `test_extracted_*.py` so pytest would discover it. Validate the
whole path from task context through returned artifact to oracle input.
Prompt reuse prevents two copies drifting; a correct oracle alone does not
make a shared case executable.

### Smoke-test the complete eval path before paying for the model matrix

The PR 25 follow-up repaired missing prompt context, output extraction,
pytest discovery, runtime dependencies, and accepted prose variants around
the same evaluation path. These are instrument failures, not questions that
need a large generation batch. First send known good and adversarial outputs
through the actual shared adapter and grader, including a runtime case that
passes pristine code and rejects the intended mutants; then run a small
generation pilot before expanding. The final 24-cell panel recorded 959,831
provider-trace tokens, making this preflight consequential. When only the
grader changes, regrade retained outputs and record both revisions instead
of paying for fresh candidates that confound the comparison.

### A clean-checkout gate must install the oracle's real dependencies

The fixture documentation called the oracles stdlib-only even though E60
invoked pytest. A developer environment could hide that dependency; a fresh
CI worker could not. The fix pinned pytest in
`skill-development/evals/requirements.txt`, installed it in the documented
local command and CI, and configured Python, Go, and Node for the common
deterministic gate. Keep runner regressions, adapter checks, and oracle
self-tests in that gate. Reproducibility starts with declared prerequisites
and a checked-in entrypoint, not the fact that it passed on the author's
machine.

### Capture exact model, reasoning, and artifact revisions at launch

The August matrix retained only `sonnet` / `opus` aliases and no committed
generation artifacts, so it cannot establish coverage of today's model
panel. The [September receipt](skill-development/evals/receipts/pr25-luna-terra-2026-09-19.md)
records exact `gpt-5.6-luna` / `gpt-5.6-terra` IDs, explicitly pinned low
reasoning, runner version, generation and final-grading commits, skill-tree
identity, and output digest. Pin the configuration before the run and capture
the resulting artifact identities as they are produced; an unrecorded
reasoning default or changing alias cannot be reconstructed confidently
later. Keep generation and grading revisions distinct when oracle
calibration continues after the outputs are collected, and state when raw
artifacts remain untracked.

### Assignment to the with-skill arm does not prove treatment uptake

The September traces showed skill-file reads in 11 of 12 with-skill cells.
Terra E59 passed without a recorded read of the mounted skill. Its result
belongs in the assigned-arm totals, but cannot demonstrate that the skill
was used. Record exposure separately from success: mounting a file, reading
it, and changing behavior because of it are different claims. A read is
useful uptake evidence, not by itself proof that the skill caused a better
answer.

### Classify the cause of a delta before attributing lift

The current-model panel passed 12/12 with skill and 11/12 without. The sole
difference was a Luna E60 baseline with an invalid Python function name,
not a missing fake/real contract-testing strategy. With one run per cell and
Terra already at 6/6 in both arms, the honest result is no observed
regression on these six cases, one noisy positive cell, and continued
frontier saturation. It is not demonstrated general quality lift. Read the
losing artifact, report the failure class, and keep non-regression, treatment
uptake, and causal improvement separate even when the aggregate looks good.

### Token accounting and prompt size answer different questions

The September receipt's input totals include repeated and cached context
across tool turns. They are a usage ledger, not the length of a prompt or
the number of unique skill tokens read. Report input/output totals and
elapsed time by model and arm, with the accounting basis, alongside the
observed benefit. Source-token reduction, run cost, and quality lift need
their own measurements; one number cannot stand in for all three.

## Evolution

### Iteration history

| Iteration | Evals | Languages | Pass Rate | Key Change |
|-----------|-------|-----------|-----------|------------|
| 1 | 3 | Python, TypeScript | 96% (24/25) | Initial skill |
| 2 | 3 | Python, TypeScript | 100% (25/25) | Added Test Desiderata, mathematical properties, golden files, Go patterns |
| 3 | 7 | Python, TypeScript, Go, Rust | 100% (49/49) | Split advanced-patterns, balanced evals, language-agnostic validation |
| 4 | 12 | + CBC fixtures (Python subscription, Go order_state) | 100% | §11 Correctness by construction + decision-tree rework + tactic A/B framing |
| 5 | + 3 types-vs-tests fixtures | Python, TS, Go | 16/16 with §10 v2 (13/16 without) | Jane Street research; §10 "Types vs tests"; `deterministic-time.md`; snapshot-tests in `golden-file-testing.md` |
| 6 | 32 eval definitions + 10 fixture oracles + 3 mini-repos | Python, TS, Go, Rust | artifact rubric 100/100; static 0 P0/0 P1; public oracles 10/10 saturated; mini-repo mutants 3/3 | Eval validity metadata, hidden hard probes, generated-artifact hygiene, best-practices audit |
| 7 | 35 eval definitions + 12 fixture oracles; +2 shared-benchmark tune cases | Python, TS, Go, Rust | paired A/B: error-path principle D 2→3 after scope clause; concurrency oracle discriminates baseline (FAIL) vs full-SKILL.md (PASS); gates 100/100 | Dan Luu research; error-path + concurrency-contract principles; E33/E34/E35; prompt-eval runner with pluggable sub-agent/judge backends |
| 8 | 41 eval definitions + 18 fixture oracles | + shadow-model, statistical-oracle, restraint probes | shadow-model discriminates + generalizes; statistical-oracle at ceiling (cue leak); over-application found+fixed; audit 110/110 | antirez insights: shadow-oracle + statistical-oracle sections, new-section adversarial-probe gate |
| 9 | 49 eval definitions + 26 fixture oracles | + cue-free statistical, testability, digest roundtrip | statistical-oracle validated cue-free (Python discriminates, Go weak); digest validated in Go holdback; testability at ceiling vs deterministic-time baseline; both restraint probes hold; 4 oracle false negatives found by reading artifacts | design-for-testability reference + whole-state digest section; cue-free fixture discipline; strongest-adjacent-baseline ablation |
| 10 | 51 eval definitions + 28 fixture oracles | + non-time testability isolation (E50 py dev, E51 go holdback) | both arms PASS both fixtures (priors build Event/WaitGroup seams); pre-registered rule fired: design-for-testability folded into deterministic-time.md, guardrails kept (E46-validated); oracle bug #5 (comment sleeps) fixed | fold decision; ≈ −700 on-demand tokens; comment-stripping oracles |
| 11 | 54 eval definitions + 31 fixture oracles | + Voas fault-masking detection (E52 py dev, E53 go holdback, E54 restraint) | detection at ceiling (priors + antipattern #2 catch it in both arms); restraint held both arms; #14 trimmed ~50% to PIE framing + pre-mask fix; mutation-testing PIE paragraph kept; oracle bug #6 (would-pass-even-if) fixed | Voas PIE delta from the literature review; re-test-inherited-practices lesson |

The biggest quality jump was iteration 1→2 (+4%, fixed assertion density). The biggest coverage jump was iteration 2→3 (3→7 evals, 2→4 languages). Iteration 5's signal was the +18.75pp aggregate from §10 v2 — only visible because we built new fixtures that weren't already at ceiling.

### The improvement story for §10 specifically

§10 went through three states:
- **None** (baseline): agents identify CBC antipatterns but don't consistently mark redundant tests as deletable
- **v1**: added abstract "delete now-redundant tests when you tighten a type" — moved TS and Go scores, Python tied
- **v2**: added "(with `xfail`, `@deprecated`, or an inline comment)" — moved all three languages to ceiling

The pattern: the conceptual instruction wasn't enough on its own. The mechanism names gave each language an anchor to translate the principle into idiomatic test annotations.

### Rebases mid-task work when the overlapping work is complementary

Mid-iteration we rebased the Jane Street branch on top of main's CBC work. The conflict was in `test-types.md` where my "Types vs tests" section overlapped with main's larger "Step Zero" rewrite. The resolution was simple — drop my section, take main's — because main's was strictly more developed and covered everything mine did. The lesson: when overlapping work emerges in parallel, the team that committed first sets the foundation, and later work integrates by deferring to whichever version is more developed.

### Token cost tracked but not optimized prematurely

We measured token cost throughout (iteration 1: ~30k with-skill, iteration 3: ~30k average) but optimized for quality first. Token savings came naturally from splitting files — we didn't sacrifice content to save tokens. Iteration 5 added ~5K tokens (deterministic-time.md, expanded golden-file-testing.md, §10) for a +18.75pp eval signal on the new fixtures and no regression on existing ones — a worthwhile trade.

Iteration 6 reversed the always-loaded token trend: the full installable skill is still broad, but the router dropped by roughly half versus the previous GitHub main version. The release lesson is to track entrypoint tokens separately from total package tokens; users pay the router cost first.
