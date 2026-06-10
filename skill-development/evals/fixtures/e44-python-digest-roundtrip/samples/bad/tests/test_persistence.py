from kvstore import KvStore, save, load

def test_save_load(tmp_path):
    store = KvStore()
    store.set("a", "1")
    save(store, tmp_path / "db", format="json")
    reloaded = load(tmp_path / "db", format="json")
    assert reloaded.get("a") == "1"
