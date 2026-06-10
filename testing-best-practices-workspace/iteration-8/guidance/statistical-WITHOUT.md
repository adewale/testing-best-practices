# Differential Testing and Pirate Testing

## Differential Testing

Test your implementation against a trusted reference implementation. The
reference IS the oracle — no hand-written expected values needed.

### When to use

- Reimplementing a standard algorithm (tokenizer, encoder, hash, parser)
- Building a simplified/educational version of a complex system
- Porting code across languages
- Optimizing a known-correct slow implementation

### When NOT to use it

If you would have to *write* the reference yourself and it would just be the
obvious one-line reimplementation of the code under test (a trivial pure
function like `slugify`, `clamp`, a small formatter), do not. That reference
duplicates the implementation, can carry its own bugs, and proves nothing the
code doesn't already say. Use pinned example cases plus a property
(idempotence, roundtrip, an invariant) instead. Reach for a written reference
only when it is *independently* trustworthy — a different algorithm, a spec, an
existing library, or a brute-force oracle for an approximate result.

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
