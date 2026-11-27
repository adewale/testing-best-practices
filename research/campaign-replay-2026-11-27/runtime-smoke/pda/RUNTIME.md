# Local PDA runtime

The source snapshot runs directly on the shared Linux x64 computer with Node 24.22.3. The same locked packages are available to every audit. From this directory run `python attach-runtime.py repo` once for a fresh copy. The attachment uses the package location in `runtime.json`, checks the pinned package-lock hash, creates local dependencies and initializes the Git metadata needed by the native Workers inventory. Each checkout gets its own Vite caches. Use the installed packages as supplied.

Run the native project commands in `task.md` from the repository directory. For example, select a test with `node node_modules/vitest/vitest.mjs run --maxWorkers=1 --config <project-config> <test-file>`. The worker fakes and generated test credentials run locally. Use `WRANGLER_SEND_METRICS=false` and a writable project-specific `XDG_CONFIG_HOME` under the system temp directory for Wrangler's runtime logs.

For another audit directory, copy `task.md`, `inventory.json`, `ci/`, the supplied repository sources and these three runtime files. Run the attachment in the new directory to give it independent caches and Git metadata. A subject needs only its assigned copy and the installed packages.
