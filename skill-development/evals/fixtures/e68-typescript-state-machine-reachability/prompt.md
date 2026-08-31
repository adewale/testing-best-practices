# Audit this state-machine test

Write an `assessment.md` for these repository artifacts. Focus on whether the
test supports its stated confidence claim and on concrete changes.

`test/users.model.test.ts` (abridged):

```ts
import fc from "fast-check";

type Model = { users: Set<string>; selected: string | null };
type Real = { api: UsersApi };

class SelectUser implements fc.AsyncCommand<Model, Real> {
  constructor(readonly id: string) {}
  check(m: Readonly<Model>) { return m.users.size > 0; }
  async run(m: Model, r: Real) {
    if (!m.users.has(this.id)) return;
    await r.api.select(this.id);
    m.selected = this.id;
    effectiveTransitions.select++;
  }
  toString() { return `select(${this.id})`; }
}

class DeleteSelected implements fc.AsyncCommand<Model, Real> {
  constructor(readonly id: string) {}
  check(m: Readonly<Model>) { return m.selected !== null; }
  async run(m: Model, r: Real) {
    if (this.id !== m.selected) return;
    await r.api.delete(this.id);
    m.users.delete(this.id);
    m.selected = null;
    effectiveTransitions.delete++;
  }
  toString() { return `delete(${this.id})`; }
}

const idArb = fc.uuid();
const commandArbs = [
  idArb.map(id => new SelectUser(id)),
  idArb.map(id => new DeleteSelected(id)),
  // CreateUser and ListUsers omitted here; they follow the same interface.
];

test("users obey the model", async () => {
  const seed = Number(process.env.FC_SEED ?? Date.now());
  await fc.assert(fc.asyncProperty(
    fc.commands(commandArbs, { maxCommands: 100 }),
    async commands => {
      const real = { api: await startUsersApi() };
      const model = { users: new Set<string>(), selected: null };
      await fc.asyncModelRun(() => ({ model, real }), commands);
    },
  ), { numRuns: 200, seed });
});
```

`package.json`:

```json
{
  "scripts": {
    "test:model": "vitest run --project api --project browser"
  }
}
```

The PR description says “20,000 state transitions per run (200 runs × 100
commands).” Instrumentation from the last ten CI runs reports:

```text
generated command slots:       200000
commands whose check was true:  74182
effective SelectUser calls:        31
effective DeleteSelected calls:     7
reported seed/path artifacts:        0
```
