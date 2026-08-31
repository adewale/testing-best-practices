# Audit this queue worker

Write an `assessment.md` for this implementation and its tests. The service
requirement is: an accepted order must eventually be processed, and a retry
must not charge the customer twice.

`orders/api.py`:

```python
async def accept_order(request, db, redis):
    order = Order.from_request(request)
    async with db.transaction():
        await db.execute(
            "INSERT INTO orders(id, status, amount) VALUES (?, 'accepted', ?)",
            order.id,
            order.amount,
        )

    await redis.rpush("orders:pending", order.id)
    return {"id": order.id, "status": "accepted"}
```

`orders/worker.py`:

```python
async def run_once(db, redis, payments, email):
    raw_id = await redis.lpop("orders:pending")
    if raw_id is None:
        return False

    order = await db.fetch_order(raw_id.decode())
    receipt = await payments.charge(order.customer_id, order.amount)
    await db.execute(
        "UPDATE orders SET status = 'paid', receipt_id = ? WHERE id = ?",
        receipt.id,
        order.id,
    )
    await email.send_receipt(order.customer_id, receipt.id)
    return True
```

`tests/test_worker.py`:

```python
async def test_worker_processes_order(redis, db, payments, email):
    await redis.rpush("orders:pending", "ord-7")
    await db.insert_order("ord-7", customer_id="cus-3", amount=500)

    assert await run_once(db, redis, payments, email)

    assert payments.charge.await_count == 1
    assert (await db.fetch_order("ord-7")).status == "paid"
    email.send_receipt.assert_awaited_once()
```

Operations reports two rare incidents: an `accepted` order that never ran
after Redis was unavailable, and a customer charged twice after a worker was
killed during deployment. Workers may run concurrently and may be terminated
at any instruction.
