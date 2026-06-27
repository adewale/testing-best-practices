# E47 Python KV-store persistence

Module `kvstore`: `KvStore()` holds string keys with values of type str, list, or set, plus an optional per-key TTL (`store.set(k, v, ttl=None)`; `store.items()` yields `(key, value, ttl)` triples in unspecified order). `save(store, path, format=...)` and `load(path, format=...)` support formats 'json' and 'binary'. Add pytest tests for persistence.
