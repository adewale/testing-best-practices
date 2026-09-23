# E67 — Registry-driven enrollment sabotage

Write a small stdlib-only Python conformance harness with this public shape:

- `REGISTRY`: canonical mapping of member IDs to implementations;
- `one_way_cases(registry)`: derives one conformance case per supplied registry member;
- each case exposes `member_id`;
- `contract_passes(case)`: returns whether that member satisfies the contract.

Add unittest tests that assert exact registry/case ID equality. In an isolated registry, inject a deliberately broken fake member, prove it is automatically enrolled, and prove its generated contract fails. Do not use a copied expected-member list or a voluntary `covered` flag.
