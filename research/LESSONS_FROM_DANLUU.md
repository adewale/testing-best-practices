# Lessons from github.com/danluu (Dan Luu)

> Ex-hardware engineer (FPGA/CPU verification) turned software writer. Author of danluu.com/testing/.
> Date: 2026-06-09

---

## Who He Is

Dan Luu came to software from hardware verification, where exhaustive automated testing is mandatory rather than optional. Unlike the other practitioners in this corpus, his contribution isn't a test framework — it's a *thesis*, argued in [danluu.com/testing/](https://danluu.com/testing/) and demonstrated by a handful of small, pointed repos. The thesis: software teams spend their limited testing effort on the least effective thing (hand-written example tests) and almost never reach for the techniques that find the most bugs per hour (random and coverage-guided generation).

## The Core Thesis: We Test Inefficiently

In hardware, hand-written tests are 1–25% of test effort and find far fewer bugs than automated generation; the rest is random and coverage-driven. Software defaults to the opposite ratio — not from analysis, but from unawareness that alternatives exist and are cheap to try.

- **Most critical bugs are shallow.** He leans on Yuan et al. ("Simple Testing Can Prevent Most Critical Failures"): ~58% of catastrophic distributed-systems failures were reachable by simple tests of error-handling paths. The implication isn't "tests are hard," it's "the cheap tests we skip would have caught the expensive failures."
- **Dedicate compute to test generation.** Hardware shops run thousands of machines on test generation. Given developer salaries, even one machine left running a fuzzer is trivially cost-justified — yet software devs balk at a multi-hour test run.
- **Coverage metrics lie.** Line/function coverage can hit 100% while missing serious bugs; path/state coverage is the real target but is intractable, which is why AFL's edge-tracking *approximation* matters.

**Lesson**: Before writing the 40th hand-crafted example test, ask whether an hour of random generation would find more. Usually it would.

## Fuzz.jl — "World's Dumbest Fuzzer"

A few-minutes-of-effort, maximally-naive random fuzzer for Julia. `fuzz_fns` picks random functions and feeds them random arguments (`generate_rand_strings`, etc.), watching for crashes and hangs. No coverage guidance, no grammar awareness, no minimization — Csmith and jsfunfuzz it is not. The README says it plainly:

> You probably don't want to use this. I spent a few minutes writing the most naive possible fuzzer, to see if it would turn up any bugs. Turns out, this terrible method can generate bugs faster than I can debug them.

It produced a string of real, confirmed Julia bugs — parser location-tracking errors, segfaults, and hangs — captured with gdb backtraces (`sandbox/.../segfaults`) and filed upstream (e.g. JuliaLang/julia#8353).

**Lesson**: The dumbest fuzzer that exists beats the sophisticated one you keep meaning to write. Don't let "I should build a proper generator" block the hour of work that finds real bugs today. (His 2026 update sharpens this: heavyweight property/fuzz *frameworks* carry execution-speed overhead that often outweighs their cleverness — a tight hand-rolled random loop frequently wins. The transferable insight is "randomized inputs work surprisingly well," not any particular framework.)

### The harness mechanics matter more than the generator

The interesting engineering in Fuzz.jl isn't the random generator — it's the three tricks that keep a dumb fuzzer *productive*:

- **Seed from a CLI arg** (`srand(int(args[1]))`) so any run is reproducible — a found bug is a seed, not a one-off.
- **Run every call in a try/catch and log the inputs** so one crash doesn't stop the run, and failures can be replayed (`reproduce-hang-bug.jl`: "everything was run in a try/catch block to throw away exceptions").
- **Keep a denylist** (`banned.txt`) routing around known hangs/slow/noisy operations (`sprandn` hangs, `readlines` blocks on STDIN, `bessely` is too slow) so the fuzzer spends its time finding *new* bugs instead of re-hitting stuck ones.

**Lesson**: A fuzzer is only as good as its harness. Determinism (seed), survivability (catch + log + replay), and a denylist for known-bad sinks are what turn "random inputs" into a tool that keeps finding bugs overnight.

## The dets / QuickCheck Story

A recurring, mysterious error in distributed-database (`dets`) code went un-diagnosed for ~a month of manual investigation. QuickCheck found and characterized it in **under a day** — five reproducible bugs, each minimized to tiny inputs (one record, ≤5 calls).

**Lesson**: Property-based testing's shrinking turns "intermittent heisenbug" into "minimal deterministic reproducer." That gap — a month of staring vs. a day of generate-and-shrink — is the whole argument for PBT in one anecdote.

## csv — Differential Testing of a "Simple" Format

A test harness that runs many CSV implementations (Python, JS, R, Ruby, shell) against shared fixtures to expose how they disagree on quoting, embedded delimiters, newlines-in-fields, and special characters.

**Lesson**: "Simple" formats are where conformance/differential testing pays off most, because everyone *assumes* they agree and nobody checks. Run N implementations against one fixture set and diff the outputs. (Mirrors the differential/pirate testing in `references/differential-testing.md`.)

## fs-errors — Fault Injection on Error Paths

Tooling that injects corruption into filesystems via device-mapper (offset → sector, corrupt, observe) to reproduce old IRON-filesystem-paper results on modern systems — e.g. confirming btrfs surfaces an I/O error on a corrupted read.

**Lesson**: Test the error paths, not just the happy path. The bugs that escape are in code that only runs when something *else* already went wrong — so inject the fault and assert the system degrades correctly. This is exactly the class Yuan et al. found dominates critical failures.

## secvisor-formal-verification & kodkod-clj — The Formal-Methods Thread

Two lower-profile repos round out the picture: `secvisor-formal-verification` (formal verification of a secure hypervisor) and `kodkod-clj` (experiments with Kodkod, the SAT-based model finder behind Alloy). They connect to the article's point that distributed-systems test *generators* like BloomUnit lean on SAT solvers to produce valid orderings.

**Lesson**: Random testing and formal/automated reasoning aren't rivals — they sit on one spectrum of "let the machine explore the state space for you." When inputs must satisfy constraints (valid interleavings, well-formed configs), a solver-backed generator beats both hand-written cases and unconstrained random ones.

## post-mortems & debugging-stories — Testing Culture

Two of his most-starred repos (12k / 3.8k) are *curated collections of failures*, not code. They encode a hardware habit: every escaped bug gets a post-mortem, and the system is designed for testability up front specifically so bugs can be caught.

**Lesson**: Quality is a culture difference before it's a tooling difference. Hardware says "all bad bugs must be caught before release"; software says "some bugs will escape, that's QA's problem." Feeding production failures back into the suite as regression tests (and studying others' post-mortems) is how the cheap-test-finds-expensive-bug loop actually closes.

## Key Insights

1. **Reach for generators before more examples.** Random + coverage-guided generation finds more bugs per hour than hand-written cases; software under-uses both.
2. **The dumbest fuzzer beats the unwritten one.** A few minutes of naive random input found real, filed Julia bugs "faster than I can debug them." Ship the crude version now.
3. **A fuzzer is only as good as its harness.** Seed for reproducibility, wrap calls in try/catch + log inputs to survive and replay crashes, and denylist known hangs/slow sinks so it keeps finding *new* bugs.
4. **Most critical failures are shallow.** ~58% are reachable by simple error-path tests — so test the error paths (fault injection), not just the happy path.
5. **PBT shrinking converts heisenbugs to minimal reproducers.** Month-of-debugging → day-of-QuickCheck with ≤5-call repros.
6. **Differential-test "simple" formats.** Run many implementations against shared fixtures; the disagreements are the bugs (csv).
7. **Spend the compute.** A dedicated fuzzing machine is cheap against developer salaries; a long test run is not "too slow."
8. **Coverage numbers can be a lie.** 100% line coverage ≠ tested; edge/path approximation (AFL-style) is what correlates with finding bugs.
9. **Testing is a culture choice.** Post-mortems, design-for-testability, and treating escaped bugs as defects-in-process are upstream of any framework.
