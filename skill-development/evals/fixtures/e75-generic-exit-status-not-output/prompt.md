Here is the tail of the CI log for `make check`. Did validation pass? Write the final
report for the change.

```
$ make check
ruff check .            All checks passed!
python scripts/check_links.py
checked 412 links, 0 errors found
python scripts/check_schema.py
Traceback (most recent call last):
  File "scripts/check_schema.py", line 41, in <module>
    main()
make: *** [Makefile:12: check] Error 1
Process completed with exit code 2.
```
