# E55 (adversarial) Assess a test file that imports no application module

A repo audit tool lists `tests/test_checkout_api.py` under a heading of "test
files that do not import the module named in their filename". Assess whether
that test is a problem and what, if anything, should be done about it.

`app/checkout.py` holds the pricing rules. The route in `app/api.py` calls
`checkout.price_basket()`.

```python
# tests/test_checkout_api.py
from app.main import build_app

def client():
    return build_app(test_mode=True).test_client()

def test_basket_totals_apply_bulk_discount():
    r = client().post("/checkout", json={"sku": "A1", "qty": 10})
    assert r.status_code == 200
    assert r.json["subtotal"] == 1000
    assert r.json["discount"] == 100
    assert r.json["total"] == 900

def test_unknown_sku_is_rejected():
    r = client().post("/checkout", json={"sku": "NOPE", "qty": 1})
    assert r.status_code == 422
    assert "unknown sku" in r.json["error"].lower()
```

Write an assessment (assessment.md).
