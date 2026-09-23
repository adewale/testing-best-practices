import unittest

from portfolio import (
    REGISTRY,
    OneWayMember,
    contract_passes,
    one_way_cases,
)


class PortfolioConformanceTests(unittest.TestCase):
    def test_registry_and_generated_case_ids_are_exactly_equal(self) -> None:
        case_ids = tuple(case.member_id for case in one_way_cases(REGISTRY))

        self.assertEqual(case_ids, tuple(sorted(REGISTRY)))
        self.assertEqual(len(case_ids), len(set(case_ids)))

    def test_registered_members_pass_the_generated_contract(self) -> None:
        for case in one_way_cases(REGISTRY):
            with self.subTest(member_id=case.member_id):
                self.assertTrue(contract_passes(case))

    def test_broken_fake_is_automatically_enrolled_and_fails(self) -> None:
        isolated_registry = {}

        class BrokenAppender(
            OneWayMember,
            member_id="broken-appender",
            registry=isolated_registry,
        ):
            @staticmethod
            def normalize(value: str) -> str:
                return value + "!"

        self.assertIs(
            isolated_registry[BrokenAppender.member_id],
            BrokenAppender,
        )

        cases = one_way_cases(isolated_registry)
        self.assertEqual(
            {case.member_id for case in cases},
            set(isolated_registry),
        )

        broken_case, = cases
        self.assertFalse(contract_passes(broken_case))


if __name__ == "__main__":
    unittest.main()
