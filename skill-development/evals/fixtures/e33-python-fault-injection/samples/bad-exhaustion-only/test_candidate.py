from unittest.mock import Mock

import pytest
from report import ReportSaveError, save_report


def test_retry_budget_when_service_stays_down():
    store = Mock()
    store.put.side_effect = ConnectionError
    with pytest.raises(ReportSaveError):
        save_report({"id": "example"}, store)
    assert store.put.call_count == 3
