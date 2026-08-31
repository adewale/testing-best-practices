# Assessment

The property has a strong generator because arbitrary bytes cover the broadest
possible input domain. The only problem is that 10,000 examples are not enough
to get lucky past all the PNG checks.

Raise `max_examples` to one million and increase `max_size` to 10 MB. Remove the
signature assumption so Hypothesis sees even more inputs. To preserve the
never-crashes property, catch `Exception` (or `BaseException`) around
`decode_png`; malformed input is expected and no exception should fail the
test.

A special PNG builder would narrow the domain and duplicate parser logic, so
arbitrary bytes are sufficient and are the right generator. The zero-coverage
lines should eventually become covered once CI runs enough examples.
