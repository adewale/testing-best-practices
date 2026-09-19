The loop and branch hide which case fails, and `balance * 0.1` mirrors the
production rule instead of providing an independent expected result. The
module-level accounts list mutated in `setUpClass` is shared mutable state.
Use fresh, local fixtures and parameterized tests so each account is a named
case with an independently reviewed expected value.
