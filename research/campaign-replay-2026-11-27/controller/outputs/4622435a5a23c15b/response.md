# Keyboardia test audit

**All 50 original tempo and swing tests passed with the mobile sliders’ touch callbacks swapped.** A 30-pixel upward Tempo drag then sent 135 to the swing callback. Four tests calculated values locally or called their own spy. Their swing fixture expected 80 from a starting value of 50. The real slider sends 59. See the pinned `app/src/components/tempo-change.test.ts:421`, `swing-control.test.ts:402`, `transport-drag.ts:4` and `StepSequencer.tsx:226`.

I replaced those four cases with four jsdom cases that render `TransportBar`. They check which callback receives each successive touch edit, lower-bound clamping, and primary- and secondary-button drags. The two-client browser test drives a separate desktop range input. I updated the pointers in `app/e2e/core.spec.ts:36` and `app/e2e/phase3-refactoring.spec.ts:180`. The diff adds 63 test/comment lines, removes 127 and changes zero production lines. See `app/src/components/TransportBar.test.tsx:28` and `:39`, and `app/e2e/multiplayer.spec.ts:140`.

### Open findings, in priority order

1. **The weekly Worker soak failed its work quota.** Replaying run `45182094013` exercised all nine transition kinds and three dirty disconnects. Every per-command state check passed. The final count was 99 against a minimum of 100. Guarantee the required work and transitions when generating schedules. The workflow preserved the failure after uploading diagnostics. See `../ci-snapshot.json:1879`, `.github/workflows/property-seed.yml:100` and `app/test/integration/state-machine-fuzz.test.ts:315`, `:494`, `:546`.
2. **The Darwin visual lane has a coverage gap.** CI run `45018066984` cancelled the macOS job before any steps because the runner configuration was unsupported. The three Holby screenshot cases require Darwin. Stack A Identity also skipped under its separate pull-request gate. See `../ci-snapshot.json:1498` and `:1602`, `.github/workflows/ci.yml:166` and `:675`, and `app/e2e/populated-visual.spec.ts:10`.
3. **The demo scale check accepts an out-of-scale note.** I changed the first active string note from MIDI 62 to 63, outside the authored D natural minor scale and inside the instrument’s 33–88 range. All five demo tests passed. The assertion checks range alone. See `app/scripts/demo-sessions/whisper-to-roar.json:28` and `:59`, and `app/src/data/phase44-demo-session.test.ts:105`.

### Existing tests worth keeping

- The three-socket Worker test derives toggle parity from sent inputs, checks every client’s sequence numbers, and compares snapshots with REST. The cold-disconnect test reads KV at 120 before hibernation and at 145 after the socket close wakes the Durable Object. See `app/test/integration/overlap-fuzz.test.ts:226`, `:254`, `:294` and `eviction-recovery.test.ts:761`.
- The client persistence tests switch sessions during a pending save and check the outbound destination. They also hold a fetch open and verify the newer edit reaches the next request. See `app/src/sync/session.persistence.test.ts:64` and `:87`.
- The native render test counts PCM onsets and checks each against a literal 125 ms step at 120 BPM, within 10 ms. The pinned CI audio-render step passed. See `app/src/audio/session-render-conservation.render.test.ts:87` and `../ci-snapshot.json:249`.

### Local evidence and scope

I surveyed assertions and setup across all 58 paths in `../sample.tsv`, spanning nine strata of the 370-file inventory at `aa67598560f8eaf2509a3ad4bc73edee2f8bea8a`. All 58 original blob hashes matched. I executed 43 sampled files. The 13 browser/identity specs, native render and real codec/browser pipeline received source review only. The component proof ends at DOM-event delivery.

The commands ran from `work/repo/` unless indicated. Counts overlap.

```bash
U=../runtime/run-unit.sh
W=../runtime/run-worker.sh
mapfile -t unit_files < <(awk -F '\t' '
  $1 ~ /^app\/(src|test)\// && $1 !~ /\/integration\/|\.render\.test|sample-pipeline-real-contract|skill-eval-manifest/ {
    print substr($1, 5)
  }' ../sample.tsv)
```

| Command or selection | Observed result |
|---|---|
| `$U`, `$W`, `$W --all` | Default unit passed 343 tests in 23 files before and 341 after two tempo cases moved outside that fixed list. Sampled Worker passed 84 in eight files. All Worker passed 131 in 11 before and after. |
| `$U src/components/{tempo-change.test.ts,swing-control.test.ts}` | Original 50/50 passed with the touch callbacks swapped. |
| `$U src/components/{TransportBar.test.tsx,tempo-change.test.ts,swing-control.test.ts}` | Swapping touch callbacks failed exactly the two touch cases. Removing the mouse-button guards separately failed exactly the two mouse cases. Restored code passed 50/50 in 4.41 s. The new file alone passed 4/4 in 1.28 s with one worker. |
| `FC_SEED=45182094013 FUZZ_SEEDS=45182094013 $W {state-machine-fuzz,overlap-fuzz,eviction-recovery}.test.ts` | 27 passed, one quota failure. |
| `$U "${unit_files[@]}" src/components/{TransportBar.test.tsx,swing-control.test.ts}` | 490/490 in 36 files, including all 34 sampled ordinary unit files. |
| `$U src/data/phase44-demo-session.test.ts` | 5/5 passed with the out-of-scale fixture. |
| From `app/`, `node node_modules/vitest/vitest.mjs run --project verification-tooling test/skill-eval-manifest.test.ts` | 12/12 passed. |

`git diff --check` passed and `git hash-object` verified both mutated files against `../source-manifest.tsv` after restoration. Under `npm run validate:test-quality`, the antipattern, subject-link and dead-export checks passed. The final collector lacked Playwright. The provisioned app also lacked ESLint for `npm run lint` and React/Node declarations for `npm run typecheck`.
