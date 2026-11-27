"""Map the original control intents to the two newly declared JSON interfaces."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import shutil


OUT = Path(__file__).resolve().parent
POS, ADV = "pos-live-editor-source-of-truth", "adv-reject-editor-html-direct-edit"
OWNER, ASSEMBLER, GENERATED = "editor/js/export.js", "scripts/site/editor.ts", "editor.html"


def inputs():
    items = []
    desc = {
        POS: {"edit": OWNER, "generated": GENERATED, "rebuild": "editor",
              "imageFormats": ["png", "svg"], "textFormats": ["ascii", "unicode"]},
        ADV: {"edit": OWNER, "generated": GENERATED, "rebuild": "editor", "siteRebuild": "website"},
    }
    for case in (POS, ADV):
        good = desc[case]

        def add(label, val, exp, kind, **fmt):
            items.append({"cohort": "independent", "case": case, "id": label, "expected": exp, "kind": kind,
                          "answer": json.dumps(val, **fmt)})

        add("maintain_owner", good, "accept", "mapped-semantic")
        standard = dict(reversed(list(good.items())))
        if case == POS:
            standard["imageFormats"] = ["svg", "png"]
            standard["textFormats"] = ["unicode", "ascii"]
        add("regenerate_paraphrase", standard, "accept", "mapped-to-field-and-array-order", indent=2)
        add("assembler_in_context", {**good, "assembler": ASSEMBLER}, "accept", "mapped-semantic")
        add("direct_edit_negated_rebuild", {**good, "edit": GENERATED, "assembler": ASSEMBLER,
                                            "rebuild": "do not rebuild"}, "reject", "mapped-semantic")
        add("wrong_owner_only", {**good, "edit": ASSEMBLER}, "reject", "mapped-semantic")
        add("skip_rebuild_only", {**good, "assembler": ASSEMBLER, "rebuild": "do not rebuild"}, "reject", "mapped-semantic")
        add("direct_edit_only", {**good, "alsoEdit": GENERATED}, "reject", "extra-action-requires-out-of-form-field")
        add("behavior_without_formats", {k: v for k, v in good.items() if not k.endswith("Formats")},
            "reject" if case == POS else "accept", "mapped-semantic")
        add("no_relevant_content", {}, "reject", "mapped-semantic")
        add("owner_directory_no_slash", {**good, "edit": "editor/js"}, "accept", "new-form-boundary")
        add("owner_directory_slash", {**good, "edit": "editor/js/"}, "accept", "new-form-boundary")
        add("wrong_optional_assembler", {**good, "assembler": OWNER}, "reject", "new-form-boundary")
        add("wrong_generated_target", {**good, "generated": OWNER}, "reject", "new-form-boundary")
        add("correct_shell_command_wrong_field_syntax", {**good, "rebuild": "bun run editor"}, "reject", "form-only-distinction")
        add("correct_owner_with_dot_slash", {**good, "edit": "./" + OWNER}, "reject", "form-only-distinction")
        if case == POS:
            add("missing_unicode_only", {**good, "textFormats": ["ascii"]}, "reject", "newly_required_format")
            add("swapped_image_text_roles", {**good, "imageFormats": good["textFormats"],
                                             "textFormats": good["imageFormats"]}, "reject", "new-form-boundary")
        else:
            add("hosted_standalone_commands_swapped", {**good, "rebuild": "website", "siteRebuild": "editor"},
                "reject", "newly_required_hosted_script")
            add("standalone_only", {k: v for k, v in good.items() if k != "siteRebuild"},
                "reject", "newly_required_hosted_script")
    return items


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitted-probes", type=Path, required=True)
    parser.add_argument("--original-manifest", type=Path, required=True)
    args = parser.parse_args()
    src = args.submitted_probes.resolve()
    dest = OUT / "submitted-editor-probes"
    dest.mkdir(exist_ok=True)
    rows = inputs()
    assert json.loads((src / "original.json").read_text()) == json.loads(args.original_manifest.read_text())
    records = list(csv.DictReader((src / "results.tsv").open(), delimiter="\t"))
    assert len(records) == 26
    for i in records:
        case, label = i["case"], i["input"]
        assert case in {POS, ADV} and all(c.isalnum() or c == "-" for c in label)
        target = dest / case / (label + ".txt")
        target.parent.mkdir(exist_ok=True)
        original = src / case / target.name
        assert original.is_file() and not original.is_symlink() and original.stat().st_size < 2000
        answer = original.read_text()
        shutil.copyfile(original, target)
        rows.append({"cohort": "subject-submitted", "case": case, "id": label, "expected": "record-submitted-outcome",
                     "kind": "subject-authored-witness", "answer": answer, "submittedComparison": i})
    shutil.copyfile(src / "results.tsv", dest / "results.tsv")
    (OUT / "exploratory-inputs.json").write_text(json.dumps({
        "purpose": "Post-submission, case-specific diagnostic. Independent inputs map known required behaviors to the candidate's requested JSON. Original source is given the identical bytes. Subject witnesses are separate.",
        "frozenControlsEdited": False, "originalSubmittedManifestSHA256": sha256((src / "original.json").read_bytes()).hexdigest(),
        "inputs": rows}, indent=2) + "\n")
