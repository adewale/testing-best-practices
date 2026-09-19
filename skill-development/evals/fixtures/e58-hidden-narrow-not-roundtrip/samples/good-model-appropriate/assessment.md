A canonical whole-state comparison is appropriate because save/load must
preserve every persisted field. Narrowing to quota fields would weaken that
contract. Keep this test, and add a separate focused quota test if useful.
