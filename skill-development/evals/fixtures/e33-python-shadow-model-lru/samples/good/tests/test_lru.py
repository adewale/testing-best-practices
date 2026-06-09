import random
from lru import LruCache

def test_lru_matches_shadow_model():
    rng = random.Random(1234)            # seed: failures replay exactly
    cache = LruCache(capacity=8)
    order, model = [], {}                 # trivial "always tells the truth" model
    for _ in range(5000):
        k = rng.randrange(20)
        if rng.random() < 0.7:            # bias toward writes / evictions
            v = rng.randrange(1000)
            cache.put(k, v); model[k] = v
            order = [x for x in order if x != k] + [k]
            if len(order) > 8:
                del model[order.pop(0)]
        else:
            assert cache.get(k) == model.get(k)        # agree on every lookup
    assert sorted(cache.items()) == sorted(model.items())  # and full contents
    assert len(cache) == len(model)
