import time
from write_buffer import WriteBuffer

def test_background_flush(tmp_path):
    path = tmp_path / "out.log"
    buf = WriteBuffer(path)
    buf.write("a")
    time.sleep(6)   # wait for the background thread, hopefully
    assert "a" in path.read_text()
