import json


class ReportSaveError(Exception):
    pass


def save_report(report, store):
    if not report:
        raise ValueError("empty report")
    key = "reports/" + str(report["id"])
    data = json.dumps(report).encode()
    for attempt in range(3):
        try:
            store.put(key, data)
            return key
        except ConnectionError as error:
            if attempt == 2:
                raise ReportSaveError("could not save report") from error
