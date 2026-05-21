def test_api_client(monkeypatch):
    monkeypatch.setattr('requests.get', lambda url: {'status': 200, 'data': []})
    result = call_api('/users')
    assert result is not None
