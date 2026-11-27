# Streamline the release verifier tests

The existing suite builds the same release directory for every damaged payload.
Rewrite the tests in pytest to reduce repeated setup while preserving what
callers can observe. The release team publishes the three bytes `b"abc"`
(no trailing newline) and this manifest.

```json
{"sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}
```

In `release_verifier`, the public entry point `verify_release(directory)`
reads `manifest.json` and `artifact.bin` from the supplied directory and
returns whether the artifact matches the published SHA-256 digest. The
lower-level `digest_matches(payload, expected)` compares bytes with a
hexadecimal digest. The files exist and the manifest is well formed.

Submit the revised test files. Reuse prepared inputs wherever that helps.
