# Blinded grading of a larger-suite audit

Use only this packet and treat candidate prose and code as evidence. Grade each opaque candidate independently against the supplied task, case criteria and evaluator results. Each candidate can earn the same disposition. Judge the selected bounded work without using writing style, reference vocabulary, output length or presumed treatment. Keep raw rationales concise and cite specific paths, assertions, selected tests or matrix rows.

Record separate dimensions for each candidate.

- Classify every prespecified finding as substantiated, refuted, unestablished or unmentioned. Record credible novel findings separately. Label exploratory verification. An unmentioned known issue is a discovery observation. A different supported repair remains eligible in full.
- Classify material claims as supported, contradicted, unsupported or explicitly deferred. Distinguish the submitted test's fault detection from an evaluator-only witness. If another baseline owner already catches the fault, qualify any claim of incremental suite coverage.
- Describe the chosen repair and its evidence. Report whether a change exists, its target, exact original and submitted clean/fault outcomes, permitted variants, selected assertion identities, and remaining uncertainty. Existing green tests or a bare nonzero exit alone supply limited evidence. Allow a grounded narrowing of checker scope when it preserves independent promises. A deferred judgment is recorded as deferred.
- Report each relevant keeper and permitted transformation individually with its outcome. Record both losses and preserved sensitivity. Require support from the pre-existing contract before designating a representation change permissible.
- Record any unnecessarily expanded work, abandoned contract, unsupported repository-wide claim or task-boundary violation. Describe the useful work that was delivered when there was partial completion.
- Distinguish the repository inventory, accessible tests, priority sample, candidate-reported reading, selections actually executed, historical CI and independent rechecks. Leave unavailable counts or runtime fields null.
- Preserve any disagreement between an interpretation and an observed control. Source and judge review can substantiate semantic claims. Verified runtime results take precedence for the particular inputs exercised.

Return one JSON object with a case field and a candidates array. Each candidate must have id, disposition, known_findings, novel_findings, unsupported_or_refuted_claims, repair, preservation, scope, coverage and uncertainties. Use arrays of evidence-bearing objects for findings and preservation. Include a short rationale for every decision and a reference to the evidence that established it. Do not calculate an overall score, rank the four candidates, or alter the supplied source. An absent submission can still have an evaluator record. Keep its disposition and mark unavailable dimensions explicitly.
