# Executed fixture grading

E08 and E33 run submitted pytest tests against a trusted reference and several
broken behaviors. Passing requires nonempty, non-skipped tests to pass on the
reference and the same tests to fail an assertion for every fault. Comments
containing `clock`, `retry` or `assert` are not evidence.

Build the runner from `skill-development/evals`:

```sh
docker build -f Dockerfile.behavioral-oracles -t tbp-behavioral-oracles:local .
python fixtures/e08-deterministic-time/oracle.py /path/to/candidate
python fixtures/e33-python-fault-injection/oracle.py /path/to/candidate
```

For a custom certificate authority, pass its public bundle with
`--secret id=proxy_ca,src=/path/to/ca-bundle.pem`. Keep TLS verification on.
The base-image digest is an integrity pin. The pytest version comes from the
existing eval requirements rather than a second version setting.

Candidate containers have no network, host credentials or Docker socket mount.
Their work tree is read-only; only an isolated result directory and temporary
filesystem are writable. They run as an unprivileged user with no capabilities
and limits on time, memory, CPU and process count. A missing Docker runner fails
grading rather than running arbitrary candidates on the host. Containment is
not an attestation against a malicious suite deliberately inspecting and gaming
the reference implementation.

`run-fixture-oracles.py` may execute this checkout's declared good/bad samples on
the host with `TBP_TRUSTED_FIXTURE_SELF_TEST=1`. That exception requires an exact
sample path from the fixture manifest. The variable never authorizes an
arbitrary candidate path. Trusted samples need the existing pytest dependency.
