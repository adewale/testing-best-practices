The nightly scheduled lane sets RUN_LIVE and fails when a live test skips, so the live
tests are exercised.

**P0: pip-audit job has `continue-on-error: true`** — an always-green gate; remove it.
