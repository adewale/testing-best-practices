import unittest
from portfolio import REGISTRY, contract_passes, one_way_cases


def test_exact_shape_only():
    cases = one_way_cases(REGISTRY)
    ids = {case.member_id for case in cases}
    self.assertEqual(ids, set(REGISTRY))


def test_sabotage_shape_only():
    isolated = dict(REGISTRY)
    fake_id = "fake"
    isolated[fake_id] = "BROKEN"
    cases = one_way_cases(isolated)
    ids = {case.member_id for case in cases}
    self.assertEqual(ids, set(isolated))
    selected = next(case for case in cases if case.member_id == fake_id)
    self.assertFalse(contract_passes(selected))
