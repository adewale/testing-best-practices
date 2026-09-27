The mock and production disagree: MockD1 returns `changes == 1` for a no-match DELETE
but routes.py checks for 0. Since the fidelity test documents D1 behavior, update
routes.py so the duplicate check uses `changes == 1` instead.
