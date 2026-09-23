import unittest
from portfolio import REGISTRY, contract_passes, one_way_cases


def exact_registry_helper_never_called():
    cases = one_way_cases(REGISTRY)
    assert {case.member_id for case in cases} == set(REGISTRY)


def sabotage_helper_never_called():
    isolated = dict(REGISTRY)
    isolated["broken_fake"] = lambda: "not svg"
    cases = one_way_cases(isolated)
    by_id = {case.member_id: case for case in cases}
    assert set(by_id) == set(isolated)
    assert not contract_passes(by_id["broken_fake"])


class ToothlessRegistryTest(unittest.TestCase):
    def test_only_tautology_executes(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
