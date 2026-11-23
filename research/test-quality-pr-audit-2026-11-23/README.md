# Test-quality PR evidence — 2026-11-23

The scope is all 92 repositories returned for the authenticated GitHub owner's
`owner` affiliation: 86 public and six private, including archived repositories
and forks. Each repository received a separate `gpt-6.2-astra` agent requested
with `max` reasoning effort. At most six discovery agents ran concurrently.
An independent authenticated `gh repo list adewale --limit 1000` inventory
returned the identical set of 92 repository names.

- [Catalogue](catalogue.md): coverage table and every included public PR, with
  its status, weakness, and attempted improvement.
- [Manifest](manifest.json): completeness, counts, public repository roster,
  source-report paths, and synthesis adjustments.
- `reports/`: detailed public-source findings, exclusions, enumeration receipts,
  concrete changed paths/diff evidence, related PRs, and verification caveats.
- [Synthesis and OpenClaw comparison](../TEST_QUALITY_PR_SYNTHESIS_2026-11.md):
  how these findings inform the installable workflow.

## Inclusion and enumeration

Agents enumerate PRs across all states, dates, base branches, and authors, then
screen titles, bodies, and changed-file inventories. Candidate diffs and relevant
history distinguish repairs of existing tests from ordinary new-feature tests.
The per-repository receipts record pagination and any unavailable/truncated
material. A zero-PR or zero-match repository remains in the coverage table.

Include explicit suite audits, focused repairs, substantive test repairs inside
broader product work, and explicit changes to testing or evaluation strategy.
Ordinary feature coverage alone, dependency bumps, lint-only edits, and CI
scheduling/cancellation-only changes are not included. Relevant neighboring
experiments can remain in source reports; manifest adjustments identify records
the synthesis treats as adjacent context rather than matching PRs.

An attempt qualifies even when unmerged, superseded, withdrawn before its current
head, or unsuccessful. Source reports identify such cases. A component PR and
the PR that incorporates it are separate PR records, not independent successful
improvements. The count is PR records, not discoveries or distinct interventions.

## Evidence boundaries

This is a historical review, not a rerun of every repository's test suite or
mutation experiment. The source reports distinguish directly inspected diffs,
archived fixtures, Git history, and hosted job results from author-reported
measurements. A merged state or green CI run does not establish test quality.
Missing CI records are not evidence that a test passed or failed.

PR state is the state observed during each repository's review, rather than an
atomic GitHub-wide snapshot. PRs created after that enumeration, including the
PR carrying this catalogue, are outside that repository's historical corpus.
The reports are intentionally detailed source records rather than a uniform
API schema; the manifest and catalogue provide the consolidated view.

Private repositories were included in discovery. Their identifiers, PR details,
and raw evidence remain in local audit records, outside this public repository.
Only aggregate private counts are present in the manifest.
