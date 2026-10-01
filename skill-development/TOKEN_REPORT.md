# Token Report

Approximation: tokens ~= characters / 4. This is not a model tokenizer; chars and words are included for transparency.

| Version | SKILL.md chars | SKILL.md words | SKILL.md approx tokens | Installable chars | Installable words | Installable approx tokens | Files |
|---|---:|---:|---:|---:|---:|---:|---:|
| First GitHub `6951b7d` | 8,893 | 1,315 | 2,223 | 35,620 | 4,685 | 8,905 | 7 |
| Historical GitHub `6e8cd8b` | 22,286 | 3,235 | 5,572 | 105,221 | 14,483 | 26,305 | 18 |
| Local working tree | 24,024 | 3,318 | 6,006 | 194,598 | 27,545 | 48,650 | 22 |

## Current local vs historical GitHub

| Metric | Change |
|---|---:|
| `SKILL.md` approximate tokens | 5,572 → 6,006 (**+7.8%**) |
| Installable total approximate tokens | 26,305 → 48,650 (**+84.9%**) |
| `SKILL.md` chars | 22,286 → 24,024 (**+7.8%**) |
| Installable total chars | 105,221 → 194,598 (**+84.9%**) |

Relative to the pre-PR-27/28 baseline `82c6ecc`, `SKILL.md` grows from 20,695 to
24,024 characters, approximately 5,174 to 6,006 tokens (**+16.1%**). This is a
real prompt-cost tradeoff, not evidence of improved agent outcomes. References
load conditionally; the installable total is not the cost of every invocation.
