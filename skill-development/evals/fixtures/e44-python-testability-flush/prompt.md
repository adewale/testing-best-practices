# E41 Python write-buffer testability

`WriteBuffer(path)` batches `write(record)` calls in memory; a background thread flushes them to the file every 5 seconds. The current test calls `time.sleep(6)` and is slow and flaky. You MAY modify WriteBuffer to make it testable. Produce one Python file containing (a) a sketch of the modified WriteBuffer and (b) deterministic pytest tests.
