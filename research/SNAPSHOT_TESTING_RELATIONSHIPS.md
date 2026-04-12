# Snapshot / Golden Testing — How It Relates to Everything Else

> Synthesis prompted by reading
> <https://github.com/jlevy/tbd/blob/main/packages/tbd/docs/guidelines/golden-testing-guidelines.md>
> and following its references section properly.

## TL;DR

Snapshot testing (also called golden testing, approval testing,
golden-master) is a **family of techniques** unified by a single idiom: *run
the system, serialize what it produced, store as baseline, diff against the
baseline on every subsequent run.*

We had this idea in three places already (`golden-file-testing.md`,
`vcr-cassettes.md`, `characterization-testing.md`) but treated them as
unrelated topics. They are dialects of the same thing.

We were also missing two dialects entirely:

1. **Structured-output snapshots** (Jest/syrupy/insta/Verify) — covered in
   `research/NOVEL_TESTING_TYPES.md` §6 but with no skill-level reference.
2. **Session/trace goldens** (jlevy's contribution) — full execution traces
   for multi-step agents and pipelines. Not covered anywhere.

This document maps the relationships, shows where each piece sits in our
skill, and records the changes made to fix the gaps.

## The conceptual map

```
                 Characterization Testing
                 (capture current behavior
                  to enable safe refactor)
                          |
                          v
Approval/Snapshot ---> Golden tests <--- Record-Replay (VCR)
(generic "compare        |  ^             (specifically the
output to stored        / | \              network boundary)
baseline" idiom)       /  |  \
                      /   |   \
       Golden-file   /    |    \  Session/trace golden
       (transform   /     |     \  (full execution trace
        pipelines) /      |      \  with stable/unstable
                  v       v       v  field classification)
              Doc-sync   Differential   Mutation
              (compare   (compare two   (perturb code,
               docs to    impls of       golden test
               registry)  same spec)     should fail)
```

## How each tradition relates

### Snapshot/approval testing is the umbrella idiom

"Run the thing, store the output, diff next time."
Golden-file, VCR cassettes, session-golden, and Jest/insta/Verify snapshots
are all dialects of this. They differ in *what gets snapshotted* and *what
gets normalized*.

### Characterization testing is the use case, not a technique

Feathers' characterization testing tells you *when* to capture current
behavior (before refactoring legacy code). Snapshot testing tells you *how*.
The two references are complements: combine them and you get a refactor
safety net.

### VCR is a snapshot of the network boundary

Specifically, VCR snapshots HTTP request/response pairs and adds *replay*
semantics: the cassette is both the stub feeding the SUT *and* the
behavioral baseline. This is why VCR feels different from `toMatchSnapshot()`
— it serves two roles at once.

### Differential testing is the inverse of snapshot testing

Snapshot testing compares today's run to a stored baseline. Differential
testing compares two live implementations to each other. The oracle is
another impl, not a file. Both fall under "compare two outputs that should
match" but they make different correctness assumptions.

### Mutation testing is the meta-test for snapshots

Snapshot suites have a famous failure mode: rubber-stamping. Devs run
`--update`, eyeball the diff for two seconds, commit. Mutation testing is
the antidote — perturb the code and verify the snapshot suite actually
fails. A snapshot suite that passes under mutation is rubber-stamped.

### Doc-sync testing is structurally similar but the oracle is live

Doc-sync ("the registry IS the oracle, compare docs to it") has the same
"compare X to Y" shape as snapshot testing, but Y is a live code structure
(CLI command list, plugin registry) rather than a stored file. Useful to
remember when extending either pattern.

## Where each piece sits in our skill / research

| Tradition | Coverage before | Coverage after |
|---|---|---|
| Characterization testing (Feathers) | `references/characterization-testing.md` | unchanged |
| Approval / snapshot testing (Falco, Jest, insta, Verify) | only `research/NOVEL_TESTING_TYPES.md` §6 | `references/snapshot-testing.md` Dialect B |
| Record-replay (VCR, PollyJS, WireMock) | `references/vcr-cassettes.md` | unchanged + cross-link to snapshot umbrella |
| Golden-file (transformation, Hashimoto, Go testdata) | `references/golden-file-testing.md` (narrow) | merged into `references/snapshot-testing.md` Dialect A |
| Session/trace golden (jlevy) | gap | `references/snapshot-testing.md` Dialect C |
| Differential testing | `references/differential-testing.md` | unchanged |
| Mutation testing | `references/mutation-testing.md` | unchanged |
| Doc-sync testing | `references/doc-sync-testing.md` | unchanged |

## Changes made

1. **Renamed** `references/golden-file-testing.md` → `references/snapshot-testing.md`,
   restructured as an umbrella with three dialects (golden-file, structured-output,
   session/trace).
2. **Cross-linked** `references/vcr-cassettes.md` to identify itself as the
   network-boundary specialization of snapshot testing.
3. **Updated** `SKILL.md` triggers to route both transformation pipelines and
   structured-output / session-trace cases to `snapshot-testing.md`.
4. **Updated** `references/test-types.md` and `research/DECISION_TREE.md` to
   replace the narrow "Golden File" entry with the snapshot umbrella, including
   the dialect selection table.
5. **Added** new eval cases targeting: session-trace golden recommendations
   for an agent pipeline, structured-output snapshot recommendations for a
   serializer, and an anti-rubber-stamp assessment case.

## Why the umbrella matters

Without the umbrella, an agent reading our skill would:

- Recommend VCR for any "I want to test my LLM agent" question (because the
  agent talks to an LLM API), missing that the *trace of agent steps* is the
  thing that matters more than any one HTTP call.
- Recommend handwritten field-by-field assertions for serializers, missing
  `syrupy`/`insta` entirely.
- Miss the stable/unstable field discipline that makes session goldens not
  flaky.
- Treat characterization testing as a separate technique rather than as the
  use case that motivates snapshot testing for legacy code.

With the umbrella, the agent gets a dialect-selection decision and the right
anti-pattern warnings (rubber-stamping, regex-on-stable-fields, surgical
extraction).

## Lineage (from jlevy's references section)

**Books**
- Feathers, *Working Effectively with Legacy Code* (2004) — characterization
  testing as the originating motivation.
- Pryce & Freeman, *Growing Object-Oriented Software, Guided by Tests* (2009)
  — assertion design philosophy that informs what's worth snapshotting.

**Articles**
- Mitchell Hashimoto, "Testing with Golden Files":
  <https://mitchellh.com/writing/golden-files>
- Llewellyn Falco, Approval Testing methodology:
  <https://approvaltests.com/>
- Wikipedia, Characterization Test:
  <https://en.wikipedia.org/wiki/Characterization_test>

**Tools and frameworks** (all dialects of the umbrella)
- Jest Snapshot Testing: <https://jestjs.io/docs/snapshot-testing>
- Playwright Snapshots: <https://playwright.dev/docs/test-snapshots>
- Go `testdata/` convention:
  <https://pkg.go.dev/cmd/go#hdr-Test_packages>
- Bazel diff-based golden tests:
  <https://bazelbuild.github.io/rules_testing/overview.html>
- VCR (Ruby): <https://github.com/vcr/vcr>
- vcrpy (Python): <https://vcrpy.readthedocs.io/>
- PollyJS (Netflix): <https://netflix.github.io/pollyjs/>
- WireMock: <https://wiremock.org/docs/record-playback/>
- insta (Rust): <https://github.com/mitsuhiko/insta>
- Verify (.NET): <https://github.com/VerifyTests/Verify>

## Open questions / followups

- Should `characterization-testing.md` get a section explicitly recommending
  snapshot tools (`syrupy`, `insta`, `Verify`) as the implementation choice
  for its safety-net tests? Currently it shows hand-written `assert`
  characterizations, which is fine but not the strongest pattern.
- Should we add a research lessons file on jlevy's session-golden pattern
  (to match the existing `LESSONS_FROM_*` files)? The pattern is original
  enough to warrant attribution if we keep building on it.
