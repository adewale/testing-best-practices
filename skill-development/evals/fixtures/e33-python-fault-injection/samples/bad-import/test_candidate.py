from report import SaveError, save_report


def test_empty_report():
    try:
        save_report({}, object())
    except SaveError:
        pass
