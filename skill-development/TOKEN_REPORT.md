# Token Report

Approximation: tokens ~= characters / 4. This is not a model tokenizer; chars and words are included for transparency.

| Version | SKILL.md chars | SKILL.md words | SKILL.md approx tokens | Installable chars | Installable words | Installable approx tokens | Files |
|---|---:|---:|---:|---:|---:|---:|---:|
| First GitHub `6951b7d` | 8,893 | 1,315 | 2,223 | 35,620 | 4,685 | 8,905 | 7 |
| Current GitHub `6e8cd8b` | 22,286 | 3,235 | 5,572 | 105,221 | 14,483 | 26,305 | 18 |
| Local working tree | 18,683 | 2,590 | 4,671 | 129,182 | 17,918 | 32,296 | 19 |

## Current local vs current GitHub

| Metric | Change |
|---|---:|
| `SKILL.md` approximate tokens | 5,572 → 4,671 (**-16.2%**) |
| Installable total approximate tokens | 26,305 → 32,296 (**+22.8%**) |
| `SKILL.md` chars | 22,286 → 18,683 (**-16.2%**) |
| Installable total chars | 105,221 → 129,182 (**+22.8%**) |

Interpretation: the local version keeps the always-loaded `SKILL.md` below the older GitHub snapshot while folding in new research-derived guidance. The full installable package is larger because more tokens now live in references; progressive disclosure remains the main budget control because those reference files are conditional.

## Cost of the false-green section

The false-green work added a 19th reference and grew the always-loaded router by
**+558 approximate tokens (4,113 → 4,671, +13.6%)**. That buys a core principle
("a green test is a claim; sabotage is the evidence"), five Detect-mode signals,
one Assess-mode check, and one validation step; the catalog itself
(~1,975 tokens) stays conditional in `references/false-green.md`. Router growth
is the number to watch here — it is paid on every invocation, while the
reference is paid only when its trigger matches.
