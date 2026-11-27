#!/usr/bin/env python3
"""Exploratory verification of the secondary pda-03 claim. Run under the shared Docker lock."""
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CASE = HERE.parents[2]/"preparation/pda/evaluator"
sys.path.insert(0, str(CASE))
import controls

PROBE = """import { env, runInDurableObject } from "cloudflare:test";
import { expect, it } from "vitest";
import { AgentData } from "../src/agent-data";
import { exportAgentData } from "../src/agent-data-export";
import type { StorageProbe } from "./worker";

it("checks erasure after a populated export row has reached its reader", async () => {
  const probes = (env as unknown as { STORAGE_PROBE: DurableObjectNamespace<StorageProbe> }).STORAGE_PROBE;
  await runInDurableObject(probes.get(probes.newUniqueId()), async (_, state) => {
    const store = state.storage;
    const eraser = new AgentData(store);
    store.sql.exec("CREATE TABLE memories (text TEXT, source TEXT, created_at INTEGER)");
    for (let i = 0; i < 5; i++) store.sql.exec("INSERT INTO memories VALUES (?, 'user', 1)", "EXPLORATORY_ROW_" + i);
    const reader = exportAgentData(store.sql, 0).getReader();
    try {
      let received = "";
      while (!received.includes("EXPLORATORY_ROW_0")) {
        const next = await reader.read();
        expect(next.done).toBe(false);
        received += new TextDecoder().decode(next.value);
      }
      expect(received).not.toContain("EXPLORATORY_ROW_4");
      await eraser.erase("exploratory-receipt");
      expect(store.sql.exec("SELECT name FROM sqlite_master WHERE name = 'memories'").toArray()).toEqual([]);
    } finally {
      await reader.cancel();
    }
  });
});
"""

def install_stream_fault(repo):
    path = repo/"src/agent-data-export.ts"
    source = path.read_text()
    for old,new in [
        ("after, limit).toArray();", "after, limit);\n        let seen = 0;"),
        ("after = Number(rowid);", "seen++;\n          after = Number(rowid);"),
        ("if (batch.length < limit)", "if (seen < limit)"),
    ]:
        assert source.count(old) == 1
        source = source.replace(old,new)
    path.write_text(source)


def main():
    deps = Path(json.loads((CASE/"local-runtime.json").read_text())["node_modules"])
    output = {"classification":"Exploratory follow-up on the submission's unmodified secondary finding. Excluded from frozen directional metrics.",
              "source":"Pinned production and original HTTP test. No candidate changes applied.",
              "variant":"Compare original batched .toArray() with an open cursor iterated across stream yields.",
              "probe":"Use the real Workers SQL storage API and AgentData.erase; read the first of five seeded memory records and pause while later records remain.",
              "results":{}}
    for live in (False, True):
        name = "live-cursor" if live else "pinned"
        with tempfile.TemporaryDirectory(prefix="pda-cursor-exploratory-") as scratch:
            repo = Path(scratch)/"repo"
            shutil.copytree(controls.PUBLIC, repo)
            (repo/"test/cursor-evaluator.test.ts").write_text(PROBE)
            if live:
                install_stream_fault(repo)
            observation = controls.execute(repo,deps,[{
                "config":"test/vitest.config.ts",
                "files":["test/agent-data.test.ts","test/cursor-evaluator.test.ts"],
                "name":"erases while an export is unread or cancelled|checks erasure after a populated export row",
            }])
        for r in observation.get("results",[]):
            r["assertions"] = [a for a in r.get("assertions",[]) if a["status"] != "pending"]
        output["results"][name] = observation
        (HERE/"cursor-exploratory.json").write_text(json.dumps(output,indent=2)+"\n")
        print(name,[(r.get("passed"),r.get("failed"),r.get("skipped"),r.get("exit"),r.get("runnerError")) for r in observation.get("results",[])],flush=True)
    return int(any("error" in o or any(r.get("runnerError") for r in o.get("results",[])) for o in output["results"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
