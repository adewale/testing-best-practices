from textutils import slugify

def test_examples():
    assert slugify("Hello World") == "hello-world"
    assert slugify("  A  B  ") == "a-b"
    assert slugify("Already-Slug") == "already-slug"

def test_idempotent():
    # A property is the light tool here, not a parallel model.
    assert slugify(slugify("Mixed   Case Text")) == slugify("Mixed   Case Text")
