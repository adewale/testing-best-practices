# E66 — Cost-aware combinatorial portfolio

Design a test portfolio for 15 renderer families, 16 Looks, 21 Palettes, four output formats, five boundaries, and four runtimes. Some combinations are invalid. Pure registry/schema slices are cheap enough to enumerate fully, while cheap in-process tests and expensive browser/hosted tests share the broader matrix. New registry members must enroll automatically, and a known four-factor font/runtime/output/family regression already exists. The blocking budget is ten minutes.

Include exactly one JSON fence with `registry_source` (`production_registry`,
`copied_ids` or `voluntary_flag`), `cheap_slices` (`exhaustive` or `sampled`),
`base_matrix` (`constrained_pairwise`, `unconstrained_pairwise` or `full_product`),
`elevated_group` (a named group of factors from `family`, `look`, `palette`,
`format`, `boundary`, `runtime`, `font`), `retain_fixed_regression` and
`delete_before_comparison` (booleans), and `costs` (a list chosen from `runtime`,
`setup`, `flake`, `maintenance`, `triage`). Explain how you would stay within the
existing budget; do not add jobs, schedules or mutation testing.
