import unittest
from portfolio import REGISTRY, contract_passes, one_way_cases


class RegistryEnrollmentTest(unittest.TestCase):
    def test_exact_registry_members_are_enrolled(self):
        self.assertEqual(
            {case.member_id for case in one_way_cases(REGISTRY)},
            set(REGISTRY),
        )

    def test_broken_fake_is_auto_enrolled_and_bites(self):
        isolated = dict(REGISTRY)
        isolated["broken_fake"] = lambda: "not svg"
        cases = one_way_cases(isolated)
        by_id = {case.member_id: case for case in cases}
        self.assertEqual(set(by_id), set(isolated))
        self.assertFalse(contract_passes(by_id["broken_fake"]))


if __name__ == "__main__":
    unittest.main()
