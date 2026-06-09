# Differential Testing and Pirate Testing

## Differential Testing

Test your implementation against a trusted reference implementation. The
reference IS the oracle — no hand-written expected values needed.

### When to use

- Reimplementing a standard algorithm (tokenizer, encoder, hash, parser)
- Building a simplified/educational version of a complex system
- Porting code across languages
- Optimizing a known-correct slow implementation

### Pattern: Same computation, two implementations

```python
# micrograd (Karpathy): test against PyTorch
def test_backward_pass():
    x = Value(-4.0)
    z = 2 * x + 2 + x; y = (z * z).relu(); y.backward()

    xpt = torch.Tensor([-4.0]).double(); xpt.requires_grad = True
    zpt = 2 * xpt + 2 + xpt; ypt = (zpt * zpt).relu(); ypt.backward()

    assert abs(y.data - ypt.data.item()) < 1e-6
    assert abs(x.grad - xpt.grad.item()) < 1e-6
```

### Pattern: Same input, compare outputs

```python
@pytest.mark.parametrize("text", test_strings)
def test_matches_reference(text):
    assert our_tokenizer.encode(text) == tiktoken.get_encoding("cl100k_base").encode(text)
```

### Pattern: Roundtrip as self-differential

```python
@pytest.mark.parametrize("text", test_strings)
def test_roundtrip(text):
    assert tokenizer.decode(tokenizer.encode(text)) == text
```

---

## When no reference exists: build a trivial shadow model

The oracle does not have to be a pre-existing library. For a custom data
structure or stateful component with no canonical implementation, write a
**deliberately dumb reference** that is obviously correct, drive both with the
same seeded random operations, and assert they agree on *every* observable
(return value of each op, size, contents, iteration order). This is
model-based testing: the model trades performance for obvious correctness.

```python
# Test a custom LRU cache against a dict + list shadow model.
import random

def test_lru_matches_shadow_model():
    rng = random.Random(1234)           # seed so a failure is reproducible
    cache = LruCache(capacity=8)
    keys, model = [], {}                  # the "always tells the truth" model
    for _ in range(10_000):
        k = rng.randrange(0, 20)
        if rng.random() < 0.7:           # bias toward writes
            v = rng.randrange(1_000)
            cache.put(k, v)
            model[k] = v
            keys = [x for x in keys if x != k] + [k]
            if len(keys) > 8:            # model the eviction rule independently
                del model[keys.pop(0)]
        else:
            assert cache.get(k) == model.get(k)   # agree on every lookup
    assert sorted(cache.items()) == sorted(model.items())  # and on full contents
```

Keys to make it bite:
- **Seed the RNG explicitly** and print/log the seed; never rely on an
  unseeded global RNG, whose sequence varies by platform and run.
- **Bias toward edge cases** the structure encodes specially (here, evictions;
  for trees, deletes; for nullable values, `None`).
- **Compare multiple observables**, not just "didn't crash."

**When NOT to use it:** if the shadow model would be as complex as the system
under test (or would just reimplement it), skip it — a model that can carry its
own bugs is worse than targeted example/property tests. For a pure function
with a stated algebraic law, a property test is the lighter tool; reach for a
shadow model only when there is real *state* to mirror.

---

## Approximate, probabilistic, or non-deterministic outputs

Exact equality is the wrong oracle for approximate nearest-neighbor search,
sampling, sketches, fuzzy matching, or rankers. Test against a **brute-force
oracle with a statistical threshold**, and separately assert the results you
*do* return are individually correct.

```python
# Approximate k-NN (e.g. an HNSW index) vs. an exact linear scan.
def test_recall_against_brute_force():
    rng = random.Random(42)
    vectors = [random_unit_vector(rng, dim=128) for _ in range(20_000)]
    index = AnnIndex(vectors)
    query = random_unit_vector(rng, dim=128)

    approx = set(index.query(query, k=50))
    exact = set(brute_force_topk(vectors, query, k=50))   # the oracle

    recall = len(approx & exact) / 50
    assert recall >= 0.90, f"recall {recall:.2f} below 0.90 threshold"   # statistical
    for item in approx & exact:                                          # exact-on-overlap
        assert abs(index.score(item, query) - exact_score(item, query)) < 1e-4
```

Discipline that keeps this honest:
- **State the threshold with margin and justify it** (a known-good build's
  recall minus headroom). A threshold of `>= 0.01` is a test that never fails —
  that is a vacuous assertion, not a statistical one. Flag those in review.
- **Pin every seed** so "approximate" never means "flaky."
- **Add an exact mode to the product if you can** (a "give me the true answer"
  flag), so the oracle ships with the code instead of living only in tests.
- **Don't reach for a threshold when the output is actually exact.** A sort, a
  parser, or a deterministic serializer must be asserted with equality;
  replacing that with a recall/closeness threshold *hides* real regressions.

---

## Pirate Testing

Language-neutral conformance tests written as data (JSON/YAML) that multiple
implementations execute via harnesses. No implementation is privileged — the
test data IS the specification.

### How it differs from differential testing

**Differential**: one trusted oracle, asymmetric.
**Pirate**: all implementations are equal peers conforming to shared test data.

### When to use

- Multiple implementations of a spec across languages
- SDKs in several languages that must behave identically
- Open standards needing conformance suites

### Pattern: Data-driven conformance

```json
[
  {"input": "https://example.com:8080/path", "expected": {"scheme": "https", "host": "example.com", "port": 8080, "path": "/path"}}
]
```

Each language loads the same JSON with its own harness.

### Real-world examples

- Twitter text processing (Java + Ruby conformance)
- JSON Schema Test Suite (20+ languages)
- Unicode conformance tests
