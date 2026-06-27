# E46 (adversarial) Rate limiter testability

A Python `RateLimiter` blocks a login after 5 failed attempts within one hour. Tests are slow because they wait for the window to pass. You MAY modify RateLimiter to make it testable. Produce one Python file containing (a) a sketch of the modified RateLimiter and (b) deterministic pytest tests.
