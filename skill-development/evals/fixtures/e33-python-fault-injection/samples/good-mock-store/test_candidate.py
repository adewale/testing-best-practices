from unittest.mock import Mock

import pytest
from report import ReportSaveError, save_report


def test_key_returned_after_recovery():
    store = Mock()
    store.put.side_effect = [ConnectionError(), ConnectionError(), None]
    key = save_report({"rows": [5, 8]}, store)
    assert key == store.put.call_args.args[0]


def test_attempt_budget_ends_in_a_save_error():
    store = Mock()
    store.put.side_effect = ConnectionError
    with pytest.raises(ReportSaveError):
        save_report({"id": "offline"}, store)
    assert store.put.call_count == 3


def test_empty_report_is_invalid():
    with pytest.raises(ValueError):
        save_report({}, Mock())
