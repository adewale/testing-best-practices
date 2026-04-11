# Lessons from github.com/tirsen (Jon Tirsen)

> ThoughtWorks alum, testing/agile practitioner.
> Date: 2026-04-11

---

## Who He Is

Jon Tirsen is a ThoughtWorks alum and agile practitioner. His public GitHub repos are primarily forks and contributions to infrastructure projects (TiDB, Vitess, rclone) rather than original testing-focused work.

## Notable Repos

- **retry-cli** — Command-line tool to retry commands with exponential backoff. Relevant to testing because retry logic is itself a common source of flaky test patterns.
- Various forks of database and infrastructure tools (TiDB, Vitess, rclone, Helm provider)

## Key Insight

1. **Retry with backoff is infrastructure, not a test pattern**: when tests need retries, the root cause (flakiness) should be fixed rather than papered over with retry logic
