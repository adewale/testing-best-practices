# Four-arm campaign replay and larger-suite audit

The revised skill and development tools are frozen at `300a179a1d622b66134409356add50e81393e95e`. The [protocol](controller/protocol.md), [freeze receipt](controller/freeze.json), [input manifest](controller/source-manifest.json) and [independent pre-run review](controller/protocol-review.md) were fixed before any subject was dispatched. This checkpoint does not contain model-comparison results.

The study schedules 48 fresh Astra 6.2 Max subjects and 12 fresh arm-blinded judges. Thirty-six subjects revisit the same nine historical planning cases with four guidance packages: none, PR41 at `379e0d9`, the revised candidate and OpenClaw at `9fd0b7d`. Twelve subjects perform one actual bounded repair in three larger native suite samples. The historical cases previously saturated at 9/9 in all three tested arms. They establish continuity rather than autonomous campaign prevention.

| Repository | Inventory | Test contents available | Priority sample |
|---|---:|---:|---:|
| Agentic Mermaid | 660 | 58 | 58 |
| Keyboardia | 370 | 370 | 58 |
| PDA | 155 | 56 | 56 |

These are reconstructed known-audit cases with purposive anchors and reproducible stratified sampling. Supplied CI observations and native command guides can direct discovery. The inventory definitions differ across repositories; none of the counts establishes how much a subject read or executed. The experiment tests OpenClaw's bounded ordinary audit path. Its full multi-reviewer subsystem campaign is outside this assignment.

The larger context corrected a previous Mermaid finding before the study: Section B explicitly promises byte-exact regenerated output, and PNG policy independently promises repeatability under pinned conditions. Pixel equivalence alone cannot replace those contracts. This correction is part of the frozen retention criteria.

## Separately verified tool repairs

[Behavioral grader controls](tool-controls/behavioral-fixtures.json) retain the actual pre-repair mistakes and the revised 26-case matrix for E08, E33 and E74. Candidate tests execute against reference behavior and specified faults. External candidates use an offline bounded container. Real SQLite execution is observed per test; full assertion-value provenance and hostile report tampering are outside that check.

[E75 and runner controls](tool-controls/e75-and-judge.json) retain the 4/9 to 9/9 calibration result, judge exit 0/7 transcripts, same-second receipt behavior and unavailable-oracle propagation. These deterministic repairs are separate from any model/skill effect.

## Retained inputs

The [archive manifest](inputs/archives.json) identifies deterministic tarballs containing complete public source packets, preparation recipes, controls, baseline receipts, licenses, exact OpenClaw guidance and subject packets. The small vendored Mermaid helpers include their notices. Installed dependency trees, image layers, credentials and private portfolio audits are excluded. Runtime dependencies have pinned recipes and hashes; obtaining them requires the named package/image sources.

To inspect an archive, use `tar -tzf inputs/<name>.tar.gz`. For a local reconstruction, extract the three repository archives under `preparation/<name>/`, the OpenClaw archive under `openclaw/`, and the packet archive under `subjects/`. Keep `controller/` and `runtime-smoke/` beside them. The committed builder reads the skill packages from this repository's pinned Git history; pass `--repo /absolute/path/to/testing-best-practices` explicitly in a separate reconstruction directory. Do not rebuild over retained trials. The freeze/verification code intentionally rejects overwriting the original experiment.

All evidence here concerns public repositories. The companion portfolio audit includes private projects and remains outside this public research folder.
