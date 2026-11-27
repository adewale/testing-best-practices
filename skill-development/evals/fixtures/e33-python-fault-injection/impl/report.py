import json
from hashlib import sha256


class ReportSaveError(Exception):
    pass


def save_report(report, store):
    if not report:
        raise ValueError("empty report")
    data = json.dumps(report).encode()
    key = "reports/" + str(report.get("id", sha256(data).hexdigest()))
    for attempt in range(3):
        try:
            store.put(key, data)
            return key
        except ConnectionError as error:
            if attempt == 2:
                raise ReportSaveError("could not save report") from error
