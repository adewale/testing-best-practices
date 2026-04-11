# Mathematical Property Tests

For domain objects with arithmetic operations, test algebraic laws.

## Associativity

```python
@given(a=st.integers(), b=st.integers(), c=st.integers())
def test_addition_is_associative(a, b, c):
    assert (Money(a, "USD") + Money(b, "USD")) + Money(c, "USD") == \
           Money(a, "USD") + (Money(b, "USD") + Money(c, "USD"))
```

## Commutativity

```python
@given(x=st.integers(), y=st.integers())
def test_addition_is_commutative(x, y):
    assert Money(x, "USD") + Money(y, "USD") == Money(y, "USD") + Money(x, "USD")
```

## Distributivity

```python
@given(k=st.integers(min_value=-100, max_value=100),
       a=st.integers(), b=st.integers())
def test_multiplication_distributes_over_addition(k, a, b):
    left = k * (Money(a, "USD") + Money(b, "USD"))
    right = (k * Money(a, "USD")) + (k * Money(b, "USD"))
    assert left == right
```

## Language integration tests

When your object implements operators, test it with the language's builtins:

```python
def test_works_with_sum():
    assert sum([Money(5, "USD"), Money(10, "USD")], Money(0, "USD")) == Money(15, "USD")

def test_works_with_sorted():
    assert sorted([Money(30, "USD"), Money(10, "USD")]) == [Money(10, "USD"), Money(30, "USD")]

def test_works_with_set_membership():
    assert Money(5, "USD") in {Money(5, "USD"), Money(10, "USD")}
```
