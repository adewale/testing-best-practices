# Current-skill comparison on Agentic Mermaid

[Results and verified findings](RESULTS.md) · [Skill-content comparison](SKILL-COMPARISON.md) · [Our original audit](ours-audit/report.md) · [OpenClaw's original audit](openclaw-audit/report.md)

Two fresh Astra 6.2 Max agents independently applied the ordinary audit workflows to the same full Agentic Mermaid source at `f49196e7`. Each had 40 minutes, Bun 1.4.4 and its own frozen-lockfile installation. Both returned without retries. They produced six distinct test-gap findings, a coverage setup defect and a separate CLI/help mismatch requiring an output-policy decision. Parent native controls reproduced their material contrasts. This is a descriptive one-replicate comparison, not a reliability ranking.

Our skill was 0.3.3 at `7ea8838f`; OpenClaw was pinned at `dff00f34`. See [protocol](protocol.json), [common brief](task-packets.json), [source hashes](source-manifest.json), [guidance hashes](guidance-manifest.json), [original-output seal](audit-output-seal.json) and [publication hash index](evidence-index.json). Source inventories identify availability; the audit read/command ledgers are self-reported and disclose narrower actual scope.

## Reproduce the inputs and controls

Use a disposable clone of `https://github.com/adewale/agentic-mermaid.git`. Fetch and detach at `f49196e7f5d6d2f0970a4a76fe62644ee5e9d004`, and verify tracked content against source-manifest.json. Install Bun **1.4.4** and run `bun install --frozen-lockfile`. The original setup used 614 packages, Node 24.22.3 and offline Chromium 156 at `/usr/bin/chromium`. Native PNG runs used the installed Noto CJK directory `/usr/share/fonts/opentype/noto`; the workflow defect concerns its absent default WenQuanYi prerequisite.

Read each original report and patch before replaying it. Apply one production fault or permitted-change patch at a time using `git apply`, run the recorded focused command, then restore the touched source. Test-repair patches affect separate files and can be applied alongside their fault. Do not edit a checkout during a running test command. Full unit shards remain with the target's normal CI policy.

Our TypeScript probes in `ours-audit/evidence/probes/` import `./src`; copy the chosen probe to the disposable repository root before running it with Bun. The color witness in `openclaw-audit/evidence/` uses the current working directory's production headers/CSS and Playwright. It needs a short, private temporary path for Chromium's Unix socket. The CLI and graph witnesses also resolve the target from the current directory. Exact commands, process exits, timings, original paths, source changes and setup failures are in each command ledger.

The parent verification scripts and raw receipts are under `verification/evidence/`. They retain the original execution workspace prefix and are records of the observed run. Adapt that prefix and the private runtime path when replaying elsewhere. Their independent worktree borrowed one completed subject's installation; it did not obtain another independent dependency build. No live model, provider, production deployment or paid benchmark is needed to replay the technical controls.

The copied OpenClaw guidance and both public-source licenses are retained with [attribution](ATTRIBUTION.md). Full source/dependency worktrees, caches, browser configuration and credentials are excluded. Raw transcripts, patch context and tables retain original whitespace so evidence hashes remain verifiable. Agentic Mermaid production, test and support files were left unchanged; proposed repairs exist only as evidence patches.
