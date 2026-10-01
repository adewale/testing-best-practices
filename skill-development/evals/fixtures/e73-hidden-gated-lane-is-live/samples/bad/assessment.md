**P0: live tests are dead.** `tests/test_live.py` is skipped unless RUN_LIVE is set, so
these tests never run in CI. Remove the skipif marker so they always run.

**P0: dependency-audit uses continue-on-error**, so pip-audit can never fail the build.
