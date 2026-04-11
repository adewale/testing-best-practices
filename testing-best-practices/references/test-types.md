# Test Type Decision Guide

Read this file when deciding which types of tests to write for a feature or
project. Tests are organized into three tiers by priority.

## Tier 1: Always Required

### Unit Tests
- **When**: Every function with non-trivial logic (`if`, loops, arithmetic)
- **Rules**: 3+ assertions per test, happy + sad path, no network/filesystem
- **Cost**: Low setup, fast, stable

### Smoke Tests
- **When**: Every deployable unit (app, service, CLI)
- **What**: "The app starts and responds to the main endpoint"
- **Cost**: Very low — one test that boots the app

### Regression Tests
- **When**: After every bug fix
- **How**: Write the failing test BEFORE fixing the bug
- **Rules**: Name after the bug/issue number, include a comment explaining it

## Tier 2: Required When Triggered

### Property-Based Tests
**Trigger**: ANY of these apply:
- [ ] Function accepts strings/numbers/binary from users
- [ ] Function serializes/deserializes data
- [ ] Function transforms data (output preserves some input property)
- [ ] Function is a parser (should never crash on arbitrary input)
- [ ] Function computes rankings/scores/orderings

**Cost**: Medium. Requires thinking in invariants, slower to run.

### E2E Tests
**Trigger**: ANY of these apply:
- [ ] Project has HTTP endpoints or a CLI with multi-step workflows
- [ ] Project runs on a specific platform (Workers, Pyodide, etc.)
- [ ] Previous bugs were missed by unit tests

**Rules**: Golden path first, gate behind env vars, limit to 5-15 tests.
**Cost**: High setup, slow, can be flaky.

### Documentation-Code Sync Tests
**Trigger**: ANY of these apply:
- [ ] Project has CLI commands listed in docs
- [ ] Project has a plugin/hook system with documented extension points
- [ ] Project has configuration settings described in docs

**How**: Parametrize over code registries, verify each item is in docs.

### Contract Tests
**Trigger**: ANY of these apply:
- [ ] Unit tests use mocks for external services
- [ ] Unit tests use stubs for browser APIs
- [ ] There are precomputed data files that code depends on

**How**: Validate mock return values against reality in a real environment.

### VCR Cassette Tests (External API Testing)
**Trigger**: ANY of these apply:
- [ ] Code calls third-party APIs (LLM providers, payment, auth)
- [ ] Tests use hand-written mock HTTP responses
- [ ] External API tests are flaky due to network issues

**How**: Record real API responses to files, replay in tests. See
the matching reference file.
**Cost**: Low maintenance, occasional re-recording needed.

### Characterization Tests
**Trigger**: ANY of these apply:
- [ ] About to refactor legacy or unfamiliar code
- [ ] No existing test suite for the code being changed
- [ ] Behavior is undocumented and unclear

**How**: Call the code, record actual outputs as assertions. See
the matching reference file.
**Cost**: Low setup, medium maintenance (must decide which behaviors to keep).

### Differential Tests
**Trigger**: ANY of these apply:
- [ ] Reimplementing a known algorithm (tokenizer, encoder, hash)
- [ ] A trusted reference implementation exists (PyTorch, tiktoken, stdlib)
- [ ] Building an optimized version of known-correct code

**How**: Run same inputs through both implementations, assert outputs match.
See the matching reference file.
**Cost**: Low if reference exists, high if you must build one.

### Golden File / Fixture-Based Tests
**Trigger**: ANY of these apply:
- [ ] Code transforms input files to output files (HTML→Markdown, compilation)
- [ ] Code generates complex output that's hard to assert on field-by-field
- [ ] You have real-world input files to test against

**How**: Store inputs in `tests/fixtures/`, expected outputs in `tests/expected/`.
Auto-discover fixtures, auto-baseline on first run. See
the matching reference file.
**Cost**: Low setup. Human-reviewable baselines. Catches drift.

### Pirate Tests (Language-Neutral Conformance)
**Trigger**: ANY of these apply:
- [ ] A specification has multiple implementations across languages
- [ ] You maintain SDKs/libraries in several languages that must behave the same
- [ ] An open standard needs a conformance test suite

**How**: Write test cases as data (JSON/YAML). Each implementation provides a
harness that loads the data and runs assertions. No implementation is privileged.
See the matching reference file.
**Cost**: Medium (harness per language), but amortized across all implementations.

## Tier 3: Use With Caution

### Visual Regression / Screenshot Tests
- **When helpful**: UI-heavy projects where pixel layout matters
- **Costs**: Cross-platform font differences cause false positives
- **Mitigations**: Skip in CI, disable animations, capture components not pages,
  mask timestamps and dynamic content

### Mutation Testing
- **When helpful**: After quality audit reveals low assertion density; for
  security-critical code; when coverage is 80%+ but bug escapes persist
- **Costs**: 10-100x test runtime. Requires interpretation.
- **Mitigations**: Run on specific critical modules, nightly not per-commit
- **Tools**: mutmut (Python), Stryker (JS/TS), PIT (Java), gremlins (Go),
  cargo-mutants (Rust). See the matching reference file.

### Performance / Benchmark Tests
- **When helpful**: A 2x slowdown would be a user-visible bug
- **Costs**: Results vary between machines
- **Mitigations**: Compare against baseline, separate from test suite

### Fuzz Testing
- **When helpful**: Security-sensitive code processing untrusted input
- **Costs**: Requires infrastructure, hard to reproduce failures
- **Mitigations**: Start with "never crashes" property tests (structured fuzzing)

## Minimum Viable Test Suite

For any project, start with:
1. One smoke test (app starts and responds)
2. Unit tests for business logic (3+ assertions, happy + sad path)
3. Regression test for every bug fix (written before the fix)
4. Property test for every parser/serializer ("never crashes" at minimum)

Add Tier 2 and 3 tests as trigger conditions apply.

## Cost-Benefit Summary

| Type | Setup | Maintenance | Speed | Bug Power | Flake Risk |
|------|-------|-------------|-------|-----------|------------|
| Unit | Low | Low | Fast | Medium | Very Low |
| Smoke | Very Low | Very Low | Fast | Low* | Low |
| Regression | Low | Low | Fast | High | Very Low |
| Property | Medium | Low | Medium | Very High | Low |
| E2E | High | Medium | Slow | High | Medium |
| Doc-sync | Low | Low | Fast | Low* | Very Low |
| Contract | Medium | Medium | Medium | High | Low |
| VCR cassette | Low | Low | Fast | Medium | Very Low |
| Characterization | Low | Medium | Fast | Medium | Very Low |
| Differential | Low | Low | Fast | Very High | Very Low |
| Golden file | Low | Low | Fast | Medium | Very Low |
| Pirate | Medium | Low | Medium | High | Very Low |
| Screenshot | High | High | Slow | Medium | High |
| Mutation | High | Low | Very Slow | Very High | Very Low |

*Low power but catches embarrassing/critical issues
