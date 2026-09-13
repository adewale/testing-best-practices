# Assessment

## P0: the implementation has two independent loss/duplication windows

`accept_order` commits the database row and only then calls Redis. That is a
dual-write gap: if `RPUSH` fails, the API has accepted a durable order but no
job exists. In the worker, `LPOP` is a destructive early acknowledgement. A
kill after the pop removes the only job before processing completes. Finally,
the payment can succeed and the worker can die before recording the receipt;
redelivery then repeats an ambiguous external effect and explains the duplicate
charge.

## Minimum durable protocol

Write an outbox row in the same database transaction as the accepted order. A
relay publishes unsent outbox rows to the queue and marks them published;
publishing is retryable and consumers deduplicate by order/event id. This
removes the database-to-Redis atomicity claim—the database transaction covers
the order and its publication intent, not Redis.

Replace `LPOP` with a durable claim/complete protocol. A claim moves the job to
`processing` with an owner/claim token and `lease_until`. Completion/ACK is a
conditional update on job id plus that token; a stale worker whose lease has
expired is fenced out. A reaper reclaims expired leases for redelivery. Renew
long-running work before expiry and cap attempts with a visible dead-letter or
repair state rather than silently dropping it.

Use the stable order id as the payment provider's idempotency key and persist
the resulting receipt. The worker must be safe under at-least-once delivery;
“exactly once” cannot be guaranteed across the database, Redis, payment
provider, and email. Email likewise needs a dedupe key or its own outbox.

## Tests

Keep the happy path, then add deterministic fault injection at each boundary:
after order/outbox commit but before publish; after claim; immediately before
and after the charge; after receipt persistence; and before conditional
completion. Restart the worker and assert eventual completion with one payment
idempotency key. With a fake clock, expire a lease, run two workers, and prove
the stale owner's token cannot complete or overwrite the reclaimed job. Also
test duplicate outbox publication and duplicate delivery. These tests exercise
the protocol; adding a catch-and-requeue block does not.
A Redis transaction cannot make the database write atomic. Retry alone is
insufficient, and this protocol cannot guarantee exactly-once effects across
independent systems.
