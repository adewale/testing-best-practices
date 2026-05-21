# E19 Order Pollution Fixture

Tests pass alone but fail when run after plugin tests because a global registry or environment variable is mutated without cleanup. Diagnose and fix the test-quality problem.
