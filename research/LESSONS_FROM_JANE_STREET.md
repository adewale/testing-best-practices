# Lessons from Jane Street

> Quantitative trading firm, heavy users of OCaml. Originated `ppx_expect`, `ppx_inline_test`, `base_quickcheck`, `patdiff`, `Bonsai`, and the library-level approach to deterministic simulation testing. Led Antithesis's $105M Series A in December 2025.
> Date: 2026-05-19

---

## Who They Are

Jane Street has built one of the most coherent testing philosophies in industry, grounded in three interlocking ideas:

1. **Expect tests** — snapshot-style inline tests that turn writing tests into a REPL session
2. **Property-based testing** via QuickCheck-style generators, integrated with expect tests
3. **Library-level simulation** — making every source of nondeterminism (time, network, scheduler) an explicit, swappable parameter so the same production code can run deterministically in tests

A common thread runs through all three: **lower the cost of writing a thorough test until it falls below the cost of not writing one**. Yaron Minsky put it bluntly in the post that introduced expect tests: "Testing is important, and it's hard to get people to do as much of it as they should."

## Expect Tests (`ppx_expect`)

The most important technique they've contributed to the wider testing world. An expect test interleaves code, output, and assertions in a single file:

```ocaml
let%expect_test "addition" =
  printf "%d" (1 + 2);
  [%expect {| 3 |}]
;;
```

### Workflow

1. Write code that produces output. Leave the `[%expect {||}]` block empty.
2. Run `dune runtest`. The test fails and a `.corrected` file is generated containing the diff (rendered by `patdiff`).
3. Inspect the diff. If correct, run `dune promote` (or use an editor keybinding). The source file is **overwritten in place** with the new expected output.

The point isn't to remove the assertion — it's to defer *what* to assert until *after* you've seen what the code does. From James Somers's "The Joy of Expect Tests" (2023):

> "Expect tests make test-writing feel like a REPL session, or like exploratory programming in a Jupyter notebook — with feedback cycles so fast and joyful that it feels almost tactile."

> "You don't just get a build failure telling you that you want 610 instead of a blank string. You get a diff showing you the exact change you'd need to make to your file to make this test pass; and with a keybinding you can 'accept' that diff."

### Three differences from regular unit tests (from Yaron Minsky's "Testing with expectations", 2015)

1. **Combined representation** — scenario, output, and comments live in one readable file
2. **Automatic generation** — the framework fills in the expected output for you
3. **Clear failure visibility** — failures display as easy-to-interpret diffs, not as `assertion failed: 3 == 5`

**Lesson**: When the cost of writing the expectation is near zero, you assert on *more* state per test. Expect tests "capture things you never expected them to" — typo'd error messages, accidental whitespace changes, the exact order of log lines, behavior of edge cases you didn't think to assert on directly.

### The implicit invariant: testable code produces good output

Expect tests push the codebase toward better introspection. From "The Joy of Expect Tests":

> "The real art lies in producing output that tells a concise story, capturing the state you care about. The best tests take pains to elide unnecessary detail."

This means custom `sexp_of_t` converters, custom pretty-printers, helper functions that format domain state for readability. The test is the *consumer* that motivates good `Show` instances.

### Advanced forms

- `[%expect_exact]` — strict matching, no whitespace normalization
- `[%expect.unreachable]` — assert a code path never executes
- `[%expect.output]` — capture output as a string for post-processing/sanitization
- `[@@expect.uncaught_exn]` — capture and assert on uncaught exceptions
- `Expect_test_config` — customize IO wrapping (for Async) or sanitization

## Inline Tests (`ppx_inline_test`)

Tests live next to the code they test:

```ocaml
let is_prime = ...

let%test _ = is_prime 5
let%test _ = is_prime 7
let%test _ = not (is_prime 1)
```

Supported forms:

```ocaml
let%test "name" = <bool expr>            (* true = pass *)
let%test_unit "name" = <unit expr>        (* exception = fail *)
module%test Name = <module_expr>          (* grouping *)
```

Selective execution via tags (`fast-flambda`, `js-only`, `64-bits-only`, etc.) and location-based filtering: `-only-test main.ml:32`.

**Lesson**: Co-location is for the *writer*. Public test files are for the *consumer*. Jane Street's house style uses inline tests for fine-grained internal invariants and dedicated `(inline_tests)` libraries for public API tests — keeping production binary size small while preserving locality where it helps comprehension.

## QuickCheck Integrated with Expect Tests (`ppx_quick_test`)

`Base_quickcheck` is Jane Street's property testing library. Generators form a monad (composable), with separate **observers** (for higher-order functions) and **shrinkers** (for counterexample minimization):

```ocaml
type t =
  | Circle of { radius: float } [@quickcheck.weight 0.5]
  | Square of { side: float }
[@@deriving quickcheck]
```

The killer move is `ppx_quick_test`, which fuses property testing with expect tests:

```ocaml
let%expect_test "int comparison is transitive" =
  let%quick_test prop (a : int) (b : int) (c : int) =
    assert (if a > b && b > c then a > c else true)
  in
  [%expect {| |}]
;;
```

When the property fails, the failing input prints into the expect block via `sexp_of_t` — so a property-test counterexample is captured in the same promote-based workflow as a regular expect test. Attributes like `[@trials 500]`, `[@generator <expr>]`, `[@examples ...]`, and `[@remember_failures]` tune the run.

**Lesson**: Property tests and example tests don't have to be separate worlds. When the failure UX is the same (a promotable diff with a pretty-printed counterexample), engineers reach for properties more readily.

From Jane Street's "Quickcheck for Core" post: the original problem QuickCheck users hit was that "it was easy to write tests that use random data, but hard to write random distributions that actually produce values that are useful to test." Their library invests heavily in *generator design* — boundary values, weighted unions, and composable monadic combinators.

## `patdiff` — Patience Diff for Snapshots

`patdiff` is an OCaml implementation of Bram Cohen's patience diff algorithm, used as the renderer for expect test failures. Patience diff produces semantically meaningful diffs by anchoring on uniquely-matching lines first — which dramatically improves readability when blocks of similar lines (`} else {`, blank lines, repeated keywords) would otherwise misalign with classic Myers diff.

Features that matter for testing: semantic diffing of numbers (with float tolerance), word-level diffing, recursive directory comparison, and a `patdiff-git-wrapper` for use as `GIT_EXTERNAL_DIFF`.

**Lesson**: Snapshot testing's UX lives or dies on the diff renderer. If the diff is noisy or misaligned, engineers stop reading it carefully and start blanket-promoting. Investing in a structural diff tool pays off across thousands of test failures.

## Bonsai Testing — Library-Level Simulation for UIs

Bonsai is Jane Street's web UI framework. Its components are purely functional state machines, which makes them trivially testable without a browser. The test handle exposes the entire DOM as a snapshot:

```ocaml
let%expect_test "shows hello to a specified user" =
  let handle = Handle.create (Result_spec.vdom Fn.id) hello_textbox in
  Handle.show handle;
  [%expect {|
    <div>
      <input oninput> </input>
      <span> hello  </span>
    </div> |}];
  Handle.input_text handle ~get_vdom:Fn.id ~selector:"input" ~text:"Bob";
  Handle.show_diff handle;
  [%expect {|
      <div>
        <input oninput> </input>
-     <span> hello  </span>
+     <span> hello Bob </span>
      </div> |}]
;;
```

Two patterns worth noting:

1. `Handle.show_diff` — shows only the DOM delta from the previous `show`. The test reads as a *trace of state transitions*, not a series of independent snapshots.
2. `Handle.advance_clock_by handle (Time_ns.Span.of_sec 2.0)` — UI tests advance virtual time manually. No `sleep`, no flakiness, no browser.

The Bonsai README claims you can "write an entire component without opening your browser" — and the test corpus bears this out.

**Lesson**: A UI framework that's hard to test will produce a culture where engineers test in the browser instead. Make the framework itself a state machine, expose its inputs and outputs structurally, and snapshot testing replaces 80% of what people use Cypress/Playwright for.

## Library-Level Simulation Testing (The Big One)

This is Jane Street's most distinctive contribution. It deserves its own treatment because the technique is widely admired and not well documented outside the OCaml ecosystem.

### The pattern in one sentence

Every source of nondeterminism — time, network IO, scheduling, external services — is an **explicit parameter** of the library APIs production code is written against. In production, the parameter is the real implementation. In tests, it is a controlled simulator. The *same production code* runs in both.

### Compared to other deterministic simulation approaches

| Approach | Level | Mechanism |
|---|---|---|
| **FoundationDB** | Runtime | Single-threaded Flow Actor scheduler replaces the entire runtime. Cannot test code not written in Flow. |
| **Antithesis** | Hypervisor | Deterministic VM runs unmodified Docker images; chaos injected at scheduler/network. |
| **TigerBeetle VOPR** | Process | All nondeterminism abstracted; simulator drives a single binary with property checks. |
| **Jane Street (library-level)** | Library + type system | `Time_source` and network are explicit parameters. OCaml compiler enforces. Same code in prod and tests. |

Jane Street's approach is unique in being **compiler-enforced**: the type system itself rejects accidental wall-clock dependence.

### The mechanism: `Time_source` and `Require_explicit_time_source`

The Async concurrency library was rebuilt to parameterize all time-dependent operations on a `Time_source`. The changelog (v113.33) describes the migration:

> "Reworked Async_kernel's clock handling to make it possible to use a notion of time distinct from the wall-clock time. ... `Clock_ns` is now a wrapper around `Time_source` that implicitly uses the Async scheduler's time source. The new power comes from the user being able to advance time distinctly from the wall clock."

The compiler-enforced testability rule is in `require_explicit_time_source.mli`:

```ocaml
(** Deprecates functions that use wall-clock time, so that code must be explicit
    about what time source is used.

    Idiomatic usage is:
    {[ open! Require_explicit_time_source ]}
*)
module Time_ns : sig
  val now : unit -> t [@@deprecated "[since 2016-02] Use [Time_source]"]
end

val at : Time_ns.t -> unit Deferred.t [@@deprecated "[since 2016-02] Use [Time_source]"]
val after : Time_ns.Span.t -> unit Deferred.t [@@deprecated "[since 2016-02] Use [Time_source]"]
val every : ... -> unit [@@deprecated "[since 2016-02] Use [Time_source]"]
val with_timeout : ... [@@deprecated "[since 2016-02] Use [Time_source]"]
```

Every file that opens `Require_explicit_time_source` at the top makes accidental wall-clock usage a compile error. This single line is the cultural fence that keeps the testable architecture testable:

```ocaml
open! Require_explicit_time_source
```

### The test API: `Synchronous_time_source`

```ocaml
let server_time_source = Synchronous_time_source.create ~now:Time_ns.epoch ()
let client_time_source = Synchronous_time_source.create ~now:Time_ns.epoch ()
```

Each side of an RPC connection gets its own time source — letting tests model clock skew between machines, which is impossible with wall-clock time.

The core advancement primitive interleaves time advance with scheduler drain:

```ocaml
let advance_by_alarms_by time_source span =
  Synchronous_time_source.advance_by_alarms_by time_source span |> ok_exn
;;

let sleep span =
  Time_source.advance_by_alarms_by time_source (Time_ns.Span.of_string span)
    ~wait_for:(Scheduler.yield_until_no_jobs_remain ~may_return_immediately:false)
;;
```

`advance_by_alarms_by` fires every alarm whose scheduled time is `<=` the new time, **in non-decreasing order**. The `~wait_for` argument drains all consequent jobs before returning. This means a single line in the test corresponds to "advance the world by 2 seconds and let everything that should have happened, happen."

### A real test (from `async_rpc_kernel/test/test_connection_time_source.ml`)

```ocaml
let test_connection_timeout heartbeat_timeout_style =
  let heartbeat_every = Time_ns.Span.of_sec 2. in
  let heartbeat_timeout = Time_ns.Span.of_sec 10. in
  let%bind (`Server (server_time_source, server_conn),
            `Client (client_time_source, client_conn)) =
    Test_helpers.setup_server_and_client_connection
      ~heartbeat_timeout ~heartbeat_every ~heartbeat_timeout_style ()
  in
  print_emphasized "Advancing time by heartbeat_every to show a heartbeat";
  advance_by_alarms_by server_time_source heartbeat_every;
  advance_by_alarms_by client_time_source heartbeat_every;
  ...
  print_emphasized "Advancing only server time by heartbeat_timeout";
  advance_by_alarms_by server_time_source heartbeat_timeout;
  ...
```

Expected output (captured deterministically — note timestamps from epoch):

```
("connection closed"
  (now         "1970-01-01 00:00:14Z")
  (description server)
  (reason
   ("No heartbeats received for 10s. Last seen at: 1969-12-31 19:00:02-05:00,
     now: 1969-12-31 19:00:14-05:00.")))
```

### Why this beats per-component mocking

From the Aria blog ("Getting from tested to battle-tested", Doug Patti, Dec 2025):

> "The ability to write tests which don't require excess mocking and are also fast and deterministic means that you can express more edge cases with less effort, get more introspection on the state of components, and run the entire suite in every build without worrying about flakiness."

With per-component mocks, the mock must mimic protocol details, error semantics, and latency for *every* dependency in *every* test. Tests get coupled to the mock surface, refactoring is expensive, and composing components in integration tests means composing mocks (which usually doesn't compose).

Library-level simulation replaces the *substrate* once, in a shared simulator. Real production code runs; it just happens to be running on top of a different `Time_source` and a different network. Fidelity comes from running real code, not from the quality of the mocks.

### State machine replication: the architectural prerequisite

Library-level simulation pairs with an inversion-of-control architecture. Jane Street builds critical distributed systems (Concord, then Aria) as **replicated state machines**: applications don't push messages, the framework pulls. From Doug Patti on the "State Machine Replication" Signals & Threads episode:

> "Our testability story is really, really good in Concord, and that's because we have the ability to take these synchronous state machines... and put messages in them, one at a time in an exact order that we can control. We can really simulate race conditions to an amazing degree and take all sorts of nearly impossible things and make them reproduce perfectly."

> "By inverting control, you have no choice but to put all of your state down into some structure that you can then poke at."

The architectural commitment is significant — it's a decade-long migration (the `Time_source` deprecations are dated `2016-02`) — but the payoff is that *every internal state is inspectable* and the test drives the schedule of message arrivals exactly.

## The Seven Layers of Aria's Testing (Defense in Depth)

From "Getting from tested to battle-tested", the production message bus Aria uses **seven complementary testing layers**:

1. **Unit tests** — modules and data structures without side effects, simple state machines
2. **Integration tests with simulated networking** — *"the most important piece"* — fine-grained interactions including delayed/dropped packets and manipulated time
3. **QuickCheck tests inside the simulator** — random event orderings fed through the deterministic network layer (this is the composition trick: property tests over schedules, deterministically replayable)
4. **Version skew tests** — new clients against old servers, old clients against new servers
5. **AFL fuzz tests** — byte stream interpreted as a sequence of state updates
6. **Lab performance tests** — nightly regression in production-like environments
7. **Chaos testing in staging** — random service restarts under prod-like load

The composition matters: a QuickCheck failure inside the deterministic simulator is *reproducible and shrinkable*. A bug found by chaos testing in staging would be hard to debug — but feeding the same event schedule through the simulator makes it deterministic.

**Lesson**: Defense in depth is the point. No single layer catches every bug. The cost is justified because each layer catches a distinct *class* of bug, and the cheapest layer (unit tests) runs first.

### The tip-retransmitter bug (a concrete payoff)

Antithesis found a bug in a production service that had been running for months. The exact failure sequence:

1. Server restarts and loads a snapshot
2. The ring buffer isn't yet refilled
3. A client requests data from *before* the snapshot

Result: the server returned uninitialized NUL bytes from the ring buffer instead of an error. Local clients were protected by service discovery; only remote-region clients with optimistic connection logic exposed the flaw.

> "Jane Street runs some of the most demanding distributed systems in the world, and Antithesis has helped us uncover issues that no other testing method could find." — Doug Patti

## Code Review and Testing Culture (Iron)

Jane Street's code review tool (Iron, since superseded internally but documented at length) was built around a workflow that *expects* tests to encode behavior:

> "Expect nearly every semantic change to be reflected in one way or another, either via a new test, or via a diff to an old one."

The pattern for bug fixes:

> "Adding an expect test in one feature that demonstrates the buggy behavior, and then fixing it in the followup feature."

(Two PRs: one adds the failing expect test, one fixes the code. The expect test diff *is* the bug report.)

From "Ironing out your development style":

> "Expect tests are used pervasively, serving as a way of capturing program traces that expose aspects of the behavior of the system to reviewers."

**Lesson**: When tests are also documentation, code review and testing converge. The expect-test diff in the PR description tells the reviewer what the change does — no separate "what does this do?" prose required.

## Hardware Testing (Hardcaml Step Testbench)

The library-level simulation idea generalizes beyond software. `Hardcaml_step_testbench` is "async for hardware testbenches" — synchronous threads that synchronize at every clock cycle:

```ocaml
run_computations
  [ (fun h -> for i = 0 to 2 do step h; printf "foo %d\n" i done)
  ; (fun h -> for i = 0 to 2 do step h; printf "bar %d\n" i done) ]
```

Combined with ASCII waveform rendering inside expect tests (from "Using ASCII waveforms to test hardware designs"), this turns FPGA verification into the same promote-based workflow as software unit tests. The newer version uses OCaml 5's algebraic effects to express the synchronization barrier.

**Lesson**: The "make non-determinism a parameter" pattern works at any level — software scheduler, distributed system, FPGA clock cycle. Each level needs its own synchronization primitive (`yield_until_no_jobs_remain`, `advance_by_alarms_by`, `step`), but the structure is identical.

## Key Insights

1. **Lower the cost of writing a test until it's lower than the cost of not writing one.** Expect tests do this for example-based testing; `ppx_quick_test` does it for property tests. The whole stack is engineered around test-writing ergonomics.

2. **Make non-determinism a parameter, not an ambient property of the runtime.** `Time_source` is the canonical example. The OCaml compiler enforces this via `open! Require_explicit_time_source`, making testability a *static* invariant of the codebase, not a discipline.

3. **Snapshot diffs are the unit of test failure.** Patdiff (patience diff) plus the `dune promote` workflow turn snapshot updates into a tactile, reviewable operation. Expect tests, Bonsai DOM tests, Hardcaml waveform tests, and ppx_quick_test all share this UX.

4. **Library-level simulation beats per-component mocking** because the *substrate* gets replaced once, not the mocks-per-test. Real production code runs in tests; only time and network are different. Multi-process simulation (independent client/server time sources) becomes possible — you can model clock skew, packet reordering, partial network partitions, all deterministically.

5. **Architecture is a testability strategy.** Replicated state machines, inversion of control, explicit time parameters, purely functional UI components — these aren't testing patterns, they're architectural patterns whose payoff is testability. Jane Street's testing story would not work if applied retroactively to a randomly-structured codebase.

6. **Composition of testing techniques is the point.** QuickCheck inside the deterministic simulator gives reproducible, shrinkable property failures over distributed-system schedules. Chaos testing in staging finds production-realistic failures. Expect tests give a snapshot of any one execution. Each technique alone is incomplete; together they're defense in depth.

7. **Tests as documentation, tests as code review artifact.** Expect-test diffs in a PR tell the reviewer what changed in observable behavior — no separate prose explanation needed. This collapses two artifacts (the test and the changelog entry) into one.

8. **The trade-off is real but pays off.** Threading `Time_source` through every function is a non-trivial architectural commitment. The `[@@deprecated "[since 2016-02]"]` tags are evidence of a decade-long migration. Jane Street reports incidents in production are "few and far between, even as Jane Street deploys new changes each week."

9. **Tooling investment is a force multiplier, not a tax.** Will Wilson (Antithesis CEO, formerly FoundationDB) on Signals & Threads: "If you have a system that can find all the bugs really, really fast, it frees you to just do crazy stuff like rewriting core algorithms." Jane Street invested in patdiff, ppx_expect, `Time_source`, Bonsai's test handle, Hardcaml_step_testbench — and got a culture that ships fast.

10. **Don't be a maximalist about any single approach.** Ron Minsky and Will Wilson both stress combining example tests, property tests, fuzzing, chaos testing, type systems, and formal methods. Library-level simulation is one tool in the kit — Jane Street still uses example tests for most code and reaches for simulation when the system is distributed enough to warrant the architectural investment.

## Primary Sources

**Centerpiece blog posts**:
- "Getting from tested to battle-tested" (Doug Patti, Dec 2025) — https://blog.janestreet.com/getting-from-tested-to-battle-tested/
- "The Joy of Expect Tests" / "What if writing tests was a joyful experience?" (James Somers, 2023) — https://blog.janestreet.com/the-joy-of-expect-tests/
- "Testing with expectations" (Yaron Minsky, 2015) — https://blog.janestreet.com/testing-with-expectations/
- "Repeatable exploratory programming" (Yaron Minsky, 2018) — https://blog.janestreet.com/repeatable-exploratory-programming/
- "Quickcheck for Core" (2015) — https://blog.janestreet.com/quickcheck-for-core/
- "Ironing out your development style" — https://blog.janestreet.com/ironing-out-your-development-style/
- "Using ASCII waveforms to test hardware designs" — https://blog.janestreet.com/using-ascii-waveforms-to-test-hardware-designs/
- "Fun with Algebraic Effects — Hardcaml" — https://blog.janestreet.com/fun-with-algebraic-effects-hardcaml/

**Signals & Threads podcast episodes**:
- "Why Testing is Hard and How to Fix It" (with Will Wilson, 2026) — https://signalsandthreads.com/why-testing-is-hard-and-how-to-fix-it/
- "State Machine Replication, and Why You Should Care" (Doug Patti) — https://signalsandthreads.com/state-machine-replication-and-why-you-should-care/
- "Multicast and the Markets" (Brian Nigito) — https://signalsandthreads.com/multicast-and-the-markets/
- "Building a UI Framework" (Ty Overby, on Bonsai) — https://signalsandthreads.com/building-a-ui-framework/
- "Building Tools for Traders" (Ian Henry) — https://signalsandthreads.com/building-tools-for-traders/

**Code**:
- `ppx_expect` — https://github.com/janestreet/ppx_expect
- `ppx_inline_test` — https://github.com/janestreet/ppx_inline_test
- `base_quickcheck` — https://github.com/janestreet/base_quickcheck
- `ppx_quick_test` — https://github.com/janestreet/ppx_quick_test
- `patdiff` — https://github.com/janestreet/patdiff
- `bonsai` — https://github.com/janestreet/bonsai
- `async_kernel` (esp. `require_explicit_time_source.mli`, `synchronous_time_source.mli`) — https://github.com/janestreet/async_kernel
- `async_rpc_kernel/test/test_connection_time_source.ml` — production-quality reference for the simulation pattern
- `hardcaml_step_testbench` — https://github.com/janestreet/hardcaml_step_testbench

**Book**:
- Real World OCaml, Chapter 18 ("Testing") — https://dev.realworldocaml.org/testing.html
