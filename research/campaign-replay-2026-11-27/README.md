# Four-arm campaign replay and larger-suite audit

A [later same-day comparison](../mermaid-skill-comparison-2026-11-27/README.md) applies current skill 0.3.3 and OpenClaw to the full Agentic Mermaid source. That separate audit does not rerun the historical R05 case or change the four-arm results below.

The revised skill and development tools are frozen at `300a179a1d622b66134409356add50e81393e95e`. The [protocol](controller/protocol.md), [freeze receipt](controller/freeze.json), [input manifest](controller/source-manifest.json) and [independent pre-run review](controller/protocol-review.md) were fixed before any subject was dispatched. The completed [results](RESULTS.md) retain both successful and failed attempts; [execution metadata](controller/execution.json) and the [artifact hash index](evidence-index.json) accompany the raw evidence.

The study attempted 48 fresh Astra 6.2 Max subjects and 12 fresh arm-blinded judges, with no retries. It obtained 45 reports, 11 completed judgments and one failed judge attempt. Three execution subjects were interrupted before reporting; another delivered a report before its backend status became unavailable. Thirty-six subjects revisit the same nine historical planning cases with four guidance packages: none, PR41 at `379e0d9`, the revised candidate and OpenClaw at `9fd0b7d`. Twelve subjects were assigned one actual bounded repair in three larger native suite samples. The historical cases previously saturated at 9/9 in all three tested arms. They establish continuity rather than autonomous campaign prevention.

| Repository | Inventory | Test contents available | Priority sample |
|---|---:|---:|---:|
| Agentic Mermaid | 660 | 58 | 58 |
| Keyboardia | 370 | 370 | 58 |
| PDA | 155 | 56 | 56 |

These are reconstructed known-audit cases with purposive anchors and reproducible stratified sampling. Supplied CI observations and native command guides can direct discovery. The inventory definitions differ across repositories; none of the counts establishes how much a subject read or executed. The experiment tests OpenClaw's bounded ordinary audit path. Its full multi-reviewer subsystem campaign is outside this assignment.

The larger context corrected a previous Mermaid finding before the study: Section B explicitly promises byte-exact regenerated output, and PNG policy independently promises repeatability under pinned conditions. Pixel equivalence alone cannot replace those contracts. This correction is part of the frozen retention criteria.

## Main findings

The fixed historical screen scored none 7/9, earlier PR41 9/9, revised candidate 8/9 and OpenClaw 9/9. The candidate missed full-caller rejection coverage. A post-replay 0.3.3 follow-up adds explicit guidance and E79's deterministic regression; it has no fresh model comparison.

Nine larger-suite reports delivered concrete repairs, independently exercised against faults and permitted changes. Different arms chose different legitimate boundaries. Three interrupted attempts and a failed Keyboardia judge prevent a complete balanced comparison. There is no evidence of revised-skill superiority. See [project-level contrasts and limitations](RESULTS.md#larger-suite-execution), including the distinction between a JSON checker improvement and model performance.

## Separately verified tool repairs

[Behavioral grader controls](tool-controls/behavioral-fixtures.json) retain the actual pre-repair mistakes and the revised 26-case matrix for E08, E33 and E74. Candidate tests execute against reference behavior and specified faults. External candidates use an offline bounded container. Real SQLite execution is observed per test; full assertion-value provenance and hostile report tampering are outside that check.

[E75 and runner controls](tool-controls/e75-and-judge.json) retain the 4/9 to 9/9 calibration result, judge exit 0/7 transcripts, same-second receipt behavior and unavailable-oracle propagation. These deterministic repairs are separate from any model/skill effect. [E79 controls](tool-controls/pipeline-rejection.json) capture the post-replay rejection-path repair.

## Retained inputs

The [independent input verification](controller/public-input-verification.json) verifies all five archives and 2,020 Git-blob receipts. The [archive manifest](inputs/archives.json) identifies deterministic tarballs containing complete public source packets, preparation recipes, controls, baseline receipts, licenses, exact OpenClaw guidance and subject packets. The small vendored Mermaid helpers include their notices. Installed dependency trees, image layers, credentials and private portfolio audits are excluded. Runtime dependencies have pinned recipes and hashes; obtaining them requires the named package/image sources.

To inspect an archive, use `tar -tzf inputs/<name>.tar.gz`. To verify the retained packets, extract the three repository archives under `preparation/<name>/`, the OpenClaw archive under `openclaw/`, and the packet archive under `subjects/`. Keep the published `controller/` and `runtime-smoke/` beside them, then run `python3 -B controller/build_packets.py verify`. This checks the retained inputs; per-cell work trees are not in the packet archive.

To reconstruct all work trees, use a second empty directory. Extract the three repository archives and OpenClaw archive in the same layout and copy `runtime-smoke/`. Copy only `controller/{build_packets.py,control_run.py,protocol.md,protocol-review.md,grading-b.md}` from this record. From that directory run `python3 -B controller/build_packets.py prepare --candidate 300a179a1d622b66134409356add50e81393e95e --repo /absolute/path/to/testing-best-practices`, then `python3 -B controller/build_packets.py verify --work`. The repository must contain the pinned Git history. Do not copy `freeze.json`, previous outputs or live trial directories into a fresh reconstruction before preparation: the guard intentionally refuses to overwrite retained experiments. Dependency provisioning is a separate step in the case runtime guides.

Raw transcripts, TSV empty columns and patches retain their original whitespace so their recorded bytes remain verifiable.

All evidence here concerns public repositories. The companion portfolio audit includes private projects and remains outside this public research folder.
