#!/usr/bin/env python3
"""Group the mechanical per-file labels into change units, and link units to records.

    python3 merge_units.py merge_labels_files.jsonl > merge_labels.jsonl
    python3 merge_units.py merge_labels_files.jsonl --records records.jsonl   # fills owner_outcome in place

A unit is one coherent thing a campaign session added: a fix, a test, a CI
lane, a budget, a script or a doc change. UNITS below groups files into units
by hand; the outcome is computed from the member files:

- kept: every file kept;
- removed: every file removed;
- changed: anything else (`conflict` counts as changed).

Campaign PRs the owner merged without any commit of their own are labelled as
one `kept` unit each (MERGED_UNCHANGED).

A record is linked to a unit when a path in its `evidence.files` is one of the
unit's files. Its `owner_outcome` is then:

- kept / removed: every linked unit has that outcome;
- changed: mixed;
- unlinked: the record's PR merged, but none of its evidence files is a file the
  PR changed (the finding was about code the PR did not touch, or about process);
- pending: its PR is still open or closed unmerged;
- null: the record has no PR (pre-campaign lessons, most pilot rows).
"""
import fnmatch
import json
import sys
from collections import defaultdict

# Records name the PR they were written against; folds moved that work into a survivor.
FOLDED_INTO = {
    ("embed.oshineye.dev", 3): 2, ("flux-search", 27): 26, ("garten", 4): 3, ("keyboardia", 126): 122,
    ("keyboardia", 123): 122, ("rogue_planet", 14): 13, ("skill-eval-harness", 102): 97,
    ("sunrise", 5): 4, ("tts-playground", 3): 2,
}

# Merged with no owner commits (every commit is a campaign or audit commit).
MERGED_UNCHANGED = {
    ("MaintainerBot", 3): ("d452c80", "Daily admission fix, Workflow binding fake checked against Miniflare, secret scanner tested both ways"),
    ("kirby_tarot", 3): ("047b4f4", "Worker share metadata, CORS and rate limiting tested through the handler; rate-limit leak fix"),
    ("lempicka", 2): ("67d678c", "Hermetic workerd tests for the Worker"),
    ("pengslide", 10): ("71390e7", "CI on the Node the tests need; painters tested through the paint"),
    ("pi-comfort", 2): ("94b1c3f", "Renderer escaping and Copy payload tests; wrapped list lines fix"),
    ("kirby_tarot", 2): ("b944321", "Offline npm test (local wrangler dev + local KV), run in CI"),
    ("pengslide", 1): ("99692d2", "Budgeted music tests, syntax checks, globe-return assertion"),
    ("geist_fabrik", 92): ("5b8bcd4", "A test suite able to fail, gated, with the product bugs it found fixed"),
}

# (repo, merged PR) -> [(unit id, kind, technique, path globs, owner's stated reason)]
U = lambda uid, kind, tech, globs, reason="": dict(unit=uid, kind=kind, technique=tech, globs=globs, reason=reason)
UNITS = {
    ("MaintainerBot", 2): [
        U("deep-verify-exec-policy", "config", "example",
          ["src/cli/deep-verify.ts", "tests/deep-verify-policy.test.ts", "README.md", "SPEC.md", "docs/CLI_OPPORTUNITIES.md"],
          "Keep verification policy unchanged (an executable allowlist for uv and make is not a sandbox)"),
        U("rejection-script-to-real-filter-tests", "test", "example",
          ["scripts/test-rejections.mjs", "tests/rejections.test.ts", "package.json"]),
        U("daily-pipeline-golden", "test", "golden",
          ["tests/daily-pipeline.golden.test.ts", "tests/fixtures/golden-run-context.json", "src/maintenance/daily.ts"],
          "Share the deterministic replay fixture; pin a real pull-request URL in the golden handoff"),
    ],
    ("embed.oshineye.dev", 2): [
        U("new-ci-workflows", "ci-lane", "browser-e2e", [".github/workflows/*"],
          "Keep embed verification within the existing default budget (main has no CI)"),
        U("claude-stop-hooks", "config", "process", [".claude/*"], "Keep embed verification within the existing default budget"),
        U("multi-instance-loader-fix", "fix", "example",
          ["public/static/loader.js", "src/embeds/v1/avatar-stack/index.html", "src/presence/identity.ts"]),
        U("unit-tests", "test", "example", ["tests/app.test.ts", "tests/identity.test.ts"]),
        U("browser-tests", "test", "browser-e2e", ["tests/e2e/*"]),
        U("test-config", "config", "browser-e2e", ["playwright.config.ts", "package.json", "tsconfig.json", ".gitignore"],
          "Browser checks run by hand"),
        U("docs", "doc", "process", ["CLAUDE.md", "README.md", "docs/*"]),
    ],
    ("flux-search", 26): [
        U("nightly-live-workflow", "ci-lane", "real-engine-double", [".github/workflows/live.yml"],
          "Keep offline verification atomic and within the existing budget"),
        U("visual-baselines-workflow", "ci-lane", "browser-e2e", [".github/workflows/visual-baselines.yml"],
          "Keep local browser checks isolated and within the existing test budget"),
        U("ci-expansion", "ci-step", "browser-e2e", [".github/workflows/ci.yml"], "main's test job and its 15 s budget"),
        U("live-tests-split", "test", "real-engine-double",
          ["test/live/*", "vitest.live.config.ts", "test/deployed-topic-*.test.ts", "test/relevance.test.ts",
           "test/search-integration.test.ts", "test/search-quality.test.ts"]),
        U("offline-hermetic-harness", "config", "real-engine-double",
          ["test/setup/no-network.ts", "vitest.config.ts", "wrangler.e2e.jsonc", "test/helpers-search-route.ts",
           "test/helpers-page.ts", "test/page-wiring.test.ts"],
          "Keep offline verification atomic"),
        U("fts-query-fix", "fix", "example", ["src/routes/search.ts"]),
        U("fts-safety-tests", "test", "example", ["test/fts-safety.test.ts"],
          "Reuse the redundant type-property budget for real FTS syntax checks"),
        U("search-state-pbt", "test", "pbt", ["test/search-state.pbt.test.ts"],
          "Reuse the redundant type-property budget for real FTS syntax checks"),
        U("corpus-and-unit-tests", "test", "example",
          ["test/corpus-*.test.ts", "test/frontend-utils.test.ts", "test/section-types.test.ts",
           "test/semantic-threshold.test.ts", "test/accessibility.test.ts", "test/topic-detail-links.test.ts",
           "test/ngram-cases.test.ts", "scripts/ngram-cases-report.mjs"]),
        U("browser-config", "config", "browser-e2e", ["playwright.config.ts"],
          "Keep local browser checks isolated and within the existing test budget"),
        U("docs", "doc", "process", ["CHANGELOG.md", "CLAUDE.md", "README.md", "package.json"]),
    ],
    ("garten", 3): [
        U("defect-probe-lane", "ci-lane", "mutation", [".github/workflows/probes.yml", "scripts/defect-probes/*"],
          "Keep Garten verification bounded"),
        U("stryker-config", "config", "mutation", ["stryker.config.json", "vitest.stryker.config.ts", "package.json"],
          "Keep Garten verification bounded (the weekly mutation schedule was removed too)"),
        U("ci-workflow", "ci-step", "mutation", [".github/workflows/ci.yml"], "Keep Garten verification bounded"),
        U("pbt-and-integration-budget", "budget", "pbt", ["src/property.test.ts", "src/integration.test.ts"],
          "Randomized PBT runs cut from about 306,096 to about 1,390, below main's 4,550"),
        U("docs-sync-registry-check", "test", "static-text", ["src/docs-sync.test.ts"]),
        U("docs", "doc", "process", ["TESTING.md", "LESSONS_LEARNED.md", "docs/*"]),
    ],
    ("keyboardia", 122): [
        U("stryker-config", "config", "mutation", ["app/stryker.config.mjs"], "No mutation configuration changes"),
        U("coverage-config", "config", "ci-gate", ["app/vitest.config.ts", "app/vite.config.ts"],
          "Preserve the existing opt-in coverage configuration"),
        U("e2e-retry-helper", "test", "browser-e2e", ["app/e2e/test-utils.ts", "app/test/e2e-test-utils.test.ts"],
          "Keep session read retries within one attempt budget"),
        U("fail-closed-gates", "test", "eval-oracle",
          ["app/scripts/*", "app/test/playwright-contract-identities.test.ts", "app/test/unit/test-quality-analyzers.test.ts",
           "evals/*", "evals/receipts/*"]),
        U("audio-render-tests", "test", "golden", ["app/src/audio/*", "app/test/instrument-quality-matrix.test.ts"]),
        U("ci-unit-lane-split", "ci-step", "example", [".github/workflows/*", "app/package.json"]),
        U("docs", "doc", "process", ["AGENTS.md", "CLAUDE.md", "README.md", "specs/*", "docs/*", ".claude/*", "app/.husky/*"]),
    ],
    ("rogue_planet", 13): [
        U("ci-workflow", "ci-step", "fuzz", [".github/workflows/*"], "No added jobs, fuzz campaigns or live-feed schedule"),
        U("xss-sink-tests", "test", "example",
          ["internal/htmlsafety/*", "cmd/rp/xss_pipeline_test.go", "testdata/hostile-feed.xml", "pkg/normalizer/normalizer_xss_test.go"],
          "Harden HTML assertions without expanding verification costs"),
        U("clock-driven-timing", "test", "example",
          ["pkg/timeprovider/*", "pkg/ratelimit/*", "pkg/fetcher/fetcher_concurrency_test.go", "pkg/crawler/*"],
          "Pin per-feed errors and fail early if retry handshake ends"),
        U("per-feed-error-pins", "test", "example",
          ["cmd/rp/cmd_helpers.go", "cmd/rp/integration_test.go", "cmd/rp/realworld_integration_test.go",
           "pkg/generator/*", "pkg/normalizer/normalizer_realworld_test.go"]),
        U("docs", "doc", "process", ["CHANGELOG.md", "CLAUDE.md", "Makefile", "README.md", "TESTING.md", "docs/*"]),
    ],
    ("skill-eval-harness", 97): [
        U("downstream-consumers-workflow", "ci-lane", "eval-oracle", [".github/workflows/downstream-consumers.yml"],
          "Focus validation repairs without downstream CI or oracle policy expansion"),
        U("lexical-oracle-retiering", "fix", "eval-oracle",
          ["findings.py", "grading_contracts.py", "tests/test_grading.py", "tests/test_gate_integrity.py",
           "tests/test_telemetry_domain.py", "docs/authoring-evals.md", "docs/vocabulary.md", "docs/migrating-evals.md",
           "docs/commands.md"],
          "Without oracle policy expansion"),
        U("manifest-guards-and-lint", "test", "eval-oracle", ["skill_benchmark.py", "tests/test_manifest.py"],
          "Kept the path and DX guards; removed the quadratic redundant-assertion lint"),
        U("consumer-checker-script", "script", "eval-oracle", ["scripts/check_consumer_manifests.py"],
          "Kept as an opt-in manual consumer checker"),
        U("grading-contract-tests", "test", "eval-oracle",
          ["tests/test_grading_contracts.py", "tests/test_consolidation_guards.py", "examples/skill-pins.json"]),
        U("docs", "doc", "process", ["CHANGELOG.md", "CONTRIBUTING.md", "README.md", "TODO.md", "docs/*"]),
    ],
    ("sunrise", 4): [
        U("ci-workflow", "ci-step", "example", [".github/workflows/ci.yml"],
          "Reconcile merged discovery tests without duplicating CI builds"),
        U("queue-and-db-tests", "test", "real-engine-double",
          ["test/queue-roundtrip.test.ts", "test/queue.test.ts", "test/db.test.ts", "test/scheduled.test.ts"],
          "Scope complete discovery snapshots to each scan and repository; return the persisted change identity"),
        U("session-and-version-tests", "test", "example",
          ["test/session.test.ts", "test/version-sync.test.ts", "test/manual-labels.test.ts", "sunrise.version.json"]),
        U("browser-global-setup", "config", "browser-e2e", ["test/browser-globalSetup.ts"],
          "Preserve cached snapshots and keep verification in existing lanes"),
        U("ship-check", "script", "process", ["scripts/ship-check.mjs", "README.md"]),
    ],
    ("tts-playground", 2): [
        U("e2e-ci-job", "ci-lane", "browser-e2e", [".github/workflows/ci.yml"],
          "Repair deployment credential journeys without expanding CI"),
        U("update-user-authz-fix", "fix", "example", ["src/auth.ts", "tests/security.test.ts"]),
        U("oauth-contract-tests", "test", "real-engine-double", ["tests/security-routes.test.ts", "tests/helpers/github-oauth.ts"],
          "Repair deployment credential journeys"),
        U("audio-format-tests", "test", "example", ["tests/audio-format.test.ts", "tests/audio.test.ts"],
          "ID3 duration fix"),
        U("e2e-aria-rework", "test", "browser-e2e", ["e2e/*"], "Repair deployment credential journeys"),
        U("stale-screenshots-deleted", "doc", "process", ["screenshots/*"]),
    ],
    ("vaders", 11): [
        U("weak-sole-assertion-checker", "script", "static-text",
          ["scripts/check-weak-sole-assertions*", "scripts/weak-sole-assertions.baseline.json",
           "scripts/audit-assertion-density.mjs", "package.json"],
          "Keep verification fixes within the existing test budget"),
        U("pbt-helper", "test", "pbt", ["web/src/testing/pbt.ts"], "Keep verification fixes within the existing test budget"),
        U("runtime-do-tests", "test", "real-engine-double",
          ["worker/runtime-test/*", "worker/vitest.runtime.config.ts", "worker/package.json"],
          "Keep verification fixes within the existing test budget"),
        U("component-assertion-upgrades", "test", "example", ["web/src/components/*"],
          "Keep verification fixes within the existing test budget"),
        U("ci-workflow", "ci-step", "example", [".github/workflows/ci.yml", "bun.lock"],
          "Keep verification fixes within the existing test budget"),
        U("interpolation-property", "test", "pbt", ["client-core/*"]),
        U("docs", "doc", "process", ["CHANGELOG.md", "CLAUDE.md", "Lessons_learned.md"]),
    ],
    ("vaders", 12): [
        U("app-render-tests", "test", "example", ["client/src/App.test.ts", "client/src/App.test.tsx"],
          "Prepare rendering and E2E fixes without adding recurring checks"),
        U("trace-and-sequence-tests-deleted", "test", "golden",
          ["client/src/render-sequence.test.ts", "client/src/render-trace.test.ts", "web/src/acceptance.test.ts",
           "web/playwright-report/*"]),
        U("color-conversion-fix", "fix", "pbt",
          ["client/src/terminal/color-conversion.property.test.ts", "client/src/terminal/compatibility.ts"]),
        U("state-defaults-fix", "fix", "example", ["shared/state-defaults.ts", "specs/*"]),
        U("playwright-config", "config", "browser-e2e", ["web/playwright.config.ts"],
          "Avoid a duplicate frontend build for local E2E startup"),
    ],
}


def outcome_of(outcomes):
    s = {"changed" if o == "conflict" else o for o in outcomes}
    return s.pop() if len(s) == 1 else "changed"


def build(files_path):
    files = [json.loads(line) for line in open(files_path)]
    merges = {(m["repo"], m["pr"]): m
              for m in json.load(open("owner_merges_2026-10-09.json"))["reworked_campaign_prs"]}
    units, path_unit, unmatched = [], {}, []
    for f in files:
        if f["campaign_status"] is None:
            continue
        key = (f["repo"], f["merged_pr"])
        for u in UNITS.get(key, []):
            if any(fnmatch.fnmatch(f["path"], g) for g in u["globs"]):
                path_unit[(f["repo"], f["merged_pr"], f["path"])] = u["unit"]
                break
        else:
            unmatched.append((key, f["path"]))
    if unmatched:
        sys.exit(f"files with no unit: {unmatched}")
    for key, defs in UNITS.items():
        repo, pr = key
        for u in defs:
            members = [f for f in files if (f["repo"], f["merged_pr"], f["path"]) in path_unit
                       and path_unit[(f["repo"], f["merged_pr"], f["path"])] == u["unit"] and (f["repo"], f["merged_pr"]) == key]
            if not members:
                continue
            units.append({
                "unit_id": f"{repo}#{pr}/{u['unit']}", "repo": repo, "merged_pr": pr,
                "campaign_head": merges[key]["campaign_head"], "merged_head": merges[key]["merged_head"],
                "kind": u["kind"], "technique": u["technique"],
                "outcome": outcome_of(m["mech_outcome"] for m in members),
                "files": {m["path"]: m["mech_outcome"] for m in members},
                "campaign_lines": [sum(m["campaign_lines"][0] for m in members), sum(m["campaign_lines"][1] for m in members)],
                "owner_edit_lines": [sum(m["owner_edit_lines"][0] for m in members), sum(m["owner_edit_lines"][1] for m in members)],
                "owner_reason": u["reason"] or None,
            })
    for (repo, pr), (head, what) in MERGED_UNCHANGED.items():
        units.append({"unit_id": f"{repo}#{pr}/whole-pr", "repo": repo, "merged_pr": pr,
                      "campaign_head": head, "merged_head": head, "kind": "pr", "technique": None,
                      "campaign_lines": None, "owner_edit_lines": [0, 0],
                      "outcome": "kept", "files": None, "owner_reason": f"Merged without owner commits: {what}"})
    return units


def link(units, records):
    by_file = defaultdict(list)
    for u in units:
        for path in (u["files"] or {}):
            by_file[(u["repo"], u["merged_pr"], path)].append(u)
    merged_prs = {(u["repo"], u["merged_pr"]) for u in units}
    whole = {(u["repo"], u["merged_pr"]): u for u in units if u["files"] is None}
    for r in records:
        repo = (r.get("repo") or "").split("/")[-1]
        pr = r.get("pr")
        if not isinstance(pr, int):
            r["owner_outcome"] = None
            continue
        pr = FOLDED_INTO.get((repo, pr), pr)
        if (repo, pr) not in merged_prs:
            r["owner_outcome"] = "pending"
            continue
        if (repo, pr) in whole:
            linked = [whole[(repo, pr)]]
        else:
            paths = [p.split(":")[0] for p in ((r.get("evidence") or {}).get("files") or []) if isinstance(p, str)]
            linked = {u["unit_id"]: u for p in paths for u in by_file.get((repo, pr, p), [])}.values()
        outs = {u["outcome"] for u in linked}
        r["owner_outcome"] = "unlinked" if not outs else (outs.pop() if len(outs) == 1 else "changed")
        r["owner_units"] = sorted(u["unit_id"] for u in linked) or None
        for u in linked:
            u.setdefault("records", []).append(r["id"])
            u.setdefault("ce", set()).update(r.get("ce") or [])
    for u in units:
        u["records"] = sorted(set(u.get("records", [])))
        u["ce"] = sorted(u.get("ce", set()))


if __name__ == "__main__":
    units = build(sys.argv[1])
    if "--records" in sys.argv:
        path = sys.argv[sys.argv.index("--records") + 1]
        records = [json.loads(line) for line in open(path)]
        link(units, records)
        with open(path, "w") as out:
            for r in records:
                out.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        records = [json.loads(line) for line in open("records.jsonl")]
        link(units, records)
    for u in units:
        print(json.dumps(u, ensure_ascii=False))
