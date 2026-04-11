# Lessons from github.com/karpathy (Andrej Karpathy)

> AI researcher, created nanoGPT, micrograd, minbpe, llm.c.
> Date: 2026-04-11

---

## Who He Is

Andrej Karpathy builds simplified, educational implementations of complex AI systems. His testing philosophy: **use a trusted reference implementation as the test oracle**.

## Differential Testing: PyTorch as Oracle (micrograd)

micrograd is a tiny autograd engine. Tests run the same computation through both micrograd and PyTorch, then compare:

```python
def test_sanity_check():
    # micrograd
    x = Value(-4.0)
    z = 2 * x + 2 + x
    q = z.relu() + z * x
    h = (z * z).relu()
    y = h + q + q * x
    y.backward()
    xmg, ymg = x, y

    # PyTorch
    x = torch.Tensor([-4.0]).double()
    x.requires_grad = True
    z = 2 * x + 2 + x
    q = z.relu() + z * x
    h = (z * z).relu()
    y = h + q + q * x
    y.backward()
    xpt, ypt = x, y

    # Differential assertion
    assert ymg.data == ypt.data.item()
    assert xmg.grad == xpt.grad.item()
```

**Lesson**: When building a simplified implementation, test it against the canonical one. No hand-calculated expected values needed.

## Differential Testing: tiktoken as Oracle (minbpe)

```python
@pytest.mark.parametrize("text", test_strings)
def test_gpt4_tiktoken_equality(text):
    text = unpack(text)
    tokenizer = GPT4Tokenizer()
    enc = tiktoken.get_encoding("cl100k_base")
    tiktoken_ids = enc.encode(text)
    gpt4_tokenizer_ids = tokenizer.encode(text)
    assert gpt4_tokenizer_ids == tiktoken_ids
```

## Roundtrip Identity as Self-Oracle

```python
@pytest.mark.parametrize("tokenizer_factory", [BasicTokenizer, RegexTokenizer, GPT4Tokenizer])
@pytest.mark.parametrize("text", test_strings)
def test_encode_decode_identity(tokenizer_factory, text):
    tokenizer = tokenizer_factory()
    assert tokenizer.decode(tokenizer.encode(text)) == text
```

## Test Data Design

Test strings are carefully chosen:
```python
test_strings = [
    "",                                              # empty
    "?",                                             # single character
    "hello world!!!? (안녕하세요!) lol123 😉",          # Unicode + emoji
    "FILE:taylorswift.txt",                          # real file (bulk content)
]
```

The `FILE:` prefix avoids printing huge files in pytest output while still testing on real-world content.

## Wikipedia-Documented Algorithm as Test Case

```python
def test_wikipedia_example(tokenizer_factory):
    """Following the Wikipedia BPE example: 'aaabdaaabac' with 3 merges → [258, 100, 258, 97, 99]"""
    tokenizer = tokenizer_factory()
    tokenizer.train("aaabdaaabac", 256 + 3)
    ids = tokenizer.encode("aaabdaaabac")
    assert ids == [258, 100, 258, 97, 99]
    assert tokenizer.decode(tokenizer.encode("aaabdaaabac")) == "aaabdaaabac"
```

**Lesson**: When an algorithm is documented on Wikipedia with a worked example, that example becomes an excellent test case.

## Key Insights

1. **Reference implementation as oracle**: test your code against the canonical one (PyTorch, tiktoken)
2. **Roundtrip identity is the fundamental property**: `decode(encode(x)) == x`
3. **Parametrize across implementations AND inputs**: test all tokenizer variants against all test strings
4. **Include real files in test data**: don't just test on toy inputs — include real documents
5. **Use documented algorithms as test cases**: Wikipedia examples are pre-verified
