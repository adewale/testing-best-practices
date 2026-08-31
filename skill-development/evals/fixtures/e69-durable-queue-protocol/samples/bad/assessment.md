# Assessment

The incidents come from missing error handling. Wrap the worker body in
`try/except`; on any exception, `RPUSH` the order id back onto the queue. Retry
and requeue alone fully solve the durability problem, so `LPOP` is safe with
that handler.

For acceptance, put the `RPUSH` in a Redis `MULTI` transaction beside the SQL
insert. The Redis transaction will make the database and queue update atomic.
Then retry `payments.charge` if the worker exits. Together these changes
guarantee exactly-once processing and exactly-once charging.

The current happy-path mock test is sufficient after adding one test where
`payments.charge` raises. Leases, ownership tokens, an outbox, idempotency keys,
and crash-point tests would add complexity without improving the guarantee.
