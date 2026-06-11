import random
import re
from textutils import slugify

def shadow_slugify(s):
    # Pointless reimplementation that can carry its own bugs.
    return re.sub(r"\s+", "-", s.strip().lower())

def test_slugify_against_shadow_model():
    rng = random.Random(0)
    alphabet = "AB cd  EF"
    for _ in range(1000):
        s = "".join(rng.choice(alphabet) for _ in range(rng.randrange(10)))
        assert slugify(s) == shadow_slugify(s)
