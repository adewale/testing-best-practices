# Keyboardia test audit

At `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a`, I surveyed all 58 sampled paths across the nine strata of the 370-file inventory. All 58 base blob IDs matched. I inspected declarations, imports, assertions and execution gates, followed selected fixtures and production callers, and ran 42 sampled files locally. [File-by-file review and execution ledger](/workspace/test-audit-replay-v2/subjects/f5740f900f52bf30/work/evidence/survey.tsv)

## Prioritized findings

1. **The macOS visual job was cancelled before checkout.** CI run `45018066984` records zero steps and an unsupported runner configuration. The three Holby screenshots require Darwin, Chromium and the mock API. Linux visuals passed. Stack A Identity was skipped under its PR-only condition. See `work/ci-snapshot.json:1476`, `:1498`, `:1602`, `.github/workflows/ci.yml:166`, `:654` and `app/e2e/populated-visual.spec.ts:10`.
2. **Repaired the rotating Worker persistence test.** Run `45182094013` passed rotating unit tests and preserved the integration failure. The seed reproduced locally. All 99 accepted commands satisfied the GET, KV and socket checks, but the workload minimum was 100. The repair draws successive schedules from each seed until it reaches that floor, observes both WebSocket write kinds and disconnects while KV lags. It allows up to one extra batch’s worth of cases, then reports any missing requirement. A diagnostic copy recorded 99 → 99 → 101 commands and four dirty disconnects. See `work/ci-snapshot.json:1669`, `:1813`, `:1879`, `.github/workflows/property-seed.yml:100` and the [repaired model](/workspace/test-audit-replay-v2/subjects/f5740f900f52bf30/work/repo/app/test/integration/state-machine-fuzz.test.ts:492).
3. **Four recorder waveform tests pass with production peaks flattened to zero.** I ran `../runtime/run-unit.sh src/components/waveform-peaks.test.ts` against that fault. The four tests exercise a calculation defined inside the test. The recorder draws from a separate implementation with a per-buffer, per-width cache. See `app/src/components/waveform-peaks.test.ts:17`, `app/src/components/Waveform.tsx:53` and `app/src/components/Recorder.tsx:230`.

## Existing tests worth retaining

- Concurrent toggle tests derive all 32 grid cells from input parity, check sequence numbers on three real sockets and compare fresh snapshots with REST. Input parity catches a wrong grid shared by every client. See `app/test/integration/overlap-fuzz.test.ts:218`, `:254` and `:294`.
- A client persistence test holds one save in flight and verifies the next request carries the later edit. A native audio test counts rendered onsets and checks them against an independent 125 ms per sixteenth at 120 BPM. The persistence test passed locally. The hosted native-render step passed. See `app/src/sync/session.persistence.test.ts:87`, `app/src/audio/session-render-conservation.render.test.ts:87` and `work/ci-snapshot.json:249`.

## Verification

Commands ran from `work/repo/`. Both seeded selections used `FC_SEED=45182094013 FUZZ_SEEDS=45182094013`.

| Selection | Observed result |
|---|---|
| Base `../runtime/run-unit.sh` and `../runtime/run-worker.sh` | 343 passed in 23 files and 84 passed in eight |
| `xargs -a ../evidence/unit-files.txt ../runtime/run-unit.sh` | 463 passed in 34 files |
| `../runtime/run-worker.sh --all` | 131 passed in all 11 Worker files |
| Seeded `../runtime/run-worker.sh state-machine-fuzz.test.ts -t 'model: read-your-writes'` | One failed before, one passed after, five filtered each time |
| Seeded `../runtime/run-worker.sh state-machine-fuzz.test.ts overlap-fuzz.test.ts eviction-recovery.test.ts` | 28 passed in three files after repair |

In disposable copies, serving stale KV at `app/src/worker/live-session.ts:370` made both model versions shrink to one tempo write of 60. GET returned 120. The CLI in `app/scripts/promote-pbt-counterexamples.ts:80` saved the schedule and replay failed at known case 0. Removing the swing generator also failed the repaired model, with zero swing writes despite 247 accepted commands. Only the model test changed in the repository. `git diff --check` passed.

Offline `npm run validate:test-quality` passed the antipattern, linkage and dead-export checks before Playwright collection stopped on the missing package. Worker `tsc -p tsconfig.json --noEmit` produced the same six configuration diagnostics on base and repair. Browser, native audio and full-suite conclusions rely on source and the supplied CI records. Raw results are in `work/evidence/`.
