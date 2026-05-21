# VCR Cassette Testing

For code that calls external APIs, record real responses once and replay them
in tests. Better than hand-written mocks, cheaper than live API calls in CI.

## How it works

1. First run: real HTTP calls, responses recorded to YAML/JSON files
2. Subsequent runs: responses replayed from cassettes — no network needed
3. Cassettes committed to repo alongside tests
4. To update: delete cassette file and re-run

## Python (pytest-recording / VCR.py)

```python
@pytest.mark.vcr
def test_api_call():
    result = call_external_api("query")
    assert result.status == "ok"

# conftest.py — filter sensitive headers
@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["Authorization", "X-API-KEY"]}
```

## TypeScript (msw)

```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.post('https://api.example.com/v1/query', () => {
    return HttpResponse.json({ status: 'ok', data: [1, 2, 3] });
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
```

## When to use

- Any test calling a third-party API (LLM providers, payment, auth)
- API client libraries
- Integration tests where external service is unreliable or paid

## Gotchas

- Cassettes go stale when APIs change — re-record periodically
- Filter credentials before committing
- Large cassettes bloat the repo — keep them focused
