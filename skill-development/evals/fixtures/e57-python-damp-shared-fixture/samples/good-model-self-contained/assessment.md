The computed expectation mirrors the implementation rule, while the loop and
branch obscure which behavior failed. The `setUpClass` mutation also creates
shared mutable state and order coupling. Replace the global fixture and loop
with focused, self-contained tests whose local account data uses independent
expected results.
