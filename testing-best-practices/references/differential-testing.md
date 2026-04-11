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
