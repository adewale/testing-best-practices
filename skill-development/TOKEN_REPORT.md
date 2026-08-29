# Token Report

Approximation: tokens ~= characters / 4. This is not a model tokenizer; chars and words are included for transparency.

| Version | SKILL.md chars | SKILL.md words | SKILL.md approx tokens | Installable chars | Installable words | Installable approx tokens | Files |
|---|---:|---:|---:|---:|---:|---:|---:|
| First GitHub `6951b7d` | 8,893 | 1,315 | 2,223 | 35,620 | 4,685 | 8,905 | 7 |
| Current GitHub `6e8cd8b` | 22,286 | 3,235 | 5,572 | 105,221 | 14,483 | 26,305 | 18 |
| Local working tree | 18,643 | 2,544 | 4,661 | 127,743 | 17,584 | 31,936 | 18 |

## Current local vs current GitHub

| Metric | Change |
|---|---:|
| `SKILL.md` approximate tokens | 5,572 → 4,661 (**-16.4%**) |
| Installable total approximate tokens | 26,305 → 31,936 (**+21.4%**) |
| `SKILL.md` chars | 22,286 → 18,643 (**-16.3%**) |
| Installable total chars | 105,221 → 127,743 (**+21.4%**) |

Interpretation: after the Google-Testing-Blog round, the always-loaded `SKILL.md` remains ~16% below the older GitHub snapshot while folding in the new research-derived guidance. The full installable package is larger because more tokens now live in references; progressive disclosure remains the main budget control because those reference files are conditional.
