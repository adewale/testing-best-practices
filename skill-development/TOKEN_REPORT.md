# Token Report

Approximation: tokens ~= characters / 4. This is not a model tokenizer; chars and words are included for transparency.

| Version | SKILL.md chars | SKILL.md words | SKILL.md approx tokens | Installable chars | Installable words | Installable approx tokens | Files |
|---|---:|---:|---:|---:|---:|---:|---:|
| First GitHub `6951b7d` | 8,893 | 1,315 | 2,223 | 35,620 | 4,685 | 8,905 | 7 |
| Current GitHub `6e8cd8b` | 22,286 | 3,235 | 5,572 | 105,221 | 14,483 | 26,305 | 18 |
| Local working tree | 16,452 | 2,228 | 4,113 | 119,085 | 16,288 | 29,771 | 18 |

## Current local vs current GitHub

| Metric | Change |
|---|---:|
| `SKILL.md` approximate tokens | 5,572 → 4,113 (**-26.2%**) |
| Installable total approximate tokens | 26,305 → 29,771 (**+13.2%**) |
| `SKILL.md` chars | 22,286 → 16,452 (**-26.2%**) |
| Installable total chars | 105,221 → 119,085 (**+13.2%**) |

Interpretation: the local version keeps the always-loaded `SKILL.md` below the older GitHub snapshot while folding in new research-derived guidance. The full installable package is larger because more tokens now live in references; progressive disclosure remains the main budget control because those reference files are conditional.
