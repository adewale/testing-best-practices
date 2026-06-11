# Lessons from github.com/antirez (Salvatore Sanfilippo)

> Created Redis, hping, dump1090, and a family of battle-tested C data-structure libraries (rax, sds, listpack). Also writes prolifically about software quality.
> Date: 2026-06-07

---

## Who He Is

Salvatore Sanfilippo ("antirez") created Redis and a constellation of small, embeddable C libraries that Redis (and many other projects) depend on. His testing work spans three eras, and all three are worth stealing from:

1. **Differential fuzzing of data structures** — fuzz a complex structure against a trivially-correct reference that "always tells the truth."
2. **A testability-first server design** — the Redis TCL harness spins up real processes and introspects internal state through a deliberate `DEBUG` command surface.
3. **AI-as-QA-engineer** — using an agent to perform the expensive exploratory/integration testing that humans usually skip, judged against *objectives* rather than hardcoded baselines.

A throughline ties them together: **antirez allocates testing effort by reuse risk.** The reusable libraries (`rax`, `sds`) are fuzzed until "battle tested"; the teaching/demo code (`kilo`, `smallchat`) has *no tests at all*, because its value is pedagogical readability, not reuse safety.

| Repo | Kind | Tests? | Strategy |
|------|------|--------|----------|
| `rax` | radix tree (embedded by Redis) | **Heavy** | Differential fuzzing vs. hash-table + sorted-array oracles, seeded RNG, regression suite, run under Valgrind |
| `sds` | dynamic strings (embedded everywhere) | **Yes** | Assertion-macro unit tests, behind a compile-time flag |
| `redis` | the database | **Heavy** | Real-process TCL harness, encoding assertions, digest roundtrips, fuzz-vs-Tcl-model, replication-stream assertions |
| Vector Sets | approximate ANN index | **Heavy** | Recall vs. brute-force oracle (threshold, not equality); SIMD-boundary fuzzing; reload roundtrips |
| `ds4` (DwarfStar) | LLM inference engine | **Agent QA** | `AGENT.md` objective-driven exploratory testing |
| `kilo`, `smallchat` | teaching code | **None** | Intentionally untested |

---

## 1. Differential fuzzing against an oracle that "always tells the truth" (rax)

`rax` is a radix tree. It is fuzz-tested by running identical random operations against the tree **and** a dead-simple chained hash table, then asserting they agree on every observable. The oracle is introduced with this comment (`rax-test.c`):

```c
/* Simple hash table implementation, no rehashing, just chaining. This is
 * used in order to test the radix tree implementation against something that
 * will always "tell the truth" :-) */
```

The fuzz loop drives both structures and compares the **return value of every operation**:

```c
int fuzzTest(int keymode, size_t count, double addprob, double remprob) {
    hashtable *ht = htNew();
    rax *rax = raxNew();
    for (size_t i = 0; i < count; i++) {
        unsigned char key[1024];
        uint32_t keylen;
        if ((double)rc4rand()/RAND_MAX < addprob) {
            keylen = int2key((char*)key,sizeof(key),i,keymode);
            void *val = (void*)(unsigned long)rc4rand();
            /* Stress NULL values more often, they use a special encoding. */
            if (!(rc4rand() % 100)) val = NULL;
            int retval1 = htAdd(ht,key,keylen,val);
            int retval2 = raxInsert(rax,key,keylen,val,NULL);
            if (retval1 != retval2) { /* report mismatch */ return 1; }
        }
        /* ...remove with remprob, comparing htRem vs raxRemove... */
    }
```

Then three more independent agreement checks: total **size**, and **per-key value** by iterating the tree and looking each key up in the oracle:

```c
    if (ht->numele != raxSize(rax)) { /* count mismatch */ return 1; }
    raxIterator iter; raxStart(&iter,rax); raxSeek(&iter,"^",NULL,0);
    while(raxNext(&iter)) {
        void *val1 = htFind(ht,iter.key,iter.key_len);
        void *val2 = raxFind(rax,iter.key,iter.key_len);
        if (val1 != val2) { /* per-key value mismatch */ return 1; }
    }
```

> **Lesson:** Test a complex data structure against a brain-dead reference that is obviously correct, drive both with the same random operations, and assert they agree on *every* observable — per-op return code, total size, and per-key value. Bias the generator toward special cases (here, forcing `NULL` ~1% of the time) instead of leaving them to chance.

### Reproducible fuzzing: a deterministic, platform-independent RNG

antirez does not use libc `rand()` — its sequence differs by platform, which makes failures non-reproducible. He ships an RC4-based RNG seeded with a fixed value, so the entire fuzz run replays identically on any machine:

```c
/* A simple RC4 based RNG that sucks less than the certain libc rand()
 * implementations, notably the incredibly bad MacOS() implementation. */
...
int main(int argc, char **argv) {
    rc4srand(1234);
```

> **Lesson:** Make fuzzing reproducible. Seed a deterministic, platform-independent RNG with a fixed value so a failing run can be replayed exactly — libc `rand()` varies between platforms and destroys reproducibility.

### Many key distributions, escalating scale

A single key shape exercises only a narrow slice of a radix tree (fan-out, prefix compression, and node splits all depend on key structure). The generator is parameterized by mode — dense integers, unique-alphanumeric (via a Feistel permutation so keys are "random-looking" but collision-free), random bytes, small charset, and long `"AAAA..."` chains — and `main()` runs every mode at 100k → 1M → 10M operations:

```c
#define KEY_INT 0
#define KEY_UNIQUE_ALPHA 1
#define KEY_RANDOM 2
#define KEY_RANDOM_ALPHA 3
#define KEY_RANDOM_SMALL_CSET 4
#define KEY_CHAIN 5
```

```c
    size_t numops = 100000, cycles = 3;
    while(cycles--) {
        if (fuzzTest(KEY_INT,numops,.7,.3)) errors++;
        /* ...every mode... */
        numops *= 10;   /* 100k, 1M, 10M ops */
    }
```

There is also a "Redis Cluster" fuzzer that mimics *production-shaped* keys (binary hash-slot prefix + hex suffix with shared prefixes) whose goal is purely to crash the tree or trip Valgrind.

> **Lesson:** Drive fuzzing with several deliberately different input distributions and at escalating scales — each shape and size exercises structurally different code paths. Include one distribution shaped like your real production data.

### Testing iteration order against a *sorted* oracle

Ordered iteration gets a second oracle: a flat array sorted with the exact ordering rule the rax iterator uses. The test fires a random seek operator at a random key, walks a random direction, and asserts the tree iterator and the array agree at every step — *including agreeing about where iteration ends*:

```c
    char *seekops[] = {"==",">=","<=",">","<","^","$"};
    char *seekop = seekops[rc4rand() % 7];
    raxSeek(&iter,seekop,key,keylen);
    int seekidx = arraySeek(array,count,key,keylen,seekop);
    /* ...walk both, assert each returned key matches and both hit EOF together... */
    if (array_res != rax_res) { /* iterators disagree about EOF */ return 1; }
```

Alongside the fuzzing, exact expected results are pinned in a table-driven unit test (`{"rpxxx",5,"<=", "romulus"}`, `{"rub",3,">", "rubens"}`, ...).

> **Lesson:** To test ordered iteration/seek, mirror the structure into a sorted array, then randomly seek with *every* operator (`>=`, `<`, `^`, `$`, ...) and walk both directions, asserting agreement on each key and on EOF. Pair the fuzzing with a small table of pinned exact cases.

### Every fixed bug becomes a named regression test, run under Valgrind

```c
/* Regression test #2: Crash when mixing NULL and not NULL values. */
int regtest2(void) {
    rax *rt = raxNew();
    raxInsert(rt,(unsigned char *)"a",1,(void *)100,NULL);
    /* ...the exact minimal sequence that used to crash... */
    raxFree(rt);
    return 0;
}
```

Several regression tests "always return success but trigger a Valgrind error" — the harness is explicitly designed to run under Valgrind, which acts as the real oracle for memory bugs.

> **Lesson:** Turn every fixed bug into a tiny named regression test that reproduces the exact original failure, and run the whole suite under a sanitizer/Valgrind so memory-safety violations are caught even when the program returns "success."

---

## 2. Minimal in-file unit tests behind a compile flag (sds)

`sds` uses a 15-line homegrown framework — two macros, two counters, no dependencies — and keeps the tests in the same `.c` file, gated behind a compile-time flag so they cost nothing in production:

```c
#define test_cond(descr,_c) do { \
    __test_num++; printf("%d - %s: ", __test_num, descr); \
    if(_c) printf("PASSED\n"); else {printf("FAILED\n"); __failed_tests++;} \
} while(0);
```

```c
    test_cond("Create a string and obtain the length",
        sdslen(x) == 3 && memcmp(x,"foo\0",4) == 0)
```

> **Lesson:** For a straightforward library, a description-first `test_cond(description, expr)` macro that counts pass/fail and `exit(1)`s on any failure is enough. Keep the tests in-file behind a compile-time flag so they ship with the source but add nothing to production builds.

---

## 3. A testability-first server: the Redis TCL harness

Redis is tested by spinning up **real `redis-server` processes** and asserting on observable, introspectable state. antirez designed the server's command surface to make this possible.

### assert_encoding — assert the optimization actually engaged

```tcl
proc assert_encoding {enc key} {
    if {$::ignoreencoding} { return }
    set val [r object encoding $key]
    assert_match $enc $val
}
```

```tcl
    assert_encoding intset myintset
    assert_encoding listpack mysmallset
    assert_encoding hashtable mylargeintset
```

> **Lesson:** Don't trust that a performance optimization engaged — assert on the observable internal state (`OBJECT ENCODING`) so a regression that silently falls back to a slower or larger representation fails the test loudly.

### DEBUG RELOAD + digest: characterization testing built into the server

A content digest of the whole dataset, plus a canonical CSV dump, lets a test assert that serialize → deserialize is identity-preserving. `check_consistency` snapshots the digest, runs an arbitrary block (a reload), and re-checks:

```tcl
proc check_consistency {dumpname code} {
    set dump [csvdump r]
    set sha1 [debug_digest]
    uplevel 1 $code
    set sha1_after [debug_digest]
    if {$sha1 eq $sha1_after} { return 1 }
    # Failed: write both csvdumps to /tmp for inspection
}
```

The same harness covers both RDB (`r debug reload`) and AOF (`r bgrewriteaof` + `r debug loadaof`) by passing a different code block — and `--accurate` scales the dataset from 1,000 to 10,000 ops.

> **Lesson:** Build a content-addressable fingerprint of your entire state (a digest) plus a human-readable dump, then assert serialize→reload is the identity. This is characterization testing that catches persistence bugs no hand-written assertion would, and it generalizes over RDB/AOF by parameterizing the "reload" step.

### The DEBUG command surface as a deliberate testability affordance

antirez exposed internal state and forced state-transitions through `DEBUG` subcommands *specifically so tests can introspect and control the engine*:

| DEBUG subcommand | What it gives the test |
|---|---|
| `RELOAD` / `LOADAOF` | Force an in-process RDB/AOF roundtrip |
| `DIGEST` / `DIGEST-VALUE` | Content fingerprint of the dataset / one key |
| `QUICKLIST-PACKED-THRESHOLD` | Force a rare internal code path at small sizes |
| `SET-ACTIVE-EXPIRE` | Disable background expiry so expiry logic is deterministic |
| `DICT-RESIZING` | Pin rehashing state |
| `SLEEP` | Block the server to test timeouts/blocking |
| `OBJECT` / `OBJECT ENCODING` / `REFCOUNT` | Read internal object metadata |

Crucially, the helpers that use this surface short-circuit to a dummy value when the `needs:debug` tag is denied, so the same test file still runs against a hardened build that omits `DEBUG`.

> **Lesson:** Make your system testable from the outside by exposing internal state and forced transitions through a first-class but namespaced/guarded command surface. Tests become introspective and deterministic instead of relying on timing, reflection, or rebuilding the engine — and gating the surface keeps it out of hardened production builds.

### start_server: real processes, tagged for the CI matrix

```tcl
start_server [list overrides [list save ""]] {
    r config set list-compress-depth 2
    ...
}
```

Tests are tagged (`slow`, `solo`, `needs:repl`, `needs:debug`, `external:skip`, ...) so the CI matrix can include or exclude whole classes by environment.

> **Lesson:** Test against the real process with real config, and tag tests by what they need so the CI matrix can run or skip whole classes by environment. Integration fidelity beats mocking the very subsystem under test.

### Poll a predicate, never sleep

```tcl
proc wait_for_condition {maxtries delay e _else_ elsescript} {
    while {[incr maxtries -1] >= 0} {
        set errcode [catch {uplevel 1 [list expr $e]} result]
        if {$errcode == 0} { if {$result} break } else { return -code $errcode $result }
        after $delay
    }
    if {$maxtries == -1} { uplevel 1 $elsescript }
}
```

Built on top: `wait_for_sync` (replica `master_link_status eq "up"`), `wait_for_ofs_sync` (offsets match), `wait_for_blocked_client`.

> **Lesson:** Never `sleep` for an asynchronous condition — poll a cheap observable predicate with a bounded retry budget and a clear failure message. It's faster on the happy path and far less flaky under load.

### Fuzz the real thing against a reference *model* in another paradigm

The type tests build a parallel Tcl `array` as a trivially-correct model, drive both with the same random operations, and assert agreement — across both encodings:

```tcl
foreach size {10 512} {
    test "Hash fuzzing #1 - $size fields" {
        array set hash {}
        # ...random hset into both Redis and the Tcl array...
        foreach {k v} [array get hash] { assert_equal $v [r hget hash $k] }
        assert_equal [array size hash] [r hlen hash]
    }
}
```

> **Lesson:** Fuzz the real implementation against a trivially-correct reference model written in a *different paradigm* (a Tcl array vs. C), drive both with the same random ops across all encodings, and gate the long runs behind a flag so dev runs stay fast while CI runs deep.

### Assert the replication *stream*, not just the replica's final state

```tcl
assert_replication_stream $repl {
    {select *}
    {rpush k hello}
    {pexpireat k *}
    {del k}
    {set somekey2 someval2}
}
```

This attaches to the replication link via `SYNC` and glob-matches the exact propagated command sequence — catching correctness-critical rewrites like a lazy-expired key being propagated as an explicit `DEL`.

> **Lesson:** For systems that propagate effects (replication, event logs, CDC), assert the exact emitted command/event stream, not just the downstream final state — rewrites and ordering are part of correctness.

### foreach encoding — write the test once, run it across every representation

```tcl
foreach type {listpack quicklist} {
    if {$type eq "listpack"} { r config set list-max-listpack-size -2 } \
    else                     { r config set list-max-listpack-size 1 }
    # ...identical test body; assert_encoding $type inside to confirm coverage...
}
```

> **Lesson:** When one logical type has multiple internal representations, write the behavioral test once and run it across every encoding by flipping the threshold config in a `foreach` — and assert the encoding *inside* the loop so you know each variant was truly exercised.

---

## 4. Testing an approximate algorithm: Vector Sets

Vector Sets (the `VADD`/`VSIM` HNSW index) pose the hard question: how do you test an *approximate* nearest-neighbor search that has no single correct answer? antirez's answer is differential testing against a brute-force oracle with a **statistical threshold** instead of exact equality.

The oracle is an O(N) linear scan using the *same scoring formula* as `VSIM`, over random normalized Gaussian vectors. The test loads 20,000 vectors, runs the approximate query with a high exploration factor, and asserts recall against the true top-K:

```python
overlap = len(redis_set & linear_set)
assert overlap >= k * 0.7, \
    f"Expected at least 70% overlap in top {k} results, got {overlap/k*100:.1f}%"

# And where they overlap, scores must match the oracle:
for item in redis_set & linear_set:
    assert abs(redis_results[item] - linear_items[item]) < 0.01
```

`random.seed(42)` keeps it deterministic. The engine also ships a `VSIM ... TRUTH` option that forces an internal linear scan — "the perfect result set... used in order to easily calculate the recall" — i.e. an in-engine oracle.

> **Lesson:** Test an approximate algorithm against a brute-force oracle using a statistical threshold (recall ≥ 70%), not exact equality — and additionally assert that the results you *do* return have correct scores. Build the oracle into the product if you can (a "give me the exact answer" mode).

### Fuzz the SIMD boundaries and overflow-prone inputs

The quantization tests (`Q8`, binary) sweep dimensions chosen to hit scalar / AVX2 / AVX512 paths (`[16, 31, 32, 33, 63, 64, 65, 128, 256, 512]`) with adversarial vectors designed to surface int8 dot-product accumulation overflow:

```python
vec1 = [1.0] * dim                                          # all max positive
vec3 = [-1.0] * dim                                         # opposite direction
vec4 = [1.0 if i % 2 == 0 else -1.0 for i in range(dim)]    # alternating extremes
assert results_dict[f'{key}:item:3'] < 0.1   # overflow would make this wrongly positive
assert 0.4 < results_dict[f'{key}:item:4'] < 0.6
```

> **Lesson:** When code has optimized variants (SIMD, scalar fallback), pick input sizes that straddle every boundary and inputs engineered to trigger the specific numeric failure (overflow, cancellation) the optimization risks — then assert the vectorized and scalar paths agree.

And, as everywhere in Redis, the index must survive a persistence roundtrip: `persistence.py` records the top-10, runs `DEBUG RELOAD`, and asserts the result set, count, and scores all match within `0.0001`.

---

## 5. AI-as-QA-engineer (DwarfStar / ds4, and "A New Era for Software Testing")

antirez's most recent contribution is a *new layer* of testing: an agent that performs the expensive exploratory and integration testing humans usually skip. His thesis (from [antirez.com/news/168](https://antirez.com/news/168)):

> "there are domains where LLMs simply open new strictly more powerful ways to automate processes, without any compromise on quality. One of those domains is software QA and testing."

The mechanism is a committed markdown file (`AGENT.md` in `antirez/ds4`) that turns an agent into a QA engineer:

> "The idea is to create a markdown file where an AI agent is asked to work as a QA engineer, performing a number of manual testings on the new release."

The file contains **infrastructure context, not granular steps** — "SSH endpoints and the key to use, the paths, and so forth" — plus high-level objectives. The agent is told to start from the diff:

> "The agent is asked to check the long list of QA activities *especially* in light of the added commits, starting with an inspection of the changes and with the identification of what could be affected."

The committed `AGENT.md` testing section is objective-driven:

```
At every major change where one of the following could be affected, make sure to:
1. Test the normal Metal path and that speed is still at the level it was.
2. Test the SSD streaming path.
3. Test the distributed inference if it could be affected, but ask the user before doing so.
4. Check if CUDA could be broken after the change ...
```

### Objective oracles, not hardcoded baselines

The most important detail: the oracle is a *judgeable objective*, not a fixed number.

> "I don't have to tell the agent what was the previous expected speed, as this is a moving target that changes with new releases."

> "Check that distributed inference works across MacBook A and MacBook B, making sure the output is coherent..."

"Output is coherent" and "speed is still at the level it was" are oracles the agent evaluates against context it infers — which is exactly what lets the test survive a moving target. (Note: an LLM judging "coherent" *is* an LLM-as-judge; treat such oracles with the same discipline as any judge — they discriminate poorly near ceiling, so use them for exploratory smoke, not release-grade pass/fail.)

### Why it's a complement, not a replacement

He positions this on top of unit/integration tests, to fill the gaps they structurally miss:

> "covering all the lines of the code does not mean covering all the possible states."

> "Integration testing is structurally hard: there are a number of timing issues, setups, and certain quality outputs that can only be visually inspected and not automatically checked."

And it reaches the usually-skipped exploratory/usability dimension — asking the agent "to identify all the new features that may look surprising, not documented enough, or generally sloppy from the POV of the user." The Redis Arrays example: "build a large array-based Redis application, ... setup a production environment with replication and persistency, ... simulate the usage of the application for days and with many users, checking if something was odd."

> **Lesson:** For integration/exploratory testing that humans skip — distributed setups, "is the output coherent," "any speed regression," "anything sloppy from the user's POV" — drive an agent from a committed markdown file that carries the infrastructure context and *high-level objectives*, told to start from the commit diff and judge against moving-target objectives rather than hardcoded baselines. It complements unit/integration tests; it does not replace them, and its judge-style oracles need the same skepticism as any LLM-as-judge.

---

## Key Insights

1. **Allocate testing effort by reuse risk.** Fuzz the reusable libraries others embed until "battle tested"; leave demo/teaching code untested. Pragmatism over uniform coverage.
2. **Differential test against an oracle that "always tells the truth"** — a trivially-correct reference (a hash table, a Tcl array, a brute-force scan), driven with the same random ops, compared on every observable.
3. **Make fuzzing reproducible** with a deterministic, platform-independent seeded RNG; libc `rand()` varies by platform and destroys replayability.
4. **Vary input distribution *and* scale** — dense ints, random bytes, small charsets, long chains, production-shaped keys, at 100k→1M→10M ops. Each shape hits different code paths.
5. **Roundtrip via a content digest** — assert serialize→reload is the identity over your whole state (RDB and AOF), the cheapest characterization test for persistence.
6. **Design for testability**: expose internal state and forced transitions through a guarded command surface (`DEBUG`, `OBJECT ENCODING`) so tests introspect instead of guessing.
7. **Assert the optimization engaged** (`assert_encoding`) — a silent fallback to a slower representation is a real bug.
8. **Test the real process, tagged for the matrix**; poll a predicate (`wait_for_condition`), never `sleep`.
9. **Assert the emitted stream, not just final state** — replication/event ordering and rewrites (expire→DEL) are part of correctness.
10. **Run one behavioral test across every internal encoding** with a `foreach`, asserting the encoding inside the loop to prove coverage.
11. **Approximate algorithms get statistical oracles** — recall ≥ threshold against brute force, plus exact-score checks on the overlap; ship a "give me the exact answer" mode as the in-product oracle.
12. **Fuzz the boundaries of optimized paths** — sizes that straddle scalar/SIMD splits, inputs engineered to trigger overflow/cancellation.
13. **Agent-as-QA fills the human-skipped gap** — exploratory/integration testing driven from a markdown file of objectives and infra context, judged against moving-target objectives, complementing (not replacing) unit/integration tests.
</content>
</invoke>
