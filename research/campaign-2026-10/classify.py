"""Tag campaign lesson records by technique and recurring-cost class (rules v1).

Usage:
  python3 classify.py records.jsonl > records.new.jsonl   # re-tag the published dataset
  python3 classify.py SRC_DIR > records.jsonl             # build from the campaign's working files
SRC_DIR holds collected/*.json (campaign), seed/*.json (pre-campaign and pilot),
comment_urls.json and ce_map.json, as produced by the 2026-10 test-audit campaign.

The rules are deliberately simple and keyword-based so that anyone can rerun
and audit them. Every record gets label_method="rules-v1"; hand corrections
should set label_method="hand" and keep the rule output in rules_v1.
"""
import json, re, sys, pathlib, collections

TECH_RULES = [  # (technique, pattern) checked against the record's prose, not its field names
    ("mutation", r"\bmutat|\bmutant|stryker|mutmut|gremlins|cosmic.?ray|pitest|kill table|survivor|equivalent mutant|defect.?probe"),
    ("fuzz", r"\bfuzz"),
    ("pbt", r"hypothesis|fast-?check|proptest|\brapid\b|property[- ]based|\bpbt\b|numruns|max_examples|property tests?\b|properties (test|over|drew|draw)|\bst\.[a-z_]+\(|\bfc\.[a-z]+\(|shrink|strateg(y|ies) (draw|generat)"),
    ("exhaustive", r"exhaustive|every (combination|element|cell)"),
    ("golden", r"golden|snapshot|hash pin|sha-?256|byte-exact|byte-for-byte"),
    ("browser-e2e", r"playwright|\be2e\b|end-to-end|browser|chromium|webkit|screenshot|visual baseline"),
    ("eval-oracle", r"\boracle|grader|\bevals?\b|benchmark manifest|llm judge|judge"),
    ("real-engine-double", r"\bfake\b|\bfakes\b|\bmock|\bstub|test double|\bdouble\b|miniflare|workerd|pyodide"),
    ("static-text", r"source[- ]text|\bgrep|\blint|regex over|text match"),
]
PRIMARY_ORDER = ["mutation", "fuzz", "pbt", "exhaustive", "golden", "browser-e2e", "eval-oracle", "real-engine-double", "static-text"]

# Hand labels (2026-10-09) for the 106 records that mention mutation, PBT, fuzzing or cost.
# primary: the technique the finding is about. concern: whose recurring cost it discusses
# (mutation | pbt | fuzz | exhaustive | ci-lane | test-runtime | eval-tokens | none).
# direction: whether its proposal limits that cost, adds to it, or neither (limits | adds | neutral).
M, P, F, X, E = "mutation", "pbt", "fuzz", "exhaustive", "example"
def h(primary, concern="none", direction="neutral", drop=()):
    return {"primary": primary, "concern": concern, "direction": direction, "drop": set(drop)}
HAND = {
 "agentic-mermaid-check-owner-before-claiming-lost-check": h(M),
 "aha-ambient-time-ratchet-blind-spots": h("static-text", drop=[P]),
 "aha-reviewer-found-lost-contracts-in-rewrite": h(M),
 "anti-slop-writing-equivalent-mutants": h(M, M, "limits"),
 "atlas-seo-copied-count": h(E, drop=[P]),
 "atlas-mutants-from-deleted-assertions": h(M),
 "audit-skill-conjunction-masks-loose-assertion": h("eval-oracle"),
 "audit-skill-old-column-without-old-tests": h(M),
 "audit-skill-regex-fitted-to-recorded-samples": h("eval-oracle"),
 "autowiki-mutation-lint-artifact": h(M),
 "bobbin-mutation-live-assets": h(M, M, "neutral"),
 "cf-workers-design-system-mutant-startup-error-counted-as-kill": h(M),
 "cfdoctor-worktree-head-trap": h(M),
 "fibonacci_durable_object-no-tests-demo": h(E, "test-runtime", "limits"),
 "flux-search-pbt-cold-start-reach": h(P),
 "flux-search-mutation-harness-reporter": h(M),
 "geist_fabrik-campaign-edit-checkout-plant": h(M),
 "good-readme-single-source-fixtures-miss-iteration-bugs": h(E),
 "guardrails-skill-boundary-check-never-red": h("static-text"),
 "keyboardia-tamper-fixture-rebuild": h(E, "test-runtime", "limits"),
 "keyboardia-or-condition-masked": h(E),
 "keyboardia-audit-cli-two-recomputes": h(E, "test-runtime", "neutral"),
 "kirby_tarot-clock-dependent-kill": h(E),
 "olsen-campaign-ci-lead-stale": h("process"),
 "oshineye-dev-utc-ci-masks-local-time": h(E),
 "oshineye-dev-docs-dead-fallback": h(E),
 "oshineye-dev-campaign-sed-mutant-unapplied": h(M),
 "pi-comfort-mutation-script-sed-ampersand": h(M),
 "python-workers-issues-pytest-bytes-diff-cost": h(E, "test-runtime", "limits"),
 "python-workers-issues-startup-spin-on-dead-server": h("real-engine-double", "test-runtime", "limits"),
 "python-workers-issues-shared-tree-mutation": h(M),
 "python-workers-skill-surviving-mutant-is-doc-signal": h(M),
 "rogue_planet-mutation-restore-from-index": h(M),
 "skill-eval-harness-not-applicable-never-aggregated": h(E),
 "skill-eval-harness-author-chosen-mutants": h(M),
 "skill-eval-harness-kill-table-needs-suite-column": h(M),
 "skill-eval-harness-new-tests-outside-discovery": h(M),
 "skill_scanner-near-miss-not-adjacent": h("eval-oracle"),
 "skill_scanner-mutant-shape-vs-copied-counts": h(M),
 "spa-redundant-guard-equivalent-mutant": h(M),
 "spa-mutation-script-false-kill": h(M),
 "sunrise-retry-helper-untested": h(E),
 "sunrise-mutation-run-cost": h(M, M, "neutral"),
 "swiss-poster-skill-mis-planted-mutant": h(M),
 "tasche-text-routing-false-kill": h(M),
 "tasche-st-text-generator-reach": h(P),
 "tts-playground-duplicate-guard-test-dropped": h(E),
 "web2kindle-mutation-loop-pipe-masked-exit": h(M),
 "yaket-bound-only-assertion": h(E, drop=[P]),
 "pilot-planet_cf-B": h(M), "pilot-planet_cf-C": h(M), "pilot-planet_cf-E": h(E),
 "pilot-claude-history-explorer-3": h(E), "pilot-claude-history-explorer-4": h(E, drop=[P]),
 "pilot-claude-history-explorer-8": h(E), "pilot-claude-history-explorer-11": h(M),
 "pilot-vaders-4": h(P),
 "pre-audit-collection-parity": h("ci-gate"),
 "pre-audit-gates-can-go-red": h("ci-gate"),
 "pre-audit-recurring-lane-contract-all-tiers": h("ci-gate", "ci-lane", "limits"),
 "pre-audit-retract-3plus-assertions": h(E, drop=[P]),
 "pre-audit-heuristic-never-quota": h(E, M, "limits", drop=[P]),
 "pre-audit-ap16-always-green-dead-gates": h("ci-gate"),
 "pre-audit-ap20-silent-tier-downgrade": h("real-engine-double"),
 "pre-audit-custom-oracle-both-sides": h("eval-oracle"),
 "pre-audit-local-runtime-emulation-rung": h("real-engine-double", drop=[F]),
 "pre-audit-wall-clock-budgets-unit-tier": h(E, "test-runtime", "limits"),
 "pre-audit-timeout-ratchet": h(E, "test-runtime", "limits"),
 "pre-audit-pbt-budgets-generator-cost": h(P, P, "limits"),
 "pre-audit-evals-cost-per-lift": h("eval-oracle", "eval-tokens", "limits"),
 "pre-mutcost-seed-faults-cheapest-first": h(M, M, "limits"),
 "pre-mutcost-change-based-triggers": h(M, M, "limits"),
 "pre-mutcost-floors-from-target-runners": h(M, M, "limits"),
 "pre-mutcost-unread-diagnostic-not-dead-gate": h(M, M, "limits"),
 "pre-mutcost-cheap-checker-self-tests": h("eval-oracle", "test-runtime", "limits"),
 "pre-mutcost-estimate-ci-minutes": h(M, M, "limits"),
 "pre-mutcost-tool-traps": h(M, M, "neutral"),
 "pre-mutcost-no-code-bent-to-score": h(M, M, "limits"),
 "pre-mutcost-run-tool-on-demand": h(M, M, "limits"),
 "pre-20-recurring-lane-operating-contract": h(M, M, "limits"),
 "pre-20-retract-nightly-weekly-cadence": h(M, M, "limits"),
 "pre-20-mutation-score-not-a-target": h(M, M, "limits"),
 "pre-20-equivalent-mutants-and-survivor-classification": h(M, M, "limits"),
 "pre-20-no-automatic-p0-survivors": h(M, M, "limits"),
 "pre-20-no-universal-enrollment": h(M, M, "limits"),
 "pre-21-constrained-variable-strength": h(X, X, "limits"),
 "pre-21-cost-vector-not-magic-score": h(X, "test-runtime", "limits"),
 "pre-21-ci-history-calibration-not-gates": h(E, "test-runtime", "limits"),
 "pre-21-shadow-validate-before-deleting": h(M),
 "pre-22-per-cell-cost-feasibility": h(X, X, "limits"),
 "pre-22-check-the-deciding-layer": h(X, X, "limits"),
 "pre-22-worked-pattern-structural-equality-budget": h(X, X, "limits"),
 "pre-22-routing-expensive-cross-products": h(X, X, "limits"),
 "pre-22-eval-exh-1-cost-blindness": h(X, X, "limits"),
}

def prose(r):
    parts = [r.get("id", ""), r.get("finding", "")]
    se = r.get("suggested_edit") or {}
    parts += [se.get("text", ""), se.get("section", "")]
    # Evidence (planted bugs, kill counts) and eval seeds describe how a finding was
    # verified, not what it is about, so they are excluded from technique detection.
    parts.append(str(r.get("counterexample", "")))
    return " ".join(p for p in parts if p).lower()

def classify(r):
    t = prose(r)
    techs = [name for name, pat in TECH_RULES if re.search(pat, t, re.I)]
    if r.get("tag") == "mutation-cost" and "mutation" not in techs:
        techs.insert(0, "mutation")
    if r.get("tag") == "eval-oracle" and "eval-oracle" not in techs:
        techs.append("eval-oracle")
    if r.get("tag") == "campaign-process":
        primary = "process"
    else:
        primary = next((p for p in PRIMARY_ORDER if p in techs), "example")
    ev = r.get("evidence") or {}
    pb = str(ev.get("planted_bug", "") if isinstance(ev, dict) else "").strip().lower()
    planted = bool(pb) and pb not in ("none", "n/a", "na", "-", "")
    tag = r.get("tag")
    concern = {"mutation-cost": "mutation", "cost": "test-runtime"}.get(tag, "none")
    out = {"techniques": techs, "primary_technique": primary, "cost_concern": concern,
           "cost_direction": "neutral", "verified_by_planted_bug": planted, "label_method": "rules-v1"}
    hand = HAND.get(r.get("id"))
    if hand:
        out["rules_v1"] = {k: out[k] for k in ("techniques", "primary_technique", "cost_concern")}
        out["techniques"] = [t for t in techs if t not in hand["drop"]]
        if hand["primary"] in PRIMARY_ORDER and hand["primary"] not in out["techniques"]:
            out["techniques"].append(hand["primary"])
        out.update(primary_technique=hand["primary"], cost_concern=hand["concern"],
                   cost_direction=hand["direction"], label_method="hand")
    return out

def main(src):
    src = pathlib.Path(src)
    urls = json.loads((src / "comment_urls.json").read_text())
    url_of = {k: re.search(r"\((https://[^)]+)\)", v).group(1) for k, v in urls.items() if "(" in v}
    ce_map = json.loads((src / "ce_map.json").read_text())
    ce_of = collections.defaultdict(list)
    for ce, ids in ce_map.items():
        for i in ids: ce_of[i].append(ce)
    seed_urls = {
        "pilot:planet_cf": ["https://github.com/adewale/testing-best-practices/issues/32#issuecomment-5964097206"],
        "pilot:claude-history-explorer": ["https://github.com/adewale/testing-best-practices/issues/32#issuecomment-5964097334"],
        "pilot:vaders": ["https://github.com/adewale/testing-best-practices/issues/32#issuecomment-5964097489"],
        "pre_audit_2026-09": [f"https://github.com/adewale/testing-best-practices/issues/32#issuecomment-{n}" for n in (5964383645, 5964383773, 5964383923)],
        "pre_mutation_cost": ["https://github.com/adewale/testing-best-practices/issues/32#issuecomment-5964384063"],
        "pre_lockin_30": [f"https://github.com/adewale/testing-best-practices/issues/32#issuecomment-{n}" for n in (5964384191, 5964384323)],
        "pre_issues_20_21_22": [f"https://github.com/adewale/testing-best-practices/issues/32#issuecomment-{n}" for n in (5964384465, 5964384575)],
    }
    out = []
    for f in sorted((src / "collected").glob("*.json")):
        for r in json.loads(f.read_text())["records"]:
            if isinstance(r, dict):
                out.append((r, "campaign", [url_of.get(f.stem, "")]))
    pilot = json.loads((src / "seed/pilot_records.json").read_text())
    for repo, rs in pilot.items():
        for r in rs: out.append((r, "pilot", seed_urls[f"pilot:{repo}"]))
    for name in ("pre_audit_2026-09", "pre_mutation_cost", "pre_lockin_30", "pre_issues_20_21_22"):
        for r in json.loads((src / f"seed/{name}.json").read_text()):
            out.append((r, "pre-campaign", seed_urls[name]))
    for r, origin, src_urls in out:
        rec = dict(r)
        rec["origin"] = origin
        rec["source_comments"] = [u for u in src_urls if u]
        rec["ce"] = ce_of.get(r.get("id"), [])
        rec.update(classify(r))
        rec["owner_outcome"] = None  # kept | changed | removed | pending; filled by the merge-label pass
        print(json.dumps(rec, ensure_ascii=False))

LABEL_KEYS = ("techniques", "primary_technique", "cost_concern", "cost_direction",
              "verified_by_planted_bug", "label_method", "rules_v1")

def retag(path):
    for line in open(path):
        rec = json.loads(line)
        for k in LABEL_KEYS: rec.pop(k, None)
        rec.update(classify(rec))
        print(json.dumps(rec, ensure_ascii=False))

if __name__ == "__main__":
    arg = sys.argv[1]
    retag(arg) if arg.endswith(".jsonl") else main(arg)
