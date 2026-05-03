# Lessons from github.com/tigerbeetle (TigerBeetle)

> Distributed financial accounting database. Famous for assertion density and deterministic simulation testing.
> Date: 2026-05-03

---

## Who They Are

TigerBeetle builds a distributed double-entry accounting database in Zig. Their `TIGER_STYLE.md` and the VOPR simulator are widely cited as state-of-the-art for testing systems where bugs cost money. The lessons here are extracted from `docs/TIGER_STYLE.md` and the public TigerBeetle docs/blog.

## 1. Assertions as the Primary Testing Substrate

Assertions are not "extra checks" — they are the structure that makes everything else (fuzzing, simulation) productive.

- **Density target**: *"a minimum of two assertions per function"* on average.
- **Pair assertions across paths**: *"For every property you want to enforce, try to find at least two different code paths where an assertion can be added."* Two independent witnesses make a bug harder to hide.
- **Positive AND negative space**: *"assert the positive space that you do expect AND the negative space that you do not expect."* Don't only check what should be true; check what must not be true.
- **Split compounds**: prefer `assert(a); assert(b);` over `assert(a and b);` — the failure tells you which clause died.
- **Crash on assertion failure**: *"the only correct way to handle corrupt code is to crash."* Operating errors are handled; programmer errors abort.

The animating idea:

> *"Assertions downgrade catastrophic correctness bugs into liveness bugs. Assertions are a force multiplier for discovering bugs by fuzzing."*

A fuzzer is only as good as the assertions it can trip. Investing in assertions multiplies every fuzzing/simulation hour you spend later.

## 2. VOPR — Deterministic Simulation Testing

VOPR (Viewstamped Operation Replicator) runs the entire cluster against simulated time, network, and storage. Every nondeterministic source is stubbed: *"clock operations, network communications, disk I/O."*

- **Reproducibility = seed + commit**: *"Because our simulator is deterministic based on a seed number and the Git commit, we can perfectly reproduce any bugs discovered in testing for easy local debugging."* CI prints a failing seed; you replay locally and get the identical bug.
- **Time dilation**: *"One minute of VOPR time is equivalent to days of real-world testing."* In one demo, *"3.3 seconds of VOPR simulation gives you 39 minutes of real-world testing time."*
- **Continuous fleet**: TigerBeetle runs *"10 simulators continuously, 24/7"* burning seeds.

**Lesson**: For any system with concurrency or I/O, hide the clock, network, and disk behind seams you can replace with deterministic fakes. The seed becomes a perfect bug repro.

## 3. Tiered Fault Injection

VOPR doesn't just toggle "chaos: on/off." It runs progressively harsher scenarios:

1. **City Breeze** — perfect conditions, no faults.
2. **Red Desert** — Jepsen-grade: *"high storage and network latency, process crashes, and a flaky network."*
3. **Radioactive** — *"up to 8% corruption probability on the storage read path, and 9% corruption probability on the storage write path — for each replica."*

**Lesson**: Most projects test only the happy path or full chaos. The middle tier is where real production bugs live — degraded but not catastrophic.

## 4. Cross-Replica Equivalence as an Oracle

Beyond per-call assertions, VOPR checks invariants that span the cluster: *"replicas' data files are designed to be byte-for-byte identical across caught-up nodes."*

**Lesson**: When you don't have a reference implementation to diff against, look for an internal equivalence oracle — replica equality, idempotency, encode→decode round-trip, commutativity. Cheaper than a model, and catches more.

## 5. Test Data That *Becomes* Invalid

> *"Tests must test exhaustively, not only with valid data but also with invalid data, and as valid data becomes invalid."*

The "becomes invalid" clause is the unusual part. Most test suites cover (a) valid input and (b) input that was always bad. They miss the transition: TOCTOU windows, post-corruption state, post-partition reads, stale references after a delete.

**Lesson**: For each invariant, write at least one test where the data starts valid, mutates, and the system has to notice.

## 6. Don't Trust the Fuzzer

> *"Assertions are a safety net, not a substitute for human understanding. With simulation testing, there is the temptation to trust the fuzzer. But a fuzzer can prove only the presence of bugs, not their absence."*

Build the mental model first. Encode it as assertions. *Then* let the simulator try to violate it. A green VOPR run is not a proof of correctness — it's evidence that this seed didn't find a counterexample.

## Key Insights

1. **Assertions are infrastructure**, not decoration. Two per function, paired across paths, positive and negative space.
2. **Determinism is a testing feature**: stub clock/network/disk, key everything off a seed, get perfect repros.
3. **Fault injection in tiers** beats binary chaos — the middle tier catches the most bugs.
4. **Find a cross-instance oracle** (replica equality, round-trip, idempotency) instead of writing a reference model.
5. **Test the transitions**: data that becomes invalid, not only data that starts invalid.
6. **The fuzzer proves presence, not absence** — keep the human mental model in the driver's seat.
