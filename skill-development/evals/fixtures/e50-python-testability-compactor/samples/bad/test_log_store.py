import time
from log_store import LogStore

def test_compaction(tmp_path):
    path = tmp_path / "log"
    store = LogStore(path)
    for i in range(200):
        store.append(f"r{i}")
    time.sleep(0.5)   # hope the worker ran
    assert "r0" in path.read_text()
