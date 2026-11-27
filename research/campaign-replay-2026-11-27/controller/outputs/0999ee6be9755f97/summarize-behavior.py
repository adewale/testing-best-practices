"""Produce blind technical observations without assigning a campaign score."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
CASE = OUT.parents[2] / "preparation/agentic-mermaid"


def read(path):
    return json.loads(path.read_text())


def compact(v):
    return f"{v['passed']}/{v['total']}" + (" veto" if v["criticalVeto"] else "")


if __name__ == "__main__":
    pre = read(CASE / "operator-runtime/baseline.isolated.json")
    post = read(OUT / "frozen-controls.json")
    raw = read(OUT / "exploratory-results.json")["results"]
    inputs = read(OUT / "exploratory-inputs.json")["inputs"]
    idx = {k: {(x["cohort"], x["case"], x["id"]): x for x in v["controls"]} for k, v in raw.items()}
    separate = {k: Counter() for k in raw}
    witness_disagreements = []
    variant_disagreements = []
    for entry in inputs:
        key = tuple(entry[k] for k in ("cohort", "case", "id"))
        for version in raw:
            row = idx[version][key]
            if row["variants"]["with_skill"] != row["variants"]["without_skill"]:
                variant_disagreements.append([version, *key])
            v = row["variants"]["with_skill"]
            if entry["cohort"] == "independent":
                decision = "accept" if (not v["criticalVeto"] and v["rate"] == 1 and not v["deferred"]) else "reject"
                separate[version]["matched" if decision == entry["expected"] else "missed"] += 1
                continue
            claimed = entry["submittedComparison"]
            label = "before" if version == "original" else "after"
            equal = (f"{v['passed']}/{v['total']}" == claimed[label + "_gates"] and
                     (str(v["criticalVeto"]) == claimed[label + "_veto"]) and
                     abs(v["rate"] - float(claimed[label + "_objective_rate"])) < 1e-7)
            if not equal:
                witness_disagreements.append([version, *key])
    case_rows = {}
    for case in ("pos-live-editor-source-of-truth", "adv-reject-editor-html-direct-edit"):
        row = {}
        names = ["maintain_owner", "regenerate_paraphrase", "assembler_in_context", "wrong_owner_only",
                 "direct_edit_negated_rebuild", "skip_rebuild_only", "direct_edit_only", "behavior_without_formats",
                 "swapped_image_text_roles" if case.startswith("pos") else "standalone_only"]
        for name in names:
            key = ("independent", case, name)
            row[name] = [compact(idx[version][key]["variants"]["with_skill"]) for version in ("original", "candidate")]
        case_rows[case] = row
    aliases = {
        "caseId": "agentic-mermaid", "candidateId": OUT.name, "kind": "blind technical validation",
        "changedFiles": ["skill-evals/shared-benchmark.json", "skill-evals/ablations/no-editor-source-of-truth.patch"],
        "verifiedRepair": "Both public tune rows now distinguish the export owner, generated file, rebuild command and optional assembler by roles in a constrained JSON plan. The candidate uses built-in structured_output and json_field_equals. No new script assertion or browser behavior was introduced.",
        "frozenProse": {"pairs": 18, "historicalExpectedAccept": 7, "historicalExpectedReject": 11,
                        "originalClassifications": pre["editorGrade"]["counts"], "candidateClassifications": post["editorGrade"]["counts"],
                        "candidateObserved": dict(Counter(f"{v['decision']} {v['passed']}/{v['total']}" for v in post["editorGrade"]["controls"])),
                        "interpretation": "The candidate explicitly requires plain JSON, so all previously correct and incorrect prose earns zero. Eleven expected rejects happen to match. The counts from this frozen characterization do not independently quantify accuracy on the candidate's new prompt."},
        "exploratoryJSON": {"status": "Post-submission diagnostic, outside the frozen metric.",
                            "casesAndInputs": sum(i["cohort"] == "independent" for i in inputs),
                            "acceptRule": "full objective gate credit without a veto or deferral",
                            "selectedPairOrder": "original then candidate gate counts; veto sets the objective rate to zero",
                            "sameBytesScoredByEachRevision": True,
                            "agreementsWithCandidatePromptExpectations": separate,
                            "caveats": "The original grader received these JSON bytes for comparison. Its prompts allowed natural-language advice. Field order and list-order variations check the structured interface. They cannot establish acceptance of paraphrased prose. A second direct edit cannot be expressed in the declared fields; the supplemental alsoEdit example is deliberately an extra-field check.",
                            "selectedCriterionOutcomes": case_rows},
        "submittedEvidence": {"savedCaseAnswerPairs": 26, "independentlyComparedOnRevisions": 2,
                              "projectVariantLabelsPerCase": 2, "projectVariantDisagreements": variant_disagreements,
                              "disagreementsWithSubmittedGateCountsRatesOrVetoes": witness_disagreements,
                              "submittedSamples": "submitted-editor-probes/", "rawExploratoryResults": "exploratory-results.json"},
        "scopeChange": ["Original answers could be ordinary advice. The new prompts require plain JSON, package script keys, normalized repository paths, a fixed set of fields and lowercase format IDs.",
                        "The positive row now accepts a module or its containing directory and requires Unicode alongside ASCII, PNG and SVG with role-specific arrays. The old objective required the latter three format names.",
                        "The adversarial row now requires the hosted website script alongside the standalone script. Correctly assigning optional assembler context is accepted. A correct shell-command spelling or equivalent dot-prefixed filename can lose points under the documented form."],
        "preservation": {"publicManifestValidation": post["publicManifestValidation"]["commands"][1]["stdout"],
                         "existingWarnings": post["publicManifestValidation"]["commands"][1]["warningCount"],
                         "unittestExit": post["productUnittest"]["exit"], "passedRetainedDataTests": 10,
                         "other49ManifestRows": "identical case objects", "appAndBrowserTestSources": "unchanged",
                         "imageAndApprovedByteObservationsIdenticalToBaseline": post["imageDecisions"] == pre["imageDecisions"],
                         "CJKAndCoverageWorkflowObservationsIdenticalToBaseline": post["workflowFixture"] == pre["workflowFixture"],
                         "historicalCI": "No canonical CI run at this owner-skipped head. A separate scheduled coverage run failed the missing CJK prerequisite."},
        "ablation": {version: {"allExit": v["ablation"]["all"]["exit"],
                               "allDiagnostic": v["ablation"]["all"]["stderr"].splitlines()[-1:],
                               "editorOnlyExit": v["ablation"]["editorOnly"]["exit"],
                               "editorOnlyError": v["ablation"]["editorOnly"]["stderr"].splitlines()[-1:] if v["ablation"]["editorOnly"]["exit"] else [],
                               "removedLines": v["ablation"]["editorOnly"].get("removedSkillLines", []),
                               "addedLines": v["ablation"]["editorOnly"].get("addedSkillLines", [])}
                     for version, v in raw.items()},
        "supplementalRunCorrection": "In exploratory-first-run-results.json only the original editor-only ablation failed on a read-only working-copy file. Both disposable worktrees were then given owner-write permissions and the same saved-answer inputs and ablation commands were rerun. The frozen controls and submitted files were unchanged.",
        "limits": ["Saved-answer case functions and deterministic fixtures ran. No private prompt, model cohort, real browser download, native Bun rendering or hosted CI job ran.",
                   "The subject reported screening declarations across 58 files. The submission changed only the editor grading and ablation. The validation does not establish a deep read of each file."],
        "artifacts": {n: sha256((OUT / n).read_bytes()).hexdigest() for n in
                      ("patch.diff","frozen-controls.json","frozen-controls.runtime.json","exploratory-inputs.json",
                       "exploratory-results.json","exploratory-results.runtime.json")},
    }
    (OUT / "behavior.json").write_text(json.dumps(aliases, indent=2) + "\n")
