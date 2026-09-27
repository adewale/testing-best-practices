No P0 or P1 dead gates.

- The live tests are reachable: the nightly scheduled lane sets RUN_LIVE, fails if
  STAGING_URL is missing, and fails if any live test skipped (`assert_no_skips.py`).
  The `skipif` only keeps them out of PR runs, which is fine.
- `dependency-audit` is advisory by design with a named owner and an issue on failure;
  that is an acceptable advisory gate. P3: consider a severity threshold so critical
  CVEs block releases.
- P3: PR runs never exercise the live path; if staging drift matters per change, add a
  post-deploy run.
