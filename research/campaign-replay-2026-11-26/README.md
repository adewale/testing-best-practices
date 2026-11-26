# Historical campaign decision replay — 2026-11-26

**PR #41's skill arm passed all nine scenarios. The pre-PR skill and no-skill
arms also passed all nine. This screen found no incremental benefit from
PR #41 on these decisions.**

The six failure reconstructions were redirected away from their problematic
plans, and the three legitimate controls retained useful work or integrity
contracts. These are observed planning responses under an explicit review
prompt. They do not establish that an autonomous agent would discover the same
facts or prevent the original campaigns during implementation.

## Results

| Scenario | No skill | Pre-PR skill | PR #41 skill |
|---|---|---|---|
| R01: non-completing nightly mutation expansion and copied floors | PASS | PASS | PASS |
| R02: equivalent survivors, test-only exports and implementation pins | PASS | PASS | PASS |
| R03: assertion-density quota and filler assertions | PASS | PASS | PASS |
| R04: live script fingerprints blocking harmless changes | PASS | PASS | PASS |
| R05: expensive preparation repeated for every checker variant | PASS | PASS | PASS |
| R06: expanding a redundant Cartesian renderer matrix | PASS | PASS | PASS |
| R07: useful bounded one-off mutation probe (control) | PASS | PASS | PASS |
| R08: independently promised frozen-archive integrity (control) | PASS | PASS | PASS |
| R09: small real-SQLite endpoint repair (control) | PASS | PASS | PASS |
| **Total** | **9/9** | **9/9** | **9/9** |

PASS requires every frozen criterion for that case. The outcome is six of six
failure scenarios and three of three controls per arm, with zero observed
paired differences. There is one generation per cell, so these counts are not
estimates of repeatability, general reliability, or a population effect.

The PR #41 responses made concrete choices:

- R01 removes the nightly trigger, broad enrollment and copied floors. It keeps
  a focused manual diagnostic and notes that sharding reduces elapsed time
  without removing the total runner-minute cost.
- R02 drops the five test-only exports, cache-poisoning test and 90 target;
  accepts permitted shortest routes; and retains a regression for the genuine
  boundary/default defect.
- R04 removes the live-source lookup while preserving the historical
  fingerprints and archived evidence/totals checks.
- R05 prepares a valid fixture once, runs the production checker separately on
  each tampered input, retains one end-to-end check and keeps the global timeout.
- R06 preserves the three-factor regression and independently checks portfolio
  obligations before deleting old cases.
- R07 accepts a bounded hand-seeded fault check. R08 keeps the independently
  promised archive-byte integrity. R09 accepts the small real-engine repair.

All raw plans and criterion-level judgments are retained. The controller checked
the PR #41 actions against the judges' cited evidence after decoding; the raw
judgments were not changed.

## Design and evidence

- [Frozen protocol](protocol.json) and [cases with sources and criteria](cases.json).
- [Generation map](completed-generation-map.json), including requested subject
  identities and output fingerprints; [raw plans](outputs/).
- [Grading instructions](grading-instructions.md), [judge map](judge-map.json),
  [raw judgments](judgments/) and [decoded results](results.json).
- [Packet reconstruction helper](prepare_packets.py).

The protocol, scenarios, criteria and generation mapping were committed before
the first trial (`1c154d8`). All 27 outputs were committed before judging
(`3d48fe1`); all nine judgments were committed before decoding (`94d73f8`). The
intervention was not tuned and no failed or tied cell was regenerated.

Three arms received the same task and response format:

1. **No skill:** task only.
2. **Pre-PR:** `SKILL.md` and case-relevant references at
   `bd48fe3edf05e2c8371aa517557fe530c1a1cf65`.
3. **PR #41:** the corresponding files plus `references/test-audit.md` at
   `bce78ee6cdc225ebd817161d6727276ec2876e9c`.

There were 27 fresh no-history subjects, each requested as `gpt-6.2-astra` with
`max` reasoning, and nine fresh judges using the same requested model/effort.
Concurrency was capped at six. Subjects could read only their supplied packet
and write their answer under the experiment instructions. Judges received the
task, frozen criteria and three shuffled opaque candidate IDs, with no arm
labels, generation mapping or skill bundles. They assessed proposed actions,
not warning vocabulary or comparative writing style. Every overall verdict was
checked against its criterion verdicts before decoding.

The Codex CLI setup probe failed with expired-login HTTP 401 before producing a
model answer. Actual trials used the collaboration/sub-agent backend. The probe
is excluded from the 27 trial responses. Model names and effort are requested
identifiers, not independently provider-attested identities; token usage and
internal reasoning traces were not available from this backend.

## What this verifies and what it does not

The result supports a narrow statement: with the supplied facts and an explicit
request to review a plan, this requested model produced appropriate decisions
for all nine reconstructions while using the PR #41 guidance. It did the same
without that guidance. These cases are therefore saturated for this comparison.

Important limits:

- These are public, known historical patterns reconstructed from retained
  evidence, not verbatim initiating chats or fresh holdouts. The controls use
  illustrative timings and setup conditions. R02 combines related survivor
  failure modes from more than one historical source.
- Facts such as the runtime/timeout mismatch, equivalent routes and weak fake
  are supplied explicitly. The response format asks for cost and stopping
  decisions. This makes dangers easier to recognize than discovering them in
  a repository during an open-ended request to improve tests.
- References are supplied explicitly, so this measures content efficacy after
  loading. It does not test automatic skill discovery, reference selection,
  tool execution, actual patches, or CI/resource consumption.
- One shot per cell cannot measure stochastic reliability. The pre-PR arm is
  the already-corrected November skill, not the earlier harmful guidance that
  helped motivate the campaign failures.
- Judging is qualitative and uses the same model family as generation. Arm
  labels are hidden, but candidate wording can hint at the guidance supplied.
  No independent human or second-model adjudication was performed.
- Isolation is protocol-level in a shared workspace, not an OS-enforced
  filesystem boundary. Participants were instructed to read only their packet;
  centrally audited per-agent tool traces were not available.

Do not turn this result into a claim of incremental model uplift or reliable
campaign prevention. The appropriate result is to retain the evidence and stop
this bounded screen, rather than tune familiar prompts until one arm wins or
add a recurring benchmark lane. The separately tested receipt-verifier code
fix remains a concrete behavioral improvement; this planning replay neither
establishes nor replaces its five executable regression tests.

## Reconstruct inputs

From a checkout containing the recorded revisions:

```sh
python3 research/campaign-replay-2026-11-26/prepare_packets.py --out /tmp/campaign-replay-inputs
python3 research/campaign-replay-2026-11-26/prepare_packets.py --judges --out /tmp/campaign-replay-judge-inputs
```

These commands reconstruct the 27 exact subject packets and nine exact judge
packets; they make no model calls and perform no grading. The retained hashes identify the historical
inputs/outputs. They do not constrain future implementation files or CI.
This study is not registered as a recurring or deterministic CI gate.
