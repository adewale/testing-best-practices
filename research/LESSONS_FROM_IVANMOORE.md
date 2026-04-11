# Lessons from github.com/ivanmoore (Ivan Moore)

> XP practitioner, refactoring expert.
> Date: 2026-04-11

---

## Who He Is

Ivan Moore is an Extreme Programming practitioner who teaches TDD through hands-on exercises. His repos are teaching katas, not production projects — but they embody specific testing principles.

## TDD Teaching Repos

- **TddSkeleton** — Empty project with JUnit/Gradle setup ready for TDD exercises
- **Camera** — Mock objects exercise (practicing interaction testing with test doubles)
- **RefactoringGolf** — Refactoring exercises with scored "holes" (fewest steps to transform code)
- **gildedrose** — The classic Gilded Rose refactoring kata
- **battleships** — Game implementation kata

## The Refactoring Golf Format

Created by Ivan Moore, Dave Cleal, and Mike Hill:
1. Start with working code
2. Transform it to a target state
3. Score: fewest refactoring steps wins
4. Each step must keep tests green

**Lesson**: Good tests enable confident refactoring. If the tests are brittle or coupled to implementation, refactoring becomes impossible.

## The Camera Exercise

Specifically designed for practicing mock object usage — the Camera repo provides a skeleton where students must use test doubles to verify interactions between components. This is notable because Ivan treats mocks as a *skill to practice*, not a default to reach for.

## Key Insights

1. **TDD is practiced through katas**: each repo is a self-contained exercise with clear constraints
2. **Mock objects are an exercise, not default**: the Camera repo is specifically for *practicing* mock usage, implying mocks are a technique that requires deliberate skill
3. **Refactoring requires green tests**: RefactoringGolf scores by keeping tests green through each step
4. **Teaching format matters**: skeleton repos with Gradle/JUnit pre-configured lower the barrier to starting TDD
