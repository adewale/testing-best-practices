// Independent evaluator check on the clean snapshot, outside the candidate test.
import { env, evictDurableObject, runInDurableObject } from "cloudflare:test";
import { createAssistantMessageEventStream, fauxAssistantMessage, fauxProvider } from "@earendil-works/pi-ai";
import { expect, it } from "vitest";
import { Ledger } from "../src/budget";
import { demoCatalogModel, ModelAccess } from "../src/model-router";
import { ModelKeys } from "../src/model-keys";
import { Sealer } from "../src/poppy/store";
import type { StorageProbe } from "./worker";

const testEnv = env as Env;
const probes = (env as unknown as { STORAGE_PROBE: DurableObjectNamespace<StorageProbe> }).STORAGE_PROBE;
const day = "2026-10-20";

it("can reach two unequal local holds through the shared budget and refuses the next call before dispatch", async () => {
  const pool = testEnv.DomainBudget.getByName(`controller-budget-${crypto.randomUUID()}`);
  const owner = probes.get(probes.newUniqueId());
  const cap = testEnv.DEMO_DAILY_USD_PER_DOMAIN;
  expect(cap).toBe(1.5);
  expect(testEnv.DEMO_DAILY_USD_PER_USER).toBe(1);

  // Three other call IDs use the real shared reservation and settlement APIs.
  // Each request fits a single person's half-dollar maximum local hold.
  for (const id of ["prior", "other-a", "other-b"]) {
    expect(await pool.reserve(id, day, 0.5, cap)).toEqual({ accepted: true, reservedUsd: 0.5 });
    if (id === "prior") await pool.settle(id, day, 0.25);
  }
  expect(await pool.spent(day)).toBe(1.25);

  async function routeOwnerCall() {
    return runInDurableObject(owner, async (_, state) => {
      const ledger = new Ledger(state.storage.sql);
      const faux = fauxProvider();
      let dispatched = false;
      let refusal: string | null = null;
      const access = new ModelAccess({
        env: testEnv, ledger, keys: new ModelKeys(state.storage.sql, () => new Sealer(testEnv), state.id.toString()),
        profile: () => ({ provider: "google", sub: "budget-test", email: "owner@example.com", domain: null }),
        lists: () => testEnv, agent: state.id.toString(), domainBudget: () => pool,
        demoLane: () => ({ provider: faux.provider, model: faux.getModel() }), ownKeyProviders: () => [],
        onRefused: async e => { refusal = e.reason; }, onKeyRefused: async () => {},
        now: () => Date.parse(day + "T12:00:00Z")
      });
      const response = await access.route(demoCatalogModel(testEnv), () => {
        dispatched = true;
        const inner = createAssistantMessageEventStream();
        const aborted = fauxAssistantMessage([], { stopReason: "aborted" });
        aborted.usage.cost.total = 0;
        inner.push({ type: "error", reason: "aborted", error: aborted });
        return inner;
      }).result();
      return { dispatched, reason: response.stopReason, refusal, local: ledger.spent(day) };
    });
  }

  // Both admitted calls have unknown usage, so the router keeps their real holds.
  expect(await routeOwnerCall()).toEqual({ dispatched: true, reason: "aborted", refusal: null, local: 0.25 });
  expect(await pool.spent(day)).toBe(1.5);
  // Without new shared room another call would fail the domain preflight.
  await pool.settle("other-a", day, 0.125);
  await pool.settle("other-b", day, 0.125);
  expect(await pool.spent(day)).toBe(0.75);
  expect(await routeOwnerCall()).toEqual({ dispatched: true, reason: "aborted", refusal: null, local: 0.75 });
  expect(await pool.spent(day)).toBe(1.25);
  await evictDurableObject(owner);
  expect(await routeOwnerCall()).toEqual({ dispatched: false, reason: "error", refusal: "user_cap", local: 0.75 });
  expect(await pool.spent(day)).toBe(1.25);
});
