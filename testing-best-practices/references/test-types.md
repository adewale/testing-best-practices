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

## Tier 3: Use With Caution

### Visual Regression / Screenshot Tests
- **When helpful**: UI-heavy projects where pixel layout matters
- **Costs**: Cross-platform font differences cause false positives
- **Mitigations**: Skip in CI, disable animations, capture components not pages,
  mask timestamps and dynamic content

### Mutation Testing
- **When helpful**: After quality audit reveals low assertion density; for
  security-critical code
- **Costs**: 10-100x test runtime. Requires interpretation.
- **Mitigations**: Run on specific modules, nightly not per-commit

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
| Screenshot | High | High | Slow | Medium | High |
| Mutation | High | Low | Very Slow | Very High | Very Low |

*Low power but catches embarrassing/critical issues
