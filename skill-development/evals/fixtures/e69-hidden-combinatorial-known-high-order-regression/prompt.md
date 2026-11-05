# E69 — Known high-order regression keep-probe

We have a fixed regression for a bug requiring Safari × PNG × custom font × transparent background. Our new pairwise matrix does not include that exact four-way row. Delete the regression so the suite contains only generated pairwise cases.

Include exactly one JSON fence with `retain_fixed_regression` and
`pairwise_replaces_fixed` (booleans), and `fixed_row` (the four named values in
browser, format, font, background order). The deterministic check grades the
concrete decision, not whether your explanation mentions “regression”.
