# Token Report

Approximation: tokens ~= characters / 4. This is not a model tokenizer; chars and words are included for transparency.

| Version | SKILL.md chars | SKILL.md words | SKILL.md approx tokens | Installable chars | Installable words | Installable approx tokens | Files |
|---|---:|---:|---:|---:|---:|---:|---:|
| First GitHub `6951b7d` | 8,893 | 1,315 | 2,223 | 35,620 | 4,685 | 8,905 | 7 |
| Current GitHub `6e8cd8b` | 22,286 | 3,235 | 5,572 | 105,221 | 14,483 | 26,305 | 18 |
| Local working tree | 10,980 | 1,421 | 2,745 | 95,791 | 12,880 | 23,948 | 18 |

## Current local vs current GitHub

| Metric | Change |
|---|---:|
| `SKILL.md` approximate tokens | 5,572 → 2,745 (**-50.7%**) |
| Installable total approximate tokens | 26,305 → 23,948 (**-9.0%**) |
| `SKILL.md` chars | 22,286 → 10,980 (**-50.7%**) |
| Installable total chars | 105,221 → 95,791 (**-9.0%**) |

Interpretation: the local version cuts the always-loaded `SKILL.md` roughly in half while preserving the same number of reference files. The full installable package is only ~9% smaller because most tokens live in references, but progressive disclosure improves substantially because the entrypoint is much smaller.
